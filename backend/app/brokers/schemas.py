from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class BrokerSchema(BaseModel):
    """Base configuration for normalized broker data."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class BrokerType(StrEnum):
    SIMULATED = "simulated"
    PRIMEXBT_MT5 = "primexbt_mt5"
    BINANCE = "binance"


class AccountMode(StrEnum):
    DEMO = "demo"
    LIVE = "live"
    CONTEST = "contest"
    UNKNOWN = "unknown"


class AssetClass(StrEnum):
    FOREX = "forex"
    METAL = "metal"
    ENERGY = "energy"
    COMMODITY = "commodity"
    INDEX = "index"
    CRYPTO = "crypto"
    EQUITY = "equity"
    ETF = "etf"
    OTHER = "other"


class MarketType(StrEnum):
    CFD = "cfd"
    SPOT = "spot"
    MARGIN = "margin"
    FUTURES = "futures"
    OTHER = "other"


class PositionSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class BrokerHealth(BrokerSchema):
    connection_id: str
    broker_type: BrokerType

    connected: bool
    read_only: bool

    message: str

    checked_at: datetime


class BrokerAccount(BrokerSchema):
    connection_id: str
    broker_type: BrokerType

    account_id: str
    account_mode: AccountMode

    server: str | None = None
    company: str | None = None

    currency: str

    balance: float
    equity: float

    margin: float = 0.0
    free_margin: float = 0.0
    margin_level: float | None = None

    leverage: int | None = None

    trade_allowed: bool = False
    expert_trading_allowed: bool = False


class Instrument(BrokerSchema):
    """
    Broker-independent representation of a tradable instrument.

    `symbol` is Trade Command Center's normalized symbol.

    `broker_symbol` is the exact native symbol used by the broker.
    """

    symbol: str
    broker_symbol: str

    display_name: str
    description: str = ""

    broker_type: BrokerType

    asset_class: AssetClass
    market_type: MarketType

    base_currency: str | None = None
    quote_currency: str | None = None
    profit_currency: str | None = None
    margin_currency: str | None = None

    digits: int = Field(ge=0)
    point: float = Field(gt=0)

    tick_size: float = Field(gt=0)

    tick_value: float | None = None
    tick_value_profit: float | None = None
    tick_value_loss: float | None = None

    contract_size: float | None = None

    minimum_quantity: float = Field(ge=0)
    maximum_quantity: float = Field(gt=0)
    quantity_step: float = Field(gt=0)

    quantity_limit: float | None = None

    stops_level: int = Field(default=0, ge=0)
    freeze_level: int = Field(default=0, ge=0)

    visible: bool = True
    tradable: bool = True


class Quote(BrokerSchema):
    symbol: str
    broker_symbol: str

    bid: float | None = None
    ask: float | None = None
    last: float | None = None

    spread: float | None = None

    timestamp: datetime


class Candle(BrokerSchema):
    symbol: str
    broker_symbol: str

    timeframe: str
    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float = 0.0
    spread: float | None = None


class BrokerPosition(BrokerSchema):
    position_id: str

    symbol: str
    broker_symbol: str

    side: PositionSide
    quantity: float

    open_price: float
    current_price: float

    stop_loss: float | None = None
    take_profit: float | None = None

    profit: float
    swap: float = 0.0

    opened_at: datetime | None = None

    comment: str | None = None


class BrokerOrder(BrokerSchema):
    order_id: str

    symbol: str
    broker_symbol: str

    side: PositionSide
    order_type: str

    initial_quantity: float
    remaining_quantity: float

    requested_price: float | None = None

    stop_loss: float | None = None
    take_profit: float | None = None

    status: str

    created_at: datetime | None = None

    comment: str | None = None