from collections.abc import Iterable

from backend.app.brokers.adapters.base import BrokerAdapter
from backend.app.brokers.schemas import BrokerType


class BrokerManagerError(RuntimeError):
    """Base error raised by the broker manager."""


class BrokerAlreadyRegisteredError(BrokerManagerError):
    """Raised when a connection ID is already registered."""


class BrokerNotRegisteredError(BrokerManagerError):
    """Raised when a connection ID is not registered."""


class BrokerManager:
    """
    Central registry for active broker adapters.

    Application services should obtain broker adapters through this
    manager rather than constructing broker-specific adapters directly.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, BrokerAdapter] = {}

    def register(
        self,
        adapter: BrokerAdapter,
        *,
        replace: bool = False,
    ) -> BrokerAdapter:
        connection_id = adapter.connection_id

        if (
            connection_id in self._adapters
            and not replace
        ):
            raise BrokerAlreadyRegisteredError(
                f"Broker connection already registered: {connection_id}"
            )

        existing = self._adapters.get(
            connection_id
        )

        if existing is not None and replace:
            existing.disconnect()

        self._adapters[connection_id] = adapter

        return adapter

    def unregister(
        self,
        connection_id: str,
        *,
        disconnect: bool = True,
    ) -> BrokerAdapter:
        adapter = self.get(
            connection_id
        )

        if disconnect:
            adapter.disconnect()

        del self._adapters[
            adapter.connection_id
        ]

        return adapter

    def get(
        self,
        connection_id: str,
    ) -> BrokerAdapter:
        cleaned_connection_id = (
            connection_id.strip()
        )

        if not cleaned_connection_id:
            raise BrokerNotRegisteredError(
                "Broker connection ID cannot be empty"
            )

        try:
            return self._adapters[
                cleaned_connection_id
            ]
        except KeyError as exc:
            raise BrokerNotRegisteredError(
                "Broker connection not registered: "
                f"{cleaned_connection_id}"
            ) from exc

    def contains(
        self,
        connection_id: str,
    ) -> bool:
        cleaned_connection_id = (
            connection_id.strip()
        )

        if not cleaned_connection_id:
            return False

        return (
            cleaned_connection_id
            in self._adapters
        )

    def list_connections(
        self,
    ) -> list[BrokerAdapter]:
        return list(
            self._adapters.values()
        )

    def list_by_broker_type(
        self,
        broker_type: BrokerType,
    ) -> list[BrokerAdapter]:
        return [
            adapter
            for adapter in self._adapters.values()
            if adapter.broker_type
            == broker_type
        ]

    def connection_ids(
        self,
    ) -> list[str]:
        return list(
            self._adapters.keys()
        )

    def register_many(
        self,
        adapters: Iterable[BrokerAdapter],
        *,
        replace: bool = False,
    ) -> None:
        for adapter in adapters:
            self.register(
                adapter,
                replace=replace,
            )

    def disconnect_all(self) -> None:
        for adapter in self._adapters.values():
            adapter.disconnect()

    def clear(
        self,
        *,
        disconnect: bool = True,
    ) -> None:
        if disconnect:
            self.disconnect_all()

        self._adapters.clear()

    def __len__(self) -> int:
        return len(
            self._adapters
        )