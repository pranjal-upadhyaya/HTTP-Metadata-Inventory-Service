from fastapi import APIRouter
from fastapi.responses import JSONResponse
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

    service_response: ScrapeMetadataResponse = await service.scrape_metadata(request=request)

    response = JSONResponse(
        content=service_response.model_dump()
    )

    return response


@router.get("/fetch")
async def fetch_metadata(url: str):
    service = HTTPMetadataInventoryService()

    request = FetchMetadataRequest(url=url)

    service_response: FetchMetadataResponse = await service.fetch_metadata(request=request)

    if service_response.metadata_available:
        return JSONResponse(
            content=service_response.model_dump()
        )
    
    response = JSONResponse(
            content=None,
            status_code=202
        )

    return response

