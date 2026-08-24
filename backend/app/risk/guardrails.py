from decimal import ROUND_FLOOR, Decimal

from backend.app.risk.position_sizing import PositionSizingResult
from backend.app.risk.schemas import (
    ONE_HUNDRED,
    ZERO,
    RiskCheckResult,
    RiskDecision,
    RiskEvaluationInput,
    RiskViolation,
    RiskViolationCode,
    TradeSide,
)


def _violation(
    code: RiskViolationCode,
    message: str,
) -> RiskViolation:
    return RiskViolation(
        code=code,
        message=message,
    )


def _require_available_sizing(
    sizing: PositionSizingResult,
) -> Decimal:
    """
    Return the finalized quantity from an available sizing result.

    Guardrails do not trust the sizing result's monetary diagnostics.
    Those values are independently reproduced from the current risk
    evaluation before they are used for any risk decision.
    """

    if not sizing.available:
        raise ValueError(
            "trade guardrails require an available position-sizing result"
        )

    if sizing.normalized_quantity is None:
        raise ValueError(
            "available position sizing must include normalized quantity"
        )

    return sizing.normalized_quantity


def _invalid_stop_loss(
    evaluation: RiskEvaluationInput,
) -> bool:
    trade = evaluation.trade

    if trade.side is TradeSide.BUY:
        return trade.stop_loss_price >= trade.entry_price

    return trade.stop_loss_price <= trade.entry_price


def _floor_to_step(
    quantity: Decimal,
    step: Decimal,
) -> Decimal:
    step_count = (quantity / step).to_integral_value(
        rounding=ROUND_FLOOR,
    )

    return step_count * step


def _quantity_grid_is_valid(
    evaluation: RiskEvaluationInput,
) -> bool:
    instrument = evaluation.instrument

    if (
        instrument.minimum_quantity % instrument.quantity_step
        != ZERO
    ):
        return False

    effective_maximum = _floor_to_step(
        instrument.maximum_quantity,
        instrument.quantity_step,
    )

    if effective_maximum <= ZERO:
        return False

    return effective_maximum >= instrument.minimum_quantity


def _authoritative_sizing_diagnostics(
    evaluation: RiskEvaluationInput,
    quantity: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal] | None:
    """
    Reproduce monetary stop-risk diagnostics from current evaluation data.

    None means the current evaluation lacks the broker-normalized
    tick-value information required to reproduce monetary risk.
    """

    instrument = evaluation.instrument
    trade = evaluation.trade

    if instrument.tick_value_loss is None:
        return None

    stop_distance = abs(
        trade.entry_price - trade.stop_loss_price
    )

    stop_ticks = (
        stop_distance / instrument.tick_size
    )

    loss_per_quantity = (
        stop_ticks * instrument.tick_value_loss
    )

    estimated_loss_at_stop = (
        quantity * loss_per_quantity
    )

    return (
        stop_distance,
        stop_ticks,
        loss_per_quantity,
        estimated_loss_at_stop,
    )


def _sizing_diagnostics_match(
    sizing: PositionSizingResult,
    authoritative: tuple[Decimal, Decimal, Decimal, Decimal],
) -> bool:
    (
        stop_distance,
        stop_ticks,
        loss_per_quantity,
        estimated_loss_at_stop,
    ) = authoritative

    return (
        sizing.stop_distance == stop_distance
        and sizing.stop_ticks == stop_ticks
        and sizing.loss_per_quantity == loss_per_quantity
        and sizing.estimated_loss_at_stop == estimated_loss_at_stop
    )


def evaluate_trade_guardrails(
    evaluation: RiskEvaluationInput,
    sizing: PositionSizingResult,
) -> RiskCheckResult:
    """
    Evaluate deterministic trade and portfolio safety boundaries.

    Monetary stop risk is reproduced from the current evaluation rather
    than trusted from supplied sizing diagnostics.

    This function is pure and broker-independent:
    - no broker calls
    - no MT5 calls
    - no HTTP calls
    - no persistence
    - no order submission
    - no execution
    """

    quantity = _require_available_sizing(
        sizing,
    )

    limits = evaluation.limits
    account = evaluation.account
    instrument = evaluation.instrument

    violations: list[RiskViolation] = []

    if account.equity <= ZERO:
        violations.append(
            _violation(
                RiskViolationCode.INVALID_ACCOUNT_EQUITY,
                "Account equity must be positive for risk evaluation.",
            )
        )

    if not instrument.tradable:
        violations.append(
            _violation(
                RiskViolationCode.INSTRUMENT_NOT_TRADABLE,
                "Instrument is not currently tradable.",
            )
        )

    invalid_stop_loss = _invalid_stop_loss(
        evaluation,
    )

    if invalid_stop_loss:
        violations.append(
            _violation(
                RiskViolationCode.INVALID_STOP_LOSS,
                "Stop-loss geometry is invalid for the trade direction.",
            )
        )

    quantity_grid_valid = _quantity_grid_is_valid(
        evaluation,
    )

    if not quantity_grid_valid:
        violations.append(
            _violation(
                RiskViolationCode.INVALID_QUANTITY_GRID,
                "Instrument quantity grid is invalid or ambiguous.",
            )
        )

    if quantity < instrument.minimum_quantity:
        violations.append(
            _violation(
                RiskViolationCode.POSITION_SIZE_BELOW_MINIMUM,
                "Finalized position quantity is below broker minimum.",
            )
        )

    if quantity > instrument.maximum_quantity:
        violations.append(
            _violation(
                RiskViolationCode.POSITION_SIZE_ABOVE_MAXIMUM,
                "Finalized position quantity exceeds broker maximum.",
            )
        )

    if (
        quantity_grid_valid
        and quantity % instrument.quantity_step != ZERO
    ):
        violations.append(
            _violation(
                RiskViolationCode.POSITION_SIZE_STEP_MISMATCH,
                "Finalized position quantity does not match broker step.",
            )
        )

    authoritative_diagnostics = None

    if not invalid_stop_loss:
        authoritative_diagnostics = (
            _authoritative_sizing_diagnostics(
                evaluation,
                quantity,
            )
        )

        if authoritative_diagnostics is None:
            violations.append(
                _violation(
                    RiskViolationCode.POSITION_SIZING_MISMATCH,
                    "Current evaluation cannot reproduce monetary "
                    "position risk.",
                )
            )
        elif not _sizing_diagnostics_match(
            sizing,
            authoritative_diagnostics,
        ):
            violations.append(
                _violation(
                    RiskViolationCode.POSITION_SIZING_MISMATCH,
                    "Position-sizing diagnostics do not match the "
                    "current risk evaluation.",
                )
            )

    if account.open_position_count >= limits.max_open_positions:
        violations.append(
            _violation(
                RiskViolationCode.MAX_OPEN_POSITIONS_REACHED,
                "Maximum open-position limit has been reached.",
            )
        )

    if instrument.gross_exposure_per_quantity is None:
        violations.append(
            _violation(
                RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE,
                "Normalized gross exposure data is unavailable.",
            )
        )

    if (
        account.equity > ZERO
        and authoritative_diagnostics is not None
    ):
        estimated_loss_at_stop = (
            authoritative_diagnostics[3]
        )

        risk_budget_amount = (
            account.equity
            * limits.risk_per_trade_pct
            / ONE_HUNDRED
        )

        if estimated_loss_at_stop > risk_budget_amount:
            violations.append(
                _violation(
                    RiskViolationCode.RISK_PER_TRADE_EXCEEDED,
                    "Finalized stop-loss risk exceeds risk-per-trade limit.",
                )
            )

        daily_loss_limit_amount = (
            account.equity
            * limits.daily_loss_limit_pct
            / ONE_HUNDRED
        )

        projected_daily_loss_amount = (
            account.daily_loss_amount
            + estimated_loss_at_stop
        )

        if account.daily_loss_amount >= daily_loss_limit_amount:
            violations.append(
                _violation(
                    RiskViolationCode.DAILY_LOSS_LIMIT_REACHED,
                    "Daily loss limit has already been reached.",
                )
            )
        elif projected_daily_loss_amount > daily_loss_limit_amount:
            violations.append(
                _violation(
                    RiskViolationCode.DAILY_LOSS_LIMIT_REACHED,
                    "Proposed trade could exceed the daily loss limit.",
                )
            )

    if (
        account.equity > ZERO
        and instrument.gross_exposure_per_quantity is not None
    ):
        proposed_exposure_amount = (
            quantity
            * instrument.gross_exposure_per_quantity
        )

        projected_total_exposure_amount = (
            account.total_exposure_amount
            + proposed_exposure_amount
        )

        max_total_exposure_amount = (
            account.equity
            * limits.max_total_exposure_pct
            / ONE_HUNDRED
        )

        if (
            projected_total_exposure_amount
            > max_total_exposure_amount
        ):
            violations.append(
                _violation(
                    RiskViolationCode.MAX_TOTAL_EXPOSURE_EXCEEDED,
                    "Projected gross exposure exceeds configured limit.",
                )
            )

    if violations:
        return RiskCheckResult(
            decision=RiskDecision.BLOCK,
            violations=tuple(violations),
        )

    return RiskCheckResult(
        decision=RiskDecision.ALLOW,
    )
