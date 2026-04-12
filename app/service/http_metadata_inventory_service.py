import requests
from app.model.http_metadata_inventory_model import (
    FetchMetadataRequest,
    FetchMetadataResponse,
    ScrapeMetadataRequest,
    ScrapeMetadataResponse
)

class HTTPMetadataInventoryService:

    def __init__(self) -> None:
        pass


    def scrape_metadata(self, request: ScrapeMetadataRequest):
        response = requests.get(url= request.url)

        page_source = response.text

        cookies = response.cookies.get_dict()

        response = ScrapeMetadataResponse(
            url=request.url,
            page_source=page_source,
            cookies=cookies
        )

        return response

    def fetch_metadata(self, request: FetchMetadataRequest):
        
        scrape_request = ScrapeMetadataRequest(url=request.url)

        scrape_response: ScrapeMetadataResponse = self.scrape_metadata(scrape_request)

        response = FetchMetadataResponse.model_validate(
            scrape_response.model_dump()
        )

        return response

