from decimal import ROUND_FLOOR, Decimal
from enum import StrEnum

from pydantic import model_validator

from backend.app.risk.schemas import (
    ONE_HUNDRED,
    ZERO,
    RiskEvaluationInput,
    RiskSchema,
    TradeSide,
)


class PositionSizingUnavailableReason(StrEnum):
    """Machine-readable reason why deterministic sizing was unavailable."""

    INVALID_ACCOUNT_EQUITY = "invalid_account_equity"
    INVALID_STOP_LOSS = "invalid_stop_loss"
    MISSING_TICK_VALUE_LOSS = "missing_tick_value_loss"
    INVALID_QUANTITY_GRID = "invalid_quantity_grid"
    POSITION_SIZE_BELOW_MINIMUM = "position_size_below_minimum"


class PositionSizingResult(RiskSchema):
    """
    Transparent deterministic position-sizing result.

    Diagnostic intermediate values are retained so later risk evaluation,
    auditing, and UI layers can explain exactly how the quantity was derived.
    """

    available: bool
    unavailable_reason: PositionSizingUnavailableReason | None = None

    risk_budget_amount: Decimal | None = None
    stop_distance: Decimal | None = None
    stop_ticks: Decimal | None = None
    loss_per_quantity: Decimal | None = None

    raw_quantity: Decimal | None = None
    normalized_quantity: Decimal | None = None

    estimated_loss_at_stop: Decimal | None = None

    capped_by_maximum: bool = False

    @model_validator(mode="after")
    def validate_result_consistency(self) -> "PositionSizingResult":
        if self.available:
            if self.unavailable_reason is not None:
                raise ValueError(
                    "available sizing results cannot have an "
                    "unavailable reason"
                )

            required_values = (
                self.risk_budget_amount,
                self.stop_distance,
                self.stop_ticks,
                self.loss_per_quantity,
                self.raw_quantity,
                self.normalized_quantity,
                self.estimated_loss_at_stop,
            )

            if any(value is None for value in required_values):
                raise ValueError(
                    "available sizing results require all calculation values"
                )

            if self.normalized_quantity is None:
                raise ValueError(
                    "available sizing results require normalized quantity"
                )

            if self.normalized_quantity <= ZERO:
                raise ValueError(
                    "available normalized quantity must be positive"
                )

            if (
                self.estimated_loss_at_stop is not None
                and self.risk_budget_amount is not None
                and self.estimated_loss_at_stop > self.risk_budget_amount
            ):
                raise ValueError(
                    "estimated stop loss cannot exceed risk budget"
                )

        elif self.unavailable_reason is None:
            raise ValueError(
                "unavailable sizing results require an unavailable reason"
            )

        return self


def _invalid_stop_loss(evaluation: RiskEvaluationInput) -> bool:
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


def calculate_position_size(
    evaluation: RiskEvaluationInput,
) -> PositionSizingResult:
    """
    Calculate the maximum deterministic quantity allowed by per-trade risk.

    This function is pure:
    - no broker calls
    - no MT5 calls
    - no HTTP calls
    - no persistence
    - no order submission
    """

    account = evaluation.account
    limits = evaluation.limits
    instrument = evaluation.instrument
    trade = evaluation.trade

    if account.equity <= ZERO:
        return PositionSizingResult(
            available=False,
            unavailable_reason=(
                PositionSizingUnavailableReason.INVALID_ACCOUNT_EQUITY
            ),
        )

    risk_budget_amount = (
        account.equity
        * limits.risk_per_trade_pct
        / ONE_HUNDRED
    )

    if _invalid_stop_loss(evaluation):
        return PositionSizingResult(
            available=False,
            unavailable_reason=(
                PositionSizingUnavailableReason.INVALID_STOP_LOSS
            ),
            risk_budget_amount=risk_budget_amount,
        )

    if instrument.tick_value_loss is None:
        return PositionSizingResult(
            available=False,
            unavailable_reason=(
                PositionSizingUnavailableReason.MISSING_TICK_VALUE_LOSS
            ),
            risk_budget_amount=risk_budget_amount,
        )

    if not _quantity_grid_is_valid(evaluation):
        return PositionSizingResult(
            available=False,
            unavailable_reason=(
                PositionSizingUnavailableReason.INVALID_QUANTITY_GRID
            ),
            risk_budget_amount=risk_budget_amount,
        )

    stop_distance = abs(
        trade.entry_price - trade.stop_loss_price
    )

    stop_ticks = stop_distance / instrument.tick_size

    loss_per_quantity = (
        stop_ticks * instrument.tick_value_loss
    )

    raw_quantity = (
        risk_budget_amount / loss_per_quantity
    )

    normalized_quantity = _floor_to_step(
        raw_quantity,
        instrument.quantity_step,
    )

    maximum_quantity = _floor_to_step(
        instrument.maximum_quantity,
        instrument.quantity_step,
    )

    capped_by_maximum = normalized_quantity > maximum_quantity

    if capped_by_maximum:
        normalized_quantity = maximum_quantity

    if (
        normalized_quantity <= ZERO
        or normalized_quantity < instrument.minimum_quantity
    ):
        return PositionSizingResult(
            available=False,
            unavailable_reason=(
                PositionSizingUnavailableReason.POSITION_SIZE_BELOW_MINIMUM
            ),
            risk_budget_amount=risk_budget_amount,
            stop_distance=stop_distance,
            stop_ticks=stop_ticks,
            loss_per_quantity=loss_per_quantity,
            raw_quantity=raw_quantity,
            capped_by_maximum=capped_by_maximum,
        )

    estimated_loss_at_stop = (
        normalized_quantity * loss_per_quantity
    )

    return PositionSizingResult(
        available=True,
        risk_budget_amount=risk_budget_amount,
        stop_distance=stop_distance,
        stop_ticks=stop_ticks,
        loss_per_quantity=loss_per_quantity,
        raw_quantity=raw_quantity,
        normalized_quantity=normalized_quantity,
        estimated_loss_at_stop=estimated_loss_at_stop,
        capped_by_maximum=capped_by_maximum,
    )
