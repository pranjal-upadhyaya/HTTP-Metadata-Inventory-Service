from pymongo import AsyncMongoClient

from app.config import app_config


class ConnectionManager:
    def get_async_client(self) -> AsyncMongoClient:
        c = app_config
        return AsyncMongoClient(
            host=c.db_host,
            port=c.db_port,
            maxPoolSize=c.db_max_pool_size,
            minPoolSize=c.db_min_pool_size,
            maxIdleTimeMS=c.db_max_idle_time_ms,
            connectTimeoutMS=c.db_connect_timeout_ms,
            socketTimeoutMS=c.db_socket_timeout_ms,
            serverSelectionTimeoutMS=c.db_server_selection_timeout_ms,
            waitQueueTimeoutMS=c.db_wait_queue_timeout_ms,
        )
