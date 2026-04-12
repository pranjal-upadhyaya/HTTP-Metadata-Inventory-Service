from enum import unique
from beanie import Document, Indexed

class MetadataInventory(Document):
    url: Indexed(str, unique = True)
    page_source: str
    cookies: dict

    class Settings:
        name = "metadata_inventory"
