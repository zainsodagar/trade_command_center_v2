from pathlib import Path

import pytest

from execution_agent.app.core.config import AgentSettings
from execution_agent.app.mt5.client import (
    MT5AccountSnapshot,
    MT5Client,
    MT5ClientError,
    MT5TerminalSnapshot,
)
from execution_agent.app.mt5.status import get_mt5_status


def make_settings(
    *,
    mt5_enabled: bool,
    terminal_path: str | None,
) -> AgentSettings:
    return AgentSettings(
        mt5_enabled=mt5_enabled,
        mt5_terminal_path=terminal_path,
        execution_enabled=False,
        live_trading_enabled=False,
    )


def make_terminal_snapshot(
    terminal_path: Path,
) -> MT5TerminalSnapshot:
    return MT5TerminalSnapshot(
        package_version="5.0.5735",
        terminal_version=500,
        terminal_build=6090,
        terminal_build_date="31 Jul 2026",
        connected=True,
        trade_allowed=False,
        trade_api_disabled=False,
        dlls_allowed=False,
        company="PXBT Trading Ltd",
        terminal_name="PXBT Trading MT5 Terminal",
        terminal_path=str(terminal_path.parent),
        data_path="C:\\MT5\\Data",
    )


def test_disabled_mt5_without_terminal() -> None:
    settings = make_settings(
        mt5_enabled=False,
        terminal_path=None,
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is False
    assert status.terminal_available is False
    assert status.initialized is False
    assert status.connected is False

    assert status.account_logged_in is False

    assert status.execution_enabled is False
    assert status.live_trading_enabled is False

    assert status.message == "MT5 integration disabled"


def test_disabled_mt5_can_detect_terminal(
    tmp_path: Path,
) -> None:
    terminal = tmp_path / "terminal64.exe"
    terminal.touch()

    settings = make_settings(
        mt5_enabled=False,
        terminal_path=str(terminal),
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is False
    assert status.terminal_available is True
    assert status.connected is False
    assert status.account_logged_in is False

    assert status.terminal_path == str(terminal)


def test_enabled_mt5_requires_terminal() -> None:
    settings = make_settings(
        mt5_enabled=True,
        terminal_path="missing-terminal64.exe",
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is True
    assert status.terminal_available is False
    assert status.connected is False
    assert status.account_logged_in is False

    assert status.message == (
        "MT5 terminal is not available"
    )


def test_successful_demo_account_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    terminal = tmp_path / "terminal64.exe"
    terminal.touch()

    terminal_snapshot = make_terminal_snapshot(
        terminal,
    )

    account_snapshot = MT5AccountSnapshot(
        login=1237959,
        masked_login="***7959",
        trade_mode="demo",
        server="PXBTTrading-1",
        company="PXBT Trading Ltd",
        currency="USD",
        leverage=100,
        trade_allowed=True,
        trade_expert=True,
    )

    def fake_initialize(
        _self: object,
    ) -> None:
        return None

    def fake_shutdown(
        _self: object,
    ) -> None:
        return None

    def fake_terminal_snapshot(
        _self: object,
    ) -> MT5TerminalSnapshot:
        return terminal_snapshot

    def fake_account_snapshot(
        _self: object,
    ) -> MT5AccountSnapshot:
        return account_snapshot

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        fake_initialize,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        fake_shutdown,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_terminal_snapshot",
        fake_terminal_snapshot,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        fake_account_snapshot,
    )

    settings = make_settings(
        mt5_enabled=True,
        terminal_path=str(terminal),
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is True
    assert status.terminal_available is True

    assert status.initialized is False
    assert status.connected is True

    assert status.account_logged_in is True
    assert status.account_login_masked == "***7959"
    assert status.account_mode == "demo"
    assert status.account_server == "PXBTTrading-1"
    assert status.account_company == "PXBT Trading Ltd"
    assert status.account_currency == "USD"
    assert status.account_leverage == 100

    assert status.account_trade_allowed is True
    assert status.account_trade_expert is True

    assert status.package_version == "5.0.5735"
    assert status.terminal_build == 6090

    assert status.execution_enabled is False
    assert status.live_trading_enabled is False

    assert status.message == (
        "MT5 terminal and demo account probe successful"
    )


def test_account_probe_failure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    terminal = tmp_path / "terminal64.exe"
    terminal.touch()

    terminal_snapshot = make_terminal_snapshot(
        terminal,
    )

    def fake_initialize(
        _self: object,
    ) -> None:
        return None

    def fake_shutdown(
        _self: object,
    ) -> None:
        return None

    def fake_terminal_snapshot(
        _self: object,
    ) -> MT5TerminalSnapshot:
        return terminal_snapshot

    def failing_account_snapshot(
        _self: object,
    ) -> MT5AccountSnapshot:
        raise MT5ClientError(
            "simulated account failure"
        )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        fake_initialize,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        fake_shutdown,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_terminal_snapshot",
        fake_terminal_snapshot,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        failing_account_snapshot,
    )

    settings = make_settings(
        mt5_enabled=True,
        terminal_path=str(terminal),
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is True
    assert status.terminal_available is True
    assert status.connected is True

    assert status.account_logged_in is False
    assert status.account_login_masked is None
    assert status.account_mode is None

    assert status.execution_enabled is False
    assert status.live_trading_enabled is False

    assert status.message == (
        "MT5 terminal probe successful; "
        "account unavailable: simulated account failure"
    )


def test_terminal_probe_failure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    terminal = tmp_path / "terminal64.exe"
    terminal.touch()

    def failing_initialize(
        _self: object,
    ) -> None:
        raise MT5ClientError(
            "simulated initialization failure"
        )

    def fake_shutdown(
        _self: object,
    ) -> None:
        return None

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        failing_initialize,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        fake_shutdown,
    )

    settings = make_settings(
        mt5_enabled=True,
        terminal_path=str(terminal),
    )

    status = get_mt5_status(
        settings=settings,
    )

    assert status.enabled is True
    assert status.terminal_available is True

    assert status.connected is False
    assert status.initialized is False
    assert status.account_logged_in is False

    assert status.execution_enabled is False
    assert status.live_trading_enabled is False

    assert status.message == (
        "MT5 probe failed: "
        "simulated initialization failure"
    )
