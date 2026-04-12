from fastapi import APIRouter
from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService
from app.model.http_metadata_inventory_model import (
    ScrapeMetadataRequest,
    ScrapeMetadataResponse,
    FetchMetadataRequest,
    FetchMetadataResponse
)

router = APIRouter(prefix="/metadata_inventory")


@router.get("/")
def startup():
    return {
        "status": 200,
        "message": "Successfull startup",
    }

@router.post("/scrape")
def scrape_metadata(request: ScrapeMetadataRequest):
    
    service = HTTPMetadataInventoryService()

    response: ScrapeMetadataResponse = service.scrape_metadata(request = request)

    return response

@router.get("/fetch")
def fetch_metadata(url: str):

    service = HTTPMetadataInventoryService()

    request = ScrapeMetadataRequest(
        url=url
    )

    response: ScrapeMetadataResponse = service.scrape_metadata(request = request)

    return response

