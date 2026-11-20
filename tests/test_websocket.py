"""Comprehensive test suite for WebSocket streaming and connection manager.

Validates:
- WebSocket connection handshake and initial metadata emission
- Bidirectional heartbeat (ping/pong)
- Live client-initiated ripple simulation broadcasts
- REST status and manual broadcast endpoints
- ConnectionManager lifecycle, disconnection cleanup, and multi-cast routing
"""

import json
import pytest
from starlette.testclient import TestClient

from src.api.app import app
from src.services.websocket_manager import ConnectionManager, get_connection_manager


@pytest.fixture
def client():
    """Sync TestClient for WebSocket and REST testing."""
    return TestClient(app)


@pytest.fixture
def fresh_manager():
    """Create an isolated ConnectionManager instance for unit tests."""
    return ConnectionManager()


@pytest.mark.unit
def test_websocket_status_rest_endpoint(client: TestClient):
    """Verify GET /api/v1/ws/status returns connection telemetry."""
    response = client.get("/api/v1/ws/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "active_connections" in data
    assert "timestamp" in data
    assert isinstance(data["active_connections"], int)


@pytest.mark.unit
def test_websocket_broadcast_rest_endpoint(client: TestClient):
    """Verify POST /api/v1/ws/broadcast routes payload to manager."""
    payload = {
        "event_type": "disruption_alert",
        "payload": {
            "node_id": "port-rotterdam-001",
            "severity": "CRITICAL",
            "message": "Labor action initiated at dock 4"
        }
    }
    response = client.post("/api/v1/ws/broadcast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "broadcast_sent"
    assert "delivered_clients" in data
    assert data["delivered_clients"] >= 0


@pytest.mark.unit
def test_websocket_connection_and_heartbeat(client: TestClient):
    """Verify WebSocket handshake, welcome message, and ping-pong heartbeat."""
    with client.websocket_connect("/ws/ripple-stream?client_id=test-client-1") as websocket:
        # 1. Welcome handshake message
        welcome_raw = websocket.receive_text()
        welcome = json.loads(welcome_raw)
        assert welcome["type"] == "connection_established"
        assert welcome["client_id"] == "test-client-1"
        assert welcome["active_connections"] >= 1

        # 2. Heartbeat ping -> pong
        websocket.send_text(json.dumps({"type": "ping"}))
        pong_raw = websocket.receive_text()
        pong = json.loads(pong_raw)
        assert pong["type"] == "pong"
        assert "timestamp" in pong


@pytest.mark.unit
def test_websocket_generic_ack(client: TestClient):
    """Verify unrecognized messages receive an acknowledgment."""
    with client.websocket_connect("/ws/ripple-stream") as websocket:
        # Consume welcome message
        websocket.receive_text()

        # Send custom event
        websocket.send_text(json.dumps({"type": "custom_filter_update", "view": "map"}))
        ack_raw = websocket.receive_text()
        ack = json.loads(ack_raw)
        assert ack["type"] == "ack"
        assert ack["received_type"] == "custom_filter_update"


@pytest.mark.unit
def test_websocket_simulate_ripple_broadcast(client: TestClient):
    """Verify client can request live ripple simulation via WebSocket message."""
    with client.websocket_connect("/ws/ripple-stream") as websocket:
        # Consume welcome message
        websocket.receive_text()

        # Trigger ripple simulation
        websocket.send_text(json.dumps({
            "type": "simulate_ripple",
            "node_id": "node-6",
            "severity": "CRITICAL"
        }))

        # Expect broadcast event
        event_raw = websocket.receive_text()
        event = json.loads(event_raw)
        assert event["type"] == "gnn_ripple_broadcast"
        assert "data" in event
        data = event["data"]
        assert data["root_node_id"] == "node-6"
        assert data["severity"] == "CRITICAL"
        assert "critical_path" in data
        assert isinstance(data["critical_path"], list)
        assert data["impacted_nodes_count"] >= 1


@pytest.mark.asyncio
async def test_connection_manager_direct_broadcasts(fresh_manager: ConnectionManager):
    """Verify isolated ConnectionManager broadcast methods without active sockets."""
    assert fresh_manager.total_connections == 0

    # Broadcast with 0 connections returns 0 cleanly
    sent = await fresh_manager.broadcast({"type": "test_event"})
    assert sent == 0

    # Test helper method broadcast_node_risk_update
    risk_sent = await fresh_manager.broadcast_node_risk_update(
        node_id="node-1",
        node_name="Chip Foundry",
        previous_risk="LOW",
        new_risk="HIGH",
        status="DELAYED",
        reason="Port congestion"
    )
    assert risk_sent == 0

    # Test helper method broadcast_ripple_event
    ripple_sent = await fresh_manager.broadcast_ripple_event(
        prediction_id="pred-123",
        root_node_id="node-1",
        root_node_name="Chip Foundry",
        severity="HIGH",
        critical_path=["node-1", "node-4"],
        impacted_nodes_count=2
    )
    assert ripple_sent == 0


@pytest.mark.unit
def test_singleton_connection_manager():
    """Verify singleton accessor returns consistent instance."""
    mgr1 = get_connection_manager()
    mgr2 = get_connection_manager()
    assert mgr1 is mgr2
