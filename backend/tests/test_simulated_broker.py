import pytest

from backend.app.brokers.adapters.base import (
    BrokerInstrumentNotFoundError,
    BrokerNotConnectedError,
    BrokerOperationNotSupported,
)
from backend.app.brokers.adapters.simulated import SimulatedBrokerAdapter
from backend.app.brokers.schemas import (
    AccountMode,
    AssetClass,
    BrokerType,
)


@pytest.fixture
def adapter() -> SimulatedBrokerAdapter:
    broker = SimulatedBrokerAdapter(
        "simulated-main",
    )
    broker.connect()
    return broker


def test_simulated_broker_connection_lifecycle() -> None:
    broker = SimulatedBrokerAdapter(
        "simulated-main",
    )

    initial_health = broker.health()

    assert initial_health.connected is False
    assert initial_health.read_only is True
    assert initial_health.broker_type == BrokerType.SIMULATED

    connected_health = broker.connect()

    assert connected_health.connected is True

    broker.disconnect()

    disconnected_health = broker.health()

    assert disconnected_health.connected is False


def test_simulated_broker_requires_connection() -> None:
    broker = SimulatedBrokerAdapter(
        "simulated-main",
    )

    with pytest.raises(
        BrokerNotConnectedError,
        match="Simulated broker is not connected",
    ):
        broker.get_account()

    with pytest.raises(BrokerNotConnectedError):
        broker.get_instruments()

    with pytest.raises(BrokerNotConnectedError):
        broker.get_positions()


def test_simulated_account(
    adapter: SimulatedBrokerAdapter,
) -> None:
    account = adapter.get_account()

    assert account.account_id == "SIM-DEMO-001"
    assert account.account_mode == AccountMode.DEMO

    assert account.currency == "USD"

    assert account.balance == 10_000.0
    assert account.equity == 10_000.0

    assert account.trade_allowed is False
    assert account.expert_trading_allowed is False


def test_simulated_instrument_catalog(
    adapter: SimulatedBrokerAdapter,
) -> None:
    instruments = adapter.get_instruments()

    assert len(instruments) == 6

    symbols = {
        instrument.symbol
        for instrument in instruments
    }

    assert symbols == {
        "EUR/USD",
        "GBP/USD",
        "XAU/USD",
        "WTI/USD",
        "NAS100/USD",
        "BTC/USD",
    }

    asset_classes = {
        instrument.asset_class
        for instrument in instruments
    }

    assert AssetClass.FOREX in asset_classes
    assert AssetClass.METAL in asset_classes
    assert AssetClass.ENERGY in asset_classes
    assert AssetClass.INDEX in asset_classes
    assert AssetClass.CRYPTO in asset_classes


def test_simulated_instrument_filtering(
    adapter: SimulatedBrokerAdapter,
) -> None:
    forex = adapter.get_instruments(
        asset_class=AssetClass.FOREX,
    )

    assert len(forex) == 2

    assert {
        instrument.symbol
        for instrument in forex
    } == {
        "EUR/USD",
        "GBP/USD",
    }

    gold = adapter.get_instruments(
        search="gold",
    )

    assert len(gold) == 1
    assert gold[0].symbol == "XAU/USD"

    bitcoin = adapter.get_instruments(
        search="BTCUSD",
    )

    assert len(bitcoin) == 1
    assert bitcoin[0].symbol == "BTC/USD"


def test_instrument_lookup_accepts_both_symbol_formats(
    adapter: SimulatedBrokerAdapter,
) -> None:
    normalized = adapter.get_instrument(
        "XAU/USD",
    )

    broker_native = adapter.get_instrument(
        "XAUUSD",
    )

    assert normalized == broker_native

    assert normalized.symbol == "XAU/USD"
    assert normalized.broker_symbol == "XAUUSD"


def test_unknown_simulated_instrument_is_rejected(
    adapter: SimulatedBrokerAdapter,
) -> None:
    with pytest.raises(
        BrokerInstrumentNotFoundError,
    ):
        adapter.get_instrument(
            "UNKNOWN",
        )


def test_simulated_quotes(
    adapter: SimulatedBrokerAdapter,
) -> None:
    gold = adapter.get_quote(
        "XAUUSD",
    )

    bitcoin = adapter.get_quote(
        "BTC/USD",
    )

    assert gold.symbol == "XAU/USD"
    assert gold.broker_symbol == "XAUUSD"

    assert gold.bid is not None
    assert gold.ask is not None
    assert gold.ask > gold.bid

    assert bitcoin.symbol == "BTC/USD"
    assert bitcoin.last == 68_456.0


def test_simulated_candles(
    adapter: SimulatedBrokerAdapter,
) -> None:
    candles = adapter.get_candles(
        "EURUSD",
        "M5",
        count=25,
    )

    assert len(candles) == 25

    assert all(
        candle.symbol == "EUR/USD"
        for candle in candles
    )

    assert all(
        candle.broker_symbol == "EURUSD"
        for candle in candles
    )

    assert all(
        candle.timeframe == "M5"
        for candle in candles
    )

    for candle in candles:
        assert candle.high >= candle.open
        assert candle.high >= candle.close

        assert candle.low <= candle.open
        assert candle.low <= candle.close


def test_candle_request_validation(
    adapter: SimulatedBrokerAdapter,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported timeframe",
    ):
        adapter.get_candles(
            "EURUSD",
            "INVALID",
        )

    with pytest.raises(
        ValueError,
        match="count must be at least 1",
    ):
        adapter.get_candles(
            "EURUSD",
            "M5",
            count=0,
        )

    with pytest.raises(
        ValueError,
        match="count cannot exceed 5000",
    ):
        adapter.get_candles(
            "EURUSD",
            "M5",
            count=5001,
        )


def test_simulated_positions_and_orders_are_empty(
    adapter: SimulatedBrokerAdapter,
) -> None:
    assert adapter.get_positions() == []
    assert adapter.get_open_orders() == []


def test_simulated_execution_remains_disabled(
    adapter: SimulatedBrokerAdapter,
) -> None:
    assert adapter.capabilities.read_only is True

    assert adapter.capabilities.market_orders is False
    assert adapter.capabilities.limit_orders is False
    assert adapter.capabilities.stop_orders is False

    with pytest.raises(
        BrokerOperationNotSupported,
    ):
        adapter.place_order(
            {
                "symbol": "EURUSD",
                "side": "buy",
                "quantity": 0.01,
            }
        )

    with pytest.raises(
        BrokerOperationNotSupported,
    ):
        adapter.modify_order(
            "ORDER-001",
            {
                "stop_loss": 1.09,
            },
        )

    with pytest.raises(
        BrokerOperationNotSupported,
    ):
        adapter.cancel_order(
            "ORDER-001",
        )

    with pytest.raises(
        BrokerOperationNotSupported,
    ):
        adapter.close_position(
            "POSITION-001",
        )