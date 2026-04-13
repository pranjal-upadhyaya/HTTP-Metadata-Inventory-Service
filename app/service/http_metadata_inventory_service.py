import asyncio
import httpx
from app.model.http_metadata_inventory_model import (
    MetadataInventoryMixin,
    FetchMetadataRequest,
    FetchMetadataResponse,
    ScrapeMetadataRequest,
    ScrapeMetadataResponse
)

from app.repository.http_metadata_inventory_repository import HTTPMetadataInventoryRepository
from app.config import app_config

from loguru import logger

class HTTPMetadataInventoryService:

    def __init__(self) -> None:
        self.repository = HTTPMetadataInventoryRepository()


    async def scrape_metadata(self, request: ScrapeMetadataRequest) -> ScrapeMetadataResponse:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=str(request.url), timeout=app_config.http_request_timeout_s)

        page_source = response.text

        headers = dict(response.headers)

        cookies = dict(response.cookies)

        response = ScrapeMetadataResponse(
            url=request.url,
            headers=headers,
            page_source=page_source,
            cookies=cookies
        )

        await self.repository.insert_metadata(response.model_dump())
        logger.info("Stored scraped metadata for url: {}", request.url)

        return response

    async def fetch_metadata(self, request: FetchMetadataRequest) -> FetchMetadataResponse:
        repository_response = await self.repository.get_metadata_by_url(
            url=request.url
        )

        if repository_response:
            logger.info("Existing metadata found for url: {}", request.url)
            return FetchMetadataResponse(
                metadata_available=True,
                metadata=MetadataInventoryMixin.model_validate(
                    repository_response.model_dump()
                )
            )

        logger.info("Existing metadata not found for url: {}", request.url)

        scrape_request = ScrapeMetadataRequest(url=request.url)

        async def _run_background_scrape() -> None:
            try:
                await self.scrape_metadata(scrape_request)
            except httpx.TimeoutException:
                logger.error("Background scrape timed out for url: {}", scrape_request.url)
            except httpx.RequestError as e:
                logger.error("Background scrape failed for url {}: {}", scrape_request.url, str(e))
            except Exception as e:
                logger.error("Unexpected error during background scrape for url {}: {}", scrape_request.url, str(e))

        asyncio.create_task(_run_background_scrape())

        return FetchMetadataResponse(
            metadata=None,
            metadata_available=False
        )

