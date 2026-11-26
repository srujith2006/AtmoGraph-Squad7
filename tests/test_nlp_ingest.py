"""Comprehensive test suite for Day 5 NLP ingestion webhook and breaking news fixtures."""

import json
import os
import pytest
from starlette.testclient import TestClient

from tests.fixtures.nlp_news_fixtures import (
    EUROPEAN_PORT_STRIKE_FIXTURE,
    SINGAPORE_PORT_CONGESTION_FIXTURE,
    SHENZHEN_FAB_DISRUPTION_FIXTURE,
)
from src.core.config import get_settings


@pytest.mark.api
def test_ingest_european_port_strike_webhook(client: TestClient):
    """Verify European port strike breaking news links to Rotterdam and North American nodes."""
    response = client.post("/api/v1/nlp/ingest", json=EUROPEAN_PORT_STRIKE_FIXTURE)
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "ingested"
    assert "alert_id" in data
    assert data["severity"] == "CRITICAL"
    assert data["matched_nodes_count"] >= 1

    # Verify node matching
    matched_ids = [m["node_id"] for m in data["matched_nodes"]]
    assert "node-6" in matched_ids or "node-9" in matched_ids

    # Verify graph node was updated in memory
    res_node = client.get("/api/v1/graph/nodes/node-6")
    assert res_node.status_code == 200
    node6 = res_node.json()
    assert node6["risk_level"] in ("High", "Critical")


@pytest.mark.api
def test_ingest_singapore_port_congestion(client: TestClient):
    """Verify Singapore port congestion links directly to Port of Singapore node."""
    response = client.post("/api/v1/nlp/ingest", json=SINGAPORE_PORT_CONGESTION_FIXTURE)
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "ingested"
    matched_ids = [m["node_id"] for m in data["matched_nodes"]]
    assert "node-4" in matched_ids  # Port of Singapore terminal


@pytest.mark.api
def test_ingest_shenzhen_fab_disruption(client: TestClient):
    """Verify Shenzhen fab incident links to Shenzhen Micro-Wafer Corp."""
    response = client.post("/api/v1/nlp/ingest", json=SHENZHEN_FAB_DISRUPTION_FIXTURE)
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "ingested"
    matched_ids = [m["node_id"] for m in data["matched_nodes"]]
    assert "node-2" in matched_ids


@pytest.mark.api
def test_get_disruption_alerts_and_filtering(client: TestClient):
    """Verify retrieving processed disruption alerts and filtering by severity."""
    # Ensure at least one alert exists
    client.post("/api/v1/nlp/ingest", json=EUROPEAN_PORT_STRIKE_FIXTURE)

    response = client.get("/api/v1/nlp/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 1

    # Filter critical
    res_crit = client.get("/api/v1/nlp/alerts?severity=CRITICAL")
    assert res_crit.status_code == 200
    crit_alerts = res_crit.json()
    for a in crit_alerts:
        assert a["severity"] == "CRITICAL"


@pytest.mark.api
def test_get_single_disruption_alert_success_and_404(client: TestClient):
    """Verify fetching single alert by ID and 404 on nonexistent ID."""
    ingest_res = client.post("/api/v1/nlp/ingest", json=SHENZHEN_FAB_DISRUPTION_FIXTURE)
    alert_id = ingest_res.json()["alert_id"]

    res_ok = client.get(f"/api/v1/nlp/alerts/{alert_id}")
    assert res_ok.status_code == 200
    assert res_ok.json()["alert_id"] == alert_id

    res_404 = client.get("/api/v1/nlp/alerts/nonexistent-alert-uuid")
    assert res_404.status_code == 404
    assert res_404.json()["error"]["error_code"] == "ENTITY_NOT_FOUND"


@pytest.mark.integration
def test_cross_team_sample_article_json_compatibility(client: TestClient):
    """Verify direct ingestion of teammate Srujith's backend/data/articles/sample_article.json."""
    file_path = os.path.join("backend", "data", "articles", "sample_article.json")
    if not os.path.exists(file_path):
        pytest.skip(f"Teammate article file {file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    response = client.post("/api/v1/nlp/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"
    assert "node-4" in [m["node_id"] for m in data["matched_nodes"]]


@pytest.mark.integration
def test_cross_team_atmograph_week2_updated_json_compatibility(client: TestClient):
    """Verify direct ingestion of teammate Lali's atmograph_week2_updated.json."""
    file_path = "atmograph_week2_updated.json"
    if not os.path.exists(file_path):
        pytest.skip(f"Teammate article file {file_path} not found")

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    response = client.post("/api/v1/nlp/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"


@pytest.mark.api
def test_reject_empty_article_text(client: TestClient):
    """Verify empty article string returns 422 validation failure envelope."""
    payload = {"article": "   "}
    response = client.post("/api/v1/nlp/ingest", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["error_code"] == "PAYLOAD_VALIDATION_ERROR"


@pytest.mark.api
def test_webhook_secret_authentication(client: TestClient):
    """Verify valid X-Webhook-Secret succeeds and invalid secret is rejected."""
    settings = get_settings()

    # Valid secret header
    res_valid = client.post(
        "/api/v1/nlp/ingest",
        json=SINGAPORE_PORT_CONGESTION_FIXTURE,
        headers={"X-Webhook-Secret": settings.nlp_webhook_secret}
    )
    assert res_valid.status_code == 201

    # Invalid secret header
    res_invalid = client.post(
        "/api/v1/nlp/ingest",
        json=SINGAPORE_PORT_CONGESTION_FIXTURE,
        headers={"X-Webhook-Secret": "wrong-malicious-token"}
    )
    assert res_invalid.status_code == 422
    assert res_invalid.json()["error"]["error_code"] == "PAYLOAD_VALIDATION_ERROR"
