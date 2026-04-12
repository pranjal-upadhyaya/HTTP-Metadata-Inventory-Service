from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

from fastapi.responses import JSONResponse as FastAPIJSONResponse
from fastapi.encoders import jsonable_encoder

Type = TypeVar("Type")

class Response(BaseModel, Generic[Type]):
    data: Optional[Type] = {}
    message: Optional[str] = None

class JSONResponse(FastAPIJSONResponse, Generic[Type]):

    def __init__(
        self,
        data: Optional[Type] = None,
        message: Optional[str] = None,
        status_code: int = 200
    ):
        super().__init__(
            content=Response(
                data=jsonable_encoder(data),
                message=message
            ).model_dump(),
            status_code=status_code
        )