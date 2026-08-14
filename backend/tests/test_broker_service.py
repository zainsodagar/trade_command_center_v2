import pytest

from backend.app.brokers.adapters.base import BrokerNotConnectedError
from backend.app.brokers.manager import (
    BrokerAlreadyRegisteredError,
    BrokerNotRegisteredError,
)
from backend.app.brokers.schemas import (
    AccountMode,
    AssetClass,
    BrokerType,
)
from backend.app.brokers.service import BrokerService


@pytest.fixture
def service() -> BrokerService:
    return BrokerService()


def test_create_simulated_connection(
    service: BrokerService,
) -> None:
    health = service.create_simulated_connection(
        "sim-main",
    )

    assert health.connected is True
    assert health.read_only is True
    assert health.broker_type == BrokerType.SIMULATED

    assert service.connection_count() == 1
    assert service.connection_ids() == [
        "sim-main"
    ]


def test_create_disconnected_simulated_connection(
    service: BrokerService,
) -> None:
    health = service.create_simulated_connection(
        "sim-main",
        connect=False,
    )

    assert health.connected is False

    with pytest.raises(
        BrokerNotConnectedError,
    ):
        service.get_account(
            "sim-main",
        )


def test_duplicate_connection_is_rejected(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    with pytest.raises(
        BrokerAlreadyRegisteredError,
        match="already registered",
    ):
        service.create_simulated_connection(
            "sim-main",
        )


def test_service_can_replace_connection(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    replacement_health = (
        service.create_simulated_connection(
            "sim-main",
            replace=True,
        )
    )

    assert replacement_health.connected is True
    assert service.connection_count() == 1


def test_service_account_and_capabilities(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    account = service.get_account(
        "sim-main",
    )

    capabilities = service.get_capabilities(
        "sim-main",
    )

    assert account.account_id == "SIM-DEMO-001"
    assert account.account_mode == AccountMode.DEMO

    assert capabilities.read_only is True
    assert capabilities.supports_cfds is True

    assert capabilities.market_orders is False
    assert capabilities.limit_orders is False


def test_service_instruments_and_filtering(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    all_instruments = service.get_instruments(
        "sim-main",
    )

    forex = service.get_instruments(
        "sim-main",
        asset_class=AssetClass.FOREX,
    )

    gold = service.get_instrument(
        "sim-main",
        "XAUUSD",
    )

    assert len(all_instruments) == 6
    assert len(forex) == 2

    assert {
        instrument.symbol
        for instrument in forex
    } == {
        "EUR/USD",
        "GBP/USD",
    }

    assert gold.symbol == "XAU/USD"
    assert gold.broker_symbol == "XAUUSD"


def test_service_quotes_and_candles(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    gold = service.get_quote(
        "sim-main",
        "XAUUSD",
    )

    candles = service.get_candles(
        "sim-main",
        "BTCUSD",
        "H1",
        count=10,
    )

    assert gold.symbol == "XAU/USD"
    assert gold.last == 2412.425

    assert len(candles) == 10

    assert all(
        candle.symbol == "BTC/USD"
        for candle in candles
    )

    assert all(
        candle.timeframe == "H1"
        for candle in candles
    )


def test_service_connection_lifecycle(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    disconnected = service.disconnect(
        "sim-main",
    )

    assert disconnected.connected is False

    connected = service.connect(
        "sim-main",
    )

    assert connected.connected is True

    all_health = service.get_all_health()

    assert len(all_health) == 1
    assert all_health[0].connected is True


def test_service_positions_orders_and_removal(
    service: BrokerService,
) -> None:
    service.create_simulated_connection(
        "sim-main",
    )

    assert service.get_positions(
        "sim-main",
    ) == []

    assert service.get_open_orders(
        "sim-main",
    ) == []

    removed_health = service.remove_connection(
        "sim-main",
    )

    assert removed_health.connected is False
    assert service.connection_count() == 0

    with pytest.raises(
        BrokerNotRegisteredError,
    ):
        service.get_health(
            "sim-main",
        )