from fastapi import APIRouter

from src.authentication.router import authentication_router
from src.core.routers.health import health_router

router_without_auth = APIRouter()
router_without_auth.include_router(health_router, tags=["Health"])
router_without_auth.include_router(authentication_router)

router_with_auth = APIRouter()
