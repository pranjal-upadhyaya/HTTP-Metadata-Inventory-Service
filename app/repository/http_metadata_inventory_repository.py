from typing import Optional

from beanie import PydanticObjectId
from db.connection_manager import ConnectionManager
from app.config import app_config

from db.schema.http_metadata_inventory_schema import MetadataInventory


class HTTPMetadataInventoryRepository:

    def __init__(self) -> None:
        connection = ConnectionManager()
        self.db = app_config.db_name
        self.collection = app_config.metadata_inventory_collection
        self.client = connection.get_async_client()

    async def insert_metadata(self, doc: dict) -> PydanticObjectId:

        metadata_inventory = MetadataInventory.model_validate(doc)

        await metadata_inventory.insert()
        
        return metadata_inventory.id

    async def get_metadata_by_url(self, url: str) -> Optional[MetadataInventory]:

        metadata_inventory = await MetadataInventory.find_one(
            MetadataInventory.url == url
        )

        return metadata_inventory