from typing import Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from pydantic import BaseModel

Type = TypeVar("Type")


class Response(BaseModel, Generic[Type]):
    data: Type | None = None
    message: str | None = None


class JSONResponse(FastAPIJSONResponse, Generic[Type]):
    def __init__(
        self,
        data: Type | None = None,
        message: str | None = None,
        status_code: int = 200,
    ):
        super().__init__(
            content=Response(data=jsonable_encoder(data), message=message).model_dump(),
            status_code=status_code,
        )
