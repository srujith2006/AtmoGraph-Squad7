"""Unit and integration tests for Neo4j connection pool manager and health check routes."""

import pytest
from starlette.testclient import TestClient

from src.core.neo4j import Neo4jConnectionPool, get_neo4j_pool
from src.core.config import Settings


@pytest.mark.unit
def test_neo4j_pool_initialization():
    """Verify pool instantiates with configuration settings."""
    settings = Settings(
        neo4j_uri="bolt://test-host:7687",
        neo4j_user="neo4j",
        neo4j_password="secretpassword",
        neo4j_database="customdb",
    )
    pool = Neo4jConnectionPool(settings=settings)
    assert pool.settings.neo4j_uri == "bolt://test-host:7687"
    assert pool.settings.neo4j_database == "customdb"
    assert pool.is_connected is False
    assert pool.is_fallback_mode is False


@pytest.mark.asyncio
async def test_neo4j_pool_fallback_on_unreachable_host():
    """Verify pool gracefully falls back to mock graph mode when host is unreachable."""
    settings = Settings(
        neo4j_uri="bolt://127.0.0.1:9999",  # Unused port
        neo4j_connection_timeout=0.2,
    )
    pool = Neo4jConnectionPool(settings=settings)
    connected = await pool.connect(max_retries=1, initial_delay=0.01)

    assert connected is False
    assert pool.is_connected is False
    assert pool.is_fallback_mode is True


@pytest.mark.asyncio
async def test_neo4j_execute_query_mock_fallback():
    """Verify Cypher query execution succeeds against fallback mock repository."""
    pool = Neo4jConnectionPool()
    # Force fallback mode
    pool._activate_fallback_mode("Test simulation")

    # Test count nodes query
    records = await pool.execute_query("MATCH (n) RETURN count(n) AS total_nodes")
    assert len(records) == 1
    assert "total_nodes" in records[0]
    assert records[0]["total_nodes"] >= 4

    # Test count relationships query
    rel_records = await pool.execute_query("MATCH ()-[r]->() RETURN count(r) AS total_relationships")
    assert len(rel_records) == 1
    assert "total_relationships" in rel_records[0]
    assert rel_records[0]["total_relationships"] >= 4


@pytest.mark.asyncio
async def test_neo4j_health_check_structure():
    """Verify health check probe returns latency, node counts, and operational mode."""
    pool = Neo4jConnectionPool()
    pool._activate_fallback_mode("Local testing fallback")

    health = await pool.check_health()
    assert "status" in health
    assert "latency_ms" in health
    assert health["mode"] == "mock_fallback"
    assert health["is_fallback"] is True
    assert health["node_count"] >= 4
    assert health["relationship_count"] >= 4


@pytest.mark.api
def test_health_neo4j_api_endpoint(client: TestClient):
    """Verify GET /health/neo4j returns HTTP 200 with diagnostic telemetry."""
    response = client.get("/health/neo4j")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "latency_ms" in data
    assert "node_count" in data
    assert "timestamp" in data
