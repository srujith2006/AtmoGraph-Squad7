"""Unit and API integration tests for Day 3 mock supply chain graph routes."""

import pytest
from starlette.testclient import TestClient


@pytest.mark.api
def test_get_graph_topology(client: TestClient):
    """Verify /api/v1/graph/topology returns valid supply chain topology with React Flow mapping."""
    response = client.get("/api/v1/graph/topology")
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert "react_flow_nodes" in data
    assert "react_flow_edges" in data
    assert data["total_nodes"] >= 9
    assert data["total_edges"] >= 8

    # Verify first React Flow node format
    rf_node = data["react_flow_nodes"][0]
    assert rf_node["type"] == "supplyChainNode"
    assert "position" in rf_node
    assert "data" in rf_node
    assert "name" in rf_node["data"]
    assert "riskFactor" in rf_node["data"]

    # Verify React Flow edge format
    rf_edge = data["react_flow_edges"][0]
    assert "source" in rf_edge
    assert "target" in rf_edge
    assert "style" in rf_edge


@pytest.mark.api
def test_list_nodes_and_filtering(client: TestClient):
    """Verify filtering nodes by classification and risk level."""
    # Filter suppliers
    res_suppliers = client.get("/api/v1/graph/nodes?node_type=supplier")
    assert res_suppliers.status_code == 200
    suppliers = res_suppliers.json()
    assert len(suppliers) >= 3
    for s in suppliers:
        assert s["node_type"] == "supplier"

    # Filter ports
    res_ports = client.get("/api/v1/graph/nodes?node_type=port")
    assert res_ports.status_code == 200
    ports = res_ports.json()
    assert len(ports) >= 2
    for p in ports:
        assert p["node_type"] == "port"

    # Filter by risk
    res_high = client.get("/api/v1/graph/nodes?risk_level=High")
    assert res_high.status_code == 200
    high_nodes = res_high.json()
    for n in high_nodes:
        assert n["risk_level"] == "High"


@pytest.mark.api
def test_get_single_node(client: TestClient):
    """Verify fetching existing node by ID and 404 for unknown ID."""
    res_ok = client.get("/api/v1/graph/nodes/node-1")
    assert res_ok.status_code == 200
    node = res_ok.json()
    assert node["id"] == "node-1"
    assert "Apex Mining" in node["name"]

    res_404 = client.get("/api/v1/graph/nodes/non-existent-999")
    assert res_404.status_code == 404
    err_data = res_404.json()
    assert "error" in err_data
    assert err_data["error"]["error_code"] == "ENTITY_NOT_FOUND"


@pytest.mark.api
def test_list_edges_and_filtering(client: TestClient):
    """Verify fetching routes with disruption filter."""
    res_disrupted = client.get("/api/v1/graph/edges?active_disruption=true")
    assert res_disrupted.status_code == 200
    edges = res_disrupted.json()
    assert len(edges) >= 2
    for e in edges:
        assert e["active_disruption"] is True


@pytest.mark.api
def test_graph_metrics_endpoint(client: TestClient):
    """Verify aggregated metrics match dashboard summary cards."""
    response = client.get("/api/v1/graph/metrics")
    assert response.status_code == 200
    metrics = response.json()

    assert metrics["total_suppliers"] >= 3
    assert metrics["manufacturing_units"] >= 2
    assert metrics["distribution_centers"] >= 3
    assert metrics["active_disruptions"] >= 2
    assert 0.0 <= metrics["network_health_score_pct"] <= 100.0


@pytest.mark.api
def test_simulate_disruption(client: TestClient):
    """Verify interactive disruption simulation updates node and edges."""
    payload = {
        "target_node_id": "node-3",
        "new_risk_level": "High",
        "disruption_description": "Factory fire halts production in Yokohama",
        "delay_added_days": 15.0,
    }
    response = client.post("/api/v1/graph/simulate-disruption", json=payload)
    assert response.status_code == 200
    topology = response.json()

    # Find disrupted node
    node3 = next(n for n in topology["nodes"] if n["id"] == "node-3")
    assert node3["risk_level"] == "High"
    assert node3["status"] == "Disrupted"

    # Find connected edge
    edge = next(e for e in topology["edges"] if e["from_id"] == "node-3")
    assert edge["active_disruption"] is True
    assert edge["lead_time_days"] >= 18.0
