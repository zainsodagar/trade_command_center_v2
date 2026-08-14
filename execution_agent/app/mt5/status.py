from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from execution_agent.app.core.config import (
    AgentSettings,
    get_agent_settings,
)


class MT5Status(BaseModel):
    """Current read-only MetaTrader 5 integration status."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    enabled: bool

    terminal_available: bool
    initialized: bool
    connected: bool
    account_logged_in: bool

    execution_enabled: bool
    live_trading_enabled: bool

    message: str

    checked_at: datetime


def get_mt5_status(
    settings: AgentSettings | None = None,
) -> MT5Status:
    """
    Return the current safe MT5 state.

    Checkpoint 4.1 does not initialize MetaTrader 5 yet, so terminal
    connectivity remains false even if MT5 support is configured.
    """

    active_settings = (
        settings
        if settings is not None
        else get_agent_settings()
    )

    if active_settings.mt5_enabled:
        message = (
            "MT5 integration enabled but not initialized"
        )
    else:
        message = "MT5 integration disabled"

    return MT5Status(
        enabled=active_settings.mt5_enabled,
        terminal_available=False,
        initialized=False,
        connected=False,
        account_logged_in=False,
        execution_enabled=active_settings.execution_enabled,
        live_trading_enabled=active_settings.live_trading_enabled,
        message=message,
        checked_at=datetime.now(UTC),
    )