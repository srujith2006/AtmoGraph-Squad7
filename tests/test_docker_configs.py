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
