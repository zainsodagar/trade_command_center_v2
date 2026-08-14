from pydantic import BaseModel, ConfigDict


class BrokerCapabilities(BaseModel):
    """
    Features supported by a broker connection.

    Trading features remain disabled until the appropriate
    execution phases are completed and tested.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    account_information: bool = True
    instruments: bool = True
    quotes: bool = True
    candles: bool = True
    positions: bool = True
    open_orders: bool = True

    supports_cfds: bool = False
    supports_spot: bool = False
    supports_margin: bool = False
    supports_futures: bool = False

    market_orders: bool = False
    limit_orders: bool = False
    stop_orders: bool = False

    order_modification: bool = False
    order_cancellation: bool = False

    position_closing: bool = False
    partial_closing: bool = False
    trailing_stop: bool = False

    order_book: bool = False

    read_only: bool = True