# 📑 AtmoGraph API Specification Reference

**Version:** `1.0.0`  
**OpenAPI Version:** `3.1.0`  

## Endpoints Summary

| Method | Endpoint Path | Summary | Tags |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/graph/benchmark` | Benchmark Graph Serialization | Supply Chain Graph |
| `GET` | `/api/v1/graph/edges` | List Graph Edges | Supply Chain Graph |
| `GET` | `/api/v1/graph/metrics` | Get Graph Metrics | Supply Chain Graph |
| `GET` | `/api/v1/graph/nodes` | List Graph Nodes | Supply Chain Graph |
| `GET` | `/api/v1/graph/nodes/{node_id}` | Get Node By Id | Supply Chain Graph |
| `POST` | `/api/v1/graph/simulate-disruption` | Simulate Disruption | Supply Chain Graph |
| `GET` | `/api/v1/graph/synthetic` | Get Synthetic Graph Topology | Supply Chain Graph |
| `GET` | `/api/v1/graph/topology` | Get Graph Topology | Supply Chain Graph |
| `GET` | `/api/v1/nlp/alerts` | List Disruption Alerts | NLP Ingestion Engine |
| `DELETE` | `/api/v1/nlp/alerts` | Clear Alerts For Testing | NLP Ingestion Engine |
| `GET` | `/api/v1/nlp/alerts/{alert_id}` | Get Disruption Alert By Id | NLP Ingestion Engine |
| `POST` | `/api/v1/nlp/ingest` | Ingest Nlp Entities | NLP Ingestion Engine |
| `GET` | `/api/v1/predictions/latest` | Get Latest Ripple Prediction | GNN Ripple Predictions |
| `POST` | `/api/v1/predictions/ripple` | Generate Ripple Prediction | GNN Ripple Predictions |
| `GET` | `/api/v1/predictions/{prediction_id}` | Get Prediction By Id | GNN Ripple Predictions |
| `GET` | `/api/v1/telemetry/profiler` | Get Profiler Summary | Observability & Profiling Telemetry |
| `DELETE` | `/api/v1/telemetry/profiler` | Reset Profiler Telemetry | Observability & Profiling Telemetry |
| `POST` | `/api/v1/ws/broadcast` | Trigger Manual Broadcast | Real-Time WebSocket Streaming |
| `GET` | `/api/v1/ws/status` | Get Websocket Manager Status | Real-Time WebSocket Streaming |
| `GET` | `/health` | Get Health Status | Health & Diagnostics |
| `GET` | `/health/neo4j` | Check Neo4J Health | Health & Diagnostics |
| `GET` | `/health/ping` | Ping | Health & Diagnostics |
