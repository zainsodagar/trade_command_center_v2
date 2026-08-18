from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from execution_agent.app.core.config import get_agent_settings
from execution_agent.app.mt5.client import (
    MAX_CANDLE_COUNT,
    MT5_TIMEFRAMES,
    MT5AccountSnapshot,
    MT5CandleSeriesSnapshot,
    MT5CandleSnapshot,
    MT5Client,
    MT5ClientError,
    MT5InstrumentSnapshot,
    MT5QuoteSnapshot,
)
from execution_agent.app.mt5.status import MT5Status, get_mt5_status

settings = get_agent_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Windows MT5 agent for Trade Command Center V2.",
)



class MT5AccountResponse(BaseModel):
    """Detailed read-only MT5 account state."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    masked_login: str

    trade_mode: str

    server: str
    company: str
    currency: str
    currency_digits: int

    leverage: int
    limit_orders: int

    trade_allowed: bool
    trade_expert: bool
    fifo_close: bool

    margin_mode: int
    margin_so_mode: int

    balance: float
    credit: float
    profit: float
    equity: float

    margin: float
    margin_free: float
    margin_level: float

    margin_so_call: float
    margin_so_so: float

    margin_initial: float
    margin_maintenance: float

    assets: float
    liabilities: float
    commission_blocked: float

class MT5InstrumentResponse(BaseModel):
    """Read-only broker instrument metadata."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    broker_symbol: str
    broker_path: str
    broker_group: str

    description: str

    currency_base: str
    currency_profit: str
    currency_margin: str

    digits: int
    point: float

    contract_size: float

    volume_min: float
    volume_max: float
    volume_step: float

    trade_mode: str
    trade_calc_mode: int
    order_mode: int

    new_order_allowed: bool
    reference_only: bool

    visible: bool
    selected: bool

class MT5QuoteResponse(BaseModel):
    """Latest available read-only MT5 broker tick."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    broker_symbol: str
    broker_path: str
    broker_group: str

    digits: int
    point: float

    trade_mode: str
    new_order_allowed: bool
    reference_only: bool

    visible: bool
    selected: bool

    quote_available: bool

    tick_time: datetime | None
    tick_time_msc: int | None

    bid: float | None
    ask: float | None
    last: float | None

    volume: int | None
    volume_real: float | None

    flags: int | None

    spread: float | None
    spread_points: float | None

    unavailable_reason: str | None

    error_code: int | None
    error_message: str | None


class MT5CandleResponse(BaseModel):
    """One read-only MT5 OHLC candle."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    bar_time: datetime

    open: float
    high: float
    low: float
    close: float

    tick_volume: int
    spread: int
    real_volume: int


class MT5CandleSeriesResponse(BaseModel):
    """Read-only MT5 OHLC candle series."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    broker_symbol: str
    broker_path: str
    broker_group: str

    digits: int
    point: float

    trade_mode: str
    new_order_allowed: bool
    reference_only: bool

    visible_before: bool
    selected_before: bool

    visible_after: bool
    selected_after: bool

    timeframe: str
    count_requested: int

    candles_available: bool
    candle_count: int

    oldest_candle_time: datetime | None
    latest_candle_time: datetime | None

    candles: list[MT5CandleResponse]

    unavailable_reason: str | None

    error_code: int | None
    error_message: str | None


def account_response(
    account: MT5AccountSnapshot,
) -> MT5AccountResponse:
    return MT5AccountResponse(
        masked_login=account.masked_login,
        trade_mode=account.trade_mode,
        server=account.server,
        company=account.company,
        currency=account.currency,
        currency_digits=account.currency_digits,
        leverage=account.leverage,
        limit_orders=account.limit_orders,
        trade_allowed=account.trade_allowed,
        trade_expert=account.trade_expert,
        fifo_close=account.fifo_close,
        margin_mode=account.margin_mode,
        margin_so_mode=account.margin_so_mode,
        balance=account.balance,
        credit=account.credit,
        profit=account.profit,
        equity=account.equity,
        margin=account.margin,
        margin_free=account.margin_free,
        margin_level=account.margin_level,
        margin_so_call=account.margin_so_call,
        margin_so_so=account.margin_so_so,
        margin_initial=account.margin_initial,
        margin_maintenance=account.margin_maintenance,
        assets=account.assets,
        liabilities=account.liabilities,
        commission_blocked=account.commission_blocked,
    )

def instrument_response(
    instrument: MT5InstrumentSnapshot,
) -> MT5InstrumentResponse:
    return MT5InstrumentResponse(
        broker_symbol=instrument.broker_symbol,
        broker_path=instrument.broker_path,
        broker_group=instrument.broker_group,
        description=instrument.description,
        currency_base=instrument.currency_base,
        currency_profit=instrument.currency_profit,
        currency_margin=instrument.currency_margin,
        digits=instrument.digits,
        point=instrument.point,
        contract_size=instrument.contract_size,
        volume_min=instrument.volume_min,
        volume_max=instrument.volume_max,
        volume_step=instrument.volume_step,
        trade_mode=instrument.trade_mode,
        trade_calc_mode=instrument.trade_calc_mode,
        order_mode=instrument.order_mode,
        new_order_allowed=instrument.new_order_allowed,
        reference_only=instrument.reference_only,
        visible=instrument.visible,
        selected=instrument.selected,
    )

def quote_response(
    quote: MT5QuoteSnapshot,
) -> MT5QuoteResponse:
    return MT5QuoteResponse(
        broker_symbol=quote.broker_symbol,
        broker_path=quote.broker_path,
        broker_group=quote.broker_group,
        digits=quote.digits,
        point=quote.point,
        trade_mode=quote.trade_mode,
        new_order_allowed=quote.new_order_allowed,
        reference_only=quote.reference_only,
        visible=quote.visible,
        selected=quote.selected,
        quote_available=quote.quote_available,
        tick_time=quote.tick_time,
        tick_time_msc=quote.tick_time_msc,
        bid=quote.bid,
        ask=quote.ask,
        last=quote.last,
        volume=quote.volume,
        volume_real=quote.volume_real,
        flags=quote.flags,
        spread=quote.spread,
        spread_points=quote.spread_points,
        unavailable_reason=quote.unavailable_reason,
        error_code=quote.error_code,
        error_message=quote.error_message,
    )



def candle_response(
    candle: MT5CandleSnapshot,
) -> MT5CandleResponse:
    return MT5CandleResponse(
        bar_time=candle.bar_time,
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        tick_volume=candle.tick_volume,
        spread=candle.spread,
        real_volume=candle.real_volume,
    )


def candle_series_response(
    series: MT5CandleSeriesSnapshot,
) -> MT5CandleSeriesResponse:
    return MT5CandleSeriesResponse(
        broker_symbol=series.broker_symbol,
        broker_path=series.broker_path,
        broker_group=series.broker_group,
        digits=series.digits,
        point=series.point,
        trade_mode=series.trade_mode,
        new_order_allowed=series.new_order_allowed,
        reference_only=series.reference_only,
        visible_before=series.visible_before,
        selected_before=series.selected_before,
        visible_after=series.visible_after,
        selected_after=series.selected_after,
        timeframe=series.timeframe,
        count_requested=series.count_requested,
        candles_available=series.candles_available,
        candle_count=series.candle_count,
        oldest_candle_time=series.oldest_candle_time,
        latest_candle_time=series.latest_candle_time,
        candles=[
            candle_response(candle)
            for candle in series.candles
        ],
        unavailable_reason=series.unavailable_reason,
        error_code=series.error_code,
        error_message=series.error_message,
    )

def filter_instruments(
    instruments: tuple[MT5InstrumentSnapshot, ...],
    *,
    broker_group: str | None,
    trade_mode: str | None,
    new_order_allowed: bool | None,
    reference_only: bool | None,
) -> tuple[MT5InstrumentSnapshot, ...]:
    filtered = instruments

    if broker_group is not None:
        wanted_group = broker_group.casefold()

        filtered = tuple(
            instrument
            for instrument in filtered
            if instrument.broker_group.casefold()
            == wanted_group
        )

    if trade_mode is not None:
        wanted_trade_mode = trade_mode.casefold()

        filtered = tuple(
            instrument
            for instrument in filtered
            if instrument.trade_mode.casefold()
            == wanted_trade_mode
        )

    if new_order_allowed is not None:
        filtered = tuple(
            instrument
            for instrument in filtered
            if instrument.new_order_allowed
            is new_order_allowed
        )

    if reference_only is not None:
        filtered = tuple(
            instrument
            for instrument in filtered
            if instrument.reference_only
            is reference_only
        )

    return filtered


@app.get("/health", tags=["system"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/v1/agent/status", tags=["system"])
def agent_status() -> dict[str, object]:
    mt5_status = get_mt5_status()

    return {
        "agent": "online",
        "mt5_enabled": mt5_status.enabled,
        "mt5_connected": mt5_status.connected,
        "execution_enabled": mt5_status.execution_enabled,
        "live_trading_enabled": mt5_status.live_trading_enabled,
    }


@app.get(
    "/api/v1/mt5/status",
    tags=["mt5"],
    response_model=MT5Status,
)
def mt5_status() -> MT5Status:
    return get_mt5_status()


@app.get(
    "/api/v1/mt5/instruments",
    tags=["mt5"],
    response_model=list[MT5InstrumentResponse],
)
def mt5_instruments(
    broker_group: str | None = None,
    trade_mode: str | None = None,
    new_order_allowed: bool | None = None,
    reference_only: bool | None = None,
) -> list[MT5InstrumentResponse]:
    active_settings = get_agent_settings()

    if not active_settings.mt5_enabled:
        raise HTTPException(
            status_code=503,
            detail="MT5 integration is disabled",
        )

    if active_settings.execution_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only instrument discovery requires "
                "execution_enabled=false"
            ),
        )

    if active_settings.live_trading_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only instrument discovery requires "
                "live_trading_enabled=false"
            ),
        )

    client = MT5Client(
        settings=active_settings,
    )

    try:
        client.initialize()

        account = client.get_account_snapshot()

        if account.trade_mode != "demo":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Phase 4 instrument discovery requires "
                    f"a demo MT5 account; detected {account.trade_mode}"
                ),
            )

        instruments = client.get_instrument_snapshots()

    except HTTPException:
        raise

    except MT5ClientError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"MT5 instrument discovery failed: {exc}",
        ) from exc

    finally:
        client.shutdown()

    instruments = filter_instruments(
        instruments,
        broker_group=broker_group,
        trade_mode=trade_mode,
        new_order_allowed=new_order_allowed,
        reference_only=reference_only,
    )

    return [
        instrument_response(instrument)
        for instrument in instruments
    ]


@app.get(
    "/api/v1/mt5/quote",
    tags=["mt5"],
    response_model=MT5QuoteResponse,
)
def mt5_quote(
    broker_symbol: str,
) -> MT5QuoteResponse:
    active_settings = get_agent_settings()

    if not active_settings.mt5_enabled:
        raise HTTPException(
            status_code=503,
            detail="MT5 integration is disabled",
        )

    if active_settings.execution_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only quote access requires "
                "execution_enabled=false"
            ),
        )

    if active_settings.live_trading_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only quote access requires "
                "live_trading_enabled=false"
            ),
        )

    wanted_symbol = broker_symbol.strip()

    if not wanted_symbol:
        raise HTTPException(
            status_code=422,
            detail="broker_symbol is required",
        )

    client = MT5Client(
        settings=active_settings,
    )

    try:
        client.initialize()

        account = client.get_account_snapshot()

        if account.trade_mode != "demo":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Phase 4 quote access requires "
                    f"a demo MT5 account; detected {account.trade_mode}"
                ),
            )

        instruments = client.get_instrument_snapshots()

        instrument_exists = any(
            instrument.broker_symbol == wanted_symbol
            for instrument in instruments
        )

        if not instrument_exists:
            raise HTTPException(
                status_code=404,
                detail=(
                    "MT5 broker symbol not found: "
                    f"{wanted_symbol}"
                ),
            )

        quote = client.get_quote_snapshot(
            wanted_symbol
        )

    except HTTPException:
        raise

    except MT5ClientError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"MT5 quote retrieval failed: {exc}",
        ) from exc

    finally:
        client.shutdown()

    return quote_response(
        quote
    )


@app.get(
    "/api/v1/mt5/candles",
    tags=["mt5"],
    response_model=MT5CandleSeriesResponse,
)
def mt5_candles(
    broker_symbol: str,
    timeframe: str = "M1",
    count: int = 100,
) -> MT5CandleSeriesResponse:
    active_settings = get_agent_settings()

    if not active_settings.mt5_enabled:
        raise HTTPException(
            status_code=503,
            detail="MT5 integration is disabled",
        )

    if active_settings.execution_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only candle access requires "
                "execution_enabled=false"
            ),
        )

    if active_settings.live_trading_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only candle access requires "
                "live_trading_enabled=false"
            ),
        )

    wanted_symbol = broker_symbol.strip()

    if not wanted_symbol:
        raise HTTPException(
            status_code=422,
            detail="broker_symbol is required",
        )

    wanted_timeframe = timeframe.strip().upper()

    if not wanted_timeframe:
        raise HTTPException(
            status_code=422,
            detail="timeframe is required",
        )

    if wanted_timeframe not in MT5_TIMEFRAMES:
        supported = ", ".join(
            MT5_TIMEFRAMES
        )

        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported MT5 timeframe: "
                f"{wanted_timeframe}. "
                f"Supported timeframes: {supported}"
            ),
        )

    if count < 1 or count > MAX_CANDLE_COUNT:
        raise HTTPException(
            status_code=422,
            detail=(
                "MT5 candle count must be between "
                f"1 and {MAX_CANDLE_COUNT}"
            ),
        )

    client = MT5Client(
        settings=active_settings,
    )

    try:
        client.initialize()

        account = client.get_account_snapshot()

        if account.trade_mode != "demo":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Phase 4 candle access requires "
                    f"a demo MT5 account; detected {account.trade_mode}"
                ),
            )

        instruments = client.get_instrument_snapshots()

        instrument_exists = any(
            instrument.broker_symbol == wanted_symbol
            for instrument in instruments
        )

        if not instrument_exists:
            raise HTTPException(
                status_code=404,
                detail=(
                    "MT5 broker symbol not found: "
                    f"{wanted_symbol}"
                ),
            )

        series = client.get_candle_series_snapshot(
            wanted_symbol,
            wanted_timeframe,
            count,
        )

    except HTTPException:
        raise

    except MT5ClientError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MT5 candle retrieval failed: "
                f"{exc}"
            ),
        ) from exc

    finally:
        client.shutdown()

    return candle_series_response(
        series
    )


@app.get(
    "/api/v1/mt5/account",
    tags=["mt5"],
    response_model=MT5AccountResponse,
)
def mt5_account() -> MT5AccountResponse:
    active_settings = get_agent_settings()

    if not active_settings.mt5_enabled:
        raise HTTPException(
            status_code=503,
            detail="MT5 integration is disabled",
        )

    if active_settings.execution_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only account access requires "
                "execution_enabled=false"
            ),
        )

    if active_settings.live_trading_enabled:
        raise HTTPException(
            status_code=409,
            detail=(
                "Read-only account access requires "
                "live_trading_enabled=false"
            ),
        )

    client = MT5Client(
        settings=active_settings,
    )

    try:
        client.initialize()

        account = client.get_account_snapshot()

        if account.trade_mode != "demo":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Phase 4 account access requires "
                    f"a demo MT5 account; detected {account.trade_mode}"
                ),
            )

    except HTTPException:
        raise

    except MT5ClientError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "MT5 account retrieval failed: "
                f"{exc}"
            ),
        ) from exc

    finally:
        client.shutdown()

    return account_response(
        account
    )
