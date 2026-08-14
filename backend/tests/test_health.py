from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "ok"
    assert payload["app"] == "Trade Command Center"
    assert payload["environment"] == "development"
    assert "timestamp" in payload


def test_system_status_is_safe_by_default() -> None:
    response = client.get("/api/v1/system/status")

    assert response.status_code == 200

    payload = response.json()

    assert payload["backend"] == "online"
    assert payload["broker_connections"] == 0
    assert payload["execution_enabled"] is False
    assert payload["live_trading_enabled"] is False
