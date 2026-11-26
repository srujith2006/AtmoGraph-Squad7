"""Unit tests for AtmoGraph environment configuration."""

import pytest
from src.core.config import Settings, get_settings


@pytest.mark.unit
def test_default_settings():
    """Verify default configuration attributes are correctly populated."""
    settings = Settings()
    assert settings.app_name == "AtmoGraph Ripple Predictor"
    assert settings.app_version == "1.0.0"
    assert settings.environment in ("development", "staging", "production")
    assert settings.port == 8000
    assert "bolt://localhost:7687" in settings.neo4j_uri
    assert settings.request_id_header == "X-Request-ID"


@pytest.mark.unit
def test_cors_origins_parsing():
    """Verify CORS origins string is parsed into a list of strings."""
    # Comma-separated string
    s1 = Settings(cors_origins="http://example.com, https://app.example.com")
    assert s1.cors_origins == ["http://example.com", "https://app.example.com"]

    # JSON formatted list string
    s2 = Settings(cors_origins='["http://localhost:3000", "http://localhost:5173"]')
    assert s2.cors_origins == ["http://localhost:3000", "http://localhost:5173"]

    # Native list
    s3 = Settings(cors_origins=["http://localhost:8080"])
    assert s3.cors_origins == ["http://localhost:8080"]


@pytest.mark.unit
def test_cached_settings_singleton():
    """Verify get_settings returns the cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
