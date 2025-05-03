import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestResponseTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.5f} s"

        return response
