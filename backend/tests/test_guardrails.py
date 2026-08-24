from decimal import Decimal

import pytest

from backend.app.risk.guardrails import evaluate_trade_guardrails
from backend.app.risk.position_sizing import (
    PositionSizingResult,
    calculate_position_size,
)
from backend.app.risk.schemas import (
    AccountRiskState,
    RiskDecision,
    RiskEvaluationInput,
    RiskInstrumentSpec,
    RiskLimits,
    RiskViolationCode,
    TradeRiskCandidate,
    TradeSide,
)


def make_evaluation(
    *,
    equity: Decimal = Decimal("10000"),
    daily_loss_amount: Decimal = Decimal("100"),
    open_position_count: int = 2,
    total_exposure_amount: Decimal = Decimal("5000"),
    tradable: bool = True,
    minimum_quantity: Decimal = Decimal("0.01"),
    maximum_quantity: Decimal = Decimal("100"),
    quantity_step: Decimal = Decimal("0.01"),
    gross_exposure_per_quantity: Decimal | None = Decimal("2400"),
    contract_size: Decimal | None = Decimal("100"),
    risk_per_trade_pct: Decimal = Decimal("1"),
    daily_loss_limit_pct: Decimal = Decimal("5"),
    max_open_positions: int = 5,
    max_total_exposure_pct: Decimal = Decimal("250"),
    tick_value_loss: Decimal | None = Decimal("1"),
    side: TradeSide = TradeSide.BUY,
    entry_price: Decimal = Decimal("2400"),
    stop_loss_price: Decimal = Decimal("2390"),
) -> RiskEvaluationInput:
    return RiskEvaluationInput(
        limits=RiskLimits(
            risk_per_trade_pct=risk_per_trade_pct,
            daily_loss_limit_pct=daily_loss_limit_pct,
            max_open_positions=max_open_positions,
            max_total_exposure_pct=max_total_exposure_pct,
        ),
        account=AccountRiskState(
            equity=equity,
            daily_loss_amount=daily_loss_amount,
            open_position_count=open_position_count,
            total_exposure_amount=total_exposure_amount,
        ),
        instrument=RiskInstrumentSpec(
            symbol="XAUUSD",
            broker_symbol="XAUUSD",
            tradable=tradable,
            minimum_quantity=minimum_quantity,
            maximum_quantity=maximum_quantity,
            quantity_step=quantity_step,
            tick_size=Decimal("0.01"),
            tick_value_loss=tick_value_loss,
            contract_size=contract_size,
            gross_exposure_per_quantity=gross_exposure_per_quantity,
        ),
        trade=TradeRiskCandidate(
            symbol="XAUUSD",
            broker_symbol="XAUUSD",
            side=side,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
        ),
    )


def make_finalized_sizing(
    *,
    quantity: Decimal = Decimal("0.10"),
    estimated_loss: Decimal = Decimal("100"),
    sizing_risk_budget: Decimal = Decimal("100"),
) -> PositionSizingResult:
    loss_per_quantity = estimated_loss / quantity

    return PositionSizingResult(
        available=True,
        risk_budget_amount=sizing_risk_budget,
        stop_distance=Decimal("10"),
        stop_ticks=Decimal("1000"),
        loss_per_quantity=loss_per_quantity,
        raw_quantity=quantity,
        normalized_quantity=quantity,
        estimated_loss_at_stop=estimated_loss,
        capped_by_maximum=False,
    )


def violation_codes(
    result,
) -> tuple[RiskViolationCode, ...]:
    return tuple(
        violation.code
        for violation in result.violations
    )


def test_valid_sized_candidate_is_allowed() -> None:
    evaluation = make_evaluation()
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.decision is RiskDecision.ALLOW
    assert result.allowed is True
    assert result.violations == ()


def test_non_tradable_instrument_is_blocked() -> None:
    evaluation = make_evaluation(
        tradable=False,
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.INSTRUMENT_NOT_TRADABLE,
    )


@pytest.mark.parametrize(
    "daily_loss_amount",
    [
        Decimal("500"),
        Decimal("600"),
    ],
)
def test_daily_loss_already_at_or_above_limit_is_blocked(
    daily_loss_amount: Decimal,
) -> None:
    evaluation = make_evaluation(
        daily_loss_amount=daily_loss_amount,
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.DAILY_LOSS_LIMIT_REACHED,
    )


def test_projected_daily_loss_exactly_at_limit_is_allowed() -> None:
    evaluation = make_evaluation(
        daily_loss_amount=Decimal("400"),
    )
    sizing = calculate_position_size(evaluation)

    assert sizing.estimated_loss_at_stop == Decimal("100")

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.allowed is True


def test_projected_daily_loss_above_limit_is_blocked() -> None:
    evaluation = make_evaluation(
        daily_loss_amount=Decimal("401"),
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.DAILY_LOSS_LIMIT_REACHED,
    )


def test_position_count_one_below_limit_is_allowed() -> None:
    evaluation = make_evaluation(
        open_position_count=4,
        max_open_positions=5,
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.allowed is True


def test_position_count_at_limit_is_blocked() -> None:
    evaluation = make_evaluation(
        open_position_count=5,
        max_open_positions=5,
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.MAX_OPEN_POSITIONS_REACHED,
    )


def test_missing_exposure_data_is_blocked() -> None:
    evaluation = make_evaluation(
        gross_exposure_per_quantity=None,
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
    )


def test_contract_size_does_not_substitute_for_exposure_data() -> None:
    evaluation = make_evaluation(
        gross_exposure_per_quantity=None,
        contract_size=Decimal("100000"),
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
    )


def test_projected_exposure_exactly_at_limit_is_allowed() -> None:
    evaluation = make_evaluation(
        total_exposure_amount=Decimal("24760"),
    )
    sizing = calculate_position_size(evaluation)

    proposed_exposure = (
        sizing.normalized_quantity
        * Decimal("2400")
    )

    assert proposed_exposure == Decimal("240")
    assert (
        evaluation.account.total_exposure_amount
        + proposed_exposure
        == Decimal("25000")
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.allowed is True


def test_projected_exposure_above_limit_is_blocked() -> None:
    evaluation = make_evaluation(
        total_exposure_amount=Decimal("24760.01"),
    )
    sizing = calculate_position_size(evaluation)

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.MAX_TOTAL_EXPOSURE_EXCEEDED,
    )


def test_risk_exactly_at_per_trade_limit_is_allowed() -> None:
    evaluation = make_evaluation()

    sizing = make_finalized_sizing(
        quantity=Decimal("0.10"),
        estimated_loss=Decimal("100"),
        sizing_risk_budget=Decimal("100"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.allowed is True


def test_finalized_risk_above_per_trade_limit_is_blocked() -> None:
    evaluation = make_evaluation()

    sizing = make_finalized_sizing(
        quantity=Decimal("0.11"),
        estimated_loss=Decimal("110"),
        sizing_risk_budget=Decimal("110"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.RISK_PER_TRADE_EXCEEDED,
    )


def test_finalized_quantity_below_minimum_is_blocked() -> None:
    evaluation = make_evaluation(
        minimum_quantity=Decimal("0.10"),
        quantity_step=Decimal("0.01"),
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.05"),
        estimated_loss=Decimal("50"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZE_BELOW_MINIMUM,
    )


def test_finalized_quantity_above_maximum_is_blocked() -> None:
    evaluation = make_evaluation(
        maximum_quantity=Decimal("0.50"),
        risk_per_trade_pct=Decimal("10"),
        daily_loss_limit_pct=Decimal("20"),
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.51"),
        estimated_loss=Decimal("510"),
        sizing_risk_budget=Decimal("510"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZE_ABOVE_MAXIMUM,
    )


def test_finalized_quantity_step_mismatch_is_blocked() -> None:
    evaluation = make_evaluation(
        quantity_step=Decimal("0.01"),
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.095"),
        estimated_loss=Decimal("95"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZE_STEP_MISMATCH,
    )


@pytest.mark.parametrize(
    "equity",
    [
        Decimal("0"),
        Decimal("-1"),
    ],
)
def test_non_positive_equity_is_blocked_defensively(
    equity: Decimal,
) -> None:
    evaluation = make_evaluation(
        equity=equity,
        daily_loss_amount=Decimal("0"),
        total_exposure_amount=Decimal("0"),
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.10"),
        estimated_loss=Decimal("100"),
        sizing_risk_budget=Decimal("100"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.INVALID_ACCOUNT_EQUITY,
    )


def test_unavailable_sizing_cannot_enter_guardrails() -> None:
    evaluation = make_evaluation(
        tick_value_loss=None,
    )

    sizing = calculate_position_size(evaluation)

    assert sizing.available is False

    with pytest.raises(
        ValueError,
        match="require an available position-sizing result",
    ):
        evaluate_trade_guardrails(
            evaluation,
            sizing,
        )


def test_tampered_sizing_diagnostics_are_blocked() -> None:
    evaluation = make_evaluation(
        daily_loss_amount=Decimal("0"),
        total_exposure_amount=Decimal("0"),
    )

    tampered = PositionSizingResult(
        available=True,
        risk_budget_amount=Decimal("100"),
        stop_distance=Decimal("10"),
        stop_ticks=Decimal("1000"),
        loss_per_quantity=Decimal("500"),
        raw_quantity=Decimal("0.10"),
        normalized_quantity=Decimal("0.10"),
        estimated_loss_at_stop=Decimal("50"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        tampered,
    )

    assert result.allowed is False
    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZING_MISMATCH,
    )


def test_missing_current_tick_value_blocks_forged_available_sizing() -> None:
    evaluation = make_evaluation(
        tick_value_loss=None,
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.10"),
        estimated_loss=Decimal("100"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZING_MISMATCH,
    )


@pytest.mark.parametrize(
    "side,stop_loss_price",
    [
        (
            TradeSide.BUY,
            Decimal("2400"),
        ),
        (
            TradeSide.SELL,
            Decimal("2390"),
        ),
    ],
)
def test_invalid_stop_geometry_is_blocked_independently(
    side: TradeSide,
    stop_loss_price: Decimal,
) -> None:
    evaluation = make_evaluation(
        side=side,
        entry_price=Decimal("2400"),
        stop_loss_price=stop_loss_price,
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.10"),
        estimated_loss=Decimal("100"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.INVALID_STOP_LOSS,
    )


def test_invalid_quantity_grid_is_blocked_independently() -> None:
    evaluation = make_evaluation(
        minimum_quantity=Decimal("0.03"),
        maximum_quantity=Decimal("10"),
        quantity_step=Decimal("0.02"),
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.04"),
        estimated_loss=Decimal("40"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert violation_codes(result) == (
        RiskViolationCode.INVALID_QUANTITY_GRID,
    )


def test_guardrail_hardening_violation_codes_are_stable() -> None:
    assert (
        RiskViolationCode.POSITION_SIZING_MISMATCH.value
        == "position_sizing_mismatch"
    )
    assert (
        RiskViolationCode.INVALID_QUANTITY_GRID.value
        == "invalid_quantity_grid"
    )


def test_multiple_violations_accumulate_in_stable_order() -> None:
    evaluation = make_evaluation(
        tradable=False,
        minimum_quantity=Decimal("0.20"),
        quantity_step=Decimal("0.01"),
        open_position_count=5,
        daily_loss_amount=Decimal("500"),
        gross_exposure_per_quantity=None,
    )

    sizing = make_finalized_sizing(
        quantity=Decimal("0.11"),
        estimated_loss=Decimal("110"),
        sizing_risk_budget=Decimal("110"),
    )

    result = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    assert result.decision is RiskDecision.BLOCK

    assert violation_codes(result) == (
        RiskViolationCode.INSTRUMENT_NOT_TRADABLE,
        RiskViolationCode.POSITION_SIZE_BELOW_MINIMUM,
        RiskViolationCode.MAX_OPEN_POSITIONS_REACHED,
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
        RiskViolationCode.RISK_PER_TRADE_EXCEEDED,
        RiskViolationCode.DAILY_LOSS_LIMIT_REACHED,
    )
