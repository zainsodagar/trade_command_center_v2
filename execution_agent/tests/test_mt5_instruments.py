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


def make_symbol(
    *,
    name: str,
    path: str,
    trade_mode: int,
    visible: bool = False,
    selected: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        path=path,
        description=f"Test {name}",
        currency_base="USD",
        currency_profit="USD",
        currency_margin="USD",
        digits=2,
        point=0.01,
        trade_contract_size=100.0,
        volume_min=0.01,
        volume_max=100.0,
        volume_step=0.01,
        trade_mode=trade_mode,
        trade_calc_mode=0,
        order_mode=127,
        visible=visible,
        select=selected,
    )


def test_instruments_require_initialization(
    tmp_path,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    with pytest.raises(
        MT5InitializationError,
        match="not initialized",
    ):
        client.get_instrument_snapshots()


def test_probe_instruments_maps_trade_modes(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    symbols = (
        make_symbol(
            name="EURUSD",
            path="Forex\\Major\\EURUSD",
            trade_mode=mt5.SYMBOL_TRADE_MODE_FULL,
            visible=True,
            selected=True,
        ),
        make_symbol(
            name="LONGONLY",
            path="Test\\LONGONLY",
            trade_mode=mt5.SYMBOL_TRADE_MODE_LONGONLY,
        ),
        make_symbol(
            name="SHORTONLY",
            path="Test\\SHORTONLY",
            trade_mode=mt5.SYMBOL_TRADE_MODE_SHORTONLY,
        ),
        make_symbol(
            name="CLOSEONLY",
            path="Crypto\\CLOSEONLY",
            trade_mode=mt5.SYMBOL_TRADE_MODE_CLOSEONLY,
        ),
        make_symbol(
            name="BTCUSD",
            path="RefSymbols\\BTCUSD",
            trade_mode=mt5.SYMBOL_TRADE_MODE_DISABLED,
            visible=True,
            selected=True,
        ),
    )

    shutdown_calls = 0

    def fake_initialize(
        *,
        path: str,
    ) -> bool:
        assert path.endswith("terminal64.exe")
        return True

    def fake_shutdown() -> None:
        nonlocal shutdown_calls
        shutdown_calls += 1

    monkeypatch.setattr(
        mt5,
        "initialize",
        fake_initialize,
    )
    monkeypatch.setattr(
        mt5,
        "shutdown",
        fake_shutdown,
    )
    monkeypatch.setattr(
        mt5,
        "symbols_get",
        lambda: symbols,
    )

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    instruments = client.probe_instruments()

    by_symbol = {
        instrument.broker_symbol: instrument
        for instrument in instruments
    }

    assert len(instruments) == 5

    assert by_symbol["EURUSD"].broker_group == "Forex"
    assert by_symbol["EURUSD"].trade_mode == "full"
    assert by_symbol["EURUSD"].new_order_allowed is True
    assert by_symbol["EURUSD"].reference_only is False
    assert by_symbol["EURUSD"].visible is True
    assert by_symbol["EURUSD"].selected is True

    assert by_symbol["LONGONLY"].trade_mode == "long_only"
    assert by_symbol["LONGONLY"].new_order_allowed is True

    assert by_symbol["SHORTONLY"].trade_mode == "short_only"
    assert by_symbol["SHORTONLY"].new_order_allowed is True

    assert by_symbol["CLOSEONLY"].trade_mode == "close_only"
    assert by_symbol["CLOSEONLY"].new_order_allowed is False

    assert by_symbol["BTCUSD"].trade_mode == "disabled"
    assert by_symbol["BTCUSD"].new_order_allowed is False
    assert by_symbol["BTCUSD"].reference_only is True

    assert client.initialized is False
    assert shutdown_calls == 1


def test_disabled_non_reference_symbol_is_not_reference_only(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    symbols = (
        make_symbol(
            name="SUSPENDED",
            path="Crypto\\SUSPENDED",
            trade_mode=mt5.SYMBOL_TRADE_MODE_DISABLED,
        ),
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
    monkeypatch.setattr(
        mt5,
        "symbols_get",
        lambda: symbols,
    )

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    instruments = client.probe_instruments()

    assert len(instruments) == 1

    instrument = instruments[0]

    assert instrument.trade_mode == "disabled"
    assert instrument.new_order_allowed is False
    assert instrument.reference_only is False


def test_instrument_catalogue_failure_is_reported(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shutdown_calls = 0

    def fake_shutdown() -> None:
        nonlocal shutdown_calls
        shutdown_calls += 1

    monkeypatch.setattr(
        mt5,
        "initialize",
        lambda **_kwargs: True,
    )
    monkeypatch.setattr(
        mt5,
        "shutdown",
        fake_shutdown,
    )
    monkeypatch.setattr(
        mt5,
        "symbols_get",
        lambda: None,
    )
    monkeypatch.setattr(
        mt5,
        "last_error",
        lambda: (5001, "simulated catalogue failure"),
    )

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    with pytest.raises(
        MT5ClientError,
        match="instrument catalogue is unavailable",
    ):
        client.probe_instruments()

    assert client.initialized is False
    assert shutdown_calls == 1