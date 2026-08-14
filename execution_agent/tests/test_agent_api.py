from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from execution_agent.app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


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