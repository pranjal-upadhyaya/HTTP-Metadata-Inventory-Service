from ast import Pass
from pydantic import BaseModel

class ScrapeMetadataRequest(BaseModel):
    url: str

class ScrapeMetadataResponse(BaseModel):
    url: str
    page_source: str
    cookies: dict

class FetchMetadataRequest(BaseModel):
    url: str

class FetchMetadataResponse(BaseModel):
    url: str
    page_source: str
    cookies: dict