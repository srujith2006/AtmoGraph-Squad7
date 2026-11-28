# 🌐 AtmoGraph: Complete Codebase Architecture & Technical Reference
## End-to-End System Design, Subsystem Manifest & Integration Guide
**Squad 7 — Internship Technical Documentation**  
**Repository Branch:** `Samarth---ITD` (Synced to `main`)  
**Version:** `1.0.0-production`  

---

## 1. System Vision & Architecture Overview

**AtmoGraph** is a real-time, event-driven intelligence platform designed to predict and visualize multi-hop supply chain disruptions across global manufacturing and logistics networks. By bridging live unstructured news streams with a topological knowledge graph and a Graph Neural Network (GNN) inference engine, AtmoGraph forecasts how an upstream disruption (e.g., a port strike in Rotterdam or container congestion in Singapore) cascades through suppliers, assembly plants, and regional warehouses over 30, 60, and 90-day horizons.

```mermaid
flowchart TD
    subgraph Data Ingestion & Enrichment
        A1["Maritime / Logistics News Webhook"] --> A2["NLP Ingestion Router<br/>(src/api/routes/nlp.py)"]
        A2 --> A3["Named Entity Linking & Disruption Classifier"]
    end

    subgraph Knowledge Graph Storage
        A3 --> B1["Neo4j Connection Pool<br/>(src/core/neo4j.py)"]
        B1 --> B2[("Neo4j AuraDB / Local Instance")]
        B1 -.->|"Self-Healing Fallback"| B3[("In-Memory Graph State")]
    end

    subgraph Analytical & Inference Engine
        B1 --> C1["GNN Inference Bridge<br/>(src/services/gnn_bridge.py)"]
        C1 --> C2["Message-Passing Graph Traversal"]
        C2 --> C3["30/60/90-Day Compounded Delay Forecast"]
        C3 --> C4["Critical Path Tracing & Mitigation Engine"]
    end

    subgraph Real-Time Streaming & API Gateway
        C4 --> D1["WebSocket ConnectionManager<br/>(src/services/websocket_manager.py)"]
        D1 --> D2["Full-Duplex Stream: /ws/ripple-stream"]
        A3 --> D1
        B1 --> D3["REST Endpoints: /api/v1/graph/*"]
    end

    subgraph Frontend User Interface
        D2 --> E1["React Flow Network Canvas<br/>(src/components/NetworkGraph.jsx)"]
        D3 --> E2["Dashboard KPI Summary Cards<br/>(src/pages/Dashboard.jsx)"]
        E1 --> E3["Dynamic Echelon Nodes<br/>(src/components/CustomNode.jsx)"]
        E1 --> E4["Interactive Ripple Simulation Trigger"]
    end

    subgraph Observability, Performance & Testing
        F1["Execution Timing Middleware"] --> F2["X-Process-Time-Ms / X-Request-ID"]
        F3["Request Latency Profiler"] --> F4["p50 / p95 / p99 Telemetry (/telemetry/profiler)"]
        F5["Synthetic Graph Generator"] --> F6["1,000+ Node NetworkX Benchmark (< 50ms)"]
        F7["84 Automated Pytest Suite"] --> F8["100% Pass Rate Across 13 Test Modules"]
    end
```

---

## 2. Complete Repository Directory Manifest

```
AtmoGraph-Squad7/
├── src/                                  # Primary Application Source Code
│   ├── api/                              # REST & WebSocket API Presentation Layer
│   │   ├── routes/                       # Modular FastAPI Route Controllers
│   │   │   ├── graph.py                  # Topology, nodes, edges, metrics, and synthetic endpoints
│   │   │   ├── health.py                 # Diagnostic health check & Neo4j connectivity probes
│   │   │   ├── nlp.py                    # Breaking news webhook, entity linking, and audit logs
│   │   │   ├── predictions.py            # GNN ripple simulation invocation & cache queries
│   │   │   ├── telemetry.py              # In-memory execution timing profiler endpoints
│   │   │   └── websocket.py              # Bidirectional WebSocket streaming & admin broadcasts
│   │   └── app.py                        # FastAPI application factory, middleware & router mounts
│   ├── core/                             # Foundational Infrastructure & Cross-Cutting Concerns
│   │   ├── config.py                     # Environment variables & Pydantic v2 settings
│   │   ├── exceptions.py                 # Centralized domain exceptions & RFC 7807 error envelopes
│   │   ├── logging.py                    # Structured JSON logger with request context vars
│   │   ├── middleware.py                 # Execution timing & X-Request-ID trace injection
│   │   ├── neo4j.py                      # Async driver pool with exponential backoff & mock fallback
│   │   └── profiler.py                   # Latency percentile (p50/p95/p99) tracker & slow query monitor
│   ├── schemas/                          # Pydantic v2 Data Contracts & Domain Specifications
│   │   ├── graph.py                      # Nodes, routes, predictions, and React Flow specifications
│   │   └── nlp.py                        # NLP webhook requests, relationships, and detected risks
│   ├── services/                         # Core Business Logic & Analytical Engines
│   │   ├── api.js                        # Frontend API service client for live backend communication
│   │   ├── gnn_bridge.py                 # PyTorch Geometric GNN prediction adapter & ripple simulator
│   │   ├── synthetic_generator.py        # 1,000+ node NetworkX DAG generator & performance benchmarker
│   │   └── websocket_manager.py          # WebSocket ConnectionManager with multi-cast broadcasting
│   ├── components/                       # React 18 Frontend UI Components
│   │   ├── CustomNode.jsx                # Custom React Flow node renderer with echelon styling
│   │   ├── Header.jsx                    # Top navigation bar with live operational telemetry badge
│   │   ├── NetworkGraph.jsx              # React Flow canvas, controls, minimap, & node inspector
│   │   ├── RiskOverview.jsx              # Supply chain risk assessment view
│   │   ├── SettingsView.jsx              # Configuration & mock preference view
│   │   ├── Sidebar.jsx                   # Collapsible application navigation sidebar
│   │   ├── SummaryCard.jsx               # Reusable KPI summary metric card
│   │   └── SuppliersView.jsx             # Supplier & facility directory view
│   ├── pages/                            # Frontend Page Containers
│   │   └── Dashboard.jsx                 # Main executive dashboard composing canvas and KPIs
│   ├── data/                             # Frontend Static Fallback Datasets
│   │   └── supplyChainData.js            # Initial mock nodes, directional edges, and KPI metrics
│   ├── App.jsx                           # Root React application container & view router
│   ├── index.css                         # Tailwind CSS base styles & custom scrollbars
│   ├── main.jsx                          # React DOM entrypoint
│   └── main.py                           # CLI entrypoint for running ASGI server
├── backend/                              # Cross-Team Data Ingestion & Batch Neo4j Scripts
│   ├── data/articles/                    # Teammates' raw & processed article payloads
│   │   ├── sample_article.json           # Sample GMRID disruption payload (Chennai port congestion)
│   │   ├── sample_article_old.json       # Previous Singapore port congestion sample
│   │   ├── team_output.json              # High-volume batch article extraction output
│   │   └── mock_supply_chain.json        # Week 1 mock supply chain entity graph
│   └── database/                         # Standalone Neo4j Cypher ingestion scripts
│       ├── article_ingest.py             # Batch Cypher ingestion script for news articles
│       ├── connection.py                 # Driver instantiation utility
│       └── ingest.py                     # Initial Neo4j node import script
├── docs/                                 # API Specifications & Architecture Documentation
│   ├── openapi.json                      # Machine-readable OpenAPI 3.1.0 specification (2,400+ lines)
│   └── API_SPECIFICATION.md              # Markdown summary table of all 20 REST & WS endpoints
├── scripts/                              # Automation Scripts & Tooling
│   └── export_openapi.py                 # CLI utility exporting OpenAPI specs directly from FastAPI app
├── tests/                                # Automated Pytest Test Harness (84 Tests, 100% Pass)
│   ├── fixtures/                         # Test fixtures & mock disruption payloads
│   │   └── nlp_news_fixtures.py          # Real-world scenario payloads (Rotterdam, Singapore, Shenzhen)
│   ├── test_config.py                    # Environment & configuration parsing unit tests
│   ├── test_docker_configs.py            # Multi-stage Dockerfile and Nginx configuration tests
│   ├── test_docs_and_profiler.py         # OpenAPI export, Swagger, and latency profiler tests
│   ├── test_gnn_bridge.py                # GNN multi-hop traversal & horizon compounding tests
│   ├── test_graph_routes.py              # Mock graph REST API endpoint tests
│   ├── test_integration.py               # Asynchronous REST & multi-client WebSocket integration tests
│   ├── test_logging.py                   # Structured JSON logging & request ID propagation tests
│   ├── test_middleware_and_exceptions.py # Execution timing middleware & RFC 7807 error tests
│   ├── test_neo4j.py                     # Neo4j pool manager, backoff retries & mock fallback tests
│   ├── test_nlp_ingest.py                # NLP news webhook & cross-team JSON compatibility tests
│   ├── test_perf_stress.py               # NetworkX 1,000-node scale generator & benchmark tests
│   ├── test_schemas.py                   # Pydantic v2 data contract & React Flow serialization tests
│   └── test_websocket.py                 # WebSocket connection manager, ping/pong, & broadcast tests
├── Dockerfile.backend                    # Multi-stage Python 3.11-slim backend container
├── Dockerfile.frontend                   # Multi-stage Node 20-alpine build to Nginx 1.25-alpine runner
├── nginx.conf                            # Nginx reverse proxy configuration for SPA routing & WebSockets
├── .dockerignore                         # Docker build isolation boundary
├── package.json                          # Node.js dependencies & Vite scripts
├── requirements.txt                      # Python dependencies
└── pytest.ini                            # Pytest configuration & custom markers
```

---

## 3. Subsystem Technical Deep Dives

### Subsystem 1: Frontend User Interface (React 18 + Vite 6 + React Flow)
* **Canvas Engine** (`src/components/NetworkGraph.jsx`): Employs `@xyflow/react` to render an interactive, pan-and-zoom supply chain graph. Nodes display lead times, capacity metrics, and risk badges with color-coded alerts (Emerald = Low, Sky = Medium, Amber = High, Rose = Critical).
* **Live Telemetry & Echelon Rendering** (`src/components/Header.jsx`, `src/components/CustomNode.jsx`): Automatically queries `/health` and displays an operational status indicator (`Operational (Mock Active)`). Provides a **⚡ Trigger Disruption Ripple** button that fires a simulation request and updates the canvas live.
* **API Service Client** (`src/services/api.js`): Uses `fetch` with graceful fallbacks. If the backend is loading or unavailable, it falls back to local static mock data (`src/data/supplyChainData.js`), ensuring zero UI blank screens.

### Subsystem 2: Core Infrastructure, Middleware & Observability
* **Configuration** (`src/core/config.py`): Pydantic `BaseSettings` reading environment variables with defaults for development and production.
* **Correlation Tracing & Timing** (`src/core/middleware.py`): Automatically extracts or generates a unique `X-Request-ID` UUID4 and injects execution timing (`X-Process-Time-Ms`) into response headers.
* **RFC 7807 Standardized Errors** (`src/core/exceptions.py`): Every exception (`EntityNotFoundError`, `DatabaseConnectionError`, `PayloadValidationError`) formats into a standard error JSON envelope containing `status_code`, `error_code`, `message`, `request_id`, and contextual details.
* **Execution Timing Profiler** (`src/core/profiler.py`): Thread-safe in-memory profiler calculating percentile latencies (**p50, p95, p99**) and logging warnings for queries exceeding the 100ms threshold.

### Subsystem 3: Graph Database Layer & Dual-Mode Resilience
* **Async Connection Pool** (`src/core/neo4j.py`): Initializes an asynchronous Neo4j driver with exponential backoff retries.
* **Self-Healing Fallback**: If Neo4j AuraDB or the local instance is offline, the connection pool automatically activates an internal in-memory graph repository. Cypher queries are translated seamlessly, ensuring 100% REST API uptime during database outages.
* **Diagnostics** (`GET /health/neo4j`): Reports driver mode (`connected` or `degraded_mock_fallback`), latency in milliseconds, and active node/edge counts.

### Subsystem 4: Machine Learning & GNN Inference Adapter
* **Multi-Hop Traversal** (`src/services/gnn_bridge.py`): Simulates downstream ripple effects using a PyTorch Geometric message-passing architecture.
* **Temporal Compounding (30/60/90 Days)**: Computes cumulative delay days and production loss percentages across 3 temporal horizons using monotonic compound multipliers.
* **Critical Delay Path**: Identifies the single worst-case bottleneck path through the multi-echelon network (e.g. Rotterdam Port -> Antwerp Warehouse -> Chicago Plant).
* **Automated Mitigation**: Automatically generates actionable contingency recommendations (e.g. *"Re-route 35% of inbound container volume to Antwerp Hub"*).

### Subsystem 5: Real-Time WebSocket Streaming Engine
* **Connection Manager** (`src/services/websocket_manager.py`): Singleton tracking active client sessions, handling disconnects, and thread-safe multi-casting.
* **Full-Duplex Stream** (`src/api/routes/websocket.py`):
  * Path: `ws://localhost:8000/ws/ripple-stream`
  * Heartbeat: Clients send `{"type": "ping"}` and receive `{"type": "pong"}`.
  * Live Simulation: Clients can trigger simulations via WebSocket message `{"type": "simulate_ripple", "node_id": "node-6"}` and broadcast the resulting ripple cascade to all connected dashboards.
* **Admin Broadcast Webhook**: `POST /api/v1/ws/broadcast` triggers manual system-wide broadcast alerts.

### Subsystem 6: Synthetic Scale Generator & Stress Testing
* **Scale Engine** (`src/services/synthetic_generator.py`): Uses NetworkX to generate realistic multi-echelon supply networks from 100 up to 5,000+ interconnected nodes.
* **DAG Flow Guarantee**: Enforces topological ordering where materials flow forward across all 6 echelons (`nx.is_directed_acyclic_graph() == True`).
* **Performance Benchmark**: 1,000 nodes and 1,735 edges generate and serialize into React Flow canvas schemas in **~47ms**, comfortably beating the 500ms target SLA.

### Subsystem 7: Production Containerization
* **Backend Image** (`Dockerfile.backend`): Multi-stage Python 3.11-slim container; non-root user `appuser`; zero-dependency Python health check.
* **Frontend Image** (`Dockerfile.frontend`): Multi-stage Node 20-alpine build to Nginx 1.25-alpine runner serving static assets (< 25MB footprint).
* **Nginx Gateway** (`nginx.conf`): Handles SPA routing (`try_files $uri $uri/ /index.html`), reverse-proxies `/api/` and `/health`, and supports WebSocket protocol upgrades (`Upgrade` / `Connection "Upgrade"`).

---

## 4. Test Verification Matrix (84 Tests, 100% Pass)

```powershell
.\.venv\Scripts\pytest
```
* **Status**: **84 passed, 0 skipped, 0 failures** in 5.67s.

| Test Module | Test Focus | Count | Status |
| :--- | :--- | :---: | :---: |
| `test_config.py` | Environment configurations & CORS parsing | 3 | **PASSED** |
| `test_docker_configs.py` | Multi-stage Dockerfiles & Nginx reverse proxy | 4 | **PASSED** |
| `test_docs_and_profiler.py`| OpenAPI schema export, Swagger, and latency profiler | 6 | **PASSED** |
| `test_gnn_bridge.py` | GNN multi-hop propagation & 30/60/90-day compounding | 8 | **PASSED** |
| `test_graph_routes.py` | Topology, nodes, edges, metrics, and simulation | 6 | **PASSED** |
| `test_integration.py` | Asynchronous REST & multi-client WebSocket feeds | 9 | **PASSED** |
| `test_logging.py` | Structured JSON logging & correlation IDs | 4 | **PASSED** |
| `test_middleware_and_exceptions.py`| Request timing & RFC 7807 error envelopes | 8 | **PASSED** |
| `test_neo4j.py` | Connection pool, exponential backoff, & mock fallback | 5 | **PASSED** |
| `test_nlp_ingest.py` | NLP news ingestion webhooks & cross-team datasets | 9 | **PASSED** |
| `test_perf_stress.py` | NetworkX 1,000-node scale generator & SLA benchmarks | 7 | **PASSED** |
| `test_schemas.py` | Pydantic contracts & React Flow serialization | 8 | **PASSED** |
| `test_websocket.py` | WebSocket manager, handshake, & live ripple broadcasts | 7 | **PASSED** |
| **Total** | **Comprehensive Full-Stack Test Harness** | **84** | **100% PASS** |

---

## 5. Developer Quickstart & Run Instructions

### 1. Prerequisites
* Python 3.11+
* Node.js v18+ & npm

### 2. Running Locally
```powershell
# Terminal 1: Start Backend API
.\.venv\Scripts\python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Frontend UI
npm run dev
```

### 3. Key Endpoints
* **Frontend Canvas:** [http://localhost:5173](http://localhost:5173)
* **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **System Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
* **Latency Telemetry Profiler:** [http://localhost:8000/api/v1/telemetry/profiler](http://localhost:8000/api/v1/telemetry/profiler)
* **WebSocket Stream:** `ws://localhost:8000/ws/ripple-stream`
