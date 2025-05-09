from fastapi.responses import ORJSONResponse

from src.core.responses.schemas import Response4xx


async def http_exception_handler(request, exc):
    content = Response4xx(
        status_code=exc.status_code,
        error_message=exc.detail,
        exception_name=exc.__class__.__name__,
    ).model_dump(mode="json")
    return ORJSONResponse(content, status_code=exc.status_code)
