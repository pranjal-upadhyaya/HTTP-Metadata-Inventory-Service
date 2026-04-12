from ast import Pass
from typing import Optional
from pydantic import BaseModel

class MetadataInventoryMixin(BaseModel):
    url: str
    page_source: str
    cookies: dict

class ScrapeMetadataRequest(BaseModel):
    url: str

class ScrapeMetadataResponse(MetadataInventoryMixin):
    pass

class FetchMetadataRequest(BaseModel):
    url: str

class FetchMetadataResponse(BaseModel):
    metadata: Optional[MetadataInventoryMixin]
    metadata_available: bool