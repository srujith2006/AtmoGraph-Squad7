"""Pydantic data contracts for AtmoGraph supply chain graph network.

Defines schemas for Supplier/Manufacturer nodes, shipping route edges,
NLP breaking news disruption alerts, 30/60/90-day GNN predictions, and React Flow / D3 UI payloads.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==============================================================================
# Enumerations
# ==============================================================================

class NodeType(str, Enum):
    """Core supply chain node classifications."""
    SUPPLIER = "supplier"
    MANUFACTURER = "manufacturer"
    PORT = "port"
    WAREHOUSE = "warehouse"
    RETAILER = "retailer"


class RiskLevel(str, Enum):
    """Normalized risk classification levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class NodeStatus(str, Enum):
    """Operational status of a supply chain entity."""
    ACTIVE = "Active"
    DEGRADED = "Degraded"
    DISRUPTED = "Disrupted"
    OFFLINE = "Offline"


class RelationshipType(str, Enum):
    """Graph edge relationship types between nodes."""
    SUPPLIES_TO = "SUPPLIES_TO"
    SHIPS_TO = "SHIPS_TO"
    TRANSPORTS_TO = "TRANSPORTS_TO"
    DISTRIBUTES_TO = "DISTRIBUTES_TO"


class TransportMode(str, Enum):
    """Logistics transit method for supply chain routes."""
    OCEAN_FREIGHT = "Ocean Freight"
    AIR_FREIGHT = "Air Freight"
    RAIL = "Rail"
    ROAD = "Road Trucking"
    MULTIMODAL = "Multimodal"


class DisruptionSeverity(str, Enum):
    """Severity rating for NLP disruption events."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TimelineHorizon(int, Enum):
    """Prediction horizon in calendar days."""
    DAY_30 = 30
    DAY_60 = 60
    DAY_90 = 90


# ==============================================================================
# React Flow Presentation Models (Frontend Alignment)
# ==============================================================================

class ReactFlowPosition(BaseModel):
    """2D coordinates on the React Flow / D3 canvas."""
    x: float
    y: float


class ReactFlowNode(BaseModel):
    """React Flow native node specification."""
    id: str
    type: str = "supplyChainNode"
    position: ReactFlowPosition
    data: Dict[str, Any]


class ReactFlowEdge(BaseModel):
    """React Flow native edge specification."""
    id: str
    source: str
    target: str
    animated: bool = True
    style: Dict[str, Any] = Field(default_factory=lambda: {"stroke": "#94a3b8", "strokeWidth": 2})
    markerEnd: Optional[Dict[str, Any]] = None


# ==============================================================================
# Core Node Models
# ==============================================================================

class SupplyChainNode(BaseModel):
    """Generic supply chain graph node representing suppliers, factories, ports, etc."""
    id: str = Field(description="Unique node identifier, e.g. S001, F001, P001")
    name: str = Field(description="Entity or facility legal name")
    node_type: NodeType = Field(default=NodeType.SUPPLIER, description="Node category")
    country: str = Field(description="ISO country name or code")
    location: Optional[str] = Field(default=None, description="City, region, or port location")
    tier: Optional[str] = Field(default="Tier 1", description="Supplier tier or facility classification")
    status: NodeStatus = Field(default=NodeStatus.ACTIVE, description="Current operational state")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Assessed disruption risk rating")
    capacity: Optional[str] = Field(default="90%", description="Current operational capacity percentage")
    lead_time: Optional[str] = Field(default="14 days", description="Estimated outbound dispatch lead time")
    transit_method: Optional[TransportMode] = Field(default=TransportMode.OCEAN_FREIGHT, description="Primary outbound transport")
    key_output: Optional[str] = Field(default=None, description="Primary produced or handled commodity")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Geographic latitude")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Geographic longitude")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary domain properties")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalize_risk_level(cls, val: Any) -> str:
        """Case-insensitively normalize risk level string."""
        if isinstance(val, str):
            val_clean = val.strip().capitalize()
            for r in RiskLevel:
                if r.value.lower() == val.lower():
                    return r.value
            return val_clean
        return val

    def to_react_flow(self, x: float = 100.0, y: float = 100.0) -> ReactFlowNode:
        """Convert this node into a React Flow canvas node schema."""
        return ReactFlowNode(
            id=self.id,
            type="supplyChainNode",
            position=ReactFlowPosition(x=x, y=y),
            data={
                "category": self.node_type,
                "nodeType": f"{self.node_type.capitalize()} Node",
                "name": self.name,
                "location": self.location or f"{self.name}, {self.country}",
                "tier": self.tier or "Tier 1",
                "status": self.status,
                "leadTime": self.lead_time or "N/A",
                "capacity": self.capacity or "N/A",
                "riskFactor": self.risk_level,
                "transitMethod": self.transit_method or "Ocean Freight",
                "keyOutput": self.key_output or "General Cargo",
            }
        )


class SupplierNode(SupplyChainNode):
    """Specialized tier supplier producing raw materials or subcomponents."""
    node_type: NodeType = Field(default=NodeType.SUPPLIER)
    materials_supplied: List[str] = Field(default_factory=list, description="Raw materials or components provided")
    supplier_reliability_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Historical delivery reliability (0-1)")


class ManufacturerNode(SupplyChainNode):
    """Assembly or manufacturing plant converting inputs into finished products."""
    node_type: NodeType = NodeType.MANUFACTURER
    product_lines: List[str] = Field(default_factory=list, description="Manufactured product SKUs")
    assembly_capacity_units_per_month: int = Field(default=10000, description="Monthly throughput capacity")
    buffer_stock_days: int = Field(default=14, ge=0, description="Inventory runway before starvation")


class PortNode(SupplyChainNode):
    """Maritime or multimodal shipping hub."""
    node_type: NodeType = NodeType.PORT
    throughput_teu: int = Field(default=500000, description="Annual container volume in TEUs")
    congestion_index: float = Field(default=0.1, ge=0.0, le=1.0, description="Live congestion scale from 0 to 1")
    avg_berth_wait_hours: float = Field(default=12.0, ge=0.0, description="Average vessel wait time")


class WarehouseNode(SupplyChainNode):
    """Regional or central distribution center."""
    node_type: NodeType = NodeType.WAREHOUSE
    storage_capacity_sqm: int = Field(default=25000, description="Total storage floor area in square meters")
    inventory_turnover_rate: float = Field(default=6.0, description="Inventory turns per year")


class RetailerNode(SupplyChainNode):
    """Consumer-facing distribution outlet or market partner."""
    node_type: NodeType = NodeType.RETAILER
    store_count: int = Field(default=50, description="Number of retail outlets served")
    market_region: str = Field(default="North America", description="Target consumer market")


# ==============================================================================
# Edge / Route Models
# ==============================================================================

class ShippingRouteEdge(BaseModel):
    """Directed connection representing logistics transit or material supply between nodes."""
    id: str = Field(description="Unique edge identifier, e.g. e-S001-F001")
    from_id: str = Field(description="Origin node ID")
    to_id: str = Field(description="Destination node ID")
    type: RelationshipType = Field(default=RelationshipType.SUPPLIES_TO, description="Graph relationship type")
    transport_mode: TransportMode = Field(default=TransportMode.OCEAN_FREIGHT, description="Transit modality")
    lead_time_days: float = Field(default=7.0, ge=0.0, description="Transit or delivery time in days")
    capacity: Optional[float] = Field(default=None, description="Volume capacity (e.g. units or TEUs)")
    risk_multiplier: float = Field(default=1.0, ge=0.1, le=10.0, description="Risk propagation coefficient")
    active_disruption: bool = Field(default=False, description="True if this route currently experiences delays")
    notes: Optional[str] = Field(default=None, description="Operational notes or route restrictions")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    def to_react_flow(self) -> ReactFlowEdge:
        """Convert edge into React Flow edge schema with dynamic stroke color based on disruption."""
        color = "#ef4444" if self.active_disruption else "#94a3b8"  # Red if disrupted, slate otherwise
        return ReactFlowEdge(
            id=self.id,
            source=self.from_id,
            target=self.to_id,
            animated=self.active_disruption,
            style={"stroke": color, "strokeWidth": 2.5 if self.active_disruption else 1.5},
            markerEnd={
                "type": "arrowclosed",
                "width": 16,
                "height": 16,
                "color": color,
            }
        )


# ==============================================================================
# NLP Ingestion & Disruption Alert Models
# ==============================================================================

class NLPExtractedEntity(BaseModel):
    """Named Entity extracted by spaCy / HuggingFace from live news text."""
    id: str = Field(description="Entity identifier, e.g. E1")
    name: str = Field(description="Entity textual mention, e.g. 'Singapore Port'")
    type: str = Field(description="Entity type: GPE, ORG, RISK, SHIPMENT, FACILITY")
    start_char: Optional[int] = Field(default=None, description="Starting character offset in source text")
    end_char: Optional[int] = Field(default=None, description="Ending character offset in source text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Model confidence score (0-1)")


class NLPDisruptionAlert(BaseModel):
    """Structured disruption alert generated by NLP ingestion engine from news streams."""
    alert_id: str = Field(description="Unique alert UUID")
    title: str = Field(description="Disruption headline or title")
    source: str = Field(description="Originating publication, e.g. 'Reuters', 'AIS Port Feed'")
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Publication timestamp")
    severity: DisruptionSeverity = Field(default=DisruptionSeverity.MEDIUM, description="Disruption severity rating")
    primary_risk: str = Field(description="Identified primary risk type, e.g. 'Port Strike', 'Canal Congestion'")
    location: Optional[str] = Field(default=None, description="Geographic location affected")
    affected_node_ids: List[str] = Field(default_factory=list, description="IDs of graph nodes directly impacted")
    entities: List[NLPExtractedEntity] = Field(default_factory=list, description="Named entities identified in article")
    evidence_text: str = Field(description="Snippet or article excerpt supporting this disruption")
    confidence_score: float = Field(default=0.88, ge=0.0, le=1.0, description="Overall NLP extraction confidence")

    model_config = ConfigDict(use_enum_values=True)


# ==============================================================================
# 30/60/90-Day GNN Prediction Models
# ==============================================================================

class HopDelayImpact(BaseModel):
    """Predicted delay and risk impact on a single node across graph hops."""
    hop_distance: int = Field(ge=1, description="Topological distance from root disruption (1 = direct child)")
    node_id: str = Field(description="Impacted supply chain node ID")
    node_name: str = Field(description="Node name")
    node_type: NodeType = Field(description="Node type")
    predicted_delay_days: float = Field(ge=0.0, description="Mean predicted delay in days")
    delay_confidence_lower: float = Field(ge=0.0, description="Lower bound of 95% confidence interval")
    delay_confidence_upper: float = Field(ge=0.0, description="Upper bound of 95% confidence interval")
    propagation_probability: float = Field(ge=0.0, le=1.0, description="Likelihood of ripple impact reaching node")
    downstream_nodes_affected: int = Field(default=0, ge=0, description="Number of additional nodes depending on this node")

    model_config = ConfigDict(use_enum_values=True)


class HorizonPrediction(BaseModel):
    """Aggregated GNN ripple effect prediction for a specific temporal window (30/60/90 days)."""
    horizon_days: int = Field(description="Simulated timeline window: 30, 60, or 90 days")
    mean_network_delay_days: float = Field(ge=0.0, description="Average delay across all impacted nodes")
    max_single_node_delay_days: float = Field(ge=0.0, description="Maximum delay sustained by any single node")
    severely_impacted_node_count: int = Field(ge=0, description="Count of nodes suffering delays > 14 days")
    impacted_nodes: List[HopDelayImpact] = Field(default_factory=list, description="Node-by-node delay breakdown")
    cumulative_production_loss_pct: float = Field(ge=0.0, le=100.0, description="Estimated total network throughput loss %")


class GNNRipplePredictionResponse(BaseModel):
    """Complete GNN prediction response containing multi-hop ripple forecasts for 30, 60, and 90 days."""
    prediction_id: str = Field(description="Unique prediction execution ID")
    disruption_alert_id: str = Field(description="Reference ID of originating NLP disruption alert")
    root_node_id: str = Field(description="Epicenter node where disruption originated")
    root_node_name: str = Field(description="Name of epicenter node")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Prediction timestamp")
    model_version: str = Field(default="gnn-sage-v1.0.0", description="PyTorch Geometric model weights version")
    critical_delay_path: List[str] = Field(
        default_factory=list,
        description="Ordered sequence of node IDs representing the worst-case propagation path"
    )
    predictions_by_horizon: Dict[str, HorizonPrediction] = Field(
        description="Horizon predictions keyed by '30_day', '60_day', and '90_day'"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable mitigation suggestions, e.g. rerouting or buffer activation"
    )

    model_config = ConfigDict(use_enum_values=True)


# ==============================================================================
# Full Graph Topology Envelope (Frontend REST & D3 Endpoint Contract)
# ==============================================================================

class SupplyChainGraphTopology(BaseModel):
    """Full supply chain graph envelope matching backend Neo4j data and React Flow canvas requirements."""
    nodes: List[SupplyChainNode] = Field(default_factory=list)
    edges: List[ShippingRouteEdge] = Field(default_factory=list)
    total_nodes: int = Field(default=0)
    total_edges: int = Field(default=0)
    react_flow_nodes: List[ReactFlowNode] = Field(default_factory=list)
    react_flow_edges: List[ReactFlowEdge] = Field(default_factory=list)
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_nodes_and_edges(
        cls,
        nodes: List[SupplyChainNode],
        edges: List[ShippingRouteEdge]
    ) -> "SupplyChainGraphTopology":
        """Factory method to assemble topology and auto-generate React Flow canvas representations."""
        # Simple coordinate distribution layout for React Flow nodes
        rf_nodes = []
        for idx, n in enumerate(nodes):
            x = 80.0 + (idx % 4) * 260.0
            y = 120.0 + (idx // 4) * 180.0
            rf_nodes.append(n.to_react_flow(x=x, y=y))

        rf_edges = [e.to_react_flow() for e in edges]

        return cls(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
            react_flow_nodes=rf_nodes,
            react_flow_edges=rf_edges,
            last_synced_at=datetime.now(timezone.utc),
        )
