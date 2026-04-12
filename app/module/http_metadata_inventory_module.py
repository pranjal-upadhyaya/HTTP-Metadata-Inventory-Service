from functools import lru_cache

from app.service.http_metadata_inventory_service import HTTPMetadataInventoryService


@lru_cache
def get_service() -> HTTPMetadataInventoryService:
    return HTTPMetadataInventoryService()
