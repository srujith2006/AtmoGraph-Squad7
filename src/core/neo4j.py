"""Asynchronous Neo4j connection pool manager with retry logic, pooling, and resilient mock fallbacks.

Provides resilient graph query execution, automated reconnection with exponential backoff,
and diagnostic health checks for AtmoGraph.
"""

import asyncio
from datetime import datetime, timezone
import json
import os
import time
from typing import Any, Dict, List, Optional

from src.core.config import Settings, get_settings
from src.core.logging import get_logger, request_id_ctx
from src.core.exceptions import GraphDatabaseConnectionError

logger = get_logger("atmograph.neo4j")

# Gracefully handle optional neo4j driver import
try:
    from neo4j import AsyncGraphDatabase, AsyncDriver, Driver
    from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
    HAS_NEO4J_LIB = True
except ImportError:  # pragma: no cover
    HAS_NEO4J_LIB = False
    AsyncGraphDatabase = None  # type: ignore
    AsyncDriver = None  # type: ignore


class Neo4jConnectionPool:
    """Asynchronous Neo4j driver manager supporting connection pooling, retries, and fallback."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._driver: Optional[Any] = None
        self._is_connected: bool = False
        self._is_fallback_mode: bool = False
        self._mock_data_cache: Optional[Dict[str, Any]] = None

    @property
    def is_connected(self) -> bool:
        """Return True if connected to live Neo4j database."""
        return self._is_connected

    @property
    def is_fallback_mode(self) -> bool:
        """Return True if currently operating in mock fallback mode."""
        return self._is_fallback_mode

    async def connect(self, max_retries: int = 3, initial_delay: float = 0.5) -> bool:
        """Initialize connection pool with exponential backoff retries.

        Falls back to mock graph mode if database is unreachable.
        """
        if not HAS_NEO4J_LIB:
            logger.warning("neo4j library not found in environment. Operating in mock fallback mode.")
            self._activate_fallback_mode("Neo4j driver library not installed")
            return False

        delay = initial_delay
        last_error: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Attempting Neo4j connection to {self.settings.neo4j_uri} (Attempt {attempt}/{max_retries})",
                    extra={"uri": self.settings.neo4j_uri, "database": self.settings.neo4j_database}
                )

                self._driver = AsyncGraphDatabase.driver(
                    self.settings.neo4j_uri,
                    auth=(self.settings.neo4j_user, self.settings.neo4j_password),
                    max_connection_pool_size=self.settings.neo4j_max_connection_pool_size,
                    connection_timeout=self.settings.neo4j_connection_timeout,
                )

                # Verify connectivity with timeout
                await asyncio.wait_for(
                    self._driver.verify_connectivity(),
                    timeout=self.settings.neo4j_connection_timeout
                )

                self._is_connected = True
                self._is_fallback_mode = False
                logger.info("Successfully established connection to Neo4j database pool.")
                return True

            except Exception as exc:
                last_error = exc
                logger.warning(
                    f"Neo4j connection attempt {attempt} failed: {str(exc)}. Retrying in {delay}s...",
                    extra={"attempt": attempt, "error": str(exc)}
                )
                if self._driver:
                    await self._driver.close()
                    self._driver = None

                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2.0

        # All retries exhausted -> Activate graceful fallback mode
        self._activate_fallback_mode(str(last_error))
        return False

    def _activate_fallback_mode(self, reason: str) -> None:
        """Activate in-memory fallback mock graph so services remain functional."""
        self._is_connected = False
        self._is_fallback_mode = True
        logger.warning(
            f"Neo4j live connection unavailable ({reason}). Active in Mock Fallback Mode.",
            extra={"fallback_mode": True, "reason": reason}
        )
        self._load_mock_data()

    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock topology from repository files or generate synthetic graph."""
        if self._mock_data_cache is not None:
            return self._mock_data_cache

        # Check teammate mock supply chain path
        candidates = [
            os.path.join("backend", "data", "mock_supply_chain.json"),
            os.path.join("..", "backend", "data", "mock_supply_chain.json"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._mock_data_cache = json.load(f)
                        return self._mock_data_cache
                except Exception:
                    pass

        # Fallback synthetic graph data
        self._mock_data_cache = {
            "suppliers": [{"id": "S001", "name": "Apex Mining", "country": "Australia", "risk_level": "Low"}],
            "factories": [{"id": "F001", "name": "Taiwan Assembly", "country": "Taiwan", "risk_level": "Low"}],
            "ports": [{"id": "P001", "name": "Port of Singapore", "country": "Singapore"}],
            "warehouses": [{"id": "W001", "name": "Rotterdam Hub", "country": "Netherlands"}],
            "retailers": [{"id": "R001", "name": "US Retailer", "country": "USA"}],
            "relationships": [
                {"type": "SUPPLIES_TO", "from_id": "S001", "to_id": "F001", "lead_time_days": 14},
                {"type": "SHIPS_TO", "from_id": "F001", "to_id": "P001", "lead_time_days": 6},
                {"type": "TRANSPORTS_TO", "from_id": "P001", "to_id": "W001", "lead_time_days": 20},
                {"type": "DISTRIBUTES_TO", "from_id": "W001", "to_id": "R001", "lead_time_days": 4},
            ]
        }
        return self._mock_data_cache

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query asynchronously.

        If live database is not connected, gracefully executes against mock state.
        """
        if self._is_connected and self._driver:
            try:
                async with self._driver.session(database=self.settings.neo4j_database) as session:
                    result = await session.run(query, parameters or {})
                    records = [record.data() async for record in result]
                    return records
            except Exception as exc:
                logger.error(f"Neo4j query execution failed: {str(exc)}", exc_info=True)
                raise GraphDatabaseConnectionError(f"Cypher query execution error: {str(exc)}")

        # Mock query simulation for decoupled testing
        logger.debug(f"Executing Cypher query in mock fallback mode: {query[:60]}...")
        mock_data = self._load_mock_data()
        
        # Simple pattern responses for common queries
        q_upper = query.upper()
        if "COUNT(N)" in q_upper:
            total_nodes = (
                len(mock_data.get("suppliers", [])) +
                len(mock_data.get("factories", [])) +
                len(mock_data.get("ports", [])) +
                len(mock_data.get("warehouses", [])) +
                len(mock_data.get("retailers", []))
            )
            return [{"total_nodes": total_nodes}]
        elif "COUNT(R)" in q_upper or "RELATIONSHIPS" in q_upper:
            return [{"total_relationships": len(mock_data.get("relationships", []))}]

        return [{"status": "mock_executed", "result": mock_data}]

    async def check_health(self) -> Dict[str, Any]:
        """Inspect health, latency, node counts, and operational mode of Neo4j pool."""
        start_time = time.perf_counter()

        if self._is_connected and self._driver:
            try:
                records = await self.execute_query("MATCH (n) RETURN count(n) AS total_nodes")
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                node_count = records[0]["total_nodes"] if records else 0

                return {
                    "status": "connected",
                    "mode": "live",
                    "latency_ms": latency_ms,
                    "database": self.settings.neo4j_database,
                    "uri": self.settings.neo4j_uri,
                    "node_count": node_count,
                    "is_fallback": False,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as exc:
                logger.warning(f"Neo4j live health check probe failed: {str(exc)}")

        # Fallback diagnostics
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        mock_data = self._load_mock_data()
        total_nodes = (
            len(mock_data.get("suppliers", [])) +
            len(mock_data.get("factories", [])) +
            len(mock_data.get("ports", [])) +
            len(mock_data.get("warehouses", [])) +
            len(mock_data.get("retailers", []))
        )
        total_relationships = len(mock_data.get("relationships", []))

        return {
            "status": "degraded_mock_fallback",
            "mode": "mock_fallback",
            "latency_ms": latency_ms,
            "database": self.settings.neo4j_database,
            "uri": self.settings.neo4j_uri,
            "node_count": total_nodes,
            "relationship_count": total_relationships,
            "is_fallback": True,
            "note": "AuraDB/local Neo4j instance offline. Mock graph repository is active.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def close(self) -> None:
        """Close driver pool and release network sockets."""
        if self._driver:
            logger.info("Closing Neo4j connection pool...")
            await self._driver.close()
            self._driver = None
            self._is_connected = False


# Module singleton instance
_neo4j_pool_instance: Optional[Neo4jConnectionPool] = None


def get_neo4j_pool() -> Neo4jConnectionPool:
    """Retrieve application-wide Neo4jConnectionPool singleton."""
    global _neo4j_pool_instance
    if _neo4j_pool_instance is None:
        _neo4j_pool_instance = Neo4jConnectionPool()
    return _neo4j_pool_instance
