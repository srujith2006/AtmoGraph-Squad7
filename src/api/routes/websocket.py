"""WebSocket and real-time streaming routes for AtmoGraph live ripple events."""

from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from pydantic import BaseModel, Field

from src.core.logging import get_logger
from src.schemas.graph import DisruptionSeverity
from src.services.websocket_manager import get_connection_manager
from src.services.gnn_bridge import get_gnn_bridge

logger = get_logger("atmograph.ws_route")

# WebSocket routes mounted at root (/ws/ripple-stream) and REST controls at /api/v1/ws
router = APIRouter(tags=["Real-Time WebSocket Streaming"])


class WebSocketBroadcastRequest(BaseModel):
    """Payload to trigger a manual WebSocket broadcast."""
    event_type: str = Field(default="system_notification", description="Event classification name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event data dictionary")


class WebSocketStatusResponse(BaseModel):
    """Telemetry response for WebSocket connection manager."""
    status: str = Field(default="active", description="Manager operational status")
    active_connections: int = Field(description="Currently connected client sessions")
    timestamp: str = Field(description="ISO 8601 UTC timestamp")


@router.websocket("/ws/ripple-stream")
async def websocket_ripple_stream(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="Optional client identifier"),
):
    """Live bidirectional WebSocket channel streaming node risk changes and GNN ripples to clients."""
    manager = get_connection_manager()
    await manager.connect(websocket, client_id=client_id)

    try:
        while True:
            # Receive client incoming text messages or heartbeats
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                data = {"type": "raw_text", "content": raw_text}

            msg_type = data.get("type", "").lower()

            # Handle heartbeat ping
            if msg_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()},
                    websocket,
                )

            # Client triggers live GNN ripple simulation directly over WebSocket
            elif msg_type == "simulate_ripple":
                target_node = data.get("node_id", "node-6")
                sev_str = data.get("severity", "CRITICAL").upper()
                sev = getattr(DisruptionSeverity, sev_str, DisruptionSeverity.HIGH)

                bridge = get_gnn_bridge()
                prediction = await bridge.predict_ripple_effect(
                    root_node_id=target_node,
                    disruption_severity=sev,
                    alert_id=f"ws-trigger-{int(datetime.now().timestamp())}",
                )

                # Broadcast ripple prediction event to all connected dashboard clients
                p90 = prediction.predictions_by_horizon["90_day"]
                await manager.broadcast_ripple_event(
                    prediction_id=prediction.prediction_id,
                    root_node_id=prediction.root_node_id,
                    root_node_name=prediction.root_node_name,
                    severity=sev_str,
                    critical_path=prediction.critical_delay_path,
                    impacted_nodes_count=len(p90.impacted_nodes),
                )

            else:
                # Echo receipt acknowledgment
                await manager.send_personal_message(
                    {
                        "type": "ack",
                        "received_type": msg_type,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.error(f"WebSocket session error: {str(exc)}", exc_info=True)
        manager.disconnect(websocket)


# ==============================================================================
# REST Telemetry & Broadcast Routes (Mounted under /api/v1/ws)
# ==============================================================================

rest_ws_router = APIRouter(prefix="/ws", tags=["Real-Time WebSocket Streaming"])


@rest_ws_router.get("/status", response_model=WebSocketStatusResponse, status_code=status.HTTP_200_OK)
async def get_websocket_manager_status() -> WebSocketStatusResponse:
    """Retrieve operational telemetry and total active connection count."""
    manager = get_connection_manager()
    return WebSocketStatusResponse(
        status="active",
        active_connections=manager.total_connections,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@rest_ws_router.post("/broadcast", status_code=status.HTTP_200_OK)
async def trigger_manual_broadcast(request: WebSocketBroadcastRequest):
    """Trigger a broadcast event payload across all connected dashboard WebSocket clients."""
    manager = get_connection_manager()
    message = {
        "type": request.event_type,
        "data": request.payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    sent_count = await manager.broadcast(message)
    return {"status": "broadcast_sent", "delivered_clients": sent_count}
