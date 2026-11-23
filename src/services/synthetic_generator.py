"""Synthetic supply chain network generator and serialization performance benchmarker.

Generates large-scale multi-echelon supply networks (100 to 5,000+ interconnected nodes)
using NetworkX directed acyclic graphs (DAGs) to stress-test:
- FastAPI Pydantic v2 model serialization throughput
- NetworkX graph traversal and multi-hop edge connectivity
- React Flow canvas rendering payload size and node layout coordinates
- Browser memory footprint and UI virtualization thresholds
"""

from datetime import datetime, timezone
import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

from src.core.logging import get_logger
from src.schemas.graph import (
    NodeType,
    NodeStatus,
    RiskLevel,
    RelationshipType,
    TransportMode,
    SupplyChainNode,
    ShippingRouteEdge,
    SupplyChainGraphTopology,
)

logger = get_logger("atmograph.synthetic_generator")

# Representative global industrial hubs for geographic dispersion
_GLOBAL_LOCATIONS = [
    {"country": "Taiwan", "city": "Hsinchu", "lat": 24.81, "lng": 120.96},
    {"country": "South Korea", "city": "Pyeongtaek", "lat": 36.99, "lng": 127.08},
    {"country": "Japan", "city": "Yokohama", "lat": 35.44, "lng": 139.63},
    {"country": "China", "city": "Shenzhen", "lat": 22.54, "lng": 114.05},
    {"country": "Singapore", "city": "Singapore", "lat": 1.35, "lng": 103.81},
    {"country": "Malaysia", "city": "Penang", "lat": 5.41, "lng": 100.33},
    {"country": "Germany", "city": "Stuttgart", "lat": 48.77, "lng": 9.18},
    {"country": "Netherlands", "city": "Rotterdam", "lat": 51.92, "lng": 4.47},
    {"country": "Belgium", "city": "Antwerp", "lat": 51.21, "lng": 4.40},
    {"country": "United States", "city": "Austin, TX", "lat": 30.26, "lng": -97.74},
    {"country": "United States", "city": "Chicago, IL", "lat": 41.87, "lng": -87.62},
    {"country": "United States", "city": "Long Beach, CA", "lat": 33.77, "lng": -118.19},
    {"country": "Australia", "city": "Perth", "lat": -31.95, "lng": 115.86},
    {"country": "Chile", "city": "Antofagasta", "lat": -23.65, "lng": -70.40},
]

# Echelon classifications with realistic tier proportions
_ECHELON_CONFIG = [
    {"echelon": 0, "type": NodeType.SUPPLIER, "tier": "Tier 3 Raw Materials", "ratio": 0.25},
    {"echelon": 1, "type": NodeType.SUPPLIER, "tier": "Tier 2 Specialized Parts", "ratio": 0.20},
    {"echelon": 2, "type": NodeType.MANUFACTURER, "tier": "Tier 1 Subsystem Assembly", "ratio": 0.20},
    {"echelon": 3, "type": NodeType.PORT, "tier": "Maritime Transshipment Port", "ratio": 0.10},
    {"echelon": 4, "type": NodeType.WAREHOUSE, "tier": "Regional Distribution Hub", "ratio": 0.15},
    {"echelon": 5, "type": NodeType.RETAILER, "tier": "Enterprise Fulfillment Outlet", "ratio": 0.10},
]

_PRODUCTS_BY_ECHELON = {
    0: ["High-Purity Silicon Ingots", "Lithium Hydroxide", "Rare Earth Neodymium", "Industrial Copper Wire", "Quartz Substrates"],
    1: ["Photolithography Masks", "Capacitor Arrays", "MEMS Sensor Dies", "IC Packaging Substrates", "Optoelectronic Transceivers"],
    2: ["Advanced AI Acceleration ASICs", "Automotive ECU Modules", "Industrial Server Blades", "Network Switching Units"],
    3: ["Containerized Maritime Cargo", "High-Priority Air Freight Pallets", "Intermodal Rail Containers"],
    4: ["Buffered Inventory Pallets", "Cross-Docked Electronic Consignments", "Fast-Track Fulfillment Stock"],
    5: ["OEM Finished Systems", "Data Center Compute Clusters", "Enterprise Partner Channels"],
}


class SyntheticSupplyChainGenerator:
    """Orchestrates generation of large-scale directed supply chain graph models using NetworkX."""

    def __init__(self, seed: Optional[int] = 42) -> None:
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def generate_network(
        self,
        node_count: int = 1000,
        edge_density: float = 1.8,
    ) -> Tuple[List[SupplyChainNode], List[ShippingRouteEdge], nx.DiGraph]:
        """Generate a realistic multi-echelon supply network.

        Args:
            node_count: Target number of nodes (e.g. 500, 1000, 2500).
            edge_density: Average outward edges per upstream node.

        Returns:
            Tuple of (Pydantic nodes, Pydantic shipping edges, NetworkX DiGraph).
        """
        if self.seed is not None:
            random.seed(self.seed)

        graph = nx.DiGraph()
        nodes_by_echelon: Dict[int, List[str]] = {cfg["echelon"]: [] for cfg in _ECHELON_CONFIG}
        pydantic_nodes: List[SupplyChainNode] = []

        # 1. Distribute node counts across 6 echelons
        remaining = node_count
        counts = {}
        for idx, cfg in enumerate(_ECHELON_CONFIG):
            if idx == len(_ECHELON_CONFIG) - 1:
                counts[cfg["echelon"]] = remaining
            else:
                c = max(1, int(round(node_count * cfg["ratio"])))
                counts[cfg["echelon"]] = min(c, remaining)
                remaining -= counts[cfg["echelon"]]

        node_index = 1
        canvas_width = 3200.0
        canvas_height = 1800.0

        for cfg in _ECHELON_CONFIG:
            ech = cfg["echelon"]
            total_in_ech = counts[ech]
            echelon_x = 100.0 + (ech * (canvas_width / len(_ECHELON_CONFIG)))

            for i in range(total_in_ech):
                nid = f"syn-node-{node_index:04d}"
                loc = random.choice(_GLOBAL_LOCATIONS)
                products = _PRODUCTS_BY_ECHELON.get(ech, ["Generic Freight Item"])
                key_prod = random.choice(products)

                # Vertical layout positioning with slight jitter
                step_y = canvas_height / max(1, total_in_ech)
                echelon_y = 60.0 + (i * step_y) + (random.uniform(-15.0, 15.0))

                risk_roll = random.random()
                if risk_roll < 0.75:
                    risk = RiskLevel.LOW
                    status = NodeStatus.ACTIVE
                elif risk_roll < 0.90:
                    risk = RiskLevel.MEDIUM
                    status = NodeStatus.ACTIVE
                elif risk_roll < 0.97:
                    risk = RiskLevel.HIGH
                    status = NodeStatus.DEGRADED
                else:
                    risk = RiskLevel.CRITICAL
                    status = NodeStatus.DISRUPTED

                node_obj = SupplyChainNode(
                    id=nid,
                    name=f"{loc['city']} {cfg['type'].value.capitalize()} #{i+1:03d}",
                    node_type=cfg["type"],
                    country=loc["country"],
                    location=f"{loc['city']}, {loc['country']}",
                    tier=cfg["tier"],
                    status=status,
                    risk_level=risk,
                    capacity=f"{random.randint(65, 98)}%",
                    lead_time=f"{random.randint(2, 28)} days",
                    transit_method=random.choice(list(TransportMode)),
                    key_output=key_prod,
                    latitude=loc["lat"] + random.uniform(-0.15, 0.15),
                    longitude=loc["lng"] + random.uniform(-0.15, 0.15),
                    metadata={
                        "echelon": ech,
                        "canvas_x": round(echelon_x, 1),
                        "canvas_y": round(echelon_y, 1),
                    },
                )
                pydantic_nodes.append(node_obj)
                nodes_by_echelon[ech].append(nid)
                graph.add_node(nid, echelon=ech, data=node_obj)
                node_index += 1

        # 2. Wire realistic forward shipping edges between echelons
        pydantic_edges: List[ShippingRouteEdge] = []
        edge_index = 1

        for ech in range(len(_ECHELON_CONFIG) - 1):
            source_pool = nodes_by_echelon[ech]
            # Primary targets in next echelon, secondary targets in skip-hop echelon
            target_pool = nodes_by_echelon[ech + 1]
            skip_target_pool = nodes_by_echelon[ech + 2] if (ech + 2) in nodes_by_echelon else []

            for src in source_pool:
                # Ensure at least 1 outbound route per node
                num_targets = max(1, int(round(random.gauss(edge_density, 0.6))))
                chosen_targets = random.sample(target_pool, min(num_targets, len(target_pool)))

                # 15% chance to have a skip-echelon express transit route (e.g. direct supplier -> assembly)
                if skip_target_pool and random.random() < 0.15:
                    chosen_targets.append(random.choice(skip_target_pool))

                for tgt in chosen_targets:
                    if not graph.has_edge(src, tgt):
                        graph.add_edge(src, tgt)
                        edge_id = f"syn-edge-{edge_index:05d}"
                        
                        # Modality based on echelon transition
                        if ech in (0, 3):
                            mode = random.choice([TransportMode.OCEAN_FREIGHT, TransportMode.RAIL])
                            rel_type = RelationshipType.SHIPS_TO
                            lead_days = float(random.randint(14, 35))
                        elif ech in (1, 2):
                            mode = random.choice([TransportMode.AIR_FREIGHT, TransportMode.MULTIMODAL])
                            rel_type = RelationshipType.SUPPLIES_TO
                            lead_days = float(random.randint(3, 12))
                        else:
                            mode = random.choice([TransportMode.ROAD, TransportMode.RAIL])
                            rel_type = RelationshipType.DISTRIBUTES_TO
                            lead_days = float(random.randint(1, 5))

                        active_dis = (random.random() < 0.06)  # 6% baseline route disruption
                        edge_obj = ShippingRouteEdge(
                            id=edge_id,
                            from_id=src,
                            to_id=tgt,
                            type=rel_type,
                            transport_mode=mode,
                            lead_time_days=lead_days,
                            capacity=float(random.randint(2000, 45000)),
                            risk_multiplier=round(random.uniform(1.0, 2.5), 2),
                            active_disruption=active_dis,
                            notes=f"Synthetic transit lane {mode.value}",
                        )
                        pydantic_edges.append(edge_obj)
                        edge_index += 1

        logger.info(
            f"Generated synthetic network: {len(pydantic_nodes)} nodes, {len(pydantic_edges)} edges",
            extra={"nodes": len(pydantic_nodes), "edges": len(pydantic_edges)}
        )
        return pydantic_nodes, pydantic_edges, graph

    def generate_topology(
        self,
        node_count: int = 1000,
        edge_density: float = 1.8,
    ) -> SupplyChainGraphTopology:
        """Generate and package full React Flow / D3 topology object."""
        nodes, edges, _ = self.generate_network(node_count=node_count, edge_density=edge_density)
        return SupplyChainGraphTopology.from_nodes_and_edges(nodes=nodes, edges=edges)

    def benchmark_serialization(
        self,
        node_count: int = 1000,
        edge_density: float = 1.8,
    ) -> Dict[str, Any]:
        """Execute end-to-end benchmark profiling generation and serialization throughput.

        Target SLA: Under 500ms for 1,000 nodes and 1,800+ edges.
        """
        # 1. Network generation
        t0 = time.perf_counter()
        nodes, edges, graph = self.generate_network(node_count=node_count, edge_density=edge_density)
        t_gen = (time.perf_counter() - t0) * 1000.0

        # 2. React Flow presentation conversion
        t1 = time.perf_counter()
        topology = SupplyChainGraphTopology.from_nodes_and_edges(nodes=nodes, edges=edges)
        t_topo = (time.perf_counter() - t1) * 1000.0

        # 3. JSON serialization throughput
        t2 = time.perf_counter()
        json_str = topology.model_dump_json()
        t_json = (time.perf_counter() - t2) * 1000.0

        total_ms = t_gen + t_topo + t_json
        payload_size_kb = len(json_str.encode("utf-8")) / 1024.0

        is_dag = nx.is_directed_acyclic_graph(graph)

        metrics = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "is_directed_acyclic_graph": is_dag,
            "generation_time_ms": round(t_gen, 2),
            "topology_mapping_time_ms": round(t_topo, 2),
            "json_serialization_time_ms": round(t_json, 2),
            "total_execution_time_ms": round(total_ms, 2),
            "payload_size_kb": round(payload_size_kb, 2),
            "payload_size_mb": round(payload_size_kb / 1024.0, 3),
            "target_sla_ms": 500.0,
            "sla_met": total_ms < 500.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            f"Benchmark completed: {metrics['node_count']} nodes / {metrics['edge_count']} edges in {metrics['total_execution_time_ms']}ms "
            f"[SLA Met: {metrics['sla_met']}]",
            extra=metrics
        )
        return metrics
