from datetime import UTC, datetime
from types import SimpleNamespace

import MetaTrader5 as mt5
import pytest

from execution_agent.app.core.config import AgentSettings
from execution_agent.app.mt5.client import (
    MT5Client,
    MT5InitializationError,
    MT5InstrumentSnapshot,
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


def make_instrument(
    *,
    symbol: str = "EURUSD",
    selected: bool = True,
    visible: bool = True,
    trade_mode: str = "full",
    new_order_allowed: bool = True,
    reference_only: bool = False,
    point: float = 0.00001,
    digits: int = 5,
) -> MT5InstrumentSnapshot:
    return MT5InstrumentSnapshot(
        broker_symbol=symbol,
        broker_path=f"Test\\{symbol}",
        broker_group="Test",
        description=f"Test {symbol}",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="EUR",
        digits=digits,
        point=point,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=100.0,
        volume_step=0.01,
        trade_mode=trade_mode,
        trade_calc_mode=0,
        order_mode=127,
        new_order_allowed=new_order_allowed,
        reference_only=reference_only,
        visible=visible,
        selected=selected,
    )


def test_quote_requires_initialization(
    tmp_path,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    with pytest.raises(
        MT5InitializationError,
        match="not initialized",
    ):
        client.get_quote_snapshot(
            "EURUSD"
        )


def test_unselected_symbol_returns_unavailable_quote(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

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

    instrument = make_instrument(
        symbol="CRUDE",
        selected=False,
        visible=False,
        point=0.001,
        digits=3,
    )

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    quote = client.get_quote_snapshot(
        "CRUDE"
    )

    assert quote.broker_symbol == "CRUDE"

    assert quote.selected is False
    assert quote.visible is False

    assert quote.quote_available is False

    assert quote.unavailable_reason == (
        "symbol_not_selected"
    )

    assert quote.bid is None
    assert quote.ask is None
    assert quote.spread is None
    assert quote.spread_points is None

    assert quote.error_code is None
    assert quote.error_message is None

    client.shutdown()


def test_selected_symbol_returns_quote(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    tick = SimpleNamespace(
        time=1786816680,
        time_msc=1786816680119,
        bid=1.15695,
        ask=1.15712,
        last=0.0,
        volume=0,
        volume_real=0.0,
        flags=6,
    )

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: tick,
    )

    quote = client.get_quote_snapshot(
        "EURUSD"
    )

    assert quote.quote_available is True

    assert quote.bid == 1.15695
    assert quote.ask == 1.15712

    assert quote.spread == pytest.approx(
        0.00017
    )

    assert quote.spread_points == pytest.approx(
        17.0
    )

    assert quote.tick_time == datetime.fromtimestamp(
        1786816680,
        tz=UTC,
    )

    assert quote.tick_time_msc == 1786816680119

    assert quote.unavailable_reason is None
    assert quote.error_code is None
    assert quote.error_message is None

    client.shutdown()


def test_tick_failure_is_reported(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: None,
    )

    monkeypatch.setattr(
        mt5,
        "last_error",
        lambda: (-4, "Terminal: Not found"),
    )

    quote = client.get_quote_snapshot(
        "EURUSD"
    )

    assert quote.quote_available is False

    assert quote.unavailable_reason == (
        "tick_unavailable"
    )

    assert quote.error_code == -4

    assert quote.error_message == (
        "Terminal: Not found"
    )

    assert quote.bid is None
    assert quote.ask is None

    client.shutdown()


def test_reference_symbol_can_have_quote_without_being_tradable(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

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

    instrument = make_instrument(
        symbol="BTCUSD",
        trade_mode="disabled",
        new_order_allowed=False,
        reference_only=True,
        point=0.1,
        digits=1,
    )

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    tick = SimpleNamespace(
        time=1786816680,
        time_msc=1786816680119,
        bid=63010.0,
        ask=63035.0,
        last=0.0,
        volume=0,
        volume_real=0.0,
        flags=1026,
    )

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: tick,
    )

    quote = client.get_quote_snapshot(
        "BTCUSD"
    )

    assert quote.quote_available is True

    assert quote.trade_mode == "disabled"
    assert quote.new_order_allowed is False
    assert quote.reference_only is True

    assert quote.bid == 63010.0
    assert quote.ask == 63035.0

    assert quote.spread == 25.0
    assert quote.spread_points == 250.0

    client.shutdown()


def test_probe_quote_always_shuts_down(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shutdown_calls = 0

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    instrument = make_instrument()

    tick = SimpleNamespace(
        time=1786816680,
        time_msc=1786816680119,
        bid=1.15695,
        ask=1.15712,
        last=0.0,
        volume=0,
        volume_real=0.0,
        flags=6,
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
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: tick,
    )

    quote = client.probe_quote(
        "EURUSD"
    )

    assert quote.quote_available is True

    assert client.initialized is False
    assert shutdown_calls == 1