from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from execution_agent.app.core.config import get_agent_settings
from execution_agent.app.main import app
from execution_agent.app.mt5.client import (
    MT5AccountSnapshot,
    MT5CandleSeriesSnapshot,
    MT5CandleSnapshot,
    MT5Client,
    MT5ClientError,
    MT5InstrumentSnapshot,
    MT5QuoteSnapshot,
)


@pytest.fixture(autouse=True)
def reset_agent_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    monkeypatch.setenv(
        "TCC_AGENT_MT5_ENABLED",
        "false",
    )

    monkeypatch.setenv(
        "TCC_AGENT_EXECUTION_ENABLED",
        "false",
    )

    monkeypatch.setenv(
        "TCC_AGENT_LIVE_TRADING_ENABLED",
        "false",
    )

    monkeypatch.delenv(
        "TCC_AGENT_MT5_TERMINAL_PATH",
        raising=False,
    )

    get_agent_settings.cache_clear()

    try:
        yield
    finally:
        get_agent_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def configure_mt5(
    monkeypatch: pytest.MonkeyPatch,
    *,
    mt5_enabled: bool = True,
    execution_enabled: bool = False,
    live_trading_enabled: bool = False,
) -> None:
    monkeypatch.setenv(
        "TCC_AGENT_MT5_ENABLED",
        str(mt5_enabled).lower(),
    )
    monkeypatch.setenv(
        "TCC_AGENT_EXECUTION_ENABLED",
        str(execution_enabled).lower(),
    )
    monkeypatch.setenv(
        "TCC_AGENT_LIVE_TRADING_ENABLED",
        str(live_trading_enabled).lower(),
    )
    monkeypatch.setenv(
        "TCC_AGENT_MT5_TERMINAL_PATH",
        "C:\\Fake\\terminal64.exe",
    )

    get_agent_settings.cache_clear()


def make_account(
    *,
    trade_mode: str = "demo",
) -> MT5AccountSnapshot:
    return MT5AccountSnapshot(
        login=1237959,
        masked_login="***7959",
        trade_mode=trade_mode,
        server="PXBTTrading-1",
        company="PXBT Trading Ltd",
        currency="USD",
        leverage=100,
        trade_allowed=True,
        trade_expert=True,
    )


def make_instruments() -> tuple[
    MT5InstrumentSnapshot,
    ...,
]:
    return (
        MT5InstrumentSnapshot(
            broker_symbol="BTCUSD",
            broker_path="RefSymbols\\BTCUSD",
            broker_group="RefSymbols",
            description="Conversion only",
            currency_base="BTC",
            currency_profit="USD",
            currency_margin="USD",
            digits=2,
            point=0.01,
            contract_size=1.0,
            volume_min=0.0001,
            volume_max=100000000000.0,
            volume_step=0.0001,
            trade_mode="disabled",
            trade_calc_mode=0,
            order_mode=127,
            new_order_allowed=False,
            reference_only=True,
            visible=True,
            selected=True,
        ),
        MT5InstrumentSnapshot(
            broker_symbol="EURUSD",
            broker_path="Forex\\Major\\EURUSD",
            broker_group="Forex",
            description="Euro vs US Dollar",
            currency_base="EUR",
            currency_profit="USD",
            currency_margin="EUR",
            digits=5,
            point=0.00001,
            contract_size=100000.0,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            trade_mode="full",
            trade_calc_mode=0,
            order_mode=127,
            new_order_allowed=True,
            reference_only=False,
            visible=True,
            selected=True,
        ),
    )


def test_agent_health(
    client: TestClient,
) -> None:
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["app"] == (
        "Trade Command Center MT5 Agent"
    )

    assert payload["environment"] == "development"

    assert "timestamp" in payload


def test_agent_status_is_safe_by_default(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/agent/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["agent"] == "online"

    assert payload["mt5_enabled"] is False
    assert payload["mt5_connected"] is False

    assert payload["execution_enabled"] is False
    assert payload["live_trading_enabled"] is False


def test_mt5_status_is_safe_by_default(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/mt5/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["enabled"] is False

    assert payload["terminal_available"] is False
    assert payload["initialized"] is False
    assert payload["connected"] is False
    assert payload["account_logged_in"] is False

    assert payload["execution_enabled"] is False
    assert payload["live_trading_enabled"] is False

    assert payload["message"] == (
        "MT5 integration disabled"
    )


def test_instruments_reject_mt5_disabled(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 integration is disabled"
    )


def test_instruments_reject_execution_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        execution_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only instrument discovery requires "
        "execution_enabled=false"
    )


def test_instruments_reject_live_trading_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        live_trading_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only instrument discovery requires "
        "live_trading_enabled=false"
    )


def test_instruments_reject_non_demo_account(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(
            trade_mode="real",
        ),
    )

    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Phase 4 instrument discovery requires "
        "a demo MT5 account; detected real"
    )


def test_instruments_reports_mt5_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    def failing_initialize(
        _self: object,
    ) -> None:
        raise MT5ClientError(
            "simulated MT5 failure"
        )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        failing_initialize,
    )

    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 instrument discovery failed: "
        "simulated MT5 failure"
    )


def test_instruments_returns_demo_catalogue(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(),
    )
    monkeypatch.setattr(
        MT5Client,
        "get_instrument_snapshots",
        lambda _self: make_instruments(),
    )

    response = client.get(
        "/api/v1/mt5/instruments"
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 2

    btcusd = payload[0]

    assert btcusd["broker_symbol"] == "BTCUSD"
    assert btcusd["broker_group"] == "RefSymbols"
    assert btcusd["trade_mode"] == "disabled"
    assert btcusd["new_order_allowed"] is False
    assert btcusd["reference_only"] is True

    eurusd = payload[1]

    assert eurusd["broker_symbol"] == "EURUSD"
    assert eurusd["broker_group"] == "Forex"
    assert eurusd["trade_mode"] == "full"
    assert eurusd["new_order_allowed"] is True
    assert eurusd["reference_only"] is False

    assert eurusd["contract_size"] == 100000.0
    assert eurusd["volume_min"] == 0.01
    assert eurusd["volume_max"] == 100.0
    assert eurusd["volume_step"] == 0.01


def test_agent_openapi_has_no_execution_routes(
    client: TestClient,
) -> None:
    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    forbidden_fragments = {
        "place-order",
        "place_order",
        "execute",
        "/buy",
        "/sell",
        "close-position",
        "close_position",
        "modify-order",
        "cancel-order",
    }

    for path in paths:
        assert not any(
            fragment in path.lower()
            for fragment in forbidden_fragments
        )


def test_expected_agent_routes_exist(
    client: TestClient,
) -> None:
    response = client.get(
        "/openapi.json"
    )

    paths = response.json()["paths"]

    assert "/health" in paths

    assert (
        "/api/v1/agent/status"
        in paths
    )

    assert (
        "/api/v1/mt5/status"
        in paths
    )

    assert (
        "/api/v1/mt5/instruments"
        in paths
    )



def install_demo_catalogue_mocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(),
    )
    monkeypatch.setattr(
        MT5Client,
        "get_instrument_snapshots",
        lambda _self: make_instruments(),
    )


def test_instruments_filter_by_broker_group(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "broker_group": "forex",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["broker_symbol"] == "EURUSD"
    assert payload[0]["broker_group"] == "Forex"


def test_instruments_filter_by_trade_mode(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "trade_mode": "DISABLED",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["broker_symbol"] == "BTCUSD"
    assert payload[0]["trade_mode"] == "disabled"


def test_instruments_filter_by_new_order_allowed(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "new_order_allowed": "false",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["broker_symbol"] == "BTCUSD"
    assert payload[0]["new_order_allowed"] is False


def test_instruments_filter_by_reference_only(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "reference_only": "true",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["broker_symbol"] == "BTCUSD"
    assert payload[0]["reference_only"] is True


def test_instruments_combined_filters(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "broker_group": "Forex",
            "trade_mode": "full",
            "new_order_allowed": "true",
            "reference_only": "false",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert len(payload) == 1
    assert payload[0]["broker_symbol"] == "EURUSD"


def test_instruments_combined_filters_can_return_empty(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_demo_catalogue_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/instruments",
        params={
            "broker_group": "Forex",
            "reference_only": "true",
        },
    )

    assert response.status_code == 200
    assert response.json() == []

def make_available_quote(
    *,
    broker_symbol: str = "EURUSD",
    trade_mode: str = "full",
    new_order_allowed: bool = True,
    reference_only: bool = False,
) -> MT5QuoteSnapshot:
    return MT5QuoteSnapshot(
        broker_symbol=broker_symbol,
        broker_path=f"Test\\{broker_symbol}",
        broker_group=(
            "RefSymbols"
            if reference_only
            else "Forex"
        ),
        digits=5,
        point=0.00001,
        trade_mode=trade_mode,
        new_order_allowed=new_order_allowed,
        reference_only=reference_only,
        visible=True,
        selected=True,
        quote_available=True,
        tick_time=None,
        tick_time_msc=1786816680119,
        bid=1.15695,
        ask=1.15712,
        last=0.0,
        volume=0,
        volume_real=0.0,
        flags=6,
        spread=0.00017,
        spread_points=17.0,
        unavailable_reason=None,
        error_code=None,
        error_message=None,
    )


def make_unavailable_quote(
    *,
    broker_symbol: str = "CRUDE",
) -> MT5QuoteSnapshot:
    return MT5QuoteSnapshot(
        broker_symbol=broker_symbol,
        broker_path=f"Commodities\\{broker_symbol}",
        broker_group="Commodities",
        digits=3,
        point=0.001,
        trade_mode="full",
        new_order_allowed=True,
        reference_only=False,
        visible=False,
        selected=False,
        quote_available=False,
        tick_time=None,
        tick_time_msc=None,
        bid=None,
        ask=None,
        last=None,
        volume=None,
        volume_real=None,
        flags=None,
        spread=None,
        spread_points=None,
        unavailable_reason="symbol_not_selected",
        error_code=None,
        error_message=None,
    )


def install_quote_mocks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    account_mode: str = "demo",
    quote: MT5QuoteSnapshot | None = None,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(
            trade_mode=account_mode,
        ),
    )
    monkeypatch.setattr(
        MT5Client,
        "get_instrument_snapshots",
        lambda _self: make_instruments(),
    )

    if quote is not None:
        monkeypatch.setattr(
            MT5Client,
            "get_quote_snapshot",
            lambda _self, _symbol: quote,
        )


def test_quote_rejects_mt5_disabled(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 integration is disabled"
    )


def test_quote_rejects_execution_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        execution_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only quote access requires "
        "execution_enabled=false"
    )


def test_quote_rejects_live_trading_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        live_trading_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only quote access requires "
        "live_trading_enabled=false"
    )


def test_quote_rejects_non_demo_account(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_quote_mocks(
        monkeypatch,
        account_mode="real",
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Phase 4 quote access requires "
        "a demo MT5 account; detected real"
    )


def test_quote_rejects_unknown_symbol(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_quote_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "DOESNOTEXIST",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "MT5 broker symbol not found: DOESNOTEXIST"
    )


def test_quote_returns_available_tick(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    quote = make_available_quote()

    install_quote_mocks(
        monkeypatch,
        quote=quote,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["broker_symbol"] == "EURUSD"
    assert payload["quote_available"] is True
    assert payload["trade_mode"] == "full"
    assert payload["new_order_allowed"] is True
    assert payload["reference_only"] is False

    assert payload["bid"] == 1.15695
    assert payload["ask"] == 1.15712

    assert payload["spread_points"] == 17.0
    assert payload["unavailable_reason"] is None


def test_quote_returns_unselected_symbol_state(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    instruments = (
        MT5InstrumentSnapshot(
            broker_symbol="CRUDE",
            broker_path="Commodities\\CRUDE",
            broker_group="Commodities",
            description="WTI Crude Oil",
            currency_base="USD",
            currency_profit="USD",
            currency_margin="USD",
            digits=3,
            point=0.001,
            contract_size=1000.0,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            trade_mode="full",
            trade_calc_mode=4,
            order_mode=127,
            new_order_allowed=True,
            reference_only=False,
            visible=False,
            selected=False,
        ),
    )

    quote = make_unavailable_quote()

    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(),
    )
    monkeypatch.setattr(
        MT5Client,
        "get_instrument_snapshots",
        lambda _self: instruments,
    )
    monkeypatch.setattr(
        MT5Client,
        "get_quote_snapshot",
        lambda _self, _symbol: quote,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "CRUDE",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["broker_symbol"] == "CRUDE"
    assert payload["quote_available"] is False
    assert payload["selected"] is False

    assert payload["unavailable_reason"] == (
        "symbol_not_selected"
    )

    assert payload["bid"] is None
    assert payload["ask"] is None


def test_reference_symbol_quote_does_not_imply_tradability(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    quote = make_available_quote(
        broker_symbol="BTCUSD",
        trade_mode="disabled",
        new_order_allowed=False,
        reference_only=True,
    )

    install_quote_mocks(
        monkeypatch,
        quote=quote,
    )

    response = client.get(
        "/api/v1/mt5/quote",
        params={
            "broker_symbol": "BTCUSD",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["broker_symbol"] == "BTCUSD"

    assert payload["quote_available"] is True
    assert payload["trade_mode"] == "disabled"
    assert payload["new_order_allowed"] is False
    assert payload["reference_only"] is True


def make_candle_series(
    *,
    broker_symbol: str = "EURUSD",
    timeframe: str = "M1",
    selected_before: bool = True,
    selected_after: bool = True,
    visible_before: bool = True,
    visible_after: bool = True,
    trade_mode: str = "full",
    new_order_allowed: bool = True,
    reference_only: bool = False,
) -> MT5CandleSeriesSnapshot:
    bar_time = datetime(
        2026,
        8,
        18,
        19,
        15,
        tzinfo=UTC,
    )

    candle = MT5CandleSnapshot(
        bar_time=bar_time,
        open=1.15767,
        high=1.15773,
        low=1.15767,
        close=1.15771,
        tick_volume=22,
        spread=1,
        real_volume=0,
    )

    if reference_only:
        broker_path = (
            f"RefSymbols\\{broker_symbol}"
        )
        broker_group = "RefSymbols"
        digits = 1
        point = 0.1
    else:
        broker_path = (
            f"Forex\\Major\\{broker_symbol}"
        )
        broker_group = "Forex"
        digits = 5
        point = 0.00001

    return MT5CandleSeriesSnapshot(
        broker_symbol=broker_symbol,
        broker_path=broker_path,
        broker_group=broker_group,
        digits=digits,
        point=point,
        trade_mode=trade_mode,
        new_order_allowed=new_order_allowed,
        reference_only=reference_only,
        visible_before=visible_before,
        selected_before=selected_before,
        visible_after=visible_after,
        selected_after=selected_after,
        timeframe=timeframe,
        count_requested=1,
        candles_available=True,
        candle_count=1,
        oldest_candle_time=bar_time,
        latest_candle_time=bar_time,
        candles=(candle,),
        unavailable_reason=None,
        error_code=None,
        error_message=None,
    )


def install_candle_mocks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    account_mode: str = "demo",
    series: MT5CandleSeriesSnapshot | None = None,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    if series is None:
        series = make_candle_series()

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )

    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )

    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: make_account(
            trade_mode=account_mode,
        ),
    )

    monkeypatch.setattr(
        MT5Client,
        "get_instrument_snapshots",
        lambda _self: make_instruments(),
    )

    monkeypatch.setattr(
        MT5Client,
        "get_candle_series_snapshot",
        lambda _self, _symbol, _timeframe, _count: series,
    )


def test_candles_reject_mt5_disabled(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 integration is disabled"
    )


def test_candles_reject_execution_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        execution_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only candle access requires "
        "execution_enabled=false"
    )


def test_candles_reject_live_trading_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        live_trading_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only candle access requires "
        "live_trading_enabled=false"
    )


def test_candles_reject_non_demo_account(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_candle_mocks(
        monkeypatch,
        account_mode="real",
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Phase 4 candle access requires "
        "a demo MT5 account; detected real"
    )


def test_candles_reject_unknown_symbol(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_candle_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "DOESNOTEXIST",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "MT5 broker symbol not found: "
        "DOESNOTEXIST"
    )


def test_candles_reject_unsupported_timeframe(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
            "timeframe": "M2",
        },
    )

    assert response.status_code == 422

    assert (
        "Unsupported MT5 timeframe: M2"
        in response.json()["detail"]
    )


def test_candles_reject_count_below_minimum(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
            "count": 0,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "MT5 candle count must be between "
        "1 and 1000"
    )


def test_candles_reject_count_above_maximum(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
            "count": 1001,
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "MT5 candle count must be between "
        "1 and 1000"
    )


def test_candles_return_ohlc_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    series = make_candle_series(
        timeframe="M5",
    )

    install_candle_mocks(
        monkeypatch,
        series=series,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
            "timeframe": "m5",
            "count": 1,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["broker_symbol"] == "EURUSD"
    assert payload["timeframe"] == "M5"

    assert payload["count_requested"] == 1
    assert payload["candle_count"] == 1

    assert payload["candles_available"] is True

    assert payload["trade_mode"] == "full"
    assert payload["new_order_allowed"] is True
    assert payload["reference_only"] is False

    assert len(payload["candles"]) == 1

    candle = payload["candles"][0]

    assert candle["open"] == 1.15767
    assert candle["high"] == 1.15773
    assert candle["low"] == 1.15767
    assert candle["close"] == 1.15771

    assert candle["tick_volume"] == 22
    assert candle["spread"] == 1
    assert candle["real_volume"] == 0

    assert payload["unavailable_reason"] is None
    assert payload["error_code"] is None
    assert payload["error_message"] is None


def test_candles_preserve_before_after_selection_state(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    series = make_candle_series(
        selected_before=False,
        selected_after=True,
        visible_before=False,
        visible_after=False,
    )

    install_candle_mocks(
        monkeypatch,
        series=series,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "EURUSD",
            "count": 1,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["selected_before"] is False
    assert payload["selected_after"] is True

    assert payload["visible_before"] is False
    assert payload["visible_after"] is False


def test_reference_symbol_can_return_candles(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    series = make_candle_series(
        broker_symbol="BTCUSD",
        trade_mode="disabled",
        new_order_allowed=False,
        reference_only=True,
    )

    install_candle_mocks(
        monkeypatch,
        series=series,
    )

    response = client.get(
        "/api/v1/mt5/candles",
        params={
            "broker_symbol": "BTCUSD",
            "count": 1,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["broker_symbol"] == "BTCUSD"

    assert payload["candles_available"] is True

    assert payload["trade_mode"] == "disabled"
    assert payload["new_order_allowed"] is False
    assert payload["reference_only"] is True



def make_detailed_account(
    *,
    trade_mode: str = "demo",
) -> MT5AccountSnapshot:
    return MT5AccountSnapshot(
        login=1237959,
        masked_login="***7959",
        trade_mode=trade_mode,
        server="PXBTTrading-1",
        company="PXBT Trading Ltd",
        currency="USD",
        leverage=100,
        trade_allowed=True,
        trade_expert=True,
        currency_digits=2,
        limit_orders=0,
        fifo_close=False,
        margin_mode=2,
        margin_so_mode=0,
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
    )


def install_account_mocks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    account: MT5AccountSnapshot | None = None,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    if account is None:
        account = make_detailed_account()

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )

    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )

    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        lambda _self: account,
    )


def test_account_endpoint_rejects_mt5_disabled(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 integration is disabled"
    )


def test_account_endpoint_rejects_execution_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        execution_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only account access requires "
        "execution_enabled=false"
    )


def test_account_endpoint_rejects_live_trading_enabled(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
        live_trading_enabled=True,
    )

    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Read-only account access requires "
        "live_trading_enabled=false"
    )


def test_account_endpoint_rejects_non_demo_account(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    account = make_detailed_account(
        trade_mode="real",
    )

    install_account_mocks(
        monkeypatch,
        account=account,
    )

    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Phase 4 account access requires "
        "a demo MT5 account; detected real"
    )


def test_account_endpoint_returns_detailed_state_without_full_login(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_account_mocks(
        monkeypatch,
    )

    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["masked_login"] == "***7959"

    assert "login" not in payload

    assert payload["trade_mode"] == "demo"
    assert payload["server"] == "PXBTTrading-1"
    assert payload["company"] == "PXBT Trading Ltd"
    assert payload["currency"] == "USD"
    assert payload["currency_digits"] == 2

    assert payload["leverage"] == 100
    assert payload["limit_orders"] == 0

    assert payload["trade_allowed"] is True
    assert payload["trade_expert"] is True
    assert payload["fifo_close"] is False

    assert payload["margin_mode"] == 2
    assert payload["margin_so_mode"] == 0

    assert payload["balance"] == 10000.0
    assert payload["credit"] == 0.0
    assert payload["profit"] == 125.50
    assert payload["equity"] == 10125.50

    assert payload["margin"] == 250.0
    assert payload["margin_free"] == 9875.50
    assert payload["margin_level"] == 4050.2

    assert payload["margin_so_call"] == 100.0
    assert payload["margin_so_so"] == 50.0

    assert payload["margin_initial"] == 0.0
    assert payload["margin_maintenance"] == 0.0

    assert payload["assets"] == 0.0
    assert payload["liabilities"] == 0.0
    assert payload["commission_blocked"] == 0.0


def test_account_endpoint_maps_mt5_client_error_to_503(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_mt5(
        monkeypatch,
    )

    monkeypatch.setattr(
        MT5Client,
        "initialize",
        lambda _self: None,
    )

    monkeypatch.setattr(
        MT5Client,
        "shutdown",
        lambda _self: None,
    )

    def raise_account_error(
        _self,
    ):
        raise MT5ClientError(
            "account unavailable"
        )

    monkeypatch.setattr(
        MT5Client,
        "get_account_snapshot",
        raise_account_error,
    )

    response = client.get(
        "/api/v1/mt5/account"
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "MT5 account retrieval failed: "
        "account unavailable"
    )
