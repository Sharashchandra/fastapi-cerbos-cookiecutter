import typing

from fastapi import status
from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask

from src.core.responses.schemas import Response2xx, Response4xx


class DefaultResponse(ORJSONResponse):
    def __init__(
        self,
        content: typing.Any,
        status_code: int = status.HTTP_200_OK,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ):
        if 200 <= status_code < 300:
            content = Response2xx(status_code=status_code, data=content).model_dump(mode="json")
        elif 400 <= status_code < 500:
            content = Response4xx(status_code=status_code, data=content).model_dump(mode="json")
        super().__init__(content, status_code, headers, media_type, background)
