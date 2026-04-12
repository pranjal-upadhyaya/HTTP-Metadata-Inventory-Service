import asyncio
import requests
from app.model.http_metadata_inventory_model import (
    MetadataInventoryMixin,
    FetchMetadataRequest,
    FetchMetadataResponse,
    ScrapeMetadataRequest,
    ScrapeMetadataResponse
)

from app.repository.http_metadata_inventory_repository import HTTPMetadataInventoryRepository

from loguru import logger

class HTTPMetadataInventoryService:

    def __init__(self) -> None:
        self.repository = HTTPMetadataInventoryRepository()


    async def scrape_metadata(self, request: ScrapeMetadataRequest):
        response = requests.get(url=request.url)

        page_source = response.text

        headers = dict(response.headers)

        cookies = response.cookies.get_dict()

        response = ScrapeMetadataResponse(
            url=request.url,
            headers=headers,
            page_source=page_source,
            cookies=cookies
        )

        await self.repository.insert_metadata(response.model_dump())
        logger.info("Stored scraped metadata for url: {}", request.url)

        return response

    async def fetch_metadata(self, request: FetchMetadataRequest):
        repository_response = await self.repository.get_metadata_by_url(
            url=request.url
        )

        if repository_response:
            logger.info("Existing metadata found for url: {}", request.url)
            return FetchMetadataResponse(
                metadata_available=True,
                metadata=  MetadataInventoryMixin.model_validate(
                    repository_response.model_dump()
                )
            )

        logger.info("Existing metadata not found for url: {}", request.url)

        scrape_request = ScrapeMetadataRequest(url=request.url)

        asyncio.create_task(
            self.scrape_metadata(scrape_request)
        )

        return FetchMetadataResponse(
            metadata=None,
            metadata_available=False
        )

