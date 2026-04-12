from fastapi import FastAPI
from app.endpoint.http_metadata_inventory import router as http_metadata_inventory_router

app = FastAPI()

app.include_router(router = http_metadata_inventory_router)
