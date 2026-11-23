"""Mock REST API routes serving supply chain graph topologies for D3.js and React Flow UI.

Provides graph topology querying, node inspection, route filtering, summary metrics,
and simulation of upstream disruptions for interactive frontend testing.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.core.exceptions import EntityNotFoundError
from src.services.synthetic_generator import SyntheticSupplyChainGenerator
from src.schemas.graph import (
    NodeType,
    RiskLevel,
    NodeStatus,
    RelationshipType,
    TransportMode,
    SupplyChainNode,
    ShippingRouteEdge,
    SupplyChainGraphTopology,
)

router = APIRouter(prefix="/graph", tags=["Supply Chain Graph"])


# ==============================================================================
# In-Memory Realistic Mock Graph Dataset
# ==============================================================================

def _generate_default_nodes() -> List[SupplyChainNode]:
    """Generate high-fidelity initial supply chain nodes matching the D3/React Flow dashboard."""
    return [
        SupplyChainNode(
            id="node-1",
            name="Apex Mining & Minerals",
            node_type=NodeType.SUPPLIER,
            country="Australia",
            location="Perth, Australia",
            tier="Tier 2",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="92%",
            lead_time="21 days",
            transit_method=TransportMode.OCEAN_FREIGHT,
            key_output="Lithium & Silicon Ingots",
            latitude=-31.95,
            longitude=115.86,
        ),
        SupplyChainNode(
            id="node-2",
            name="Shenzhen Micro-Wafer Corp",
            node_type=NodeType.SUPPLIER,
            country="China",
            location="Shenzhen, China",
            tier="Tier 1",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.MEDIUM,
            capacity="78%",
            lead_time="14 days",
            transit_method=TransportMode.OCEAN_FREIGHT,
            key_output="Wafer Substrates & Raw ICs",
            latitude=22.54,
            longitude=114.05,
        ),
        SupplyChainNode(
            id="node-3",
            name="Tokyo Precision Fab",
            node_type=NodeType.SUPPLIER,
            country="Japan",
            location="Yokohama, Japan",
            tier="Tier 1",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="95%",
            lead_time="10 days",
            transit_method=TransportMode.AIR_FREIGHT,
            key_output="Microcontrollers & Sensors",
            latitude=35.44,
            longitude=139.63,
        ),
        SupplyChainNode(
            id="node-4",
            name="Port of Singapore Terminal",
            node_type=NodeType.PORT,
            country="Singapore",
            location="Singapore",
            tier="Logistics Hub",
            status=NodeStatus.DEGRADED,
            risk_level=RiskLevel.HIGH,
            capacity="64%",
            lead_time="7 days",
            transit_method=TransportMode.OCEAN_FREIGHT,
            key_output="Maritime Transshipment TEU",
            latitude=1.35,
            longitude=103.81,
        ),
        SupplyChainNode(
            id="node-5",
            name="Taiwan Semiconductor Assembly",
            node_type=NodeType.MANUFACTURER,
            country="Taiwan",
            location="Hsinchu, Taiwan",
            tier="Primary Assembly",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="88%",
            lead_time="18 days",
            transit_method=TransportMode.OCEAN_FREIGHT,
            key_output="Finished Logic Chipsets",
            latitude=24.81,
            longitude=120.96,
        ),
        SupplyChainNode(
            id="node-6",
            name="Rotterdam Gateway Logistics",
            node_type=NodeType.PORT,
            country="Netherlands",
            location="Rotterdam, Netherlands",
            tier="Logistics Hub",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="91%",
            lead_time="5 days",
            transit_method=TransportMode.OCEAN_FREIGHT,
            key_output="Inbound European Freight",
            latitude=51.92,
            longitude=4.47,
        ),
        SupplyChainNode(
            id="node-7",
            name="Munich Automotive Electronics",
            node_type=NodeType.MANUFACTURER,
            country="Germany",
            location="Munich, Germany",
            tier="OEM Assembly",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.MEDIUM,
            capacity="82%",
            lead_time="12 days",
            transit_method=TransportMode.ROAD,
            key_output="Automotive Telematics Units",
            latitude=48.13,
            longitude=11.58,
        ),
        SupplyChainNode(
            id="node-8",
            name="Chicago Central Distribution",
            node_type=NodeType.WAREHOUSE,
            country="USA",
            location="Chicago, IL, USA",
            tier="Regional DC",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="85%",
            lead_time="3 days",
            transit_method=TransportMode.RAIL,
            key_output="Component Buffer Inventory",
            latitude=41.87,
            longitude=-87.62,
        ),
        SupplyChainNode(
            id="node-9",
            name="North America Retail Electronics",
            node_type=NodeType.RETAILER,
            country="USA",
            location="San Jose, CA, USA",
            tier="Consumer Market",
            status=NodeStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
            capacity="96%",
            lead_time="1 day",
            transit_method=TransportMode.ROAD,
            key_output="Consumer Electronic Goods",
            latitude=37.33,
            longitude=-121.88,
        ),
    ]


def _generate_default_edges() -> List[ShippingRouteEdge]:
    """Generate high-fidelity initial shipping route edges."""
    return [
        ShippingRouteEdge(
            id="e1-2",
            from_id="node-1",
            to_id="node-2",
            type=RelationshipType.SUPPLIES_TO,
            transport_mode=TransportMode.OCEAN_FREIGHT,
            lead_time_days=21.0,
            capacity=12000.0,
            active_disruption=False,
        ),
        ShippingRouteEdge(
            id="e2-4",
            from_id="node-2",
            to_id="node-4",
            type=RelationshipType.SHIPS_TO,
            transport_mode=TransportMode.OCEAN_FREIGHT,
            lead_time_days=6.0,
            capacity=8000.0,
            active_disruption=True,
            risk_multiplier=2.8,
            notes="Delayed due to regional port congestion",
        ),
        ShippingRouteEdge(
            id="e3-5",
            from_id="node-3",
            to_id="node-5",
            type=RelationshipType.SUPPLIES_TO,
            transport_mode=TransportMode.AIR_FREIGHT,
            lead_time_days=3.0,
            capacity=4500.0,
            active_disruption=False,
        ),
        ShippingRouteEdge(
            id="e4-5",
            from_id="node-4",
            to_id="node-5",
            type=RelationshipType.SHIPS_TO,
            transport_mode=TransportMode.OCEAN_FREIGHT,
            lead_time_days=8.0,
            capacity=7500.0,
            active_disruption=True,
            risk_multiplier=3.2,
        ),
        ShippingRouteEdge(
            id="e5-6",
            from_id="node-5",
            to_id="node-6",
            type=RelationshipType.SHIPS_TO,
            transport_mode=TransportMode.OCEAN_FREIGHT,
            lead_time_days=24.0,
            capacity=15000.0,
            active_disruption=False,
        ),
        ShippingRouteEdge(
            id="e6-7",
            from_id="node-6",
            to_id="node-7",
            type=RelationshipType.TRANSPORTS_TO,
            transport_mode=TransportMode.ROAD,
            lead_time_days=3.0,
            capacity=6000.0,
            active_disruption=False,
        ),
        ShippingRouteEdge(
            id="e5-8",
            from_id="node-5",
            to_id="node-8",
            type=RelationshipType.SHIPS_TO,
            transport_mode=TransportMode.MULTIMODAL,
            lead_time_days=18.0,
            capacity=9000.0,
            active_disruption=False,
        ),
        ShippingRouteEdge(
            id="e8-9",
            from_id="node-8",
            to_id="node-9",
            type=RelationshipType.DISTRIBUTES_TO,
            transport_mode=TransportMode.ROAD,
            lead_time_days=2.0,
            capacity=5000.0,
            active_disruption=False,
        ),
    ]


# Active mock memory state
_MOCK_NODES: Dict[str, SupplyChainNode] = {n.id: n for n in _generate_default_nodes()}
_MOCK_EDGES: Dict[str, ShippingRouteEdge] = {e.id: e for e in _generate_default_edges()}


# ==============================================================================
# Request & Response Schemas
# ==============================================================================

class GraphMetricsResponse(BaseModel):
    """Summary metrics schema aligned with React dashboard KPI cards."""
    total_suppliers: int = Field(description="Count of active supplier entities")
    manufacturing_units: int = Field(description="Count of manufacturing and assembly plants")
    distribution_centers: int = Field(description="Count of warehouses and logistics ports")
    retail_locations: int = Field(description="Count of retail distribution nodes")
    active_disruptions: int = Field(description="Count of routes currently suffering active disruptions")
    high_risk_node_count: int = Field(description="Count of nodes in High or Critical risk states")
    network_health_score_pct: float = Field(description="Overall network operational efficiency score (0-100)")


class SimulateDisruptionRequest(BaseModel):
    """Payload to trigger an interactive disruption simulation."""
    target_node_id: str = Field(description="Node to disrupt, e.g. 'node-4'")
    new_risk_level: RiskLevel = Field(default=RiskLevel.HIGH, description="Target node risk level")
    disruption_description: str = Field(description="Description of incident, e.g. 'Port congestion in Singapore'")
    delay_added_days: float = Field(default=12.0, ge=1.0, description="Transit delay to inject on connected routes")


# ==============================================================================
# Route Endpoints
# ==============================================================================

@router.get("/topology", response_model=SupplyChainGraphTopology, status_code=status.HTTP_200_OK)
async def get_graph_topology() -> SupplyChainGraphTopology:
    """Retrieve full supply chain topology formatted for both D3.js and React Flow canvas."""
    return SupplyChainGraphTopology.from_nodes_and_edges(
        nodes=list(_MOCK_NODES.values()),
        edges=list(_MOCK_EDGES.values())
    )


@router.get("/nodes", response_model=List[SupplyChainNode], status_code=status.HTTP_200_OK)
async def list_graph_nodes(
    node_type: Optional[NodeType] = Query(None, description="Filter by node classification"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk rating"),
    country: Optional[str] = Query(None, description="Filter by country of operation"),
    status: Optional[NodeStatus] = Query(None, description="Filter by operational status"),
) -> List[SupplyChainNode]:
    """List supply chain nodes with optional filtering."""
    results = list(_MOCK_NODES.values())
    if node_type:
        results = [n for n in results if n.node_type == node_type]
    if risk_level:
        results = [n for n in results if n.risk_level == risk_level]
    if country:
        results = [n for n in results if n.country.lower() == country.lower()]
    if status:
        results = [n for n in results if n.status == status]
    return results


@router.get("/nodes/{node_id}", response_model=SupplyChainNode, status_code=status.HTTP_200_OK)
async def get_node_by_id(node_id: str) -> SupplyChainNode:
    """Retrieve detailed metadata for a single supply chain node."""
    if node_id not in _MOCK_NODES:
        raise EntityNotFoundError(entity_type="SupplyChainNode", entity_id=node_id)
    return _MOCK_NODES[node_id]


@router.get("/edges", response_model=List[ShippingRouteEdge], status_code=status.HTTP_200_OK)
async def list_graph_edges(
    from_id: Optional[str] = Query(None, description="Filter routes departing from node ID"),
    to_id: Optional[str] = Query(None, description="Filter routes arriving at node ID"),
    active_disruption: Optional[bool] = Query(None, description="Filter by active disruption status"),
) -> List[ShippingRouteEdge]:
    """List directed shipping routes and transport edges."""
    results = list(_MOCK_EDGES.values())
    if from_id:
        results = [e for e in results if e.from_id == from_id]
    if to_id:
        results = [e for e in results if e.to_id == to_id]
    if active_disruption is not None:
        results = [e for e in results if e.active_disruption == active_disruption]
    return results


@router.get("/metrics", response_model=GraphMetricsResponse, status_code=status.HTTP_200_OK)
async def get_graph_metrics() -> GraphMetricsResponse:
    """Provide aggregated supply chain metrics for executive dashboard cards."""
    nodes = list(_MOCK_NODES.values())
    edges = list(_MOCK_EDGES.values())

    suppliers = sum(1 for n in nodes if n.node_type == NodeType.SUPPLIER)
    manufacturers = sum(1 for n in nodes if n.node_type == NodeType.MANUFACTURER)
    logistics = sum(1 for n in nodes if n.node_type in (NodeType.PORT, NodeType.WAREHOUSE))
    retailers = sum(1 for n in nodes if n.node_type == NodeType.RETAILER)
    disruptions = sum(1 for e in edges if e.active_disruption)
    high_risk = sum(1 for n in nodes if n.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL))

    # Health score computation
    total_nodes = len(nodes) or 1
    degraded_penalty = (high_risk / total_nodes) * 50.0 + (disruptions / (len(edges) or 1)) * 30.0
    health_score = max(0.0, round(100.0 - degraded_penalty, 1))

    return GraphMetricsResponse(
        total_suppliers=suppliers,
        manufacturing_units=manufacturers,
        distribution_centers=logistics,
        retail_locations=retailers,
        active_disruptions=disruptions,
        high_risk_node_count=high_risk,
        network_health_score_pct=health_score,
    )


@router.post("/simulate-disruption", response_model=SupplyChainGraphTopology, status_code=status.HTTP_200_OK)
async def simulate_disruption(payload: SimulateDisruptionRequest) -> SupplyChainGraphTopology:
    """Simulate an upstream disruption incident and return updated graph topology."""
    if payload.target_node_id not in _MOCK_NODES:
        raise EntityNotFoundError(entity_type="SupplyChainNode", entity_id=payload.target_node_id)

    # 1. Update target node risk and status
    target_node = _MOCK_NODES[payload.target_node_id]
    target_node.risk_level = payload.new_risk_level
    target_node.status = NodeStatus.DISRUPTED if payload.new_risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) else NodeStatus.DEGRADED
    target_node.metadata["last_incident"] = payload.disruption_description
    target_node.metadata["incident_timestamp"] = datetime.now(timezone.utc).isoformat()

    # 2. Propagate disruption to outbound and inbound edges
    for edge in _MOCK_EDGES.values():
        if edge.from_id == payload.target_node_id or edge.to_id == payload.target_node_id:
            edge.active_disruption = True
            edge.lead_time_days += payload.delay_added_days
            edge.risk_multiplier = 3.5
            edge.notes = f"Impacted by incident: {payload.disruption_description}"

    return SupplyChainGraphTopology.from_nodes_and_edges(
        nodes=list(_MOCK_NODES.values()),
        edges=list(_MOCK_EDGES.values())
    )


@router.get("/synthetic", response_model=SupplyChainGraphTopology, status_code=status.HTTP_200_OK)
async def get_synthetic_graph_topology(
    node_count: int = Query(default=1000, ge=10, le=5000, description="Target total node count"),
    edge_density: float = Query(default=1.8, ge=1.0, le=5.0, description="Average forward outward edges per node"),
    seed: Optional[int] = Query(default=42, description="Random seed for reproducible graph structure"),
) -> SupplyChainGraphTopology:
    """Generate large-scale synthetic supply chain topology for UI rendering and stress testing."""
    generator = SyntheticSupplyChainGenerator(seed=seed)
    return generator.generate_topology(node_count=node_count, edge_density=edge_density)


@router.get("/benchmark", status_code=status.HTTP_200_OK)
async def benchmark_graph_serialization(
    node_count: int = Query(default=1000, ge=10, le=5000, description="Node count to profile"),
    edge_density: float = Query(default=1.8, ge=1.0, le=5.0, description="Edge density"),
    seed: Optional[int] = Query(default=42, description="Random seed"),
) -> Dict[str, Any]:
    """Benchmark Pydantic model serialization speed and payload footprint for large graphs."""
    generator = SyntheticSupplyChainGenerator(seed=seed)
    return generator.benchmark_serialization(node_count=node_count, edge_density=edge_density)
