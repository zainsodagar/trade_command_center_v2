from backend.app.brokers.adapters.simulated import SimulatedBrokerAdapter
from backend.app.brokers.capabilities import BrokerCapabilities
from backend.app.brokers.manager import BrokerManager
from backend.app.brokers.schemas import (
    AssetClass,
    BrokerAccount,
    BrokerHealth,
    BrokerOrder,
    BrokerPosition,
    Candle,
    Instrument,
    Quote,
)


class BrokerService:
    """
    Application service for broker operations.

    API routes and future application services should use this layer
    instead of interacting with BrokerManager or broker adapters
    directly.
    """

    def __init__(
        self,
        manager: BrokerManager | None = None,
    ) -> None:
        self.manager = (
            manager
            if manager is not None
            else BrokerManager()
        )

    def create_simulated_connection(
        self,
        connection_id: str,
        *,
        connect: bool = True,
        replace: bool = False,
    ) -> BrokerHealth:
        adapter = SimulatedBrokerAdapter(
            connection_id,
        )

        self.manager.register(
            adapter,
            replace=replace,
        )

        if connect:
            return adapter.connect()

        return adapter.health()

    def remove_connection(
        self,
        connection_id: str,
    ) -> BrokerHealth:
        adapter = self.manager.unregister(
            connection_id,
            disconnect=True,
        )

        return adapter.health()

    def connect(
        self,
        connection_id: str,
    ) -> BrokerHealth:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.connect()

    def disconnect(
        self,
        connection_id: str,
    ) -> BrokerHealth:
        adapter = self.manager.get(
            connection_id,
        )

        adapter.disconnect()

        return adapter.health()

    def get_health(
        self,
        connection_id: str,
    ) -> BrokerHealth:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.health()

    def get_all_health(
        self,
    ) -> list[BrokerHealth]:
        return [
            adapter.health()
            for adapter in self.manager.list_connections()
        ]

    def get_capabilities(
        self,
        connection_id: str,
    ) -> BrokerCapabilities:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.capabilities

    def get_account(
        self,
        connection_id: str,
    ) -> BrokerAccount:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_account()

    def get_instruments(
        self,
        connection_id: str,
        *,
        search: str | None = None,
        asset_class: AssetClass | None = None,
        tradable_only: bool = True,
    ) -> list[Instrument]:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_instruments(
            search=search,
            asset_class=asset_class,
            tradable_only=tradable_only,
        )

    def get_instrument(
        self,
        connection_id: str,
        symbol: str,
    ) -> Instrument:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_instrument(
            symbol,
        )

    def get_quote(
        self,
        connection_id: str,
        symbol: str,
    ) -> Quote:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_quote(
            symbol,
        )

    def get_candles(
        self,
        connection_id: str,
        symbol: str,
        timeframe: str,
        *,
        count: int = 200,
    ) -> list[Candle]:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_candles(
            symbol,
            timeframe,
            count=count,
        )

    def get_positions(
        self,
        connection_id: str,
    ) -> list[BrokerPosition]:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_positions()

    def get_open_orders(
        self,
        connection_id: str,
    ) -> list[BrokerOrder]:
        adapter = self.manager.get(
            connection_id,
        )

        return adapter.get_open_orders()

    def connection_ids(
        self,
    ) -> list[str]:
        return self.manager.connection_ids()

    def connection_count(
        self,
    ) -> int:
        return len(
            self.manager
        )