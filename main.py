import uvicorn

from app.config import app_config
from app.endpoint.router import app  # noqa: F401 — re-exported for uvicorn

if __name__ == "__main__":
    reload = app_config.env != "prod"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)
