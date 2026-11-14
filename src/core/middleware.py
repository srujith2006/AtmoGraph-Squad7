"""Asynchronous structured logging and correlation ID middleware for FastAPI.

Extracts or generates unique Request IDs, attaches distributed trace headers,
and records high-precision execution timings in structured JSON.
"""

import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.logging import get_logger, request_id_ctx
from src.core.config import get_settings

logger = get_logger("atmograph.middleware.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Intercepts every incoming HTTP request to attach correlation tracking and record telemetry."""

    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract existing correlation ID or generate a new UUID4
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        
        # Bind correlation ID to contextvars for current async call stack
        token = request_id_ctx.set(request_id)

        # Store on request state for easy access in route handlers
        request.state.request_id = request_id

        # Record start timestamp
        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        logger.debug(
            f"Incoming {method} request to {path}",
            extra={
                "http_method": method,
                "path": path,
                "client_ip": client_ip,
                "request_id": request_id,
            }
        )

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Inject tracking headers into response
            response.headers[self.header_name] = request_id
            response.headers["X-Process-Time-Ms"] = str(duration_ms)

            # Emit structured access log
            logger.info(
                f"{method} {path} completed with {response.status_code} in {duration_ms}ms",
                extra={
                    "http_method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "request_id": request_id,
                }
            )
            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Unhandled exception during {method} {path}: {str(exc)}",
                exc_info=True,
                extra={
                    "http_method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "client_ip": client_ip,
                    "request_id": request_id,
                }
            )
            raise exc

        finally:
            # Reset contextvar token to prevent leakage across pooled event loops
            request_id_ctx.reset(token)
