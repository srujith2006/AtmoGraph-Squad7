"""Integration and unit tests for middleware, correlation IDs, and centralized exception handlers."""

import pytest
from starlette.testclient import TestClient


@pytest.mark.api
def test_health_endpoint_success(client: TestClient):
    """Verify /health returns 200 with service metadata and uptime."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AtmoGraph" in data["service"]
    assert "uptime_seconds" in data
    assert "version" in data


@pytest.mark.api
def test_ping_endpoint(client: TestClient):
    """Verify /health/ping probe returns pong."""
    response = client.get("/health/ping")
    assert response.status_code == 200
    assert response.json()["ping"] == "pong"


@pytest.mark.api
def test_middleware_attaches_request_id_and_timing_headers(client: TestClient):
    """Verify RequestLoggingMiddleware automatically generates correlation ID and process time."""
    response = client.get("/health/ping")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 10
    assert "X-Process-Time-Ms" in response.headers


@pytest.mark.api
def test_middleware_propagates_client_provided_request_id(client: TestClient):
    """Verify RequestLoggingMiddleware preserves and returns client-supplied correlation ID."""
    custom_id = "trace-client-uuid-999"
    response = client.get("/health/ping", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.api
def test_standard_404_error_envelope(client: TestClient):
    """Verify unknown route returns standardized error envelope."""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["status_code"] == 404
    assert error["error_code"] == "HTTP_404"
    assert "request_id" in error
    assert "timestamp" in error


@pytest.mark.api
def test_custom_domain_not_found_exception(client: TestClient):
    """Verify custom EntityNotFoundError returns 404 with structured entity details."""
    response = client.get("/health/test-error?error_type=notfound")
    assert response.status_code == 404
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["error_code"] == "ENTITY_NOT_FOUND"
    assert error["details"]["entity_type"] == "SupplierNode"
    assert error["details"]["entity_id"] == "TEST-NODE-001"
    assert "request_id" in error


@pytest.mark.api
def test_custom_database_connection_exception(client: TestClient):
    """Verify Neo4j connection failure maps to HTTP 503."""
    response = client.get("/health/test-error?error_type=database")
    assert response.status_code == 503
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["error_code"] == "NEO4J_CONNECTION_ERROR"
    assert "Neo4j" in error["message"]


@pytest.mark.api
def test_unhandled_500_exception_envelope(client: TestClient):
    """Verify unexpected 500 error produces structured envelope without crashing app."""
    response = client.get("/health/test-error?error_type=unhandled")
    assert response.status_code == 500
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["status_code"] == 500
    assert error["error_code"] == "INTERNAL_SERVER_ERROR"
    assert "request_id" in error
