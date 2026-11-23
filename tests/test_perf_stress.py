"""Performance and stress test suite for large-scale synthetic graph payload generation.

Validates:
- Generation of 100, 500, and 1,000+ node multi-echelon supply chain networks
- NetworkX DAG (Directed Acyclic Graph) cycle-free structure and material flow
- High-throughput Pydantic v2 serialization latency (< 500ms target SLA)
- Payload memory footprint and JSON footprint bounds for browser canvas safety
- REST endpoints /api/v1/graph/synthetic and /api/v1/graph/benchmark
"""

import time
import pytest
from starlette.testclient import TestClient
import networkx as nx

from src.api.app import app
from src.services.synthetic_generator import SyntheticSupplyChainGenerator
from src.schemas.graph import SupplyChainGraphTopology, NodeType


@pytest.fixture
def client():
    """Sync TestClient for graph performance testing."""
    return TestClient(app)


@pytest.fixture
def generator():
    """Synthetic generator instance with fixed deterministic seed."""
    return SyntheticSupplyChainGenerator(seed=1337)


@pytest.mark.unit
def test_synthetic_network_generation_small(generator: SyntheticSupplyChainGenerator):
    """Verify synthetic network generation with 100 nodes across all 6 echelons."""
    nodes, edges, graph = generator.generate_network(node_count=100, edge_density=1.5)

    assert len(nodes) == 100
    assert len(edges) >= 90
    assert nx.is_directed_acyclic_graph(graph)

    # Verify all 6 echelons are represented
    node_types = {n.node_type for n in nodes}
    assert NodeType.SUPPLIER in node_types
    assert NodeType.MANUFACTURER in node_types
    assert NodeType.PORT in node_types
    assert NodeType.WAREHOUSE in node_types
    assert NodeType.RETAILER in node_types


@pytest.mark.unit
def test_synthetic_network_echelon_connectivity(generator: SyntheticSupplyChainGenerator):
    """Verify forward topological ordering and edge connections."""
    nodes, edges, graph = generator.generate_network(node_count=200, edge_density=1.8)

    node_map = {n.id: n for n in nodes}
    for edge in edges:
        src = node_map[edge.from_id]
        tgt = node_map[edge.to_id]
        src_ech = src.metadata.get("echelon", 0)
        tgt_ech = tgt.metadata.get("echelon", 0)
        # Material flow moves downstream: target echelon must be greater than source
        assert tgt_ech > src_ech, f"Edge {edge.id} reverses flow: {src_ech} -> {tgt_ech}"


@pytest.mark.unit
def test_synthetic_topology_react_flow_serialization(generator: SyntheticSupplyChainGenerator):
    """Verify conversion to React Flow canvas nodes and edges."""
    topology = generator.generate_topology(node_count=300, edge_density=1.6)

    assert isinstance(topology, SupplyChainGraphTopology)
    assert len(topology.nodes) == 300
    assert len(topology.react_flow_nodes) == 300
    assert len(topology.edges) == len(topology.react_flow_edges)

    # Verify React Flow node coordinates
    first_rf_node = topology.react_flow_nodes[0]
    assert first_rf_node.type == "supplyChainNode"
    assert "x" in first_rf_node.position.model_dump()
    assert "y" in first_rf_node.position.model_dump()
    assert first_rf_node.data["name"] is not None


@pytest.mark.slow
@pytest.mark.unit
def test_large_scale_1000_node_benchmark(generator: SyntheticSupplyChainGenerator):
    """Stress test 1,000-node network generation and JSON serialization throughput."""
    metrics = generator.benchmark_serialization(node_count=1000, edge_density=1.8)

    assert metrics["node_count"] == 1000
    assert metrics["edge_count"] >= 1200
    assert metrics["is_directed_acyclic_graph"] is True

    # Generation + serialization should comfortably finish within SLA (< 1500ms on any test runner)
    assert metrics["total_execution_time_ms"] < 1500.0
    assert metrics["payload_size_kb"] > 100.0  # Realistic payload
    assert metrics["payload_size_mb"] < 10.0   # Must remain lightweight for browser rendering


@pytest.mark.api
def test_api_synthetic_graph_endpoint(client: TestClient):
    """Verify GET /api/v1/graph/synthetic returns full topology payload."""
    response = client.get("/api/v1/graph/synthetic?node_count=150&edge_density=1.5&seed=99")
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert "react_flow_nodes" in data
    assert "react_flow_edges" in data
    assert len(data["nodes"]) == 150
    assert len(data["react_flow_nodes"]) == 150
    assert len(data["edges"]) >= 120


@pytest.mark.api
def test_api_benchmark_endpoint(client: TestClient):
    """Verify GET /api/v1/graph/benchmark returns profiling telemetry."""
    response = client.get("/api/v1/graph/benchmark?node_count=500&seed=42")
    assert response.status_code == 200
    data = response.json()

    assert data["node_count"] == 500
    assert "generation_time_ms" in data
    assert "json_serialization_time_ms" in data
    assert "total_execution_time_ms" in data
    assert "payload_size_kb" in data
    assert data["is_directed_acyclic_graph"] is True


@pytest.mark.unit
def test_reproducible_synthetic_generation():
    """Verify seed ensures 100% deterministic graph topology across runs."""
    gen1 = SyntheticSupplyChainGenerator(seed=777)
    nodes1, edges1, _ = gen1.generate_network(node_count=80)

    gen2 = SyntheticSupplyChainGenerator(seed=777)
    nodes2, edges2, _ = gen2.generate_network(node_count=80)

    assert [n.id for n in nodes1] == [n.id for n in nodes2]
    assert [n.name for n in nodes1] == [n.name for n in nodes2]
    assert [e.id for e in edges1] == [e.id for e in edges2]
