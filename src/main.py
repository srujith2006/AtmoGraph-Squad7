"""CLI entrypoint for running the AtmoGraph FastAPI application."""

import uvicorn
from src.core.config import get_settings


def start():
    """Run uvicorn server with loaded settings."""
    settings = get_settings()
    uvicorn.run(
        "src.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Handled by our custom structured JSON logger
    )


if __name__ == "__main__":
    start()
