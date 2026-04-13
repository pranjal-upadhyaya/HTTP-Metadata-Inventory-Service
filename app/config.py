import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    app_host: str
    app_port: int

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    db_max_pool_size: int = 100
    db_min_pool_size: int = 10
    db_max_idle_time_ms: int = 30_000
    db_connect_timeout_ms: int = 3_000
    db_socket_timeout_ms: int = 10_000
    db_server_selection_timeout_ms: int = 5_000
    db_wait_queue_timeout_ms: int = 5_000

    metadata_inventory_collection: str

    http_request_timeout_s: int = 10

    env: str

    model_config = SettingsConfigDict(
        env_file = os.getenv("ENV_FILE", ".env"),
        env_file_encoding = "utf-8",
        case_sensitive = False,
        extra = "ignore",
    )


app_config = AppConfig()