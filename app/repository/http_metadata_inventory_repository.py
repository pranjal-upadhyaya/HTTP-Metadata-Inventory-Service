from db.connection_manager import ConnectionManager
from app.config import app_config


class HTTPMetadataInventoryRepository:

    def __init__(self) -> None:
        connection = ConnectionManager()
        self.db = app_config.db_name
        self.collection = app_config.metadata_inventory_collection
        self.client = connection.get_client()

    def insert_metadata(self, doc: dict):
        db = self.client[self.db]
        col = db[self.collection]
        
        output = col.insert_one(
            document=doc
        )
        return output.inserted_id

    def get_metadata_by_url(self, url: str):

        db = self.client[self.db]
        col = db[self.collection]

        query = {
            "url": url
        }

        output = col.find_one(query)

        return output