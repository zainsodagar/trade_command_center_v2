from datetime import UTC, datetime

from fastapi import FastAPI

from backend.app.brokers.api import (
    get_broker_service,
)
from backend.app.brokers.api import (
    router as broker_router,
)
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend API for Trade Command Center V2.",
)

app.include_router(broker_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/v1/system/status", tags=["system"])
def system_status() -> dict[str, object]:
    broker_service = get_broker_service()

    return {
        "backend": "online",
        "broker_connections": broker_service.connection_count(),
        "execution_enabled": False,
        "live_trading_enabled": False,
    }