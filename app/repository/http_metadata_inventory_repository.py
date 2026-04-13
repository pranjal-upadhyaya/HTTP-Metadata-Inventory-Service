from beanie import PydanticObjectId

from db.schema.http_metadata_inventory_schema import MetadataInventory


class HTTPMetadataInventoryRepository:
    def __init__(self) -> None:
        pass

    async def insert_metadata(self, doc: dict) -> PydanticObjectId:
        metadata_inventory = MetadataInventory.model_validate(doc)

        await metadata_inventory.insert()

        return metadata_inventory.id

    async def get_metadata_by_url(self, url: str) -> MetadataInventory | None:
        metadata_inventory = await MetadataInventory.find_one(
            MetadataInventory.url == url
        )

        return metadata_inventory
