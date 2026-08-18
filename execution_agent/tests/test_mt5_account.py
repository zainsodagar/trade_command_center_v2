from types import SimpleNamespace

import MetaTrader5 as mt5
import pytest

from execution_agent.app.core.config import AgentSettings
from execution_agent.app.mt5.client import (
    MT5Client,
    MT5ClientError,
    MT5InitializationError,
)


def make_settings(
    tmp_path,
) -> AgentSettings:
    terminal = tmp_path / "terminal64.exe"
    terminal.touch()

    return AgentSettings(
        mt5_enabled=True,
        mt5_terminal_path=str(terminal),
        execution_enabled=False,
        live_trading_enabled=False,
    )


def make_account_info(
    *,
    login: int = 1237959,
    trade_mode: int = mt5.ACCOUNT_TRADE_MODE_DEMO,
):
    return SimpleNamespace(
        login=login,
        trade_mode=trade_mode,
        leverage=100,
        limit_orders=0,
        margin_so_mode=0,
        trade_allowed=True,
        trade_expert=True,
        margin_mode=2,
        currency_digits=2,
        fifo_close=False,
        balance=10000.0,
        credit=0.0,
        profit=125.50,
        equity=10125.50,
        margin=250.0,
        margin_free=9875.50,
        margin_level=4050.2,
        margin_so_call=100.0,
        margin_so_so=50.0,
        margin_initial=0.0,
        margin_maintenance=0.0,
        assets=0.0,
        liabilities=0.0,
        commission_blocked=0.0,
        server="PXBTTrading-1",
        currency="USD",
        company="PXBT Trading Ltd",
    )


def initialize_client(
    client: MT5Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mt5,
        "initialize",
        lambda **_kwargs: True,
    )

    monkeypatch.setattr(
        mt5,
        "shutdown",
        lambda: None,
    )

    client.initialize()


def test_account_snapshot_requires_initialization(
    tmp_path,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    with pytest.raises(
        MT5InitializationError,
        match="not initialized",
    ):
        client.get_account_snapshot()


def test_account_snapshot_maps_detailed_pxbt_values(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    initialize_client(
        client,
        monkeypatch,
    )

    account_info = make_account_info()

    monkeypatch.setattr(
        mt5,
        "account_info",
        lambda: account_info,
    )

    snapshot = client.get_account_snapshot()

    assert snapshot.login == 1237959
    assert snapshot.masked_login == "***7959"

    assert snapshot.trade_mode == "demo"

    assert snapshot.server == "PXBTTrading-1"
    assert snapshot.company == "PXBT Trading Ltd"
    assert snapshot.currency == "USD"

    assert snapshot.currency_digits == 2

    assert snapshot.leverage == 100
    assert snapshot.limit_orders == 0

    assert snapshot.trade_allowed is True
    assert snapshot.trade_expert is True
    assert snapshot.fifo_close is False

    assert snapshot.margin_mode == 2
    assert snapshot.margin_so_mode == 0

    assert snapshot.balance == 10000.0
    assert snapshot.credit == 0.0
    assert snapshot.profit == 125.50
    assert snapshot.equity == 10125.50

    assert snapshot.margin == 250.0
    assert snapshot.margin_free == 9875.50
    assert snapshot.margin_level == 4050.2

    assert snapshot.margin_so_call == 100.0
    assert snapshot.margin_so_so == 50.0

    assert snapshot.margin_initial == 0.0
    assert snapshot.margin_maintenance == 0.0

    assert snapshot.assets == 0.0
    assert snapshot.liabilities == 0.0
    assert snapshot.commission_blocked == 0.0

    client.shutdown()


@pytest.mark.parametrize(
    (
        "raw_trade_mode",
        "expected_trade_mode",
    ),
    [
        (
            mt5.ACCOUNT_TRADE_MODE_DEMO,
            "demo",
        ),
        (
            mt5.ACCOUNT_TRADE_MODE_CONTEST,
            "contest",
        ),
        (
            mt5.ACCOUNT_TRADE_MODE_REAL,
            "real",
        ),
        (
            999,
            "unknown",
        ),
    ],
)
def test_account_trade_mode_mapping(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    raw_trade_mode: int,
    expected_trade_mode: str,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    initialize_client(
        client,
        monkeypatch,
    )

    monkeypatch.setattr(
        mt5,
        "account_info",
        lambda: make_account_info(
            trade_mode=raw_trade_mode,
        ),
    )

    snapshot = client.get_account_snapshot()

    assert snapshot.trade_mode == (
        expected_trade_mode
    )

    client.shutdown()


def test_account_info_failure_is_reported(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    initialize_client(
        client,
        monkeypatch,
    )

    monkeypatch.setattr(
        mt5,
        "account_info",
        lambda: None,
    )

    monkeypatch.setattr(
        mt5,
        "last_error",
        lambda: (-6, "Terminal: account unavailable"),
    )

    with pytest.raises(
        MT5ClientError,
        match="account information is unavailable",
    ):
        client.get_account_snapshot()

    client.shutdown()


def test_short_login_is_never_exposed_unmasked(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    initialize_client(
        client,
        monkeypatch,
    )

    monkeypatch.setattr(
        mt5,
        "account_info",
        lambda: make_account_info(
            login=1234,
        ),
    )

    snapshot = client.get_account_snapshot()

    assert snapshot.login == 1234
    assert snapshot.masked_login == "****"

    client.shutdown()


def test_probe_account_always_shuts_down(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shutdown_calls = 0

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    monkeypatch.setattr(
        mt5,
        "initialize",
        lambda **_kwargs: True,
    )

    def fake_shutdown() -> None:
        nonlocal shutdown_calls
        shutdown_calls += 1

    monkeypatch.setattr(
        mt5,
        "shutdown",
        fake_shutdown,
    )

    monkeypatch.setattr(
        mt5,
        "account_info",
        lambda: make_account_info(),
    )

    snapshot = client.probe_account()

    assert snapshot.trade_mode == "demo"
    assert snapshot.masked_login == "***7959"

    assert snapshot.balance == 10000.0
    assert snapshot.equity == 10125.50

    assert client.initialized is False
    assert shutdown_calls == 1