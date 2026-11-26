"""In-memory request execution timing profiler and latency telemetry engine.

Tracks high-precision execution timings, percentile latencies (p50, p95, p99),
and slow query thresholds across all REST API endpoints.
"""

from collections import defaultdict
from datetime import datetime, timezone
import math
import threading
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.core.logging import get_logger

logger = get_logger("atmograph.profiler")


class LatencyBreakdown(BaseModel):
    """Percentile latency metrics for an endpoint route."""
    p50_ms: float = Field(description="50th percentile latency (median)")
    p95_ms: float = Field(description="95th percentile latency")
    p99_ms: float = Field(description="99th percentile latency")
    min_ms: float = Field(description="Minimum execution duration recorded")
    max_ms: float = Field(description="Maximum execution duration recorded")
    avg_ms: float = Field(description="Arithmetic mean execution duration")


class EndpointMetrics(BaseModel):
    """Detailed operational metrics for a specific HTTP method and path."""
    method: str
    path: str
    total_calls: int
    error_calls: int
    slow_calls: int
    latencies: LatencyBreakdown


class ProfilerSummaryResponse(BaseModel):
    """Aggregated profiler telemetry payload."""
    status: str = "operational"
    total_requests_profiled: int
    slow_request_threshold_ms: float
    total_slow_requests: int
    uptime_since: str
    endpoints: List[EndpointMetrics]


class RequestProfiler:
    """Thread-safe request execution latency tracker and percentile calculator."""

    def __init__(self, slow_threshold_ms: float = 100.0) -> None:
        self.slow_threshold_ms = slow_threshold_ms
        self._lock = threading.Lock()
        self._samples: Dict[str, List[float]] = defaultdict(list)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._slow_counts: Dict[str, int] = defaultdict(int)
        self._started_at = datetime.now(timezone.utc).isoformat()

    def record(self, method: str, path: str, duration_ms: float, status_code: int) -> None:
        """Record a single request execution sample."""
        key = f"{method.upper()} {path}"
        with self._lock:
            # Keep sample window to last 5,000 requests per endpoint to bound memory
            if len(self._samples[key]) >= 5000:
                self._samples[key].pop(0)
            self._samples[key].append(duration_ms)

            if status_code >= 400:
                self._error_counts[key] += 1

            if duration_ms >= self.slow_threshold_ms:
                self._slow_counts[key] += 1
                logger.warning(
                    f"Slow request detected: {key} took {duration_ms}ms (threshold: {self.slow_threshold_ms}ms)",
                    extra={"endpoint": key, "duration_ms": duration_ms, "threshold_ms": self.slow_threshold_ms}
                )

    def _calculate_percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile from sorted list."""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1

    def get_summary(self) -> ProfilerSummaryResponse:
        """Calculate aggregate latency percentiles across all recorded endpoints."""
        endpoints: List[EndpointMetrics] = []
        total_requests = 0
        total_slow = 0

        with self._lock:
            for key, samples in sorted(self._samples.items()):
                if not samples:
                    continue
                parts = key.split(" ", 1)
                method = parts[0]
                path = parts[1] if len(parts) > 1 else key

                sorted_samples = sorted(samples)
                count = len(samples)
                total_requests += count
                slow_count = self._slow_counts[key]
                total_slow += slow_count
                error_count = self._error_counts[key]

                p50 = round(self._calculate_percentile(sorted_samples, 50.0), 2)
                p95 = round(self._calculate_percentile(sorted_samples, 95.0), 2)
                p99 = round(self._calculate_percentile(sorted_samples, 99.0), 2)
                min_v = round(sorted_samples[0], 2)
                max_v = round(sorted_samples[-1], 2)
                avg_v = round(sum(sorted_samples) / count, 2)

                endpoints.append(
                    EndpointMetrics(
                        method=method,
                        path=path,
                        total_calls=count,
                        error_calls=error_count,
                        slow_calls=slow_count,
                        latencies=LatencyBreakdown(
                            p50_ms=p50,
                            p95_ms=p95,
                            p99_ms=p99,
                            min_ms=min_v,
                            max_ms=max_v,
                            avg_ms=avg_v,
                        ),
                    )
                )

        return ProfilerSummaryResponse(
            status="operational",
            total_requests_profiled=total_requests,
            slow_request_threshold_ms=self.slow_threshold_ms,
            total_slow_requests=total_slow,
            uptime_since=self._started_at,
            endpoints=endpoints,
        )

    def reset(self) -> None:
        """Clear all profiling history."""
        with self._lock:
            self._samples.clear()
            self._error_counts.clear()
            self._slow_counts.clear()
            self._started_at = datetime.now(timezone.utc).isoformat()


# Global Singleton instance
_profiler_instance: Optional[RequestProfiler] = None


def get_request_profiler(slow_threshold_ms: float = 100.0) -> RequestProfiler:
    """Retrieve application-wide RequestProfiler singleton."""
    global _profiler_instance
    if _profiler_instance is None:
        _profiler_instance = RequestProfiler(slow_threshold_ms=slow_threshold_ms)
    return _profiler_instance
