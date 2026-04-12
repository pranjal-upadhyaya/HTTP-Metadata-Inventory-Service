from app.utility.logging_utility.logging_utility import configure_logging


configure_logging()

import uvicorn
from app.endpoint.router import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)