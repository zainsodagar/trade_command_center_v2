from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from execution_agent.app.core.config import (
    AgentSettings,
    get_agent_settings,
)
from execution_agent.app.mt5.client import (
    MT5AccountSnapshot,
    MT5Client,
    MT5ClientError,
)


class MT5Status(BaseModel):
    """Current MetaTrader 5 read-only integration status."""

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

    package_version: str | None = None

    terminal_version: int | None = None
    terminal_build: int | None = None
    terminal_build_date: str | None = None

    trade_allowed: bool | None = None
    trade_api_disabled: bool | None = None
    dlls_allowed: bool | None = None

    company: str | None = None
    terminal_name: str | None = None

    terminal_path: str | None = None
    data_path: str | None = None

    account_login_masked: str | None = None
    account_mode: str | None = None
    account_server: str | None = None
    account_company: str | None = None
    account_currency: str | None = None
    account_leverage: int | None = None

    account_trade_allowed: bool | None = None
    account_trade_expert: bool | None = None

    message: str

    checked_at: datetime


def get_mt5_status(
    settings: AgentSettings | None = None,
) -> MT5Status:
    """
    Return the current MT5 integration state.

    When MT5 integration is enabled, the agent temporarily initializes
    the configured terminal, inspects terminal/account state, and then
    shuts down the Python MT5 connection.

    No login or order execution is performed.
    """

    active_settings = (
        settings
        if settings is not None
        else get_agent_settings()
    )

    configured_path = active_settings.mt5_terminal_path

    terminal_available = bool(
        configured_path
        and Path(configured_path).is_file()
    )

    if not active_settings.mt5_enabled:
        return MT5Status(
            enabled=False,
            terminal_available=terminal_available,
            initialized=False,
            connected=False,
            account_logged_in=False,
            execution_enabled=active_settings.execution_enabled,
            live_trading_enabled=active_settings.live_trading_enabled,
            terminal_path=configured_path,
            message="MT5 integration disabled",
            checked_at=datetime.now(UTC),
        )

    if not terminal_available:
        return MT5Status(
            enabled=True,
            terminal_available=False,
            initialized=False,
            connected=False,
            account_logged_in=False,
            execution_enabled=active_settings.execution_enabled,
            live_trading_enabled=active_settings.live_trading_enabled,
            terminal_path=configured_path,
            message="MT5 terminal is not available",
            checked_at=datetime.now(UTC),
        )

    client = MT5Client(
        settings=active_settings,
    )

    account_snapshot: MT5AccountSnapshot | None = None
    account_error: str | None = None

    try:
        client.initialize()

        terminal_snapshot = client.get_terminal_snapshot()

        try:
            account_snapshot = client.get_account_snapshot()
        except MT5ClientError as exc:
            account_error = str(exc)

    except MT5ClientError as exc:
        return MT5Status(
            enabled=True,
            terminal_available=True,
            initialized=False,
            connected=False,
            account_logged_in=False,
            execution_enabled=active_settings.execution_enabled,
            live_trading_enabled=active_settings.live_trading_enabled,
            terminal_path=configured_path,
            message=f"MT5 probe failed: {exc}",
            checked_at=datetime.now(UTC),
        )

    finally:
        client.shutdown()

    if account_snapshot is None:
        message = (
            "MT5 terminal probe successful; "
            f"account unavailable: {account_error}"
        )
    elif account_snapshot.trade_mode == "demo":
        message = (
            "MT5 terminal and demo account probe successful"
        )
    else:
        message = (
            "MT5 terminal probe successful; "
            f"non-demo account detected: "
            f"{account_snapshot.trade_mode}"
        )

    return MT5Status(
        enabled=True,
        terminal_available=True,
        initialized=False,
        connected=terminal_snapshot.connected,
        account_logged_in=account_snapshot is not None,
        execution_enabled=active_settings.execution_enabled,
        live_trading_enabled=active_settings.live_trading_enabled,
        package_version=terminal_snapshot.package_version,
        terminal_version=terminal_snapshot.terminal_version,
        terminal_build=terminal_snapshot.terminal_build,
        terminal_build_date=terminal_snapshot.terminal_build_date,
        trade_allowed=terminal_snapshot.trade_allowed,
        trade_api_disabled=terminal_snapshot.trade_api_disabled,
        dlls_allowed=terminal_snapshot.dlls_allowed,
        company=terminal_snapshot.company,
        terminal_name=terminal_snapshot.terminal_name,
        terminal_path=terminal_snapshot.terminal_path,
        data_path=terminal_snapshot.data_path,
        account_login_masked=(
            account_snapshot.masked_login
            if account_snapshot is not None
            else None
        ),
        account_mode=(
            account_snapshot.trade_mode
            if account_snapshot is not None
            else None
        ),
        account_server=(
            account_snapshot.server
            if account_snapshot is not None
            else None
        ),
        account_company=(
            account_snapshot.company
            if account_snapshot is not None
            else None
        ),
        account_currency=(
            account_snapshot.currency
            if account_snapshot is not None
            else None
        ),
        account_leverage=(
            account_snapshot.leverage
            if account_snapshot is not None
            else None
        ),
        account_trade_allowed=(
            account_snapshot.trade_allowed
            if account_snapshot is not None
            else None
        ),
        account_trade_expert=(
            account_snapshot.trade_expert
            if account_snapshot is not None
            else None
        ),
        message=message,
        checked_at=datetime.now(UTC),
    )
