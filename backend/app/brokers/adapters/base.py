from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from backend.app.brokers.capabilities import BrokerCapabilities
from backend.app.brokers.schemas import (
    AssetClass,
    BrokerAccount,
    BrokerHealth,
    BrokerOrder,
    BrokerPosition,
    BrokerType,
    Candle,
    Instrument,
    Quote,
)


class BrokerAdapterError(RuntimeError):
    """Base exception for all broker adapter errors."""


class BrokerConnectionError(BrokerAdapterError):
    """Raised when a broker connection cannot be established."""


class BrokerNotConnectedError(BrokerAdapterError):
    """Raised when an operation requires an active connection."""


class BrokerInstrumentNotFoundError(BrokerAdapterError):
    """Raised when a requested broker instrument cannot be found."""


class BrokerOperationNotSupported(BrokerAdapterError):
    """Raised when an adapter does not support an operation."""


class BrokerAdapter(ABC):
    """
    Broker-independent contract for Trade Command Center.

    PrimeXBT MT5, simulated brokers, and future Binance adapters
    must implement this interface instead of exposing broker-specific
    behavior directly to the rest of the application.
    """

    def __init__(self, connection_id: str) -> None:
        cleaned_connection_id = connection_id.strip()

        if not cleaned_connection_id:
            raise ValueError("connection_id cannot be empty")

        self.connection_id = cleaned_connection_id

    @property
    @abstractmethod
    def broker_type(self) -> BrokerType:
        """Return the normalized broker type."""

    @property
    @abstractmethod
    def capabilities(self) -> BrokerCapabilities:
        """Return capabilities supported by the broker adapter."""

    @abstractmethod
    def connect(self) -> BrokerHealth:
        """Establish the broker connection."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the broker connection safely."""

    @abstractmethod
    def health(self) -> BrokerHealth:
        """Return the current broker connection health."""

    @abstractmethod
    def get_account(self) -> BrokerAccount:
        """Return normalized broker account information."""

    @abstractmethod
    def get_instruments(
        self,
        *,
        search: str | None = None,
        asset_class: AssetClass | None = None,
        tradable_only: bool = True,
    ) -> list[Instrument]:
        """Return normalized instruments available through the broker."""

    @abstractmethod
    def get_instrument(
        self,
        symbol: str,
    ) -> Instrument:
        """Return one normalized instrument."""

    @abstractmethod
    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        """Return the latest normalized quote."""

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        count: int = 200,
    ) -> list[Candle]:
        """Return normalized historical candles."""

    @abstractmethod
    def get_positions(self) -> list[BrokerPosition]:
        """Return currently open positions."""

    @abstractmethod
    def get_open_orders(self) -> list[BrokerOrder]:
        """Return currently open pending orders."""

    def place_order(
        self,
        request: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Place an order.

        Disabled by default. Execution-capable adapters must explicitly
        override this method in later execution phases.
        """

        raise BrokerOperationNotSupported(
            f"{self.broker_type.value} order placement is disabled"
        )

    def modify_order(
        self,
        order_id: str,
        changes: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Modify an existing order.

        Disabled by default.
        """

        raise BrokerOperationNotSupported(
            f"{self.broker_type.value} order modification is disabled"
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> Mapping[str, Any]:
        """
        Cancel an existing order.

        Disabled by default.
        """

        raise BrokerOperationNotSupported(
            f"{self.broker_type.value} order cancellation is disabled"
        )

    def close_position(
        self,
        position_id: str,
        *,
        quantity: float | None = None,
    ) -> Mapping[str, Any]:
        """
        Close all or part of an open position.

        Disabled by default.
        """

        raise BrokerOperationNotSupported(
            f"{self.broker_type.value} position closing is disabled"
        )