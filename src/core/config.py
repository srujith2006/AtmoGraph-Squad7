"""Centralized application configuration management for AtmoGraph.

Loads environment variables with type validation, defaults, and cached access.
"""

from functools import lru_cache
from typing import List, Union
import json
import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field, field_validator
except ImportError:  # pragma: no cover
    # Graceful fallback if pydantic-settings is not yet installed in clean environment
    from pydantic import BaseModel as BaseSettings, Field  # type: ignore
    SettingsConfigDict = dict  # type: ignore
    def field_validator(*args, **kwargs):  # type: ignore
        def decorator(f):
            return f
        return decorator


class Settings(BaseSettings):
    """AtmoGraph runtime environment configuration."""

    # Application Metadata
    app_name: str = Field(default="AtmoGraph Ripple Predictor", description="Application display name")
    app_version: str = Field(default="1.0.0", description="Semantic version")
    environment: str = Field(default="development", description="Runtime environment: development | staging | production")
    debug: bool = Field(default=True, description="Enable verbose debug mode and tracebacks")
    api_prefix: str = Field(default="/api/v1", description="Global REST API route prefix")

    # Network / Host
    host: str = Field(default="0.0.0.0", description="Bind IP address")
    port: int = Field(default=8000, description="Listening TCP port")

    # Security & CORS
    cors_origins: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origin domains"
    )

    # Observability & Structured Logging
    log_level: str = Field(default="INFO", description="Standard logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    log_json_format: bool = Field(default=True, description="Output structured JSON instead of plain text")
    request_id_header: str = Field(default="X-Request-ID", description="HTTP header key for distributed correlation ID")

    # Graph Database (Neo4j)
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j Bolt connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j authentication user")
    neo4j_password: str = Field(default="password", description="Neo4j authentication password")
    neo4j_database: str = Field(default="neo4j", description="Target Neo4j graph database")
    neo4j_max_connection_pool_size: int = Field(default=50, description="Max connection pool size")
    neo4j_connection_timeout: float = Field(default=5.0, description="Connection timeout in seconds")

    # NLP Ingestion & GNN Bridge
    nlp_webhook_secret: str = Field(
        default="atmo-graph-secret-key-change-in-prod",
        description="Shared HMAC secret for verifying NLP worker webhooks"
    )
    gnn_model_path: str = Field(default="models/gnn_ripple_predictor.pt", description="Path to trained GNN weights")
    gnn_device: str = Field(default="cpu", description="Compute device for PyTorch Geometric (cpu, cuda, mps)")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins whether provided as a JSON array or comma-separated string."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    ) if "SettingsConfigDict" in globals() else {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve cached instance of application settings."""
    return Settings()
