"""Diagnostic and health check endpoints for AtmoGraph service monitoring."""

from datetime import datetime, timezone
import time
from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from src.core.config import get_settings
from src.core.exceptions import EntityNotFoundError, GraphDatabaseConnectionError

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])
_START_TIME = time.time()


class HealthResponse(BaseModel):
    """Schema for health status payload."""
    status: str = Field(default="healthy", description="Overall health state")
    service: str = Field(description="Service identifier")
    version: str = Field(description="API version")
    environment: str = Field(description="Runtime environment")
    uptime_seconds: float = Field(description="Uptime duration in seconds")
    timestamp: str = Field(description="ISO 8601 UTC timestamp")


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_health_status() -> HealthResponse:
    """Return runtime health status and system telemetry."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=round(time.time() - _START_TIME, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    """Ultra-lightweight ping probe for load balancer health checks."""
    return {"ping": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/test-error", include_in_schema=False)
async def trigger_test_error(
    error_type: str = Query("custom", description="Type of error to trigger: custom | notfound | database | unhandled")
):
    """Internal test route used by QA suites to verify centralized exception handling."""
    if error_type == "notfound":
        raise EntityNotFoundError(entity_type="SupplierNode", entity_id="TEST-NODE-001")
    elif error_type == "database":
        raise GraphDatabaseConnectionError("Test simulation: Neo4j pool exhausted")
    elif error_type == "unhandled":
        raise ZeroDivisionError("Deliberate division by zero to trigger 500 handler")
    raise EntityNotFoundError(entity_type="MockResource", entity_id="UNKNOWN")
