"""Shared pytest configuration, fixtures, and mock instances for AtmoGraph testing."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from src.api.app import create_app
from src.core.config import Settings, get_settings


@pytest.fixture(scope="session")
def app_instance():
    """Create a FastAPI application instance for test suites."""
    return create_app()


@pytest.fixture(scope="session")
def client(app_instance):
    """Provide a synchronous TestClient configured with the FastAPI test app."""
    with TestClient(app_instance, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
async def async_client(app_instance):
    """Provide an asynchronous httpx client configured with the ASGI application."""
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def mock_custom_settings(monkeypatch):
    """Fixture providing helper to temporarily patch settings during tests."""
    def _override(**kwargs):
        test_settings = Settings(**kwargs)
        monkeypatch.setattr("src.core.config.get_settings", lambda: test_settings)
        return test_settings
    return _override
