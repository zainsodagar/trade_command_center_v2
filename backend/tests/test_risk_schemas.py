from decimal import Decimal

import pytest
from pydantic import ValidationError

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


def make_limits() -> RiskLimits:
    return RiskLimits(
        risk_per_trade_pct=Decimal("1.25"),
        daily_loss_limit_pct=Decimal("5.00"),
        max_open_positions=4,
        max_total_exposure_pct=Decimal("250.00"),
    )


def test_risk_limits_preserve_decimal_values_exactly() -> None:
    limits = make_limits()

    assert limits.risk_per_trade_pct == Decimal("1.25")
    assert limits.daily_loss_limit_pct == Decimal("5.00")
    assert limits.max_total_exposure_pct == Decimal("250.00")
    assert isinstance(limits.risk_per_trade_pct, Decimal)


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("risk_per_trade_pct", Decimal("0")),
        ("risk_per_trade_pct", Decimal("-0.01")),
        ("risk_per_trade_pct", Decimal("100.01")),
        ("daily_loss_limit_pct", Decimal("0")),
        ("daily_loss_limit_pct", Decimal("-1")),
        ("daily_loss_limit_pct", Decimal("101")),
        ("max_total_exposure_pct", Decimal("0")),
        ("max_total_exposure_pct", Decimal("-1")),
    ],
)
def test_risk_limits_reject_invalid_numeric_boundaries(
    field_name: str,
    value: Decimal,
) -> None:
    data = {
        "risk_per_trade_pct": Decimal("1"),
        "daily_loss_limit_pct": Decimal("5"),
        "max_open_positions": 4,
        "max_total_exposure_pct": Decimal("250"),
    }
    data[field_name] = value

    with pytest.raises(ValidationError):
        RiskLimits(**data)


@pytest.mark.parametrize(
    "field_name",
    [
        "risk_per_trade_pct",
        "daily_loss_limit_pct",
        "max_total_exposure_pct",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_risk_limits_reject_non_finite_decimals(
    field_name: str,
    value: Decimal,
) -> None:
    data = {
        "risk_per_trade_pct": Decimal("1"),
        "daily_loss_limit_pct": Decimal("5"),
        "max_open_positions": 4,
        "max_total_exposure_pct": Decimal("250"),
    }
    data[field_name] = value

    with pytest.raises(ValidationError):
        RiskLimits(**data)


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
    ],
)
def test_risk_limits_require_at_least_one_open_position(
    value: int,
) -> None:
    with pytest.raises(ValidationError):
        RiskLimits(
            risk_per_trade_pct=Decimal("1"),
            daily_loss_limit_pct=Decimal("5"),
            max_open_positions=value,
            max_total_exposure_pct=Decimal("250"),
        )


def test_total_exposure_limit_may_exceed_one_hundred_percent() -> None:
    limits = RiskLimits(
        risk_per_trade_pct=Decimal("1"),
        daily_loss_limit_pct=Decimal("5"),
        max_open_positions=4,
        max_total_exposure_pct=Decimal("500"),
    )

    assert limits.max_total_exposure_pct == Decimal("500")


def test_risk_models_are_immutable() -> None:
    limits = make_limits()

    with pytest.raises(ValidationError):
        limits.risk_per_trade_pct = Decimal("2")


def test_risk_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RiskLimits(
            risk_per_trade_pct=Decimal("1"),
            daily_loss_limit_pct=Decimal("5"),
            max_open_positions=4,
            max_total_exposure_pct=Decimal("250"),
            unexpected_setting=True,
        )


def test_allow_result_contains_no_violations() -> None:
    result = RiskCheckResult(
        decision=RiskDecision.ALLOW,
    )

    assert result.allowed is True
    assert result.violations == ()


def test_allow_result_rejects_violations() -> None:
    violation = RiskViolation(
        code=RiskViolationCode.INVALID_STOP_LOSS,
        message="Stop loss is invalid.",
    )

    with pytest.raises(ValidationError):
        RiskCheckResult(
            decision=RiskDecision.ALLOW,
            violations=(violation,),
        )


def test_block_result_requires_at_least_one_violation() -> None:
    with pytest.raises(ValidationError):
        RiskCheckResult(
            decision=RiskDecision.BLOCK,
        )


def test_block_result_preserves_machine_readable_violation() -> None:
    violation = RiskViolation(
        code=RiskViolationCode.MAX_OPEN_POSITIONS_REACHED,
        message="Maximum open-position limit has been reached.",
    )

    result = RiskCheckResult(
        decision=RiskDecision.BLOCK,
        violations=(violation,),
    )

    assert result.allowed is False
    assert result.violations == (violation,)
    assert (
        result.violations[0].code
        is RiskViolationCode.MAX_OPEN_POSITIONS_REACHED
    )

def make_account_state(
    *,
    equity: Decimal = Decimal("10000"),
) -> AccountRiskState:
    return AccountRiskState(
        equity=equity,
        daily_loss_amount=Decimal("125.50"),
        open_position_count=2,
        total_exposure_amount=Decimal("8500.25"),
    )


def make_instrument_spec(
    **overrides: object,
) -> RiskInstrumentSpec:
    data: dict[str, object] = {
        "symbol": "XAUUSD",
        "broker_symbol": "XAUUSD",
        "tradable": True,
        "minimum_quantity": Decimal("0.01"),
        "maximum_quantity": Decimal("100"),
        "quantity_step": Decimal("0.01"),
        "tick_size": Decimal("0.01"),
        "tick_value_loss": Decimal("1.00"),
        "contract_size": Decimal("100"),
    }
    data.update(overrides)

    return RiskInstrumentSpec(**data)


def make_trade_candidate(
    **overrides: object,
) -> TradeRiskCandidate:
    data: dict[str, object] = {
        "symbol": "XAUUSD",
        "broker_symbol": "XAUUSD",
        "side": TradeSide.BUY,
        "entry_price": Decimal("2400.50"),
        "stop_loss_price": Decimal("2390.25"),
        "take_profit_price": Decimal("2425.75"),
    }
    data.update(overrides)

    return TradeRiskCandidate(**data)


@pytest.mark.parametrize(
    "equity",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("-250.75"),
    ],
)
def test_account_risk_state_accepts_non_positive_equity_for_engine_decision(
    equity: Decimal,
) -> None:
    state = make_account_state(equity=equity)

    assert state.equity == equity


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("daily_loss_amount", Decimal("-0.01")),
        ("open_position_count", -1),
        ("total_exposure_amount", Decimal("-0.01")),
    ],
)
def test_account_risk_state_rejects_negative_bounded_values(
    field_name: str,
    value: object,
) -> None:
    data: dict[str, object] = {
        "equity": Decimal("10000"),
        "daily_loss_amount": Decimal("100"),
        "open_position_count": 2,
        "total_exposure_amount": Decimal("5000"),
    }
    data[field_name] = value

    with pytest.raises(ValidationError):
        AccountRiskState(**data)


@pytest.mark.parametrize(
    "field_name",
    [
        "equity",
        "daily_loss_amount",
        "total_exposure_amount",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_account_risk_state_rejects_non_finite_decimals(
    field_name: str,
    value: Decimal,
) -> None:
    data: dict[str, object] = {
        "equity": Decimal("10000"),
        "daily_loss_amount": Decimal("100"),
        "open_position_count": 2,
        "total_exposure_amount": Decimal("5000"),
    }
    data[field_name] = value

    with pytest.raises(ValidationError):
        AccountRiskState(**data)


def test_instrument_spec_preserves_exact_decimal_sizing_values() -> None:
    instrument = make_instrument_spec()

    assert instrument.minimum_quantity == Decimal("0.01")
    assert instrument.maximum_quantity == Decimal("100")
    assert instrument.quantity_step == Decimal("0.01")
    assert instrument.tick_size == Decimal("0.01")
    assert instrument.tick_value_loss == Decimal("1.00")
    assert instrument.contract_size == Decimal("100")


def test_instrument_spec_allows_missing_optional_value_inputs() -> None:
    instrument = make_instrument_spec(
        tick_value_loss=None,
        contract_size=None,
    )

    assert instrument.tick_value_loss is None
    assert instrument.contract_size is None


def test_instrument_spec_rejects_minimum_above_maximum() -> None:
    with pytest.raises(ValidationError):
        make_instrument_spec(
            minimum_quantity=Decimal("5"),
            maximum_quantity=Decimal("1"),
        )


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("minimum_quantity", Decimal("-0.01")),
        ("maximum_quantity", Decimal("0")),
        ("quantity_step", Decimal("0")),
        ("tick_size", Decimal("0")),
        ("tick_value_loss", Decimal("0")),
        ("contract_size", Decimal("0")),
    ],
)
def test_instrument_spec_rejects_invalid_quantity_or_value_inputs(
    field_name: str,
    value: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        make_instrument_spec(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "minimum_quantity",
        "maximum_quantity",
        "quantity_step",
        "tick_size",
        "tick_value_loss",
        "contract_size",
    ],
)
def test_instrument_spec_rejects_non_finite_decimals(
    field_name: str,
) -> None:
    with pytest.raises(ValidationError):
        make_instrument_spec(
            **{field_name: Decimal("NaN")}
        )


@pytest.mark.parametrize(
    "side",
    [
        TradeSide.BUY,
        TradeSide.SELL,
    ],
)
def test_trade_candidate_preserves_exact_prices_and_side(
    side: TradeSide,
) -> None:
    trade = make_trade_candidate(side=side)

    assert trade.side is side
    assert trade.entry_price == Decimal("2400.50")
    assert trade.stop_loss_price == Decimal("2390.25")
    assert trade.take_profit_price == Decimal("2425.75")


@pytest.mark.parametrize(
    "side,entry_price,stop_loss_price",
    [
        (
            TradeSide.BUY,
            Decimal("100"),
            Decimal("100"),
        ),
        (
            TradeSide.BUY,
            Decimal("100"),
            Decimal("101"),
        ),
        (
            TradeSide.SELL,
            Decimal("100"),
            Decimal("100"),
        ),
        (
            TradeSide.SELL,
            Decimal("100"),
            Decimal("99"),
        ),
    ],
)
def test_trade_candidate_allows_stop_geometry_for_engine_to_decide(
    side: TradeSide,
    entry_price: Decimal,
    stop_loss_price: Decimal,
) -> None:
    trade = make_trade_candidate(
        side=side,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
    )

    assert trade.stop_loss_price == stop_loss_price


@pytest.mark.parametrize(
    "field_name",
    [
        "entry_price",
        "stop_loss_price",
        "take_profit_price",
    ],
)
def test_trade_candidate_rejects_non_positive_prices(
    field_name: str,
) -> None:
    with pytest.raises(ValidationError):
        make_trade_candidate(
            **{field_name: Decimal("0")}
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "entry_price",
        "stop_loss_price",
        "take_profit_price",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_trade_candidate_rejects_non_finite_prices(
    field_name: str,
    value: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        make_trade_candidate(
            **{field_name: value}
        )


def test_risk_evaluation_input_accepts_matching_identity() -> None:
    limits = make_limits()
    account = make_account_state()
    instrument = make_instrument_spec()
    trade = make_trade_candidate()

    evaluation = RiskEvaluationInput(
        limits=limits,
        account=account,
        instrument=instrument,
        trade=trade,
    )

    assert evaluation.instrument.symbol == "XAUUSD"
    assert evaluation.trade.symbol == "XAUUSD"
    assert evaluation.instrument.broker_symbol == "XAUUSD"
    assert evaluation.trade.broker_symbol == "XAUUSD"


def test_risk_evaluation_input_rejects_normalized_symbol_mismatch() -> None:
    with pytest.raises(ValidationError):
        RiskEvaluationInput(
            limits=make_limits(),
            account=make_account_state(),
            instrument=make_instrument_spec(),
            trade=make_trade_candidate(
                symbol="BTCUSDT",
            ),
        )


def test_risk_evaluation_input_rejects_broker_symbol_mismatch() -> None:
    with pytest.raises(ValidationError):
        RiskEvaluationInput(
            limits=make_limits(),
            account=make_account_state(),
            instrument=make_instrument_spec(),
            trade=make_trade_candidate(
                broker_symbol="GOLD",
            ),
        )


def test_risk_evaluation_input_rejects_runtime_client_objects() -> None:
    with pytest.raises(ValidationError):
        RiskEvaluationInput(
            limits=make_limits(),
            account=make_account_state(),
            instrument=make_instrument_spec(),
            trade=make_trade_candidate(),
            broker_client=object(),
        )

def test_gross_exposure_per_quantity_preserves_decimal_exactly() -> None:
    instrument = make_instrument_spec(
        gross_exposure_per_quantity=Decimal("12345.6789"),
    )

    assert (
        instrument.gross_exposure_per_quantity
        == Decimal("12345.6789")
    )
    assert isinstance(
        instrument.gross_exposure_per_quantity,
        Decimal,
    )


def test_gross_exposure_per_quantity_may_be_omitted() -> None:
    instrument = make_instrument_spec()

    assert instrument.gross_exposure_per_quantity is None


@pytest.mark.parametrize(
    "value",
    [
        Decimal("0"),
        Decimal("-0.01"),
        Decimal("-100"),
    ],
)
def test_gross_exposure_per_quantity_rejects_non_positive_values(
    value: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        make_instrument_spec(
            gross_exposure_per_quantity=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_gross_exposure_per_quantity_rejects_non_finite_values(
    value: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        make_instrument_spec(
            gross_exposure_per_quantity=value,
        )


def test_contract_size_does_not_imply_gross_exposure() -> None:
    instrument = make_instrument_spec(
        contract_size=Decimal("100000"),
        gross_exposure_per_quantity=None,
    )

    assert instrument.contract_size == Decimal("100000")
    assert instrument.gross_exposure_per_quantity is None


def test_exposure_data_unavailable_violation_code_is_stable() -> None:
    assert (
        RiskViolationCode.EXPOSURE_DATA_UNAVAILABLE.value
        == "exposure_data_unavailable"
    )

def test_missing_tick_value_loss_violation_code_is_stable() -> None:
    assert (
        RiskViolationCode.MISSING_TICK_VALUE_LOSS.value
        == "missing_tick_value_loss"
    )
