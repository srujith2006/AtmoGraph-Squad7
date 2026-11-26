# 🚀 AtmoGraph: 20-Day Engineering, Integration & Deployment Plan (Days 11 – 30)
**Role:** Senior QA Automation, API Integration & DevOps Architect  
**Project:** AtmoGraph — Supply Chain Ripple Effect Predictor  
**Timeline:** November 24, 2026 – December 13, 2026  
**Commit Message Requirement:** Strictly > 51 characters (All planned commits: 78–92 characters)

---

## Master Roadmap Overview

```
Phase 1: CI/CD & Containerization (Days 11–14)
   └── Docker Multi-Stage -> Docker Compose -> GitHub Actions CI -> Test Coverage Gates

Phase 2: Security, Auth & Hardening (Days 15–18)
   └── JWT & API Keys -> Rate Limiting -> OWASP/Bandit Audits -> TLS & CORS Whitelists

Phase 3: Performance, Caching & Data Ops (Days 19–22)
   └── Redis/LRU Cache -> Cypher Index Optimization -> GeoJSON/CSV Exports -> Snapshot Backups

Phase 4: Chaos Engineering & End-to-End Testing (Days 23–26)
   └── Socket Chaos Injection -> UI WebSocket Reconnect -> Circuit Breakers -> Playwright E2E

Phase 5: Cloud Deployment & Production Handover (Days 27–30)
   └── Prometheus Exporter -> Kubernetes Manifests -> Blue-Green Deployments -> Final Runbook
```

---

## 📅 Daily Commit Plan (Days 11 to 30)

| Day # | Calendar Date | Scope / Milestone | Exact Commit Message (> 51 chars) | Char Count | Primary Files / Deliverables |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **Day 11** | Nov 24, 2026 | **Multi-Stage Dockerfiles** | `ci(docker): create multi-stage dockerfiles for fastapi backend and vite frontend` | 78 | `Dockerfile.backend`, `Dockerfile.frontend`, `.dockerignore` |
| **Day 12** | Nov 25, 2026 | **Docker Compose Orchestration** | `ci(compose): orchestrate full stack multi-service docker compose environment with neo4j` | 89 | `docker-compose.yml`, `docker-compose.override.yml`, `nginx.conf` |
| **Day 13** | Nov 26, 2026 | **GitHub Actions CI Matrix** | `ci(github): configure automated github actions workflow for pytest test matrix and linting` | 90 | `.github/workflows/ci.yml`, `.github/workflows/lint.yml` |
| **Day 14** | Nov 27, 2026 | **Coverage Threshold Gates** | `test(coverage): enforce 85 percent test coverage threshold in pytest-cov configuration` | 85 | `pytest.ini`, `tests/conftest.py`, `.codecov.yml` |
| **Day 15** | Nov 28, 2026 | **JWT & API Key Authentication** | `feat(auth): implement jwt token and api key authentication middleware for protected routes` | 90 | `src/core/auth.py`, `src/core/security.py`, `tests/test_auth.py` |
| **Day 16** | Nov 29, 2026 | **Sliding Window Rate Limiter** | `feat(ratelimit): add in-memory sliding window rate limiting middleware to prevent api abuse` | 92 | `src/core/ratelimit.py`, `tests/test_ratelimit.py` |
| **Day 17** | Nov 30, 2026 | **Security Vulnerability Scanner** | `sec(deps): add automated bandit security vulnerability audit and input sanitization check` | 89 | `.bandit.yaml`, `scripts/run_security_audit.py` |
| **Day 18** | Dec 01, 2026 | **CORS & TLS Hardening** | `sec(cors): harden cors origin whitelist and configure https tls termination settings` | 85 | `src/core/config.py`, `nginx/ssl.conf`, `tests/test_cors.py` |
| **Day 19** | Dec 02, 2026 | **LRU & Redis Caching Layer** | `feat(cache): integrate in-memory lru and redis caching adapter for topology queries` | 83 | `src/services/cache.py`, `tests/test_cache.py` |
| **Day 20** | Dec 03, 2026 | **Cypher Index & Leak Detection** | `perf(db): optimize neo4j cypher index constraints and connection leak detection suite` | 86 | `src/core/neo4j.py`, `scripts/init_neo4j_indexes.cypher` |
| **Day 21** | Dec 04, 2026 | **GeoJSON & CSV Data Export** | `feat(export): add bulk export endpoints for geojson, csv, and excel supply chain reports` | 88 | `src/api/routes/export.py`, `tests/test_export.py` |
| **Day 22** | Dec 05, 2026 | **Backup & Snapshot Automation** | `ops(backup): create automated neo4j graph snapshot backup and recovery test script` | 82 | `scripts/backup_graph.py`, `scripts/restore_graph.py` |
| **Day 23** | Dec 06, 2026 | **Chaos & Network Fault Injection**| `test(chaos): implement chaos fault injection harness simulating network connection drops` | 89 | `tests/chaos/test_network_drops.py`, `src/core/neo4j.py` |
| **Day 24** | Dec 07, 2026 | **UI WebSocket Auto-Reconnect** | `feat(ui): implement exponential backoff reconnection protocol in react websocket client` | 88 | `src/services/websocket.js`, `src/components/Header.jsx` |
| **Day 25** | Dec 08, 2026 | **Circuit Breaker Resiliency** | `feat(resilience): add circuit breaker pattern to protect against external gnn timeouts` | 87 | `src/core/circuit_breaker.py`, `tests/test_resilience.py` |
| **Day 26** | Dec 09, 2026 | **Playwright E2E UI Suite** | `test(e2e): build playwright automated browser test suite for react flow canvas navigation` | 90 | `tests/e2e/test_dashboard.spec.js`, `playwright.config.js` |
| **Day 27** | Dec 10, 2026 | **Prometheus Metrics Exporter** | `feat(metrics): add prometheus metrics exporter endpoint for p99 latency observability` | 86 | `src/core/metrics.py`, `src/api/routes/metrics.py` |
| **Day 28** | Dec 11, 2026 | **Kubernetes Helm & Manifests** | `deploy(k8s): author kubernetes deployment manifests with horizontal pod autoscaler` | 82 | `k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/hpa.yaml` |
| **Day 29** | Dec 12, 2026 | **Zero-Downtime Blue-Green Deploy**| `deploy(bluegreen): script zero-downtime blue-green deployment and rollback health probe` | 88 | `scripts/deploy_blue_green.sh`, `scripts/verify_rollback.py` |
| **Day 30** | Dec 13, 2026 | **Production Runbook & Handover** | `docs(release): compile final system architecture runbook and v1.0.0 production checklist` | 88 | `docs/PRODUCTION_RUNBOOK.md`, `CHANGELOG.md` |

---

## 🛠️ Step-by-Step Execution Protocol

1. **Daily Cadence**: Implement one day's deliverable per calendar day.
2. **Pre-Commit Verification**: Run `pytest` and `npm run build` to confirm zero regressions before staging.
3. **Commit & Push**:
   ```bash
   git add <modified_files>
   git commit -m "<EXACT_MESSAGE_FROM_TABLE>"
   git push origin Samarth---ITD
   ```
4. **Synchronization to `main`**: Merge to `main` at the end of each milestone phase.
