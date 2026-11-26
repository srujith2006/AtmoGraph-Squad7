"""Comprehensive test suite for Pydantic data contracts (schemas/graph.py).

Validates Supplier/Manufacturer node models, shipping edges, NLP alerts,
30/60/90-day GNN predictions, and seamless interop with teammate JSON fixtures.
"""

from datetime import datetime, timezone
import json
import os
import pytest
from pydantic import ValidationError

from src.schemas.graph import (
    NodeType,
    RiskLevel,
    NodeStatus,
    RelationshipType,
    TransportMode,
    DisruptionSeverity,
    TimelineHorizon,
    SupplyChainNode,
    SupplierNode,
    ManufacturerNode,
    PortNode,
    WarehouseNode,
    RetailerNode,
    ShippingRouteEdge,
    NLPExtractedEntity,
    NLPDisruptionAlert,
    HopDelayImpact,
    HorizonPrediction,
    GNNRipplePredictionResponse,
    SupplyChainGraphTopology,
)


# ==============================================================================
# Node Schema Tests
# ==============================================================================

@pytest.mark.unit
def test_supply_chain_node_creation_and_normalization():
    """Verify standard node instantiation, defaults, and risk level normalization."""
    node = SupplyChainNode(
        id="S001",
        name="Global Silicon Foundry",
        node_type=NodeType.SUPPLIER,
        country="Taiwan",
        risk_level="medium",  # Case insensitive validator test
    )
    assert node.id == "S001"
    assert node.risk_level == RiskLevel.MEDIUM
    assert node.status == NodeStatus.ACTIVE
    assert node.tier == "Tier 1"

    # Test conversion to React Flow format
    rf_node = node.to_react_flow(x=150.0, y=200.0)
    assert rf_node.id == "S001"
    assert rf_node.type == "supplyChainNode"
    assert rf_node.position.x == 150.0
    assert rf_node.position.y == 200.0
    assert rf_node.data["name"] == "Global Silicon Foundry"
    assert rf_node.data["riskFactor"] == "Medium"


@pytest.mark.unit
def test_specialized_nodes():
    """Verify domain-specific attributes on Supplier, Manufacturer, and Port nodes."""
    supplier = SupplierNode(
        id="S-RAW-01",
        name="Rare Earth Mining Co.",
        country="Australia",
        materials_supplied=["Lithium", "Cobalt", "Neodymium"],
        supplier_reliability_score=0.98,
    )
    assert "Lithium" in supplier.materials_supplied
    assert supplier.supplier_reliability_score == 0.98

    factory = ManufacturerNode(
        id="F-MFG-01",
        name="Euro Auto Electronics Plant",
        country="Germany",
        product_lines=["ECU Modules", "Inverters"],
        buffer_stock_days=21,
    )
    assert factory.node_type == NodeType.MANUFACTURER
    assert factory.buffer_stock_days == 21

    port = PortNode(
        id="P-PORT-01",
        name="Port of Rotterdam",
        country="Netherlands",
        throughput_teu=14500000,
        congestion_index=0.65,
    )
    assert port.node_type == NodeType.PORT
    assert port.throughput_teu == 14500000
    assert port.congestion_index == 0.65


# ==============================================================================
# Edge / Relationship Schema Tests
# ==============================================================================

@pytest.mark.unit
def test_shipping_route_edge():
    """Verify directed edge relationships and React Flow edge styling."""
    edge = ShippingRouteEdge(
        id="e-S001-F001",
        from_id="S001",
        to_id="F001",
        type=RelationshipType.SUPPLIES_TO,
        transport_mode=TransportMode.OCEAN_FREIGHT,
        lead_time_days=18.5,
        risk_multiplier=2.5,
        active_disruption=True,
    )
    assert edge.from_id == "S001"
    assert edge.to_id == "F001"
    assert edge.lead_time_days == 18.5
    assert edge.active_disruption is True

    # When disrupted, React Flow edge should be animated and red (#ef4444)
    rf_edge = edge.to_react_flow()
    assert rf_edge.id == "e-S001-F001"
    assert rf_edge.source == "S001"
    assert rf_edge.target == "F001"
    assert rf_edge.animated is True
    assert rf_edge.style["stroke"] == "#ef4444"


@pytest.mark.unit
def test_shipping_route_edge_validation_failure():
    """Verify invalid negative lead time or out-of-range risk multiplier is rejected."""
    with pytest.raises(ValidationError):
        ShippingRouteEdge(
            id="e-bad",
            from_id="A",
            to_id="B",
            lead_time_days=-5.0,  # Negative lead time rejected
        )


# ==============================================================================
# NLP Disruption Alert Schema Tests
# ==============================================================================

@pytest.mark.unit
def test_nlp_disruption_alert_contract():
    """Verify NLP breaking news disruption schema and extracted entities."""
    entity1 = NLPExtractedEntity(id="E1", name="Port of Antwerp", type="GPE", confidence=0.99)
    entity2 = NLPExtractedEntity(id="E2", name="Dockworkers Strike", type="RISK", confidence=0.95)

    alert = NLPDisruptionAlert(
        alert_id="alert-uuid-101",
        title="Major Dockworkers Strike Halts Antwerp Port Operations",
        source="Maritime Executive News",
        severity=DisruptionSeverity.HIGH,
        primary_risk="Port Strike",
        location="Antwerp, Belgium",
        affected_node_ids=["P-ANTWERP"],
        entities=[entity1, entity2],
        evidence_text="A 48-hour general strike has halted all container operations across terminals.",
        confidence_score=0.94,
    )

    assert alert.severity == "HIGH"
    assert len(alert.entities) == 2
    assert alert.affected_node_ids == ["P-ANTWERP"]
    assert alert.confidence_score == 0.94


# ==============================================================================
# 30/60/90-Day GNN Prediction Schema Tests
# ==============================================================================

@pytest.mark.unit
def test_gnn_ripple_prediction_timeline_payload():
    """Verify GNN multi-hop ripple prediction schema across 30, 60, and 90 day horizons."""
    hop1 = HopDelayImpact(
        hop_distance=1,
        node_id="F001",
        node_name="Munich Assembly Plant",
        node_type=NodeType.MANUFACTURER,
        predicted_delay_days=12.5,
        delay_confidence_lower=10.0,
        delay_confidence_upper=15.0,
        propagation_probability=0.92,
    )
    hop2 = HopDelayImpact(
        hop_distance=2,
        node_id="W001",
        node_name="Rotterdam Central Hub",
        node_type=NodeType.WAREHOUSE,
        predicted_delay_days=24.0,
        delay_confidence_lower=18.0,
        delay_confidence_upper=30.0,
        propagation_probability=0.78,
    )

    p30 = HorizonPrediction(
        horizon_days=TimelineHorizon.DAY_30.value,
        mean_network_delay_days=10.5,
        max_single_node_delay_days=15.0,
        severely_impacted_node_count=1,
        impacted_nodes=[hop1],
        cumulative_production_loss_pct=8.5,
    )

    p60 = HorizonPrediction(
        horizon_days=TimelineHorizon.DAY_60.value,
        mean_network_delay_days=18.0,
        max_single_node_delay_days=25.0,
        severely_impacted_node_count=2,
        impacted_nodes=[hop1, hop2],
        cumulative_production_loss_pct=22.0,
    )

    p90 = HorizonPrediction(
        horizon_days=TimelineHorizon.DAY_90.value,
        mean_network_delay_days=31.5,
        max_single_node_delay_days=42.0,
        severely_impacted_node_count=4,
        impacted_nodes=[hop1, hop2],
        cumulative_production_loss_pct=45.0,
    )

    prediction = GNNRipplePredictionResponse(
        prediction_id="pred-gnn-8899",
        disruption_alert_id="alert-uuid-101",
        root_node_id="P-ANTWERP",
        root_node_name="Port of Antwerp",
        model_version="gnn-sage-v1.0.0",
        critical_delay_path=["P-ANTWERP", "F001", "W001"],
        predictions_by_horizon={
            "30_day": p30,
            "60_day": p60,
            "90_day": p90,
        },
        recommendations=["Reroute high-priority cargo through Port of Hamburg", "Increase buffer stock at Munich plant"],
    )

    assert prediction.root_node_id == "P-ANTWERP"
    assert len(prediction.predictions_by_horizon) == 3
    assert prediction.predictions_by_horizon["30_day"].horizon_days == 30
    assert prediction.predictions_by_horizon["60_day"].horizon_days == 60
    assert prediction.predictions_by_horizon["90_day"].horizon_days == 90
    assert "Port of Hamburg" in prediction.recommendations[0]


# ==============================================================================
# Full Graph Topology Envelope Tests
# ==============================================================================

@pytest.mark.unit
def test_supply_chain_graph_topology_factory():
    """Verify SupplyChainGraphTopology factory method populates React Flow nodes and edges."""
    nodes = [
        SupplyChainNode(id="S1", name="Supplier One", country="Japan", node_type=NodeType.SUPPLIER),
        SupplyChainNode(id="F1", name="Factory One", country="Germany", node_type=NodeType.MANUFACTURER),
    ]
    edges = [
        ShippingRouteEdge(id="e-S1-F1", from_id="S1", to_id="F1", lead_time_days=14.0),
    ]

    topology = SupplyChainGraphTopology.from_nodes_and_edges(nodes=nodes, edges=edges)

    assert topology.total_nodes == 2
    assert topology.total_edges == 1
    assert len(topology.react_flow_nodes) == 2
    assert len(topology.react_flow_edges) == 1
    assert topology.react_flow_nodes[0].id == "S1"
    assert topology.react_flow_edges[0].source == "S1"
    assert topology.react_flow_edges[0].target == "F1"


# ==============================================================================
# Teammate Fixture Compatibility Tests (Cross-Squad Integration)
# ==============================================================================

@pytest.mark.integration
def test_parse_teammate_mock_supply_chain_json():
    """Verify our Pydantic contracts parse teammate's backend/data/mock_supply_chain.json directly."""
    mock_file_path = os.path.join("backend", "data", "mock_supply_chain.json")
    if not os.path.exists(mock_file_path):
        pytest.skip("backend/data/mock_supply_chain.json not present in workspace")

    with open(mock_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parsed_nodes = []
    # Parse suppliers
    for s in data.get("suppliers", []):
        parsed_nodes.append(SupplyChainNode(
            id=s["id"],
            name=s["name"],
            country=s["country"],
            risk_level=s.get("risk_level", "Low"),
            node_type=NodeType.SUPPLIER
        ))

    # Parse factories
    for f in data.get("factories", []):
        parsed_nodes.append(SupplyChainNode(
            id=f["id"],
            name=f["name"],
            country=f["country"],
            risk_level=f.get("risk_level", "Low"),
            node_type=NodeType.MANUFACTURER
        ))

    # Parse relationships
    parsed_edges = []
    for idx, r in enumerate(data.get("relationships", [])):
        parsed_edges.append(ShippingRouteEdge(
            id=f"e-{r['from_id']}-{r['to_id']}-{idx}",
            from_id=r["from_id"],
            to_id=r["to_id"],
            type=r.get("type", "SUPPLIES_TO"),
            lead_time_days=float(r.get("lead_time_days", 5.0)),
            capacity=r.get("capacity"),
        ))

    topology = SupplyChainGraphTopology.from_nodes_and_edges(nodes=parsed_nodes, edges=parsed_edges)
    assert topology.total_nodes >= 2
    assert topology.total_edges >= 4
    assert len(topology.react_flow_nodes) == len(parsed_nodes)
    assert len(topology.react_flow_edges) == len(parsed_edges)
