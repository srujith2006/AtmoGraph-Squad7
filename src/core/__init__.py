"""Core infrastructure package for AtmoGraph.

Exports configuration, structured logging, middleware, and exception handling.
"""

from src.core.config import Settings, get_settings
from src.core.logging import StructuredJSONFormatter, get_logger, request_id_ctx, setup_logging
from src.core.middleware import RequestLoggingMiddleware
from src.core.exceptions import (
    AtmoGraphException,
    EntityNotFoundError,
    GraphDatabaseConnectionError,
    InferenceBridgeError,
    PayloadValidationError,
    register_exception_handlers,
)

__all__ = [
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
    "request_id_ctx",
    "StructuredJSONFormatter",
    "RequestLoggingMiddleware",
    "AtmoGraphException",
    "EntityNotFoundError",
    "GraphDatabaseConnectionError",
    "InferenceBridgeError",
    "PayloadValidationError",
    "register_exception_handlers",
]
