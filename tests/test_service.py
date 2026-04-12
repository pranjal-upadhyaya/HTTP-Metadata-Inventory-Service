from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests as req_lib

from app.model.http_metadata_inventory_model import (
    FetchMetadataRequest,
    FetchMetadataResponse,
    ScrapeMetadataRequest,
    ScrapeMetadataResponse,
)
from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService

MOCK_URL = "https://example.com"

MOCK_METADATA = {
    "url": MOCK_URL,
    "headers": {"Content-Type": "text/html"},
    "page_source": "<html></html>",
    "cookies": {},
}


@pytest.fixture
def service():
    with patch("app.service.http_metadata_inventory_service.HTTPMetadataInventoryRepository"):
        yield HTTPMetadataInventoryService()


class TestScrapeMetadata:

    async def test_scrape_success(self, service):
        mock_http_response = MagicMock()
        mock_http_response.text = "<html></html>"
        mock_http_response.headers = {"Content-Type": "text/html"}
        mock_http_response.cookies.get_dict.return_value = {}

        service.repository.insert_metadata = AsyncMock(return_value="mock_id")

        with patch("requests.get", return_value=mock_http_response):
            result = await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

        assert isinstance(result, ScrapeMetadataResponse)
        assert result.url == MOCK_URL
        assert result.page_source == "<html></html>"
        assert result.headers == {"Content-Type": "text/html"}
        assert result.cookies == {}
        service.repository.insert_metadata.assert_called_once()

    async def test_scrape_stores_correct_payload(self, service):
        mock_http_response = MagicMock()
        mock_http_response.text = "<html>test</html>"
        mock_http_response.headers = {"X-Custom": "value"}
        mock_http_response.cookies.get_dict.return_value = {"session": "abc"}

        service.repository.insert_metadata = AsyncMock(return_value="mock_id")

        with patch("requests.get", return_value=mock_http_response):
            await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

        call_arg = service.repository.insert_metadata.call_args[0][0]
        assert call_arg["url"] == MOCK_URL
        assert call_arg["page_source"] == "<html>test</html>"
        assert call_arg["headers"] == {"X-Custom": "value"}
        assert call_arg["cookies"] == {"session": "abc"}

    async def test_scrape_timeout_propagates(self, service):
        with patch("requests.get", side_effect=req_lib.exceptions.Timeout()):
            with pytest.raises(req_lib.exceptions.Timeout):
                await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

    async def test_scrape_connection_error_propagates(self, service):
        with patch("requests.get", side_effect=req_lib.exceptions.ConnectionError()):
            with pytest.raises(req_lib.exceptions.ConnectionError):
                await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))


class TestFetchMetadata:

    async def test_fetch_found_returns_metadata(self, service):
        mock_doc = MagicMock()
        mock_doc.model_dump.return_value = MOCK_METADATA
        service.repository.get_metadata_by_url = AsyncMock(return_value=mock_doc)

        result = await service.fetch_metadata(FetchMetadataRequest(url=MOCK_URL))

        assert isinstance(result, FetchMetadataResponse)
        assert result.metadata_available is True
        assert result.metadata.url == MOCK_URL
        assert result.metadata.headers == {"Content-Type": "text/html"}

    async def test_fetch_not_found_returns_metadata_unavailable(self, service):
        service.repository.get_metadata_by_url = AsyncMock(return_value=None)

        with patch("asyncio.create_task"):
            result = await service.fetch_metadata(FetchMetadataRequest(url=MOCK_URL))

        assert result.metadata_available is False
        assert result.metadata is None

    async def test_fetch_not_found_schedules_background_task(self, service):
        service.repository.get_metadata_by_url = AsyncMock(return_value=None)

        with patch("asyncio.create_task") as mock_create_task:
            await service.fetch_metadata(FetchMetadataRequest(url=MOCK_URL))

        mock_create_task.assert_called_once()

    async def test_fetch_not_found_does_not_block_on_scrape(self, service):
        import asyncio

        service.repository.get_metadata_by_url = AsyncMock(return_value=None)
        scrape_started = []

        async def slow_scrape(req):
            scrape_started.append(True)
            await asyncio.sleep(10)

        service.scrape_metadata = slow_scrape

        # Should return immediately; slow_scrape is only scheduled, not awaited
        result = await service.fetch_metadata(FetchMetadataRequest(url=MOCK_URL))
        assert result.metadata_available is False
        assert not scrape_started
