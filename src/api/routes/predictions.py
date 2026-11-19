"""GNN Multi-Hop Ripple Prediction API routes.

Provides endpoints to trigger PyTorch Geometric multi-hop delay simulations,
query 30/60/90-day timeline forecasts, and inspect critical propagation paths.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.core.exceptions import EntityNotFoundError
from src.schemas.graph import DisruptionSeverity, GNNRipplePredictionResponse
from src.services.gnn_bridge import get_gnn_bridge

router = APIRouter(prefix="/predictions", tags=["GNN Ripple Predictions"])


class RipplePredictionRequest(BaseModel):
    """Payload to initiate a GNN multi-hop delay ripple forecast."""
    root_node_id: str = Field(description="Epicenter node ID to simulate, e.g. 'node-4' or 'node-6'")
    severity: DisruptionSeverity = Field(default=DisruptionSeverity.HIGH, description="Incident severity level")
    alert_id: Optional[str] = Field(default=None, description="Optional triggering NLP disruption alert ID")


@router.post("/ripple", response_model=GNNRipplePredictionResponse, status_code=status.HTTP_200_OK)
async def generate_ripple_prediction(payload: RipplePredictionRequest) -> GNNRipplePredictionResponse:
    """Execute GNN ripple-effect inference for an epicenter node across 30, 60, and 90-day horizons."""
    bridge = get_gnn_bridge()
    return await bridge.predict_ripple_effect(
        root_node_id=payload.root_node_id,
        disruption_severity=payload.severity,
        alert_id=payload.alert_id,
    )


@router.get("/latest", response_model=GNNRipplePredictionResponse, status_code=status.HTTP_200_OK)
async def get_latest_ripple_prediction() -> GNNRipplePredictionResponse:
    """Retrieve the most recent GNN ripple forecast generated."""
    bridge = get_gnn_bridge()
    latest = bridge.get_latest_prediction()
    if not latest:
        # Generate initial default prediction for Rotterdam hub if none exists
        latest = await bridge.predict_ripple_effect(
            root_node_id="node-6",
            disruption_severity=DisruptionSeverity.CRITICAL,
            alert_id="default-startup-alert",
        )
    return latest


@router.get("/{prediction_id}", response_model=GNNRipplePredictionResponse, status_code=status.HTTP_200_OK)
async def get_prediction_by_id(prediction_id: str) -> GNNRipplePredictionResponse:
    """Retrieve a previously calculated GNN prediction by prediction ID."""
    bridge = get_gnn_bridge()
    prediction = bridge.get_cached_prediction(prediction_id)
    if not prediction:
        raise EntityNotFoundError(entity_type="GNNPrediction", entity_id=prediction_id)
    return prediction
