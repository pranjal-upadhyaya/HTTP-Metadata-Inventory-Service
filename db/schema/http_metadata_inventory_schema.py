from beanie import Document, Indexed

class MetadataInventory(Document):
    url: Indexed(str, unique = True)
    headers: dict
    page_source: str
    cookies: dict

    class Settings:
        name = "metadata_inventory"
