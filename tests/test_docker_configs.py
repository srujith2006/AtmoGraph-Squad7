"""Automated validation test suite for Docker containerization and Nginx reverse proxy configs.

Validates:
- Multi-stage build patterns in Dockerfile.backend and Dockerfile.frontend
- Non-root user security enforcement in backend container
- Nginx SPA client-side routing fallback and WebSocket upgrade reverse proxy
- Comprehensive .dockerignore boundary enforcement to avoid bloated or insecure image builds
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.unit
def test_dockerfile_backend_structure():
    """Verify Dockerfile.backend adheres to production container standards."""
    dockerfile_path = REPO_ROOT / "Dockerfile.backend"
    assert dockerfile_path.exists(), "Dockerfile.backend is missing"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage validation
    assert "AS builder" in content
    assert "AS runner" in content
    assert "python:3.11-slim" in content

    # Security: non-root user
    assert "useradd" in content or "adduser" in content
    assert "USER appuser" in content

    # Healthcheck & Port
    assert "EXPOSE 8000" in content
    assert "HEALTHCHECK" in content
    assert "/health" in content

    # Entrypoint command
    assert "uvicorn" in content
    assert "src.api.app:app" in content


@pytest.mark.unit
def test_dockerfile_frontend_structure():
    """Verify Dockerfile.frontend adheres to production container standards."""
    dockerfile_path = REPO_ROOT / "Dockerfile.frontend"
    assert dockerfile_path.exists(), "Dockerfile.frontend is missing"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage validation
    assert "node:" in content and "AS builder" in content
    assert "nginx:" in content and "AS runner" in content

    # Build and static transfer
    assert "npm run build" in content
    assert "COPY --from=builder" in content
    assert "/usr/share/nginx/html" in content

    # Port and Nginx configuration
    assert "EXPOSE 80" in content
    assert "nginx.conf" in content
    assert "HEALTHCHECK" in content


@pytest.mark.unit
def test_nginx_conf_routing_and_websocket_proxy():
    """Verify nginx.conf provides SPA fallback and full-duplex WebSocket reverse proxy."""
    nginx_path = REPO_ROOT / "nginx.conf"
    assert nginx_path.exists(), "nginx.conf is missing"

    content = nginx_path.read_text(encoding="utf-8")

    # Upstream definition
    assert "upstream backend_api" in content
    assert "backend:8000" in content

    # SPA routing fallback
    assert "try_files $uri $uri/ /index.html;" in content

    # Reverse proxy paths
    assert "location /api/" in content
    assert "location /health" in content
    assert "location ~ ^/(docs|redoc|openapi.json)" in content

    # Real-time WebSocket proxy directives
    assert "location /ws/" in content
    assert "proxy_set_header Upgrade $http_upgrade;" in content
    assert 'proxy_set_header Connection "Upgrade";' in content


@pytest.mark.unit
def test_dockerignore_rules():
    """Verify .dockerignore excludes heavy build artifacts and secret files."""
    dockerignore_path = REPO_ROOT / ".dockerignore"
    assert dockerignore_path.exists(), ".dockerignore is missing"

    content = dockerignore_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

    # Essential exclusions
    assert ".git/" in lines or ".git" in lines
    assert ".venv/" in lines or ".venv" in lines
    assert "node_modules/" in lines or "node_modules" in lines
    assert "__pycache__/" in lines or "__pycache__" in lines
    assert ".env" in lines


@pytest.mark.unit
def test_docker_compose_production_stack():
    """Verify docker-compose.yml correctly specifies neo4j, backend, and frontend services."""
    import yaml

    compose_path = REPO_ROOT / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml is missing"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    assert "services" in compose_data, "No services defined in docker-compose.yml"
    services = compose_data["services"]

    # 1. Neo4j Service Verification
    assert "neo4j" in services
    neo4j_svc = services["neo4j"]
    assert "neo4j:5.15" in neo4j_svc["image"]
    assert "7474:7474" in neo4j_svc["ports"]
    assert "7687:7687" in neo4j_svc["ports"]
    assert "healthcheck" in neo4j_svc
    assert "networks" in neo4j_svc

    # 2. Backend Service Verification
    assert "backend" in services
    backend_svc = services["backend"]
    assert backend_svc["build"]["dockerfile"] == "Dockerfile.backend"
    assert "8000:8000" in backend_svc["ports"]
    assert "neo4j" in backend_svc["depends_on"]
    assert backend_svc["depends_on"]["neo4j"]["condition"] == "service_healthy"
    assert "healthcheck" in backend_svc

    # 3. Frontend Service Verification
    assert "frontend" in services
    frontend_svc = services["frontend"]
    assert frontend_svc["build"]["dockerfile"] == "Dockerfile.frontend"
    assert "80:80" in frontend_svc["ports"]
    assert "backend" in frontend_svc["depends_on"]
    assert frontend_svc["depends_on"]["backend"]["condition"] == "service_healthy"

    # 4. Shared Networks and Persistent Volumes
    assert "networks" in compose_data
    assert "atmograph-net" in compose_data["networks"]
    assert "volumes" in compose_data
    assert "neo4j_data" in compose_data["volumes"]
    assert "neo4j_logs" in compose_data["volumes"]


@pytest.mark.unit
def test_docker_compose_override_dev_profile():
    """Verify docker-compose.override.yml provides hot-reloading dev mounts and debug ports."""
    import yaml

    override_path = REPO_ROOT / "docker-compose.override.yml"
    assert override_path.exists(), "docker-compose.override.yml is missing"

    with open(override_path, "r", encoding="utf-8") as f:
        override_data = yaml.safe_load(f)

    services = override_data.get("services", {})
    assert "backend" in services
    assert "frontend" in services

    # Backend dev reload configuration
    backend_dev = services["backend"]
    assert any("./src:/app/src" in v for v in backend_dev.get("volumes", []))
    assert "--reload" in " ".join(backend_dev.get("command", []))

    # Frontend dev port exposure
    frontend_dev = services["frontend"]
    assert "5173:5173" in frontend_dev.get("ports", [])

