from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.endpoint.http_metadata_inventory import router as http_metadata_inventory_router
from app.logging_setup import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=http_metadata_inventory_router)
