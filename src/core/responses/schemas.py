import typing

from fastapi import status
from pydantic import BaseModel


class Response2xx(BaseModel):
    success: bool = True
    status_code: int = status.HTTP_200_OK
    data: typing.Any | None = None


class Response4xx(BaseModel):
    success: bool = False
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_message: str | None = None
    exception_name: str | None = None
