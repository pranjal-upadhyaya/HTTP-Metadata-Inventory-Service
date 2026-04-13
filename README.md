# HTTP Metadata Inventory Service

A FastAPI service that scrapes and stores HTTP metadata (headers, cookies, page source) for given URLs, backed by MongoDB.

---

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ and [Poetry](https://python-poetry.org/) (for local development)

---

## Running with Docker Compose

```bash
cp .env.sample .env
docker-compose up --build
```

The API will be available at `http://localhost:8000`.
Interactive API docs (Swagger UI) at `http://localhost:8000/docs`.

---

## Running Locally

```bash
cp .env.sample .env
poetry install
poetry run python main.py
```

> Ensure a MongoDB instance is running and `.env` is configured to point to it.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_HOST` | Host the API binds to | `0.0.0.0` |
| `APP_PORT` | Port the API listens on | `8000` |
| `EXTERNAL_APP_PORT` | Host port mapped by Docker | `8000` |
| `DB_HOST` | MongoDB host | `127.0.0.1` |
| `DB_PORT` | MongoDB port | `27017` |
| `DB_NAME` | Database name | `metadata` |
| `DB_USER` | MongoDB username | `` |
| `DB_PASSWORD` | MongoDB password | `` |
| `METADATA_INVENTORY_COLLECTION` | Collection name | `metadata_inventory` |
| `HTTP_REQUEST_TIMEOUT_S` | Timeout for outbound HTTP requests (seconds) | `10` |
| `ENV` | Environment name (`dev` enables hot reload) | `` |

---

## API Reference

### POST `/metadata_inventory/scrape`

Scrapes and stores headers, cookies, and page source for a URL.

**Request**
```json
{
  "url": "https://example.com"
}
```

**Response `200`**
```json
{
  "data": {
    "url": "https://example.com",
    "headers": { "Content-Type": "text/html" },
    "cookies": {},
    "page_source": "<html>...</html>"
  },
  "message": null
}
```

| Status | Reason |
|---|---|
| `200` | Metadata scraped and stored |
| `409` | Metadata for this URL already exists |
| `422` | Invalid URL format |
| `502` | Failed to reach the target URL |

---

### GET `/metadata_inventory/fetch?url=<url>`

Returns stored metadata for a URL. If not found, triggers a background scrape and returns `202`.

**Response `200` — metadata found**
```json
{
  "data": {
    "metadata_available": true,
    "metadata": {
      "url": "https://example.com",
      "headers": { "Content-Type": "text/html" },
      "cookies": {},
      "page_source": "<html>...</html>"
    }
  },
  "message": null
}
```

**Response `202` — metadata not yet available**
```json
{
  "data": null,
  "message": "Url metadata request logged"
}
```

| Status | Reason |
|---|---|
| `200` | Metadata found and returned |
| `202` | Metadata not found; background scrape initiated |
| `400` | Invalid URL format |

---

## Running Tests

```bash
poetry install --with dev
poetry run pytest tests/ -v
```

> Repository tests spin up a real MongoDB container via Docker. Ensure Docker is running before executing the test suite.

### Test structure

| File | Layer tested |
|---|---|
| `tests/test_endpoint.py` | API endpoints (mocked service) |
| `tests/test_service.py` | Business logic (mocked repository) |
| `tests/test_repository.py` | Database operations (MongoDB via testcontainers) |
