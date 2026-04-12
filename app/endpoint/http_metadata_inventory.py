import requests

from fastapi import APIRouter
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService
from app.model.http_metadata_inventory_model import (
    ScrapeMetadataRequest,
    ScrapeMetadataResponse,
    FetchMetadataRequest,
    FetchMetadataResponse
)
from app.utility.api_utility.api_response_utility import JSONResponse
from app.utility.error_handling.exceptions import DuplicateURLError, InvalidURLError, URLFetchError

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

    try:
        service_response: ScrapeMetadataResponse = await service.scrape_metadata(request=request)
    except requests.exceptions.RequestException as e:
        raise URLFetchError(url=str(request.url), reason=str(e))
    except DuplicateKeyError:
        raise DuplicateURLError(url=str(request.url))

    return JSONResponse(
        data=service_response,
        message=None,
    )


@router.get("/fetch")
async def fetch_metadata(url: str):
    service = HTTPMetadataInventoryService()

    try:
        request = FetchMetadataRequest(url=url)
    except ValidationError:
        raise InvalidURLError(url=url)

    service_response: FetchMetadataResponse = await service.fetch_metadata(request=request)

    if service_response.metadata_available:
        return JSONResponse(
            data=service_response,
            message=None
        )

    return JSONResponse(
        data=None,
        message="Url metadata request logged",
        status_code=202
    )

