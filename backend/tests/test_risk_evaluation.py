from decimal import Decimal

import pytest
from pydantic import ValidationError

import backend.app.risk.risk_evaluation as risk_evaluation_module
from backend.app.risk.position_sizing import (
    PositionSizingResult,
    PositionSizingUnavailableReason,
)
from backend.app.risk.risk_evaluation import (
    RiskEvaluationResult,
    evaluate_risk,
)
from backend.app.risk.schemas import (
    AccountRiskState,
    RiskCheckResult,
    RiskDecision,
    RiskEvaluationInput,
    RiskInstrumentSpec,
    RiskLimits,
    RiskViolation,
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
    tick_value_loss: Decimal | None = Decimal("1"),
    gross_exposure_per_quantity: Decimal | None = Decimal("2400"),
    risk_per_trade_pct: Decimal = Decimal("1"),
    daily_loss_limit_pct: Decimal = Decimal("5"),
    max_open_positions: int = 5,
    max_total_exposure_pct: Decimal = Decimal("250"),
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
            contract_size=Decimal("100"),
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


def violation_codes(
    result: RiskEvaluationResult,
) -> tuple[RiskViolationCode, ...]:
    return tuple(
        violation.code
        for violation in result.violations
    )


def test_valid_candidate_returns_complete_allow_result() -> None:
    evaluation = make_evaluation()

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is True
    assert (
        result.position_sizing.normalized_quantity
        == Decimal("0.10")
    )
    assert (
        result.position_sizing.estimated_loss_at_stop
        == Decimal("100")
    )

    assert result.risk_check.decision is RiskDecision.ALLOW
    assert result.decision is RiskDecision.ALLOW
    assert result.allowed is True
    assert result.violations == ()


def test_invalid_account_equity_maps_to_final_violation() -> None:
    evaluation = make_evaluation(
        equity=Decimal("0"),
        daily_loss_amount=Decimal("0"),
        total_exposure_amount=Decimal("0"),
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is False
    assert (
        result.position_sizing.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_ACCOUNT_EQUITY
    )
    assert violation_codes(result) == (
        RiskViolationCode.INVALID_ACCOUNT_EQUITY,
    )


def test_invalid_stop_loss_maps_to_final_violation() -> None:
    evaluation = make_evaluation(
        side=TradeSide.BUY,
        entry_price=Decimal("2400"),
        stop_loss_price=Decimal("2400"),
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is False
    assert (
        result.position_sizing.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_STOP_LOSS
    )
    assert violation_codes(result) == (
        RiskViolationCode.INVALID_STOP_LOSS,
    )


def test_missing_tick_value_maps_to_final_violation() -> None:
    evaluation = make_evaluation(
        tick_value_loss=None,
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is False
    assert (
        result.position_sizing.unavailable_reason
        is PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
    )
    assert violation_codes(result) == (
        RiskViolationCode.MISSING_TICK_VALUE_LOSS,
    )


def test_invalid_quantity_grid_maps_to_final_violation() -> None:
    evaluation = make_evaluation(
        minimum_quantity=Decimal("0.03"),
        maximum_quantity=Decimal("100"),
        quantity_step=Decimal("0.02"),
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is False
    assert (
        result.position_sizing.unavailable_reason
        is PositionSizingUnavailableReason.INVALID_QUANTITY_GRID
    )
    assert violation_codes(result) == (
        RiskViolationCode.INVALID_QUANTITY_GRID,
    )


def test_below_minimum_size_maps_to_final_violation() -> None:
    evaluation = make_evaluation(
        minimum_quantity=Decimal("0.20"),
        quantity_step=Decimal("0.01"),
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is False
    assert (
        result.position_sizing.unavailable_reason
        is PositionSizingUnavailableReason.POSITION_SIZE_BELOW_MINIMUM
    )
    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZE_BELOW_MINIMUM,
    )


def test_unavailable_sizing_short_circuits_guardrails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluation = make_evaluation(
        tick_value_loss=None,
    )

    def forbidden_guardrail_call(*args, **kwargs):
        raise AssertionError(
            "Guardrails must not run when position sizing is unavailable."
        )

    monkeypatch.setattr(
        risk_evaluation_module,
        "evaluate_trade_guardrails",
        forbidden_guardrail_call,
    )

    result = risk_evaluation_module.evaluate_risk(
        evaluation,
    )

    assert result.position_sizing.available is False
    assert result.allowed is False
    assert violation_codes(result) == (
        RiskViolationCode.MISSING_TICK_VALUE_LOSS,
    )


def test_available_sizing_calls_guardrails_exactly_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluation = make_evaluation()

    calls = []

    def fake_guardrails(
        supplied_evaluation,
        supplied_sizing,
    ) -> RiskCheckResult:
        calls.append(
            (
                supplied_evaluation,
                supplied_sizing,
            )
        )

        return RiskCheckResult(
            decision=RiskDecision.ALLOW,
        )

    monkeypatch.setattr(
        risk_evaluation_module,
        "evaluate_trade_guardrails",
        fake_guardrails,
    )

    result = risk_evaluation_module.evaluate_risk(
        evaluation,
    )

    assert result.position_sizing.available is True
    assert result.allowed is True

    assert len(calls) == 1

    supplied_evaluation, supplied_sizing = calls[0]

    assert supplied_evaluation is evaluation
    assert supplied_sizing == result.position_sizing


def test_guardrail_block_result_is_preserved() -> None:
    evaluation = make_evaluation(
        tradable=False,
        open_position_count=5,
        max_open_positions=5,
        gross_exposure_per_quantity=None,
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is True
    assert result.decision is RiskDecision.BLOCK

    assert violation_codes(result) == (
        RiskViolationCode.INSTRUMENT_NOT_TRADABLE,
        RiskViolationCode.MAX_OPEN_POSITIONS_REACHED,
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
    )


def test_missing_exposure_is_guardrail_failure_not_sizing_failure() -> None:
    evaluation = make_evaluation(
        gross_exposure_per_quantity=None,
    )

    result = evaluate_risk(evaluation)

    assert result.position_sizing.available is True
    assert result.allowed is False
    assert violation_codes(result) == (
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
    )


def test_sizing_reason_mappings_cover_complete_current_enum() -> None:
    expected = set(
        PositionSizingUnavailableReason
    )

    assert (
        set(
            risk_evaluation_module._SIZING_VIOLATION_CODES
        )
        == expected
    )

    assert (
        set(
            risk_evaluation_module._SIZING_VIOLATION_MESSAGES
        )
        == expected
    )


def test_risk_evaluation_result_is_immutable() -> None:
    evaluation = make_evaluation()

    result = evaluate_risk(evaluation)

    replacement = RiskCheckResult(
        decision=RiskDecision.BLOCK,
        violations=(
            RiskViolation(
                code=RiskViolationCode.INSTRUMENT_NOT_TRADABLE,
                message="Replacement result.",
            ),
        ),
    )

    with pytest.raises(ValidationError):
        result.risk_check = replacement


def test_repeated_evaluation_is_deterministic() -> None:
    evaluation = make_evaluation()

    first = evaluate_risk(evaluation)
    second = evaluate_risk(evaluation)

    assert first == second
    assert first.model_dump() == second.model_dump()


def test_risk_evaluation_does_not_mutate_input() -> None:
    evaluation = make_evaluation()

    before = evaluation.model_dump()

    evaluate_risk(evaluation)

    after = evaluation.model_dump()

    assert after == before

def test_unavailable_sizing_cannot_coexist_with_allow() -> None:
    sizing = PositionSizingResult(
        available=False,
        unavailable_reason=(
            PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
        ),
    )

    allow_check = RiskCheckResult(
        decision=RiskDecision.ALLOW,
    )

    with pytest.raises(
        ValidationError,
        match=(
            "unavailable position sizing cannot produce "
            "an ALLOW risk decision"
        ),
    ):
        RiskEvaluationResult(
            position_sizing=sizing,
            risk_check=allow_check,
        )


def test_missing_sizing_reason_mapping_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reason = (
        PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
    )

    monkeypatch.delitem(
        risk_evaluation_module._SIZING_VIOLATION_CODES,
        reason,
    )

    evaluation = make_evaluation(
        tick_value_loss=None,
    )

    result = risk_evaluation_module.evaluate_risk(
        evaluation,
    )

    assert result.position_sizing.available is False
    assert result.allowed is False
    assert violation_codes(result) == (
        RiskViolationCode.POSITION_SIZING_MISMATCH,
    )
