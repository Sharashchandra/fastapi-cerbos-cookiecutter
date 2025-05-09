from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse

# health router configuration
health_router = APIRouter(prefix="/health", tags=["Health"])


# health check application
@health_router.get("/app/", summary="Application Health Checkup", status_code=status.HTTP_200_OK)
async def app_health() -> ORJSONResponse:
    """
    ### Application Health check
    This endpoint returns the status of the application.
    """
    return {"status": "ok"}
