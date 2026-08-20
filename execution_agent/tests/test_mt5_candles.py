from datetime import UTC, datetime

import MetaTrader5 as mt5
import pytest

from execution_agent.app.core.config import AgentSettings
from execution_agent.app.mt5.client import (
    CANDLE_HISTORY_SYNC_ATTEMPTS,
    CANDLE_HISTORY_SYNC_DELAY_SECONDS,
    MAX_CANDLE_COUNT,
    MT5Client,
    MT5ClientError,
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


def test_candles_require_initialization(
    tmp_path,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    with pytest.raises(
        MT5InitializationError,
        match="not initialized",
    ):
        client.get_candle_series_snapshot(
            "EURUSD",
            "M1",
            5,
        )


def test_candles_return_ohlc_series(
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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    rates = [
        {
            "time": 1787086740,
            "open": 1.13863,
            "high": 1.13863,
            "low": 1.13863,
            "close": 1.13863,
            "tick_volume": 1,
            "spread": 2,
            "real_volume": 0,
        },
        {
            "time": 1787086500,
            "open": 1.13859,
            "high": 1.13863,
            "low": 1.13859,
            "close": 1.13863,
            "tick_volume": 20,
            "spread": 1,
            "real_volume": 0,
        },
    ]

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: rates,
    )

    result = client.get_candle_series_snapshot(
        "EURUSD",
        "m1",
        2,
    )

    assert result.broker_symbol == "EURUSD"
    assert result.timeframe == "M1"

    assert result.candles_available is True
    assert result.candle_count == 2
    assert result.count_requested == 2

    assert result.candles[0].bar_time < (result.candles[1].bar_time)

    assert result.oldest_candle_time == (result.candles[0].bar_time)

    assert result.latest_candle_time == (result.candles[-1].bar_time)

    assert result.candles[0].open == 1.13859
    assert result.candles[0].high == 1.13863
    assert result.candles[0].low == 1.13859
    assert result.candles[0].close == 1.13863

    assert result.candles[0].tick_volume == 20
    assert result.candles[0].spread == 1
    assert result.candles[0].real_volume == 0

    assert result.unavailable_reason is None
    assert result.error_code is None
    assert result.error_message is None

    client.shutdown()


def test_unselected_symbol_can_return_candles(
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

    rates = [
        {
            "time": 1787088900,
            "open": 85.01,
            "high": 85.04,
            "low": 84.97,
            "close": 85.005,
            "tick_volume": 23,
            "spread": 55,
            "real_volume": 0,
        },
    ]

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: rates,
    )

    result = client.get_candle_series_snapshot(
        "CRUDE",
        "M1",
        1,
    )

    assert result.selected_before is False
    assert result.visible_before is False

    assert result.selected_after is False
    assert result.visible_after is False

    assert result.candles_available is True
    assert result.candle_count == 1

    assert result.candles[0].close == 85.005
    assert result.candles[0].spread == 55

    client.shutdown()


def test_reference_symbol_can_have_candles(
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

    rates = [
        {
            "time": 1787088900,
            "open": 64732.2,
            "high": 64732.2,
            "low": 64732.2,
            "close": 64732.2,
            "tick_volume": 1,
            "spread": 250,
            "real_volume": 0,
        },
    ]

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: rates,
    )

    result = client.get_candle_series_snapshot(
        "BTCUSD",
        "M1",
        1,
    )

    assert result.candles_available is True

    assert result.trade_mode == "disabled"
    assert result.new_order_allowed is False
    assert result.reference_only is True

    assert result.candles[0].close == 64732.2

    client.shutdown()


def test_rates_failure_is_reported(
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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: None,
    )

    monkeypatch.setattr(
        mt5,
        "last_error",
        lambda: (-4, "Terminal: Not found"),
    )

    result = client.get_candle_series_snapshot(
        "EURUSD",
        "M1",
        5,
    )

    assert result.candles_available is False
    assert result.candle_count == 0
    assert result.candles == ()

    assert result.unavailable_reason == ("rates_unavailable")

    assert result.error_code == -4
    assert result.error_message == ("Terminal: Not found")

    client.shutdown()


def test_empty_rates_are_reported_without_error(
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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: [],
    )

    result = client.get_candle_series_snapshot(
        "EURUSD",
        "M5",
        10,
    )

    assert result.candles_available is False
    assert result.candle_count == 0

    assert result.oldest_candle_time is None
    assert result.latest_candle_time is None

    assert result.unavailable_reason == "no_rates"

    assert result.error_code is None
    assert result.error_message is None

    client.shutdown()


def test_invalid_timeframe_is_rejected(
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

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    with pytest.raises(
        MT5ClientError,
        match="Unsupported MT5 timeframe",
    ):
        client.get_candle_series_snapshot(
            "EURUSD",
            "M2",
            5,
        )

    client.shutdown()


@pytest.mark.parametrize(
    "count",
    [
        0,
        -1,
        MAX_CANDLE_COUNT + 1,
        True,
    ],
)
def test_invalid_candle_count_is_rejected(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    count,
) -> None:
    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    initialize_client(
        client,
        monkeypatch,
    )

    instrument = make_instrument()

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    with pytest.raises(
        MT5ClientError,
    ):
        client.get_candle_series_snapshot(
            "EURUSD",
            "M1",
            count,
        )

    client.shutdown()


def test_probe_candles_always_shuts_down(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shutdown_calls = 0

    client = MT5Client(
        settings=make_settings(tmp_path),
    )

    instrument = make_instrument()

    rates = [
        {
            "time": 1787088900,
            "open": 1.13859,
            "high": 1.13863,
            "low": 1.13858,
            "close": 1.13863,
            "tick_volume": 20,
            "spread": 1,
            "real_volume": 0,
        },
    ]

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
        "copy_rates_from_pos",
        lambda *_args: rates,
    )

    result = client.probe_candles(
        "EURUSD",
        "M1",
        1,
    )

    assert result.candles_available is True

    assert client.initialized is False
    assert shutdown_calls == 1

    expected_time = datetime.fromtimestamp(
        1787088900,
        tz=UTC,
    )

    assert result.latest_candle_time == expected_time


def test_candle_history_can_change_mt5_selected_state(
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

    instrument = make_instrument(
        symbol="US500",
        selected=False,
        visible=False,
        point=0.01,
        digits=2,
    )

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    rates = [
        {
            "time": 1787088900,
            "open": 6500.0,
            "high": 6501.0,
            "low": 6499.0,
            "close": 6500.5,
            "tick_volume": 25,
            "spread": 50,
            "real_volume": 0,
        },
    ]

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        lambda *_args: rates,
    )

    class AfterSymbolInfo:
        visible = False
        select = True

    monkeypatch.setattr(
        mt5,
        "symbol_info",
        lambda _symbol: AfterSymbolInfo(),
    )

    result = client.get_candle_series_snapshot(
        "US500",
        "M1",
        1,
    )

    assert result.candles_available is True

    assert result.visible_before is False
    assert result.selected_before is False

    assert result.visible_after is False
    assert result.selected_after is True

    assert result.candle_count == 1

    client.shutdown()


def test_stale_history_retries_until_current(
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

    instrument = make_instrument(
        symbol="GBPUSD",
    )

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    tick_time = 1_787_247_600
    stale_rate_time = tick_time - 3600
    fresh_rate_time = tick_time - 30

    stale_rates = [
        {
            "time": stale_rate_time,
            "open": 1.36200,
            "high": 1.36210,
            "low": 1.36190,
            "close": 1.36205,
            "tick_volume": 10,
            "spread": 12,
            "real_volume": 0,
        },
    ]

    fresh_rates = [
        {
            "time": fresh_rate_time,
            "open": 1.36210,
            "high": 1.36230,
            "low": 1.36200,
            "close": 1.36220,
            "tick_volume": 20,
            "spread": 12,
            "real_volume": 0,
        },
    ]

    rate_calls = 0

    def fake_copy_rates(*_args):
        nonlocal rate_calls
        rate_calls += 1

        if rate_calls == 1:
            return stale_rates

        return fresh_rates

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        fake_copy_rates,
    )

    class Tick:
        time = tick_time

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: Tick(),
    )

    class SymbolAfter:
        visible = True
        select = True

    monkeypatch.setattr(
        mt5,
        "symbol_info",
        lambda _symbol: SymbolAfter(),
    )

    sleep_calls: list[float] = []

    monkeypatch.setattr(
        "execution_agent.app.mt5.client.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    result = client.get_candle_series_snapshot(
        "GBPUSD",
        "M1",
        1,
    )

    assert result.candles_available is True
    assert result.candle_count == 1
    assert result.unavailable_reason is None

    assert result.latest_candle_time == (
        datetime.fromtimestamp(
            fresh_rate_time,
            tz=UTC,
        )
    )

    assert rate_calls == 2

    assert sleep_calls == [
        CANDLE_HISTORY_SYNC_DELAY_SECONDS,
    ]

    client.shutdown()


def test_history_still_stale_after_retries_is_unavailable(
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

    instrument = make_instrument(
        symbol="GBPUSD",
    )

    monkeypatch.setattr(
        client,
        "get_instrument_snapshot",
        lambda _symbol: instrument,
    )

    tick_time = 1_787_247_600
    stale_rate_time = tick_time - 86400

    stale_rates = [
        {
            "time": stale_rate_time,
            "open": 1.36000,
            "high": 1.36010,
            "low": 1.35990,
            "close": 1.36005,
            "tick_volume": 10,
            "spread": 12,
            "real_volume": 0,
        },
    ]

    rate_calls = 0

    def fake_copy_rates(*_args):
        nonlocal rate_calls
        rate_calls += 1
        return stale_rates

    monkeypatch.setattr(
        mt5,
        "copy_rates_from_pos",
        fake_copy_rates,
    )

    class Tick:
        time = tick_time

    monkeypatch.setattr(
        mt5,
        "symbol_info_tick",
        lambda _symbol: Tick(),
    )

    class SymbolAfter:
        visible = True
        select = True

    monkeypatch.setattr(
        mt5,
        "symbol_info",
        lambda _symbol: SymbolAfter(),
    )

    sleep_calls: list[float] = []

    monkeypatch.setattr(
        "execution_agent.app.mt5.client.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    result = client.get_candle_series_snapshot(
        "GBPUSD",
        "M1",
        1,
    )

    assert result.candles_available is False
    assert result.candle_count == 0
    assert result.candles == ()

    assert result.oldest_candle_time is None
    assert result.latest_candle_time is None

    assert result.unavailable_reason == "history_stale"
    assert result.error_code is None
    assert result.error_message is None

    assert rate_calls == (CANDLE_HISTORY_SYNC_ATTEMPTS)

    assert sleep_calls == [CANDLE_HISTORY_SYNC_DELAY_SECONDS] * (CANDLE_HISTORY_SYNC_ATTEMPTS - 1)

    client.shutdown()
