from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

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


def _make_mock_http_response(text="<html></html>", headers=None, cookies=None):
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.text = text
    mock_response.headers = headers or {"Content-Type": "text/html"}
    mock_response.cookies = cookies or {}
    return mock_response


class TestScrapeMetadata:

    async def test_scrape_success(self, service):
        mock_response = _make_mock_http_response()
        service.repository.insert_metadata = AsyncMock(return_value="mock_id")

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

        assert isinstance(result, ScrapeMetadataResponse)
        assert result.url == MOCK_URL
        assert result.page_source == "<html></html>"
        assert result.headers == {"Content-Type": "text/html"}
        assert result.cookies == {}
        service.repository.insert_metadata.assert_called_once()

    async def test_scrape_stores_correct_payload(self, service):
        mock_response = _make_mock_http_response(
            text="<html>test</html>",
            headers={"X-Custom": "value"},
            cookies={"session": "abc"},
        )
        service.repository.insert_metadata = AsyncMock(return_value="mock_id")

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

        call_arg = service.repository.insert_metadata.call_args[0][0]
        assert call_arg["url"] == MOCK_URL
        assert call_arg["page_source"] == "<html>test</html>"
        assert call_arg["headers"] == {"X-Custom": "value"}
        assert call_arg["cookies"] == {"session": "abc"}

    async def test_scrape_timeout_propagates(self, service):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException(""))
        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            with pytest.raises(httpx.TimeoutException):
                await service.scrape_metadata(ScrapeMetadataRequest(url=MOCK_URL))

    async def test_scrape_connection_error_propagates(self, service):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            with pytest.raises(httpx.ConnectError):
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

        result = await service.fetch_metadata(FetchMetadataRequest(url=MOCK_URL))
        assert result.metadata_available is False
        assert not scrape_started
