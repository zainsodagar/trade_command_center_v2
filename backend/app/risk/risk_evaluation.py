from pydantic import model_validator

from backend.app.risk.guardrails import evaluate_trade_guardrails
from backend.app.risk.position_sizing import (
    PositionSizingResult,
    PositionSizingUnavailableReason,
    calculate_position_size,
)
from backend.app.risk.schemas import (
    RiskCheckResult,
    RiskDecision,
    RiskEvaluationInput,
    RiskSchema,
    RiskViolation,
    RiskViolationCode,
)


class RiskEvaluationResult(RiskSchema):
    """
    Final deterministic risk-evaluation output.

    Position-sizing diagnostics are preserved for auditability while
    `risk_check` contains the authoritative ALLOW/BLOCK decision.
    """

    position_sizing: PositionSizingResult
    risk_check: RiskCheckResult

    @model_validator(mode="after")
    def validate_sizing_decision_consistency(
        self,
    ) -> "RiskEvaluationResult":
        if (
            not self.position_sizing.available
            and self.risk_check.decision is RiskDecision.ALLOW
        ):
            raise ValueError(
                "unavailable position sizing cannot produce an "
                "ALLOW risk decision"
            )

        return self

    @property
    def decision(self) -> RiskDecision:
        return self.risk_check.decision

    @property
    def allowed(self) -> bool:
        return self.risk_check.allowed

    @property
    def violations(self) -> tuple[RiskViolation, ...]:
        return self.risk_check.violations


_SIZING_VIOLATION_CODES = {
    PositionSizingUnavailableReason.INVALID_ACCOUNT_EQUITY: (
        RiskViolationCode.INVALID_ACCOUNT_EQUITY
    ),
    PositionSizingUnavailableReason.INVALID_STOP_LOSS: (
        RiskViolationCode.INVALID_STOP_LOSS
    ),
    PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS: (
        RiskViolationCode.MISSING_TICK_VALUE_LOSS
    ),
    PositionSizingUnavailableReason.INVALID_QUANTITY_GRID: (
        RiskViolationCode.INVALID_QUANTITY_GRID
    ),
    PositionSizingUnavailableReason.POSITION_SIZE_BELOW_MINIMUM: (
        RiskViolationCode.POSITION_SIZE_BELOW_MINIMUM
    ),
}


_SIZING_VIOLATION_MESSAGES = {
    PositionSizingUnavailableReason.INVALID_ACCOUNT_EQUITY: (
        "Account equity must be positive for position sizing."
    ),
    PositionSizingUnavailableReason.INVALID_STOP_LOSS: (
        "Stop-loss geometry is invalid for the trade direction."
    ),
    PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS: (
        "Broker-normalized loss tick value is unavailable."
    ),
    PositionSizingUnavailableReason.INVALID_QUANTITY_GRID: (
        "Instrument quantity grid is invalid or ambiguous."
    ),
    PositionSizingUnavailableReason.POSITION_SIZE_BELOW_MINIMUM: (
        "Risk-constrained position size is below broker minimum."
    ),
}


def _blocked_for_unavailable_sizing(
    sizing: PositionSizingResult,
) -> RiskCheckResult:
    """
    Convert a sizing failure into a deterministic final BLOCK result.

    Unknown future sizing reasons fail closed as POSITION_SIZING_MISMATCH
    rather than being silently allowed.
    """

    reason = sizing.unavailable_reason

    if reason is None:
        return RiskCheckResult(
            decision=RiskDecision.BLOCK,
            violations=(
                RiskViolation(
                    code=RiskViolationCode.POSITION_SIZING_MISMATCH,
                    message=(
                        "Position sizing is unavailable without a "
                        "machine-readable reason."
                    ),
                ),
            ),
        )

    code = _SIZING_VIOLATION_CODES.get(
        reason,
        RiskViolationCode.POSITION_SIZING_MISMATCH,
    )

    message = _SIZING_VIOLATION_MESSAGES.get(
        reason,
        "Position sizing is unavailable for the current risk evaluation.",
    )

    return RiskCheckResult(
        decision=RiskDecision.BLOCK,
        violations=(
            RiskViolation(
                code=code,
                message=message,
            ),
        ),
    )


def evaluate_risk(
    evaluation: RiskEvaluationInput,
) -> RiskEvaluationResult:
    """
    Perform the complete deterministic risk evaluation.

    Position sizing runs first. An unavailable sizing result immediately
    fails closed and guardrail evaluation is not attempted.

    Available sizing is then evaluated by the deterministic trade and
    portfolio guardrails.

    This service contains no broker, MT5, HTTP, persistence, AI, order,
    or execution mechanism.
    """

    sizing = calculate_position_size(
        evaluation,
    )

    if not sizing.available:
        return RiskEvaluationResult(
            position_sizing=sizing,
            risk_check=_blocked_for_unavailable_sizing(
                sizing,
            ),
        )

    risk_check = evaluate_trade_guardrails(
        evaluation,
        sizing,
    )

    return RiskEvaluationResult(
        position_sizing=sizing,
        risk_check=risk_check,
    )
