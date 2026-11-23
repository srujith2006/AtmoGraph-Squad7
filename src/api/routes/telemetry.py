"""Telemetry and request timing profiler routes for AtmoGraph observability."""

from fastapi import APIRouter, status
from typing import Dict, Any

from src.core.logging import get_logger
from src.core.profiler import get_request_profiler, ProfilerSummaryResponse

logger = get_logger("atmograph.telemetry_routes")

router = APIRouter(prefix="/telemetry", tags=["Observability & Profiling Telemetry"])


@router.get("/profiler", response_model=ProfilerSummaryResponse, status_code=status.HTTP_200_OK)
async def get_profiler_summary() -> ProfilerSummaryResponse:
    """Retrieve runtime request execution profiling, percentiles (p50, p95, p99), and latency breakdowns."""
    profiler = get_request_profiler()
    return profiler.get_summary()


@router.delete("/profiler", status_code=status.HTTP_200_OK)
async def reset_profiler_telemetry() -> Dict[str, Any]:
    """Reset in-memory profiling metrics (used for benchmark test isolation)."""
    profiler = get_request_profiler()
    profiler.reset()
    return {"status": "reset", "message": "Profiler metrics have been cleared."}
