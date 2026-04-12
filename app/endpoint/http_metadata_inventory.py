from fastapi import APIRouter
from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService
from app.model.http_metadata_inventory_model import (
    ScrapeMetadataRequest,
    ScrapeMetadataResponse,
    FetchMetadataRequest,
    FetchMetadataResponse
)

router = APIRouter(
    prefix="/metadata_inventory",
    tags=["Metadata Inventory"]
)


@router.get("/")
def startup():
    return {
        "status": 200,
        "message": "Successfull startup",
    }

@router.post("/scrape")
async def scrape_metadata(request: ScrapeMetadataRequest):
    service = HTTPMetadataInventoryService()

    response: ScrapeMetadataResponse = await service.scrape_metadata(request=request)

    return response


@router.get("/fetch")
async def fetch_metadata(url: str):
    service = HTTPMetadataInventoryService()

    request = FetchMetadataRequest(url=url)

    response: FetchMetadataResponse = await service.fetch_metadata(request=request)

    return response

