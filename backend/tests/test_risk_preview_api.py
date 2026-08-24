from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

RISK_PREVIEW_PATH = "/api/v1/risk/preview"


def make_request_body() -> dict[str, object]:
    return {
        "limits": {
            "risk_per_trade_pct": "1",
            "daily_loss_limit_pct": "5",
            "max_open_positions": 5,
            "max_total_exposure_pct": "250",
        },
        "account": {
            "equity": "10000",
            "daily_loss_amount": "100",
            "open_position_count": 2,
            "total_exposure_amount": "5000",
        },
        "instrument": {
            "symbol": "XAUUSD",
            "broker_symbol": "XAUUSD",
            "tradable": True,
            "minimum_quantity": "0.01",
            "maximum_quantity": "100",
            "quantity_step": "0.01",
            "tick_size": "0.01",
            "tick_value_loss": "1",
            "contract_size": "100",
            "gross_exposure_per_quantity": "2400",
        },
        "trade": {
            "symbol": "XAUUSD",
            "broker_symbol": "XAUUSD",
            "side": "buy",
            "entry_price": "2400",
            "stop_loss_price": "2390",
            "take_profit_price": None,
        },
    }


def test_openapi_exposes_exactly_one_risk_preview_endpoint() -> None:
    openapi = app.openapi()

    risk_paths = {
        path: operations
        for path, operations in openapi["paths"].items()
        if path.startswith("/api/v1/risk")
    }

    assert set(risk_paths) == {
        RISK_PREVIEW_PATH,
    }

    assert set(
        risk_paths[RISK_PREVIEW_PATH]
    ) == {
        "post",
    }


def test_valid_risk_preview_returns_allow_and_safety_flags() -> None:
    response = client.post(
        RISK_PREVIEW_PATH,
        json=make_request_body(),
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["read_only"] is True
    assert payload["execution_enabled"] is False
    assert payload["live_trading_enabled"] is False

    evaluation = payload["evaluation"]

    assert evaluation["risk_check"]["decision"] == "allow"
    assert evaluation["risk_check"]["violations"] == []

    sizing = evaluation["position_sizing"]

    assert sizing["available"] is True

    assert (
        Decimal(
            str(
                sizing["normalized_quantity"]
            )
        )
        == Decimal("0.10")
    )

    assert (
        Decimal(
            str(
                sizing["estimated_loss_at_stop"]
            )
        )
        == Decimal("100")
    )


def test_untradable_instrument_returns_guardrail_block() -> None:
    request_body = make_request_body()

    request_body["instrument"]["tradable"] = False

    response = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    assert response.status_code == 200

    payload = response.json()
    evaluation = payload["evaluation"]

    assert evaluation["position_sizing"]["available"] is True
    assert evaluation["risk_check"]["decision"] == "block"

    codes = [
        violation["code"]
        for violation in evaluation[
            "risk_check"
        ][
            "violations"
        ]
    ]

    assert codes == [
        "instrument_not_tradable",
    ]

    assert payload["execution_enabled"] is False
    assert payload["live_trading_enabled"] is False


def test_missing_tick_value_returns_sizing_block() -> None:
    request_body = make_request_body()

    request_body["instrument"]["tick_value_loss"] = None

    response = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    assert response.status_code == 200

    payload = response.json()
    evaluation = payload["evaluation"]

    sizing = evaluation["position_sizing"]

    assert sizing["available"] is False
    assert (
        sizing["unavailable_reason"]
        == "missing_tick_value_loss"
    )

    assert evaluation["risk_check"]["decision"] == "block"

    codes = [
        violation["code"]
        for violation in evaluation[
            "risk_check"
        ][
            "violations"
        ]
    ]

    assert codes == [
        "missing_tick_value_loss",
    ]


def test_invalid_request_returns_validation_error() -> None:
    request_body = make_request_body()

    request_body["account"]["equity"] = "not-a-number"

    response = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    assert response.status_code == 422


def test_request_cannot_override_execution_safety_flags() -> None:
    request_body = make_request_body()

    request_body["execution_enabled"] = True
    request_body["live_trading_enabled"] = True

    response = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    assert response.status_code == 422


def test_get_is_not_supported_for_risk_preview() -> None:
    response = client.get(
        RISK_PREVIEW_PATH,
    )

    assert response.status_code == 405


def test_repeated_risk_previews_are_deterministic() -> None:
    request_body = make_request_body()

    first = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    second = client.post(
        RISK_PREVIEW_PATH,
        json=request_body,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json() == second.json()


def test_risk_preview_does_not_mutate_system_status() -> None:
    before_response = client.get(
        "/api/v1/system/status",
    )

    assert before_response.status_code == 200

    before = before_response.json()

    preview_response = client.post(
        RISK_PREVIEW_PATH,
        json=make_request_body(),
    )

    assert preview_response.status_code == 200

    after_response = client.get(
        "/api/v1/system/status",
    )

    assert after_response.status_code == 200

    after = after_response.json()

    assert after == before

    assert after["execution_enabled"] is False
    assert after["live_trading_enabled"] is False
