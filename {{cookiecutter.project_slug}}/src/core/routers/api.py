from fastapi import APIRouter, Depends

from src.authentication.router import authentication_router
from src.core.routers.health import health_router
from src.core.security.dependencies import verify_http_token
from src.users.router import user_router

router_without_auth = APIRouter()
router_without_auth.include_router(health_router, tags=["Health"])
router_without_auth.include_router(authentication_router)

router_with_auth = APIRouter(dependencies=[Depends(verify_http_token)])
router_with_auth.include_router(user_router)
