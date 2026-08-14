from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.brokers.api import get_broker_service
from backend.app.main import app


@pytest.fixture(autouse=True)
def reset_broker_service() -> Generator[None, None, None]:
    service = get_broker_service()

    service.manager.clear()

    try:
        yield
    finally:
        service.manager.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_broker_list_starts_empty(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/brokers"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_create_simulated_broker_updates_system_status(
    client: TestClient,
) -> None:
    before = client.get(
        "/api/v1/system/status"
    )

    assert before.status_code == 200
    assert before.json()["broker_connections"] == 0

    created = client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
            "connect": True,
        },
    )

    assert created.status_code == 201

    payload = created.json()

    assert payload["connection_id"] == "sim-main"
    assert payload["broker_type"] == "simulated"
    assert payload["connected"] is True
    assert payload["read_only"] is True

    after = client.get(
        "/api/v1/system/status"
    )

    assert after.status_code == 200
    assert after.json()["broker_connections"] == 1

    brokers = client.get(
        "/api/v1/brokers"
    )

    assert brokers.status_code == 200
    assert len(brokers.json()) == 1


def test_duplicate_simulated_connection_returns_conflict(
    client: TestClient,
) -> None:
    first = client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    assert duplicate.status_code == 409

    assert "already registered" in (
        duplicate.json()["detail"]
    )


def test_disconnected_broker_can_be_connected(
    client: TestClient,
) -> None:
    created = client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
            "connect": False,
        },
    )

    assert created.status_code == 201
    assert created.json()["connected"] is False

    account_before = client.get(
        "/api/v1/brokers/sim-main/account"
    )

    assert account_before.status_code == 409

    connected = client.post(
        "/api/v1/brokers/sim-main/connect"
    )

    assert connected.status_code == 200
    assert connected.json()["connected"] is True

    account_after = client.get(
        "/api/v1/brokers/sim-main/account"
    )

    assert account_after.status_code == 200
    assert account_after.json()["account_id"] == "SIM-DEMO-001"


def test_account_and_capabilities_endpoints(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    account = client.get(
        "/api/v1/brokers/sim-main/account"
    )

    assert account.status_code == 200

    account_payload = account.json()

    assert account_payload["account_id"] == "SIM-DEMO-001"
    assert account_payload["account_mode"] == "demo"
    assert account_payload["currency"] == "USD"
    assert account_payload["trade_allowed"] is False

    capabilities = client.get(
        "/api/v1/brokers/sim-main/capabilities"
    )

    assert capabilities.status_code == 200

    capability_payload = capabilities.json()

    assert capability_payload["read_only"] is True
    assert capability_payload["supports_cfds"] is True

    assert capability_payload["market_orders"] is False
    assert capability_payload["limit_orders"] is False
    assert capability_payload["stop_orders"] is False


def test_instrument_discovery_and_filtering(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    all_instruments = client.get(
        "/api/v1/brokers/sim-main/instruments"
    )

    assert all_instruments.status_code == 200
    assert len(all_instruments.json()) == 6

    forex = client.get(
        "/api/v1/brokers/sim-main/instruments",
        params={
            "asset_class": "forex",
        },
    )

    assert forex.status_code == 200
    assert len(forex.json()) == 2

    assert {
        instrument["symbol"]
        for instrument in forex.json()
    } == {
        "EUR/USD",
        "GBP/USD",
    }

    gold_search = client.get(
        "/api/v1/brokers/sim-main/instruments",
        params={
            "search": "gold",
        },
    )

    assert gold_search.status_code == 200
    assert len(gold_search.json()) == 1
    assert gold_search.json()[0]["symbol"] == "XAU/USD"

    instrument = client.get(
        "/api/v1/brokers/sim-main/instrument",
        params={
            "symbol": "XAUUSD",
        },
    )

    assert instrument.status_code == 200
    assert instrument.json()["symbol"] == "XAU/USD"
    assert instrument.json()["broker_symbol"] == "XAUUSD"


def test_quote_and_candle_endpoints(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    quote = client.get(
        "/api/v1/brokers/sim-main/quote",
        params={
            "symbol": "XAUUSD",
        },
    )

    assert quote.status_code == 200

    quote_payload = quote.json()

    assert quote_payload["symbol"] == "XAU/USD"
    assert quote_payload["broker_symbol"] == "XAUUSD"
    assert quote_payload["last"] == 2412.425

    candles = client.get(
        "/api/v1/brokers/sim-main/candles",
        params={
            "symbol": "BTCUSD",
            "timeframe": "H1",
            "count": 5,
        },
    )

    assert candles.status_code == 200
    assert len(candles.json()) == 5

    assert all(
        candle["symbol"] == "BTC/USD"
        for candle in candles.json()
    )

    assert all(
        candle["timeframe"] == "H1"
        for candle in candles.json()
    )


def test_broker_api_error_handling(
    client: TestClient,
) -> None:
    missing = client.get(
        "/api/v1/brokers/missing/health"
    )

    assert missing.status_code == 404

    created = client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    assert created.status_code == 201

    unknown_instrument = client.get(
        "/api/v1/brokers/sim-main/quote",
        params={
            "symbol": "UNKNOWN",
        },
    )

    assert unknown_instrument.status_code == 404

    invalid_timeframe = client.get(
        "/api/v1/brokers/sim-main/candles",
        params={
            "symbol": "EURUSD",
            "timeframe": "INVALID",
            "count": 5,
        },
    )

    assert invalid_timeframe.status_code == 422

    invalid_count = client.get(
        "/api/v1/brokers/sim-main/candles",
        params={
            "symbol": "EURUSD",
            "timeframe": "M5",
            "count": 0,
        },
    )

    assert invalid_count.status_code == 422


def test_positions_and_orders_are_read_only(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    positions = client.get(
        "/api/v1/brokers/sim-main/positions"
    )

    orders = client.get(
        "/api/v1/brokers/sim-main/orders"
    )

    assert positions.status_code == 200
    assert positions.json() == []

    assert orders.status_code == 200
    assert orders.json() == []


def test_disconnect_remove_and_missing_connection(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/brokers/simulated",
        json={
            "connection_id": "sim-main",
        },
    )

    disconnected = client.post(
        "/api/v1/brokers/sim-main/disconnect"
    )

    assert disconnected.status_code == 200
    assert disconnected.json()["connected"] is False

    health = client.get(
        "/api/v1/brokers/sim-main/health"
    )

    assert health.status_code == 200
    assert health.json()["connected"] is False

    removed = client.delete(
        "/api/v1/brokers/sim-main"
    )

    assert removed.status_code == 200
    assert removed.json()["connected"] is False

    missing = client.get(
        "/api/v1/brokers/sim-main/health"
    )

    assert missing.status_code == 404

    system_status = client.get(
        "/api/v1/system/status"
    )

    assert system_status.json()["broker_connections"] == 0


def test_openapi_has_no_execution_endpoints(
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
    }

    for path in paths:
        assert not any(
            fragment in path.lower()
            for fragment in forbidden_fragments
        )