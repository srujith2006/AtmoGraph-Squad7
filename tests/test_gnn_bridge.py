"""PyTorch Geometric GNN inference bridge contract tests and ripple validation suite."""

import pytest
from starlette.testclient import TestClient

from src.services.gnn_bridge import GNNInferenceBridge, get_gnn_bridge
from src.schemas.graph import DisruptionSeverity, TimelineHorizon


@pytest.mark.unit
def test_gnn_bridge_singleton_and_version():
    """Verify bridge initializes with configured model version."""
    bridge = get_gnn_bridge()
    assert bridge.model_version == "gnn-sage-v1.0.0"


@pytest.mark.asyncio
async def test_gnn_ripple_multi_hop_traversal():
    """Verify graph traversal identifies 1-hop, 2-hop, and downstream connections."""
    bridge = get_gnn_bridge()
    raw_impacts = bridge._traverse_multi_hop_impacts("node-1", DisruptionSeverity.HIGH)
    assert len(raw_impacts) >= 3

    # Check hops are present in order
    hops = [imp[0] for imp in raw_impacts]
    assert 1 in hops
    assert 2 in hops


@pytest.mark.asyncio
async def test_gnn_ripple_horizons_progression():
    """Verify 30, 60, and 90-day simulation horizons compound in delay and loss."""
    bridge = get_gnn_bridge()
    prediction = await bridge.predict_ripple_effect(
        root_node_id="node-4",
        disruption_severity=DisruptionSeverity.HIGH,
        alert_id="test-alert-singapore",
    )

    assert "30_day" in prediction.predictions_by_horizon
    assert "60_day" in prediction.predictions_by_horizon
    assert "90_day" in prediction.predictions_by_horizon

    p30 = prediction.predictions_by_horizon["30_day"]
    p60 = prediction.predictions_by_horizon["60_day"]
    p90 = prediction.predictions_by_horizon["90_day"]

    assert p30.horizon_days == 30
    assert p60.horizon_days == 60
    assert p90.horizon_days == 90

    # Delay and affected nodes should compound over time
    assert p30.mean_network_delay_days <= p60.mean_network_delay_days <= p90.mean_network_delay_days
    assert len(p30.impacted_nodes) <= len(p90.impacted_nodes)
    assert p30.cumulative_production_loss_pct <= p90.cumulative_production_loss_pct


@pytest.mark.asyncio
async def test_gnn_european_port_strike_core_use_case():
    """Verify core project problem statement: European port strike propagating to North American electronics."""
    bridge = get_gnn_bridge()
    # node-6 is Rotterdam Gateway Logistics
    prediction = await bridge.predict_ripple_effect(
        root_node_id="node-6",
        disruption_severity=DisruptionSeverity.CRITICAL,
        alert_id="test-alert-rotterdam-strike",
    )

    assert prediction.root_node_id == "node-6"
    assert "Rotterdam" in prediction.root_node_name

    # 90-day horizon should impact downstream nodes
    p90 = prediction.predictions_by_horizon["90_day"]
    impacted_node_ids = [n.node_id for n in p90.impacted_nodes]
    assert "node-7" in impacted_node_ids  # Munich plant

    # Check confidence bounds validity
    for node_impact in p90.impacted_nodes:
        assert node_impact.delay_confidence_lower <= node_impact.predicted_delay_days <= node_impact.delay_confidence_upper
        assert 0.0 <= node_impact.propagation_probability <= 1.0


@pytest.mark.unit
def test_gnn_critical_delay_path_and_recommendations():
    """Verify critical path tracing and actionable operational suggestions."""
    bridge = get_gnn_bridge()
    raw = bridge._traverse_multi_hop_impacts("node-1", DisruptionSeverity.HIGH)
    crit_path = bridge._determine_critical_delay_path("node-1", raw)

    assert len(crit_path) >= 2
    assert crit_path[0] == "node-1"

    p90 = bridge._generate_horizon_prediction(90, raw)
    recs = bridge._generate_recommendations("Apex Mining", crit_path, p90)
    assert len(recs) >= 2
    assert any("buffer" in r.lower() or "reroute" in r.lower() for r in recs)


@pytest.mark.api
def test_post_ripple_prediction_api_endpoint(client: TestClient):
    """Verify POST /api/v1/predictions/ripple returns 200 with complete timeline forecast."""
    payload = {
        "root_node_id": "node-4",
        "severity": "CRITICAL",
        "alert_id": "api-test-alert",
    }
    response = client.post("/api/v1/predictions/ripple", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "prediction_id" in data
    assert data["root_node_id"] == "node-4"
    assert "predictions_by_horizon" in data
    assert len(data["critical_delay_path"]) >= 1
    assert len(data["recommendations"]) >= 1


@pytest.mark.api
def test_get_latest_and_by_id_prediction_endpoints(client: TestClient):
    """Verify GET /api/v1/predictions/latest and GET /api/v1/predictions/{id}."""
    # Ensure at least one prediction exists
    post_res = client.post("/api/v1/predictions/ripple", json={"root_node_id": "node-6", "severity": "HIGH"})
    pred_id = post_res.json()["prediction_id"]

    # Fetch by ID
    res_id = client.get(f"/api/v1/predictions/{pred_id}")
    assert res_id.status_code == 200
    assert res_id.json()["prediction_id"] == pred_id

    # Fetch latest
    res_latest = client.get("/api/v1/predictions/latest")
    assert res_latest.status_code == 200
    assert "prediction_id" in res_latest.json()

    # 404 for unknown prediction ID
    res_404 = client.get("/api/v1/predictions/nonexistent-prediction-999")
    assert res_404.status_code == 404
    assert res_404.json()["error"]["error_code"] == "ENTITY_NOT_FOUND"


@pytest.mark.api
def test_ripple_prediction_unknown_node_404(client: TestClient):
    """Verify passing unknown node ID raises 404 EntityNotFoundError."""
    payload = {"root_node_id": "invalid-node-id-xyz"}
    response = client.post("/api/v1/predictions/ripple", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["error_code"] == "ENTITY_NOT_FOUND"
