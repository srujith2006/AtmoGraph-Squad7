"""Asynchronous integration test suite for REST endpoints and live WebSocket feeds.

Validates:
- End-to-end asynchronous REST workflows via httpx.AsyncClient (ASGITransport)
- Multi-client real-time WebSocket broadcasting and ripple cascade fan-out
- NLP disruption webhook ingestion to Neo4j graph entity risk mutation
- GNN inference ripple prediction and multi-horizon delay progression
- High concurrency stability and non-blocking I/O execution
- Request-ID trace propagation and RFC 7807 problem details error handling
"""

import asyncio
import json
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient

from src.api.app import app
from src.schemas.graph import DisruptionSeverity
from src.services.websocket_manager import get_connection_manager


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_health_and_neo4j_probes(async_client: AsyncClient):
    """Verify core health, ping, and diagnostic Neo4j endpoints respond asynchronously."""
    # 1. Main health check
    res_health = await async_client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] in ("healthy", "operational")
    assert "version" in data_health
    assert "timestamp" in data_health
    assert "X-Request-ID" in res_health.headers
    assert "X-Process-Time-Ms" in res_health.headers

    # 2. Ping probe
    res_ping = await async_client.get("/health/ping")
    assert res_ping.status_code == 200
    assert res_ping.json()["ping"] == "pong"

    # 3. Neo4j diagnostic probe
    res_neo4j = await async_client.get("/health/neo4j")
    assert res_neo4j.status_code == 200
    data_neo4j = res_neo4j.json()
    assert any(term in data_neo4j["status"] for term in ("healthy", "degraded", "operational"))
    assert "latency_ms" in data_neo4j
    assert "node_count" in data_neo4j or "active_connections" in data_neo4j


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_topology_and_metrics_consistency(async_client: AsyncClient):
    """Verify supply chain topology and aggregate metrics reflect consistent graph state."""
    res_topo = await async_client.get("/api/v1/graph/topology")
    assert res_topo.status_code == 200
    topo = res_topo.json()
    assert "nodes" in topo
    assert "edges" in topo
    assert len(topo["nodes"]) >= 6
    assert len(topo["edges"]) >= 5

    res_metrics = await async_client.get("/api/v1/graph/metrics")
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()
    assert metrics["total_suppliers"] >= 1
    assert metrics["manufacturing_units"] >= 1
    assert metrics["distribution_centers"] >= 1
    assert metrics["network_health_score_pct"] >= 0.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_concurrent_requests_stability(async_client: AsyncClient):
    """Verify system handles rapid burst of concurrent asynchronous requests without race conditions."""
    endpoints = [
        "/api/v1/graph/topology",
        "/api/v1/graph/metrics",
        "/api/v1/graph/nodes",
        "/api/v1/graph/edges",
        "/health",
        "/health/neo4j",
    ] * 4  # 24 concurrent asynchronous requests

    tasks = [async_client.get(endpoint) for endpoint in endpoints]
    responses = await asyncio.gather(*tasks)

    for idx, resp in enumerate(responses):
        assert resp.status_code == 200, f"Request {idx} to {resp.url} failed with {resp.status_code}"
        assert "X-Request-ID" in resp.headers
        assert "X-Process-Time-Ms" in resp.headers


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_nlp_ingest_to_graph_disruption_pipeline(async_client: AsyncClient):
    """Verify full pipeline: NLP news webhook -> node risk transition -> alert indexing."""
    payload = {
        "article": (
            "Labor union members have initiated an indefinite strike across Rotterdam container terminals. "
            "Semiconductor cargo destined for assembly facilities has halted indefinitely."
        ),
        "title": "Dockworkers Strike Paralyzes Port of Rotterdam Terminals",
        "source": "Maritime Logistics Daily",
        "entities": [
            {"id": "E1", "name": "Port of Rotterdam", "type": "PORT", "confidence": 0.98},
            {"id": "E2", "name": "Rotterdam Gateway Logistics", "type": "PORT", "confidence": 0.95},
            {"id": "E3", "name": "Semiconductors", "type": "SHIPMENT", "confidence": 0.92},
        ],
        "relationships": [
            {
                "entity_1": "Rotterdam Gateway Logistics",
                "entity_2": "Port of Rotterdam",
                "relation": "LOCATED_IN"
            }
        ],
        "detected_risks": [
            {
                "risk": "Port strike",
                "location": "Rotterdam",
                "affected_entities": ["Semiconductors"],
                "severity": "CRITICAL"
            }
        ],
    }

    # 1. Post news disruption webhook
    ingest_res = await async_client.post("/api/v1/nlp/ingest", json=payload)
    assert ingest_res.status_code == 201
    alert_data = ingest_res.json()
    assert alert_data["status"] == "ingested"
    assert alert_data["severity"] == "CRITICAL"
    alert_id = alert_data["alert_id"]

    # 2. Verify alert indexed in REST query
    alert_res = await async_client.get(f"/api/v1/nlp/alerts/{alert_id}")
    assert alert_res.status_code == 200
    retrieved = alert_res.json()
    assert retrieved["alert_id"] == alert_id
    assert retrieved["severity"] == "CRITICAL"

    # 3. Verify target node risk transitioned on the graph
    node_res = await async_client.get("/api/v1/graph/nodes/node-6")
    assert node_res.status_code == 200
    node = node_res.json()
    assert node["risk_level"].upper() in ("HIGH", "CRITICAL")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_gnn_prediction_ripple_flow(async_client: AsyncClient):
    """Verify end-to-end GNN inference ripple prediction and multi-horizon compound escalation."""
    pred_req = {
        "root_node_id": "node-6",
        "severity": "CRITICAL",
        "alert_id": "alert-async-gnn-001",
    }

    # 1. Trigger GNN prediction endpoint
    res_pred = await async_client.post("/api/v1/predictions/ripple", json=pred_req)
    assert res_pred.status_code == 200
    pred_data = res_pred.json()

    assert pred_data["root_node_id"] == "node-6"
    assert len(pred_data["critical_delay_path"]) >= 2
    assert len(pred_data["recommendations"]) >= 1

    horizons = pred_data["predictions_by_horizon"]
    assert "30_day" in horizons
    assert "60_day" in horizons
    assert "90_day" in horizons

    p30 = horizons["30_day"]
    p60 = horizons["60_day"]
    p90 = horizons["90_day"]

    # Compounding impact progression
    assert p30["mean_network_delay_days"] <= p60["mean_network_delay_days"]
    assert p60["mean_network_delay_days"] <= p90["mean_network_delay_days"]
    assert p30["cumulative_production_loss_pct"] <= p60["cumulative_production_loss_pct"]
    assert p60["cumulative_production_loss_pct"] <= p90["cumulative_production_loss_pct"]

    # 2. Check latest prediction cache endpoint
    res_latest = await async_client.get("/api/v1/predictions/latest")
    assert res_latest.status_code == 200
    assert res_latest.json()["prediction_id"] == pred_data["prediction_id"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_malformed_payloads_rfc7807_rejection(async_client: AsyncClient):
    """Verify malformed payloads return compliant RFC 7807 problem details with error envelopes."""
    # 1. Missing required article field on NLP ingest
    res_bad_nlp = await async_client.post("/api/v1/nlp/ingest", json={"title": "Incomplete Article"})
    assert res_bad_nlp.status_code in (400, 422)
    err_nlp = res_bad_nlp.json()
    assert "error" in err_nlp or "detail" in err_nlp

    # 2. Unknown node for GNN prediction
    res_unknown_gnn = await async_client.post(
        "/api/v1/predictions/ripple",
        json={"root_node_id": "nonexistent-facility-9999", "severity": "HIGH"}
    )
    assert res_unknown_gnn.status_code == 404
    err_gnn = res_unknown_gnn.json()
    assert "error" in err_gnn
    assert err_gnn["error"]["error_code"] == "ENTITY_NOT_FOUND"

    # 3. Route 404 envelope
    res_not_found = await async_client.get("/api/v1/nonexistent/endpoint/path")
    assert res_not_found.status_code == 404
    err_404 = res_not_found.json()
    assert "error" in err_404
    assert err_404["error"]["error_code"] in ("ROUTE_NOT_FOUND", "HTTP_404")


@pytest.mark.integration
@pytest.mark.websocket
def test_websocket_multi_client_broadcast_feed():
    """Verify live WebSocket feed fans out broadcasts concurrently across multiple connected clients."""
    sync_client = TestClient(app)

    with sync_client.websocket_connect("/ws/ripple-stream?client_id=subscriber-alpha") as ws1:
        with sync_client.websocket_connect("/ws/ripple-stream?client_id=subscriber-beta") as ws2:
            # Consume connection acknowledgments
            msg1 = json.loads(ws1.receive_text())
            msg2 = json.loads(ws2.receive_text())
            assert msg1["type"] == "connection_established"
            assert msg2["type"] == "connection_established"

            # Dispatch REST broadcast
            broadcast_payload = {
                "event_type": "tier1_disruption_alert",
                "payload": {
                    "source": "Singapore Logistics Center",
                    "severity": "HIGH",
                    "impact": "Customs clearance delay"
                }
            }
            res_bc = sync_client.post("/api/v1/ws/broadcast", json=broadcast_payload)
            assert res_bc.status_code == 200
            assert res_bc.json()["delivered_clients"] >= 2

            # Both connected clients receive the exact broadcast payload
            received_1 = json.loads(ws1.receive_text())
            received_2 = json.loads(ws2.receive_text())

            assert received_1["type"] == "tier1_disruption_alert"
            assert received_1["data"]["source"] == "Singapore Logistics Center"

            assert received_2["type"] == "tier1_disruption_alert"
            assert received_2["data"]["source"] == "Singapore Logistics Center"


@pytest.mark.integration
@pytest.mark.websocket
def test_websocket_live_ripple_cascade_to_multiple_listeners():
    """Verify client-triggered GNN simulation over WebSocket broadcasts ripple cascade to all peers."""
    sync_client = TestClient(app)

    with sync_client.websocket_connect("/ws/ripple-stream?client_id=commander-node") as ws_commander:
        with sync_client.websocket_connect("/ws/ripple-stream?client_id=listener-node") as ws_listener:
            # Consume handshakes
            ws_commander.receive_text()
            ws_listener.receive_text()

            # Commander triggers simulation
            ws_commander.send_text(json.dumps({
                "type": "simulate_ripple",
                "node_id": "node-6",
                "severity": "CRITICAL"
            }))

            # Both clients receive the resulting ripple cascade broadcast
            event_commander = json.loads(ws_commander.receive_text())
            event_listener = json.loads(ws_listener.receive_text())

            assert event_commander["type"] == "gnn_ripple_broadcast"
            assert event_listener["type"] == "gnn_ripple_broadcast"
            assert event_commander["data"]["root_node_id"] == "node-6"
            assert event_listener["data"]["root_node_id"] == "node-6"
            assert len(event_listener["data"]["critical_path"]) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_id_tracing_end_to_end(async_client: AsyncClient):
    """Verify client-injected X-Request-ID propagates across all asynchronous REST endpoints."""
    custom_trace_id = "trace-qa-automation-uuid-8877"
    headers = {"X-Request-ID": custom_trace_id}

    res = await async_client.get("/api/v1/graph/metrics", headers=headers)
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == custom_trace_id

    # Test propagation in error responses
    res_err = await async_client.get("/api/v1/graph/nodes/invalid-id-xyz", headers=headers)
    assert res_err.status_code == 404
    assert res_err.headers["X-Request-ID"] == custom_trace_id
    err_body = res_err.json()
    assert err_body["error"]["request_id"] == custom_trace_id
    assert err_body["error"]["error_code"] == "ENTITY_NOT_FOUND"
