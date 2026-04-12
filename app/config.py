from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):

    app_host: str
    app_port: int

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    metadata_inventory_collection: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

app_config = AppConfig()