"""Centralized exception hierarchy and FastAPI exception handlers for AtmoGraph.

Ensures all errors return a standardized JSON schema with correlation IDs,
status codes, and actionable diagnostic messages.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.logging import get_logger, request_id_ctx
from src.core.config import get_settings

logger = get_logger("atmograph.exceptions")


# ==============================================================================
# Domain Exception Hierarchy
# ==============================================================================

class AtmoGraphException(Exception):
    """Base exception for all domain errors within AtmoGraph."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "ATMOGRAPH_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundError(AtmoGraphException):
    """Raised when a requested supply chain node, route, or alert does not exist."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_type} with ID '{entity_id}' was not found in the knowledge graph.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ENTITY_NOT_FOUND",
            details={"entity_type": entity_type, "entity_id": entity_id},
        )


class GraphDatabaseConnectionError(AtmoGraphException):
    """Raised when Neo4j pool exhaustion or connection failure occurs."""

    def __init__(self, message: str = "Neo4j graph database is unreachable or connection timed out.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="NEO4J_CONNECTION_ERROR",
        )


class InferenceBridgeError(AtmoGraphException):
    """Raised when PyTorch Geometric GNN inference fails or returns invalid tensors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="GNN_INFERENCE_ERROR",
            details=details,
        )


class PayloadValidationError(AtmoGraphException):
    """Raised when incoming NLP ingestion webhook or schema validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="PAYLOAD_VALIDATION_ERROR",
            details=details,
        )


# ==============================================================================
# Standardized Error Envelope Helper
# ==============================================================================

def build_error_payload(
    status_code: int,
    error_code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble standardized JSON error structure."""
    return {
        "error": {
            "status_code": status_code,
            "error_code": error_code,
            "message": message,
            "request_id": request_id or request_id_ctx.get() or "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }
    }


# ==============================================================================
# FastAPI Centralized Handlers
# ==============================================================================

async def atmograph_exception_handler(request: Request, exc: AtmoGraphException) -> JSONResponse:
    """Handle custom application exceptions."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    logger.warning(
        f"Domain error [{exc.error_code}]: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "request_id": req_id,
            "path": request.url.path,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_payload(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            request_id=req_id,
            details=exc.details,
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard Starlette / FastAPI HTTP exceptions (e.g. 404, 405, 401)."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    error_code = f"HTTP_{exc.status_code}"
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_payload(
            status_code=exc.status_code,
            error_code=error_code,
            message=str(exc.detail),
            request_id=req_id,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request payload / query validation errors cleanly."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    formatted_errors = []
    for err in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg"),
            "type": err.get("type"),
        })

    logger.info(
        f"Request validation failure on {request.url.path}: {len(formatted_errors)} field errors",
        extra={"request_id": req_id, "path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_error_payload(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="Request schema validation failed. Check 'details.errors' for invalid fields.",
            request_id=req_id,
            details={"errors": formatted_errors},
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected internal server errors (HTTP 500)."""
    req_id = getattr(request.state, "request_id", None) or request_id_ctx.get()
    settings = get_settings()

    logger.error(
        f"Unhandled 500 internal server error on {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={"request_id": req_id, "path": request.url.path}
    )

    message = str(exc) if settings.debug else "An unexpected internal server error occurred."
    details = {"exception_type": exc.__class__.__name__} if settings.debug else {}

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_payload(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            request_id=req_id,
            details=details,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers to a FastAPI application instance."""
    app.add_exception_handler(AtmoGraphException, atmograph_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
