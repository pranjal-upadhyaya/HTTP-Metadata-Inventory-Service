from pymongo import MongoClient
from app.config import app_config


class ConnectionManager:

    def __init__(self) -> None:
        self.client = MongoClient(
            host=app_config.db_host,
            port=app_config.db_port,
        )

    def get_client(self):
        return self.client