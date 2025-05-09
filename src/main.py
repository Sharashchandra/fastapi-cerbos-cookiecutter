from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import config
from src.core.constants import Environment
from src.core.event_handlers.lifespan import lifespan
from src.core.exception_handlers.http import http_exception_handler
from src.core.helpers.rq import dashboard
from src.core.middlewares.request_response_timing import RequestResponseTimingMiddleware
from src.core.responses.default import DefaultResponse
from src.core.routers.api import router_with_auth, router_without_auth

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url=f"{config.API_PREFIX}/openapi.json",
    docs_url=f"{config.API_PREFIX}/docs",
    debug=config.ENVIRONMENT == Environment.LOCAL,
    default_response_class=DefaultResponse,
    lifespan=lifespan,
)

# Mount EQ dashboard
app.mount("/rq", dashboard)

# Add custom timing middleware
app.add_middleware(RequestResponseTimingMiddleware)

# Add custom exception handler
app.add_exception_handler(HTTPException, http_exception_handler)


# Add CORS middleware if allowed origins are set
if config.ALLOWED_CORS_ORIGINS:
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=[str(url).rstrip("/") for url in config.ALLOWED_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )

app.include_router(router_without_auth, prefix=config.API_PREFIX)
app.include_router(router_with_auth, prefix=config.API_PREFIX)
