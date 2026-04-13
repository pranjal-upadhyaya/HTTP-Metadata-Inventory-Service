import pytest
from beanie import PydanticObjectId, init_beanie
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError
from testcontainers.mongodb import MongoDbContainer

from app.repository.http_metadata_inventory_repository import (
    HTTPMetadataInventoryRepository,
)
from db.schema.http_metadata_inventory_schema import MetadataInventory

MOCK_DOC = {
    "url": "https://example.com",
    "headers": {"Content-Type": "text/html"},
    "page_source": "<html></html>",
    "cookies": {},
}


@pytest.fixture(scope="session")
def mongo_container():
    with MongoDbContainer("mongo:8.0") as container:
        yield container


@pytest.fixture
async def initialized_db(mongo_container):
    client = AsyncMongoClient(mongo_container.get_connection_url())
    await init_beanie(database=client["test_db"], document_models=[MetadataInventory])
    yield
    await MetadataInventory.find().delete()
    await client.close()


@pytest.fixture
async def repository(initialized_db):
    return HTTPMetadataInventoryRepository()


class TestInsertMetadata:
    async def test_insert_success_returns_id(self, repository):
        result = await repository.insert_metadata(MOCK_DOC)
        assert isinstance(result, PydanticObjectId)

    async def test_insert_stores_correct_data(self, repository):
        await repository.insert_metadata(MOCK_DOC)
        doc = await MetadataInventory.find_one(MetadataInventory.url == MOCK_DOC["url"])
        assert doc.url == MOCK_DOC["url"]
        assert doc.headers == MOCK_DOC["headers"]
        assert doc.page_source == MOCK_DOC["page_source"]
        assert doc.cookies == MOCK_DOC["cookies"]

    async def test_insert_duplicate_url_raises(self, repository):
        await repository.insert_metadata(MOCK_DOC)
        with pytest.raises(DuplicateKeyError):
            await repository.insert_metadata(MOCK_DOC)


class TestGetMetadataByUrl:
    async def test_get_found_returns_document(self, repository):
        await repository.insert_metadata(MOCK_DOC)
        result = await repository.get_metadata_by_url(MOCK_DOC["url"])
        assert result is not None
        assert result.url == MOCK_DOC["url"]

    async def test_get_not_found_returns_none(self, repository):
        result = await repository.get_metadata_by_url("https://notfound.com")
        assert result is None
