from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.app.risk.position_sizing import (
    PositionSizingResult,
    PositionSizingUnavailableReason,
    calculate_position_size,
)
from backend.app.risk.schemas import (
    AccountRiskState,
    RiskEvaluationInput,
    RiskInstrumentSpec,
    RiskLimits,
    TradeRiskCandidate,
    TradeSide,
)


def make_evaluation(
    *,
    side: TradeSide = TradeSide.BUY,
    equity: Decimal = Decimal("10000"),
    risk_per_trade_pct: Decimal = Decimal("1"),
    entry_price: Decimal = Decimal("2400"),
    stop_loss_price: Decimal = Decimal("2390"),
    minimum_quantity: Decimal = Decimal("0.01"),
    maximum_quantity: Decimal = Decimal("100"),
    quantity_step: Decimal = Decimal("0.01"),
    tick_size: Decimal = Decimal("0.01"),
    tick_value_loss: Decimal | None = Decimal("1"),
    contract_size: Decimal | None = Decimal("100"),
) -> RiskEvaluationInput:
    return RiskEvaluationInput(
        limits=RiskLimits(
            risk_per_trade_pct=risk_per_trade_pct,
            daily_loss_limit_pct=Decimal("5"),
            max_open_positions=5,
            max_total_exposure_pct=Decimal("250"),
        ),
        account=AccountRiskState(
            equity=equity,
            daily_loss_amount=Decimal("0"),
            open_position_count=0,
            total_exposure_amount=Decimal("0"),
        ),
        instrument=RiskInstrumentSpec(
            symbol="XAUUSD",
            broker_symbol="XAUUSD",
            tradable=True,
            minimum_quantity=minimum_quantity,
            maximum_quantity=maximum_quantity,
            quantity_step=quantity_step,
            tick_size=tick_size,
            tick_value_loss=tick_value_loss,
            contract_size=contract_size,
        ),
        trade=TradeRiskCandidate(
            symbol="XAUUSD",
            broker_symbol="XAUUSD",
            side=side,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
        ),
    )


def test_buy_position_size_exact_known_calculation() -> None:
    result = calculate_position_size(make_evaluation())

    assert result.available is True
    assert result.unavailable_reason is None

    assert result.risk_budget_amount == Decimal("100")
    assert result.stop_distance == Decimal("10")
    assert result.stop_ticks == Decimal("1000")
    assert result.loss_per_quantity == Decimal("1000")

    assert result.raw_quantity == Decimal("0.10")
    assert result.normalized_quantity == Decimal("0.10")

    assert result.estimated_loss_at_stop == Decimal("100")
    assert result.capped_by_maximum is False


def test_sell_position_size_uses_same_absolute_stop_distance() -> None:
    result = calculate_position_size(
        make_evaluation(
            side=TradeSide.SELL,
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2410"),
        )
    )

    assert result.available is True
    assert result.stop_distance == Decimal("10")
    assert result.stop_ticks == Decimal("1000")
    assert result.normalized_quantity == Decimal("0.10")
    assert result.estimated_loss_at_stop == Decimal("100")


def test_quantity_is_rounded_down_to_broker_step() -> None:
    result = calculate_position_size(
        make_evaluation(
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2393"),
        )
    )

    assert result.available is True

    assert result.risk_budget_amount == Decimal("100")
    assert result.stop_distance == Decimal("7")
    assert result.stop_ticks == Decimal("700")
    assert result.loss_per_quantity == Decimal("700")

    assert result.raw_quantity > Decimal("0.14")
    assert result.raw_quantity < Decimal("0.15")

    assert result.normalized_quantity == Decimal("0.14")
    assert result.estimated_loss_at_stop == Decimal("98")


def test_rounding_up_would_exceed_budget_but_engine_does_not_round_up() -> None:
    result = calculate_position_size(
        make_evaluation(
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2393"),
        )
    )

    assert result.available is True
    assert result.loss_per_quantity == Decimal("700")
    assert result.risk_budget_amount == Decimal("100")

    hypothetical_rounded_up_loss = (
        Decimal("0.15") * result.loss_per_quantity
    )

    assert hypothetical_rounded_up_loss == Decimal("105")
    assert hypothetical_rounded_up_loss > result.risk_budget_amount

    assert result.normalized_quantity == Decimal("0.14")
    assert result.estimated_loss_at_stop == Decimal("98")
    assert result.estimated_loss_at_stop <= result.risk_budget_amount


def test_quantity_respects_non_centimal_broker_step() -> None:
    result = calculate_position_size(
        make_evaluation(
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2396"),
            minimum_quantity=Decimal("0.05"),
            quantity_step=Decimal("0.05"),
        )
    )

    assert result.available is True

    assert result.raw_quantity == Decimal("0.25")
    assert result.normalized_quantity == Decimal("0.25")

    assert (
        result.normalized_quantity % Decimal("0.05")
        == Decimal("0")
    )


def test_position_size_is_capped_by_broker_maximum() -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=Decimal("100000"),
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2399"),
            minimum_quantity=Decimal("0.10"),
            maximum_quantity=Decimal("2.50"),
            quantity_step=Decimal("0.10"),
        )
    )

    assert result.available is True

    assert result.risk_budget_amount == Decimal("1000")
    assert result.raw_quantity == Decimal("10")

    assert result.normalized_quantity == Decimal("2.50")
    assert result.capped_by_maximum is True

    assert result.estimated_loss_at_stop == Decimal("250")
    assert result.estimated_loss_at_stop <= result.risk_budget_amount


def test_maximum_quantity_is_never_exceeded_when_not_step_aligned() -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=Decimal("100000"),
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2399"),
            minimum_quantity=Decimal("0.10"),
            maximum_quantity=Decimal("2.57"),
            quantity_step=Decimal("0.10"),
        )
    )

    assert result.available is True

    assert result.normalized_quantity == Decimal("2.50")
    assert result.normalized_quantity <= Decimal("2.57")
    assert result.capped_by_maximum is True


def test_misaligned_minimum_and_step_is_rejected_safely() -> None:
    result = calculate_position_size(
        make_evaluation(
            minimum_quantity=Decimal("0.03"),
            maximum_quantity=Decimal("10"),
            quantity_step=Decimal("0.02"),
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_QUANTITY_GRID
    )
    assert result.risk_budget_amount == Decimal("100")
    assert result.normalized_quantity is None


def test_maximum_below_first_positive_step_is_rejected_safely() -> None:
    result = calculate_position_size(
        make_evaluation(
            minimum_quantity=Decimal("0"),
            maximum_quantity=Decimal("0.05"),
            quantity_step=Decimal("0.10"),
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_QUANTITY_GRID
    )
    assert result.risk_budget_amount == Decimal("100")
    assert result.normalized_quantity is None


def test_non_aligned_maximum_uses_largest_safe_grid_quantity() -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=Decimal("100000"),
            entry_price=Decimal("2400"),
            stop_loss_price=Decimal("2399"),
            minimum_quantity=Decimal("0.10"),
            maximum_quantity=Decimal("2.57"),
            quantity_step=Decimal("0.10"),
        )
    )

    assert result.available is True
    assert result.normalized_quantity == Decimal("2.50")
    assert result.normalized_quantity <= Decimal("2.57")
    assert (
        result.normalized_quantity % Decimal("0.10")
        == Decimal("0")
    )


def test_position_size_below_minimum_is_unavailable() -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=Decimal("1000"),
            minimum_quantity=Decimal("0.10"),
            maximum_quantity=Decimal("100"),
            quantity_step=Decimal("0.01"),
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.POSITION_SIZE_BELOW_MINIMUM
    )

    assert result.risk_budget_amount == Decimal("10")
    assert result.raw_quantity == Decimal("0.01")
    assert result.normalized_quantity is None
    assert result.estimated_loss_at_stop is None


@pytest.mark.parametrize(
    "equity",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("-1000"),
    ],
)
def test_non_positive_equity_returns_deterministic_unavailable_result(
    equity: Decimal,
) -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=equity,
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_ACCOUNT_EQUITY
    )

    assert result.risk_budget_amount is None
    assert result.normalized_quantity is None


@pytest.mark.parametrize(
    "stop_loss_price",
    [
        Decimal("2400"),
        Decimal("2400.01"),
        Decimal("2500"),
    ],
)
def test_buy_requires_stop_below_entry(
    stop_loss_price: Decimal,
) -> None:
    result = calculate_position_size(
        make_evaluation(
            side=TradeSide.BUY,
            entry_price=Decimal("2400"),
            stop_loss_price=stop_loss_price,
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_STOP_LOSS
    )

    assert result.risk_budget_amount == Decimal("100")
    assert result.normalized_quantity is None


@pytest.mark.parametrize(
    "stop_loss_price",
    [
        Decimal("2400"),
        Decimal("2399.99"),
        Decimal("2300"),
    ],
)
def test_sell_requires_stop_above_entry(
    stop_loss_price: Decimal,
) -> None:
    result = calculate_position_size(
        make_evaluation(
            side=TradeSide.SELL,
            entry_price=Decimal("2400"),
            stop_loss_price=stop_loss_price,
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_STOP_LOSS
    )

    assert result.risk_budget_amount == Decimal("100")
    assert result.normalized_quantity is None


def test_missing_tick_value_loss_returns_safe_unavailable_result() -> None:
    result = calculate_position_size(
        make_evaluation(
            tick_value_loss=None,
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
    )

    assert result.risk_budget_amount == Decimal("100")
    assert result.normalized_quantity is None


def test_contract_size_is_not_used_as_guess_for_missing_tick_value() -> None:
    result = calculate_position_size(
        make_evaluation(
            tick_value_loss=None,
            contract_size=Decimal("100000"),
        )
    )

    assert result.available is False
    assert (
        result.unavailable_reason
        is PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
    )


def test_contract_size_is_not_required_when_tick_value_loss_exists() -> None:
    result = calculate_position_size(
        make_evaluation(
            contract_size=None,
        )
    )

    assert result.available is True
    assert result.normalized_quantity == Decimal("0.10")


@pytest.mark.parametrize(
    "equity,risk_pct,entry,stop",
    [
        (
            Decimal("10000"),
            Decimal("1"),
            Decimal("2400"),
            Decimal("2393"),
        ),
        (
            Decimal("25000"),
            Decimal("0.50"),
            Decimal("100"),
            Decimal("98.73"),
        ),
        (
            Decimal("9999.99"),
            Decimal("1.25"),
            Decimal("50"),
            Decimal("47.11"),
        ),
        (
            Decimal("123456.78"),
            Decimal("0.37"),
            Decimal("3500"),
            Decimal("3481.25"),
        ),
    ],
)
def test_normalized_position_never_exceeds_risk_budget(
    equity: Decimal,
    risk_pct: Decimal,
    entry: Decimal,
    stop: Decimal,
) -> None:
    result = calculate_position_size(
        make_evaluation(
            equity=equity,
            risk_per_trade_pct=risk_pct,
            entry_price=entry,
            stop_loss_price=stop,
        )
    )

    assert result.available is True
    assert result.estimated_loss_at_stop is not None
    assert result.risk_budget_amount is not None

    assert result.estimated_loss_at_stop <= result.risk_budget_amount


def test_position_sizing_outputs_remain_decimal_values() -> None:
    result = calculate_position_size(make_evaluation())

    assert result.available is True

    assert isinstance(result.risk_budget_amount, Decimal)
    assert isinstance(result.stop_distance, Decimal)
    assert isinstance(result.stop_ticks, Decimal)
    assert isinstance(result.loss_per_quantity, Decimal)
    assert isinstance(result.raw_quantity, Decimal)
    assert isinstance(result.normalized_quantity, Decimal)
    assert isinstance(result.estimated_loss_at_stop, Decimal)


def test_unavailable_result_requires_machine_readable_reason() -> None:
    with pytest.raises(ValidationError):
        PositionSizingResult(
            available=False,
        )


def test_available_result_cannot_contain_unavailable_reason() -> None:
    with pytest.raises(ValidationError):
        PositionSizingResult(
            available=True,
            unavailable_reason=(
                PositionSizingUnavailableReason.INVALID_STOP_LOSS
            ),
            risk_budget_amount=Decimal("100"),
            stop_distance=Decimal("10"),
            stop_ticks=Decimal("1000"),
            loss_per_quantity=Decimal("1000"),
            raw_quantity=Decimal("0.10"),
            normalized_quantity=Decimal("0.10"),
            estimated_loss_at_stop=Decimal("100"),
        )


def test_available_result_rejects_estimated_loss_above_budget() -> None:
    with pytest.raises(ValidationError):
        PositionSizingResult(
            available=True,
            risk_budget_amount=Decimal("100"),
            stop_distance=Decimal("10"),
            stop_ticks=Decimal("1000"),
            loss_per_quantity=Decimal("1000"),
            raw_quantity=Decimal("0.11"),
            normalized_quantity=Decimal("0.11"),
            estimated_loss_at_stop=Decimal("110"),
        )
