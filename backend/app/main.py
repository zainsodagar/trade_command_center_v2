from datetime import datetime, timezone

from fastapi import FastAPI

from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend API for Trade Command Center V2.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/system/status", tags=["system"])
def system_status() -> dict[str, object]:
    return {
        "backend": "online",
        "broker_connections": 0,
        "execution_enabled": False,
        "live_trading_enabled": False,
    }
