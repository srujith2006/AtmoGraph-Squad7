"""Structured JSON logging foundation for AtmoGraph.

Provides context-aware JSON log formatting with correlation ID tracking,
execution timings, and standardized log schemas for observability in distributed pipelines.
"""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import sys
from typing import Any, Dict, Optional

# Context variable for propagating correlation IDs across asynchronous tasks
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id_ctx", default=None)


class StructuredJSONFormatter(logging.Formatter):
    """Custom formatter rendering Python log records into structured single-line JSON."""

    def __init__(self, service_name: str = "atmograph-api") -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "location": f"{record.module}:{record.funcName}:{record.lineno}",
        }

        # Inject correlation ID from contextvars or explicit extra attribute
        req_id = getattr(record, "request_id", None) or request_id_ctx.get()
        if req_id:
            log_payload["request_id"] = req_id

        # Merge additional structured attributes passed via extra={}
        extra_fields = [
            "http_method", "path", "status_code", "duration_ms",
            "client_ip", "user_agent", "endpoint", "error_code"
        ]
        for field in extra_fields:
            if hasattr(record, field):
                log_payload[field] = getattr(record, field)

        # Include custom extra metadata dictionary if supplied
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_payload["data"] = record.extra_data

        # Serialize stack traces if an exception is attached
        if record.exc_info:
            log_payload["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "UnknownException",
                "message": str(record.exc_info[1]),
                "stack_trace": self.formatException(record.exc_info).splitlines(),
            }

        return json.dumps(log_payload, default=str)


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """Configure system-wide logging with JSON formatting or standard console stream.

    Args:
        log_level: Logging severity threshold ("DEBUG", "INFO", "WARNING", "ERROR").
        json_format: When True, formats output as JSON strings; otherwise standard text.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate lines
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if json_format:
        formatter = StructuredJSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] [req:%(request_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            defaults={"request_id": "-"}
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Align third-party loggers (uvicorn, fastapi)
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        u_logger = logging.getLogger(uvicorn_logger_name)
        u_logger.handlers = []
        u_logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """Convenience helper to obtain a named logger."""
    return logging.getLogger(name)
