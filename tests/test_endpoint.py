from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
import requests as req_lib
from fastapi import FastAPI
from pymongo.errors import DuplicateKeyError
from starlette.testclient import TestClient

from app.endpoint.http_metadata_inventory import router
from app.model.http_metadata_inventory_model import (
    FetchMetadataResponse,
    MetadataInventoryMixin,
    ScrapeMetadataResponse,
)
from app.utility.error_handling.exceptions import ServiceError
from app.utility.error_handling.handlers import service_error_handler, unhandled_exception_handler

MOCK_METADATA = {
    "url": "https://example.com",
    "headers": {"Content-Type": "text/html"},
    "page_source": "<html></html>",
    "cookies": {},
}


@asynccontextmanager
async def _mock_lifespan(_app: FastAPI):
    yield


@pytest.fixture
def client():
    test_app = FastAPI(lifespan=_mock_lifespan)
    test_app.include_router(router)
    test_app.add_exception_handler(ServiceError, service_error_handler)
    test_app.add_exception_handler(Exception, unhandled_exception_handler)
    with TestClient(test_app) as c:
        yield c


class TestScrapeEndpoint:

    def test_scrape_success(self, client):
        mock_response = ScrapeMetadataResponse(**MOCK_METADATA)
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.scrape_metadata = AsyncMock(return_value=mock_response)
            response = client.post(
                "/metadata_inventory/scrape",
                json={"url": "https://example.com"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["url"] == "https://example.com"
        assert body["data"]["page_source"] == "<html></html>"
        assert body["data"]["headers"] == {"Content-Type": "text/html"}

    def test_scrape_invalid_url_returns_422(self, client):
        response = client.post(
            "/metadata_inventory/scrape",
            json={"url": "not-a-valid-url"},
        )
        assert response.status_code == 422

    def test_scrape_url_fetch_error_returns_502(self, client):
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.scrape_metadata = AsyncMock(
                side_effect=req_lib.exceptions.ConnectionError("connection refused")
            )
            response = client.post(
                "/metadata_inventory/scrape",
                json={"url": "https://example.com"},
            )
        assert response.status_code == 502
        assert "https://example.com" in response.json()["message"]

    def test_scrape_timeout_returns_502(self, client):
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.scrape_metadata = AsyncMock(
                side_effect=req_lib.exceptions.Timeout()
            )
            response = client.post(
                "/metadata_inventory/scrape",
                json={"url": "https://example.com"},
            )
        assert response.status_code == 502

    def test_scrape_duplicate_url_returns_409(self, client):
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.scrape_metadata = AsyncMock(
                side_effect=DuplicateKeyError("duplicate key error", 11000, {})
            )
            response = client.post(
                "/metadata_inventory/scrape",
                json={"url": "https://example.com"},
            )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"]


class TestFetchEndpoint:

    def test_fetch_metadata_found_returns_200(self, client):
        mock_response = FetchMetadataResponse(
            metadata_available=True,
            metadata=MetadataInventoryMixin(**MOCK_METADATA),
        )
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.fetch_metadata = AsyncMock(return_value=mock_response)
            response = client.get(
                "/metadata_inventory/fetch",
                params={"url": "https://example.com"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["metadata_available"] is True
        assert body["data"]["metadata"]["url"] == "https://example.com"

    def test_fetch_metadata_not_found_returns_202(self, client):
        mock_response = FetchMetadataResponse(metadata_available=False, metadata=None)
        with patch("app.endpoint.http_metadata_inventory.HTTPMetadataInventoryService") as MockService:
            MockService.return_value.fetch_metadata = AsyncMock(return_value=mock_response)
            response = client.get(
                "/metadata_inventory/fetch",
                params={"url": "https://example.com"},
            )
        assert response.status_code == 202
        assert response.json()["message"] == "Url metadata request logged"

    def test_fetch_invalid_url_returns_400(self, client):
        response = client.get(
            "/metadata_inventory/fetch",
            params={"url": "not-a-valid-url"},
        )
        assert response.status_code == 400
        assert "not-a-valid-url" in response.json()["message"]
