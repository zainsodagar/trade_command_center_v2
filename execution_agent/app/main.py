from datetime import UTC, datetime

from fastapi import FastAPI

from execution_agent.app.core.config import get_agent_settings
from execution_agent.app.mt5.status import MT5Status, get_mt5_status

settings = get_agent_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Windows MT5 agent for Trade Command Center V2.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/v1/agent/status", tags=["system"])
def agent_status() -> dict[str, object]:
    mt5_status = get_mt5_status()

    return {
        "agent": "online",
        "mt5_enabled": mt5_status.enabled,
        "mt5_connected": mt5_status.connected,
        "execution_enabled": mt5_status.execution_enabled,
        "live_trading_enabled": mt5_status.live_trading_enabled,
    }


@app.get(
    "/api/v1/mt5/status",
    tags=["mt5"],
    response_model=MT5Status,
)
def mt5_status() -> MT5Status:
    return get_mt5_status()