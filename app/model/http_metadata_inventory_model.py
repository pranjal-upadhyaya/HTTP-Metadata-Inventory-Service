from pydantic import BaseModel, HttpUrl, field_validator


class MetadataInventoryMixin(BaseModel):
    url: str
    headers: dict
    page_source: str
    cookies: dict


class ScrapeMetadataRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        HttpUrl(v)
        return v


class ScrapeMetadataResponse(MetadataInventoryMixin):
    pass


class FetchMetadataRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        HttpUrl(v)
        return v


class FetchMetadataResponse(BaseModel):
    metadata: MetadataInventoryMixin | None
    metadata_available: bool
