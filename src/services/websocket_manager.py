"""WebSocket connection manager for real-time supply chain disruption and ripple streaming.

Manages active client sessions, channel subscriptions, and thread-safe broadcasts
delivering live risk state changes to the React dashboard.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

from src.core.logging import get_logger

logger = get_logger("atmograph.websocket")


class ConnectionManager:
    """Manages active WebSocket connections and handles pub/sub event broadcasting."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self._connection_meta: Dict[WebSocket, Dict[str, Any]] = {}

    @property
    def total_connections(self) -> int:
        """Return total active WebSocket clients connected."""
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> None:
        """Accept an incoming WebSocket connection and register client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self._connection_meta[websocket] = {
            "client_id": client_id or f"client-{id(websocket)}",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "subscriptions": set(),
        }
        logger.info(
            f"WebSocket client connected: {self._connection_meta[websocket]['client_id']}",
            extra={"client_id": self._connection_meta[websocket]["client_id"], "active_clients": self.total_connections}
        )

        # Send initial connection acknowledgment
        await self.send_personal_message(
            {
                "type": "connection_established",
                "client_id": self._connection_meta[websocket]["client_id"],
                "active_connections": self.total_connections,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            websocket,
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Unregister a disconnected WebSocket client."""
        if websocket in self.active_connections:
            meta = self._connection_meta.pop(websocket, {})
            client_id = meta.get("client_id", "unknown")
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket client disconnected: {client_id}",
                extra={"client_id": client_id, "remaining_clients": self.total_connections}
            )

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """Send a JSON payload to a specific WebSocket client."""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as exc:
            logger.warning(f"Failed to deliver personal message to client: {str(exc)}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast an event payload to all currently connected clients.

        Returns:
            Number of clients successfully sent the message.
        """
        if not self.active_connections:
            logger.debug("Broadcast called with no active WebSocket clients connected.")
            return 0

        payload_text = json.dumps(message, default=str)
        stale_connections = []
        sent_count = 0

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload_text)
                sent_count += 1
            except Exception as exc:
                logger.warning(f"Error broadcasting to client, queuing removal: {str(exc)}")
                stale_connections.append(connection)

        # Clean up any stale sockets
        for stale in stale_connections:
            self.disconnect(stale)

        logger.debug(f"Broadcasted '{message.get('type', 'generic')}' event to {sent_count} clients")
        return sent_count

    async def broadcast_node_risk_update(
        self,
        node_id: str,
        node_name: str,
        previous_risk: str,
        new_risk: str,
        status: str,
        reason: str,
    ) -> int:
        """Broadcast single node risk state transition to frontend canvas."""
        event = {
            "type": "node_risk_updated",
            "data": {
                "node_id": node_id,
                "node_name": node_name,
                "previous_risk": previous_risk,
                "new_risk": new_risk,
                "status": status,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self.broadcast(event)

    async def broadcast_ripple_event(
        self,
        prediction_id: str,
        root_node_id: str,
        root_node_name: str,
        severity: str,
        critical_path: List[str],
        impacted_nodes_count: int,
    ) -> int:
        """Broadcast live multi-hop GNN ripple propagation event."""
        event = {
            "type": "gnn_ripple_broadcast",
            "data": {
                "prediction_id": prediction_id,
                "root_node_id": root_node_id,
                "root_node_name": root_node_name,
                "severity": severity,
                "critical_path": critical_path,
                "impacted_nodes_count": impacted_nodes_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self.broadcast(event)


# Application-wide singleton manager
_ws_manager_instance: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Retrieve application-wide ConnectionManager singleton."""
    global _ws_manager_instance
    if _ws_manager_instance is None:
        _ws_manager_instance = ConnectionManager()
    return _ws_manager_instance
