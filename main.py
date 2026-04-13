from app.utility.logging_utility.logging_utility import configure_logging
from app.config import app_config


configure_logging()

import uvicorn
from app.endpoint.router import app

if __name__ == "__main__":
    reload = False if app_config.env == "prod" else True
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)