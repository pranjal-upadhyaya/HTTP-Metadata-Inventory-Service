import httpx

from fastapi import APIRouter, Depends
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from app.module.http_metadata_inventory_module import get_service
from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService
from app.model.http_metadata_inventory_model import (
    ScrapeMetadataRequest,
    ScrapeMetadataResponse,
    FetchMetadataRequest,
    FetchMetadataResponse
)
from app.utility.api_utility.api_response_utility import JSONResponse, Response
from app.utility.error_handling.exceptions import DuplicateURLError, InvalidURLError, URLFetchError

router = APIRouter(
    prefix="/metadata_inventory",
    tags=["Metadata Inventory"]
)


@router.post("/scrape", response_model=Response[ScrapeMetadataResponse])
async def scrape_metadata(
    request: ScrapeMetadataRequest,
    service: HTTPMetadataInventoryService = Depends(get_service)
) -> JSONResponse:

    try:
        service_response: ScrapeMetadataResponse = await service.scrape_metadata(request=request)
    except httpx.RequestError as e:
        raise URLFetchError(url=str(request.url), reason=str(e))
    except DuplicateKeyError:
        raise DuplicateURLError(url=str(request.url))

    return JSONResponse(
        data=service_response,
        message=None,
    )


@router.get("/fetch", response_model=Response[FetchMetadataResponse])
async def fetch_metadata(
    url: str,
    service: HTTPMetadataInventoryService = Depends(get_service)
) -> JSONResponse:

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

