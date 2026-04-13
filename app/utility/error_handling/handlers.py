from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.utility.error_handling.exceptions import ServiceError


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    logger.error(f"Service error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code, content={"data": None, "message": exc.message}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"data": None, "message": "An unexpected error occurred"},
    )
