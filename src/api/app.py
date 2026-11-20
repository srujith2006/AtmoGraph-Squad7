"""FastAPI application factory and middleware wiring for AtmoGraph."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.logging import setup_logging, get_logger
from src.core.middleware import RequestLoggingMiddleware
from src.core.exceptions import register_exception_handlers
from src.core.neo4j import get_neo4j_pool
from src.api.routes.health import router as health_router
from src.api.routes.graph import router as graph_router
from src.api.routes.nlp import router as nlp_router
from src.api.routes.predictions import router as predictions_router
from src.api.routes.websocket import router as websocket_router, rest_ws_router

logger = get_logger("atmograph.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager initializing resources and structured logging."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, json_format=settings.log_json_format)
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} [{settings.environment}]",
        extra={"environment": settings.environment, "debug": settings.debug}
    )
    # Initialize Neo4j connection pool with resilient fallback
    pool = get_neo4j_pool()
    await pool.connect(max_retries=1, initial_delay=0.1)
    yield
    logger.info(f"Shutting down {settings.app_name}")
    await pool.close()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AtmoGraph API: Supply Chain Ripple Effect Predictor. "
            "Predicting multi-hop delays by mapping live news disruptions onto a global supply chain graph."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Register Centralized Exception Handlers
    register_exception_handlers(app)

    # 2. Attach Custom Observability & Request Logging Middleware
    app.add_middleware(RequestLoggingMiddleware, header_name=settings.request_id_header)

    # 3. Attach CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[settings.request_id_header, "X-Process-Time-Ms"],
    )

    # 4. Mount System Routers
    app.include_router(health_router)
    app.include_router(graph_router, prefix=settings.api_prefix)
    app.include_router(nlp_router, prefix=settings.api_prefix)
    app.include_router(predictions_router, prefix=settings.api_prefix)
    app.include_router(websocket_router)
    app.include_router(rest_ws_router, prefix=settings.api_prefix)

    return app


# Module-level instance for ASGI servers (uvicorn src.api.app:app)
app = create_app()
