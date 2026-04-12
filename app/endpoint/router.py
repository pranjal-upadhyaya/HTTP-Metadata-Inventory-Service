from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI

from app.config import app_config
from app.endpoint.http_metadata_inventory import router as http_metadata_inventory_router
from app.logging_setup import configure_logging
from db.connection_manager import ConnectionManager


from db.schema.http_metadata_inventory_schema import MetadataInventory


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()

    connection_manager = ConnectionManager()
    async_client = connection_manager.get_async_client()
    db = async_client[app_config.db_name]
    await init_beanie(
        database=db,
        document_models=[MetadataInventory]
    )

    yield

    async_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router=http_metadata_inventory_router)
