"""Pydantic data contracts and schemas package for AtmoGraph.

Defines unified types for supply chain graph nodes, shipping route edges,
NLP breaking news disruption alerts, and multi-hop GNN ripple-effect predictions.
"""

from src.schemas.graph import (
    # Enums
    NodeType,
    RiskLevel,
    NodeStatus,
    RelationshipType,
    TransportMode,
    DisruptionSeverity,
    TimelineHorizon,
    
    # Node Models
    SupplyChainNode,
    SupplierNode,
    ManufacturerNode,
    PortNode,
    WarehouseNode,
    RetailerNode,
    
    # Edge Models
    ShippingRouteEdge,
    
    # NLP Models
    NLPExtractedEntity,
    NLPDisruptionAlert,
    
    # GNN Prediction Models
    HopDelayImpact,
    HorizonPrediction,
    GNNRipplePredictionResponse,
    
    # React Flow / D3 UI Interop Models
    ReactFlowPosition,
    ReactFlowNode,
    ReactFlowEdge,
    SupplyChainGraphTopology,
)

from src.schemas.nlp import (
    NLPRelationship,
    NLPDetectedRisk,
    NLPIngestRequest,
    NLPIngestResponse,
    MatchedNodeImpact,
)

__all__ = [
    "NodeType",
    "RiskLevel",
    "NodeStatus",
    "RelationshipType",
    "TransportMode",
    "DisruptionSeverity",
    "TimelineHorizon",
    "SupplyChainNode",
    "SupplierNode",
    "ManufacturerNode",
    "PortNode",
    "WarehouseNode",
    "RetailerNode",
    "ShippingRouteEdge",
    "NLPExtractedEntity",
    "NLPDisruptionAlert",
    "NLPRelationship",
    "NLPDetectedRisk",
    "NLPIngestRequest",
    "NLPIngestResponse",
    "MatchedNodeImpact",
    "HopDelayImpact",
    "HorizonPrediction",
    "GNNRipplePredictionResponse",
    "ReactFlowPosition",
    "ReactFlowNode",
    "ReactFlowEdge",
    "SupplyChainGraphTopology",
]
