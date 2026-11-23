"""Test suite for OpenAPI schema export, Swagger documentation, and request timing profiler.

Validates:
- Export of valid OpenAPI 3.1.0 specifications to docs/openapi.json
- Swagger UI (/docs) and ReDoc (/redoc) availability
- In-memory RequestProfiler telemetry recording, percentile calculations (p50/p95/p99)
- Endpoint profiling breakdown and telemetry reset lifecycle
"""

import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from src.api.app import app
from src.core.profiler import RequestProfiler, get_request_profiler
from scripts.export_openapi import export_openapi_schema


@pytest.fixture
def client():
    """Sync TestClient for docs and profiler validation."""
    return TestClient(app)


@pytest.mark.unit
def test_export_openapi_script_generation(tmp_path: Path):
    """Verify export_openapi_schema generates valid json and markdown files."""
    json_path = export_openapi_schema(output_dir=tmp_path)
    assert json_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["openapi"].startswith("3.")
    assert data["info"]["title"] == "AtmoGraph Ripple Predictor"
    assert "paths" in data
    assert len(data["paths"]) >= 15
    assert (tmp_path / "API_SPECIFICATION.md").exists()


@pytest.mark.api
def test_openapi_json_endpoint(client: TestClient):
    """Verify /openapi.json serves the live FastAPI OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert schema["info"]["title"] == "AtmoGraph Ripple Predictor"
    paths = schema["paths"]
    assert "/health" in paths
    assert "/api/v1/graph/topology" in paths
    assert "/api/v1/nlp/ingest" in paths
    assert "/api/v1/predictions/ripple" in paths
    assert "/api/v1/telemetry/profiler" in paths


@pytest.mark.api
def test_swagger_and_redoc_ui_endpoints(client: TestClient):
    """Verify Swagger UI and ReDoc HTML documentation endpoints load successfully."""
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    assert "swagger-ui" in res_docs.text.lower()

    res_redoc = client.get("/redoc")
    assert res_redoc.status_code == 200
    assert "redoc" in res_redoc.text.lower()


@pytest.mark.unit
def test_request_profiler_percentile_math():
    """Verify RequestProfiler percentile calculation accurately computes p50, p95, p99."""
    profiler = RequestProfiler(slow_threshold_ms=50.0)
    samples = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    p50 = profiler._calculate_percentile(samples, 50.0)
    p95 = profiler._calculate_percentile(samples, 95.0)
    p99 = profiler._calculate_percentile(samples, 99.0)

    assert 50.0 <= p50 <= 60.0
    assert 90.0 <= p95 <= 100.0
    assert 95.0 <= p99 <= 100.0


@pytest.mark.unit
def test_slow_request_threshold_detection():
    """Verify profiler records slow requests exceeding the configurable threshold."""
    profiler = RequestProfiler(slow_threshold_ms=80.0)
    profiler.record("GET", "/test/slow", 120.5, 200)
    profiler.record("GET", "/test/fast", 15.2, 200)

    summary = profiler.get_summary()
    assert summary.total_requests_profiled == 2
    assert summary.total_slow_requests == 1

    ep = next(e for e in summary.endpoints if e.path == "/test/slow")
    assert ep.slow_calls == 1
    assert ep.latencies.max_ms == 120.5


@pytest.mark.api
def test_profiler_telemetry_rest_api_lifecycle(client: TestClient):
    """Verify GET /api/v1/telemetry/profiler reports active metrics and DELETE resets it."""
    # 1. Reset metrics first
    res_reset = client.delete("/api/v1/telemetry/profiler")
    assert res_reset.status_code == 200
    assert res_reset.json()["status"] == "reset"

    # 2. Make multiple calls to generate profiling telemetry
    client.get("/health")
    client.get("/health/ping")
    client.get("/api/v1/graph/metrics")

    # 3. Retrieve telemetry summary
    res_summary = client.get("/api/v1/telemetry/profiler")
    assert res_summary.status_code == 200
    summary = res_summary.json()

    assert summary["status"] == "operational"
    assert summary["total_requests_profiled"] >= 3
    assert len(summary["endpoints"]) >= 2

    # Verify endpoint metrics structure
    for ep in summary["endpoints"]:
        assert "method" in ep
        assert "path" in ep
        assert ep["total_calls"] >= 1
        assert ep["latencies"]["p50_ms"] >= 0.0
        assert ep["latencies"]["min_ms"] <= ep["latencies"]["max_ms"]
