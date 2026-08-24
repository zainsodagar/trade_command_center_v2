from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


class RiskSchema(BaseModel):
    """Immutable base model for deterministic risk-domain data."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )


class RiskDecision(StrEnum):
    """Final deterministic result of a risk evaluation."""

    ALLOW = "allow"
    BLOCK = "block"


class TradeSide(StrEnum):
    """Broker-independent trade direction evaluated by the risk engine."""

    BUY = "buy"
    SELL = "sell"


class RiskViolationCode(StrEnum):
    """Stable machine-readable reasons for blocking a trade candidate."""

    INVALID_ACCOUNT_EQUITY = "invalid_account_equity"
    INVALID_STOP_LOSS = "invalid_stop_loss"

    RISK_PER_TRADE_EXCEEDED = "risk_per_trade_exceeded"
    DAILY_LOSS_LIMIT_REACHED = "daily_loss_limit_reached"
    MAX_OPEN_POSITIONS_REACHED = "max_open_positions_reached"
    MAX_TOTAL_EXPOSURE_EXCEEDED = "max_total_exposure_exceeded"
    EXPOSURE_DATA_UNAVAILABLE = "exposure_data_unavailable"

    INSTRUMENT_NOT_TRADABLE = "instrument_not_tradable"

    POSITION_SIZING_MISMATCH = "position_sizing_mismatch"
    INVALID_QUANTITY_GRID = "invalid_quantity_grid"
    MISSING_TICK_VALUE_LOSS = "missing_tick_value_loss"

    POSITION_SIZE_BELOW_MINIMUM = "position_size_below_minimum"
    POSITION_SIZE_ABOVE_MAXIMUM = "position_size_above_maximum"
    POSITION_SIZE_STEP_MISMATCH = "position_size_step_mismatch"


class RiskLimits(RiskSchema):
    """
    Deterministic limits used by the risk engine.

    Percent values are represented with Decimal so risk calculations do not
    depend on binary floating-point arithmetic.
    """

    risk_per_trade_pct: Decimal = Field(
        gt=ZERO,
        le=ONE_HUNDRED,
    )
    daily_loss_limit_pct: Decimal = Field(
        gt=ZERO,
        le=ONE_HUNDRED,
    )
    max_open_positions: int = Field(
        ge=1,
    )
    max_total_exposure_pct: Decimal = Field(
        gt=ZERO,
    )

    @field_validator(
        "risk_per_trade_pct",
        "daily_loss_limit_pct",
        "max_total_exposure_pct",
    )
    @classmethod
    def validate_finite_decimal(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("risk limits must contain finite decimal values")

        return value


class AccountRiskState(RiskSchema):
    """
    Read-only account state supplied to the deterministic risk engine.

    `daily_loss_amount` is a positive loss amount, not signed PnL.

    `total_exposure_amount` is gross current exposure expressed in the
    account risk currency.

    Equity is intentionally allowed to be zero or negative at schema level.
    The deterministic engine will BLOCK non-positive equity and return the
    machine-readable INVALID_ACCOUNT_EQUITY violation.
    """

    equity: Decimal
    daily_loss_amount: Decimal = Field(
        ge=ZERO,
    )
    open_position_count: int = Field(
        ge=0,
    )
    total_exposure_amount: Decimal = Field(
        ge=ZERO,
    )

    @field_validator(
        "equity",
        "daily_loss_amount",
        "total_exposure_amount",
    )
    @classmethod
    def validate_finite_decimal(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError(
                "account risk state must contain finite decimal values"
            )

        return value


class RiskInstrumentSpec(RiskSchema):
    """
    Broker-independent instrument data required for risk calculations.

    All sizing inputs use Decimal even when the originating broker API
    supplies floating-point values.

    `gross_exposure_per_quantity`, when supplied, is the gross exposure in
    the account risk currency represented by one normalized quantity for
    this risk evaluation. The deterministic risk engine must not infer this
    value from `contract_size` because broker and currency-conversion
    semantics can differ across instruments.
    """

    symbol: str = Field(
        min_length=1,
        max_length=120,
    )
    broker_symbol: str = Field(
        min_length=1,
        max_length=120,
    )

    tradable: bool

    minimum_quantity: Decimal = Field(
        ge=ZERO,
    )
    maximum_quantity: Decimal = Field(
        gt=ZERO,
    )
    quantity_step: Decimal = Field(
        gt=ZERO,
    )

    tick_size: Decimal = Field(
        gt=ZERO,
    )
    tick_value_loss: Decimal | None = Field(
        default=None,
        gt=ZERO,
    )
    contract_size: Decimal | None = Field(
        default=None,
        gt=ZERO,
    )
    gross_exposure_per_quantity: Decimal | None = Field(
        default=None,
        gt=ZERO,
    )

    @field_validator(
        "minimum_quantity",
        "maximum_quantity",
        "quantity_step",
        "tick_size",
        "tick_value_loss",
        "contract_size",
        "gross_exposure_per_quantity",
    )
    @classmethod
    def validate_finite_decimal(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError(
                "instrument risk specification must contain "
                "finite decimal values"
            )

        return value

    @model_validator(mode="after")
    def validate_quantity_range(self) -> "RiskInstrumentSpec":
        if self.minimum_quantity > self.maximum_quantity:
            raise ValueError(
                "minimum quantity cannot exceed maximum quantity"
            )

        return self


class TradeRiskCandidate(RiskSchema):
    """
    Proposed trade data supplied for deterministic risk evaluation.

    This model describes a candidate only. It does not place, submit,
    transmit, or execute an order.
    """

    symbol: str = Field(
        min_length=1,
        max_length=120,
    )
    broker_symbol: str = Field(
        min_length=1,
        max_length=120,
    )

    side: TradeSide

    entry_price: Decimal = Field(
        gt=ZERO,
    )
    stop_loss_price: Decimal = Field(
        gt=ZERO,
    )
    take_profit_price: Decimal | None = Field(
        default=None,
        gt=ZERO,
    )

    @field_validator(
        "entry_price",
        "stop_loss_price",
        "take_profit_price",
    )
    @classmethod
    def validate_finite_decimal(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError(
                "trade candidate must contain finite decimal prices"
            )

        return value


class RiskEvaluationInput(RiskSchema):
    """
    Complete immutable input to one deterministic risk evaluation.

    No broker client, MT5 object, HTTP client, credentials, or execution
    mechanism is permitted in this contract.
    """

    limits: RiskLimits
    account: AccountRiskState
    instrument: RiskInstrumentSpec
    trade: TradeRiskCandidate

    @model_validator(mode="after")
    def validate_instrument_identity(self) -> "RiskEvaluationInput":
        if self.trade.symbol != self.instrument.symbol:
            raise ValueError(
                "trade symbol must match instrument symbol"
            )

        if self.trade.broker_symbol != self.instrument.broker_symbol:
            raise ValueError(
                "trade broker symbol must match instrument broker symbol"
            )

        return self


class RiskViolation(RiskSchema):
    """One deterministic reason why a risk evaluation was blocked."""

    code: RiskViolationCode
    message: str = Field(
        min_length=1,
        max_length=500,
    )


class RiskCheckResult(RiskSchema):
    """
    Deterministic risk result.

    ALLOW results cannot contain violations.
    BLOCK results must contain at least one violation.
    """

    decision: RiskDecision
    violations: tuple[RiskViolation, ...] = ()

    @model_validator(mode="after")
    def validate_decision_consistency(self) -> "RiskCheckResult":
        if self.decision is RiskDecision.ALLOW and self.violations:
            raise ValueError(
                "ALLOW risk results cannot contain violations"
            )

        if self.decision is RiskDecision.BLOCK and not self.violations:
            raise ValueError(
                "BLOCK risk results must contain at least one violation"
            )

        return self

    @property
    def allowed(self) -> bool:
        return self.decision is RiskDecision.ALLOW
