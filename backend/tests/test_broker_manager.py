import pytest

from backend.app.brokers.adapters.simulated import SimulatedBrokerAdapter
from backend.app.brokers.manager import (
    BrokerAlreadyRegisteredError,
    BrokerManager,
    BrokerNotRegisteredError,
)
from backend.app.brokers.schemas import BrokerType


def test_register_and_get_broker() -> None:
    manager = BrokerManager()

    adapter = SimulatedBrokerAdapter(
        "sim-main",
    )

    registered = manager.register(
        adapter,
    )

    assert registered is adapter
    assert len(manager) == 1

    assert manager.contains(
        "sim-main"
    ) is True

    assert manager.get(
        "sim-main"
    ) is adapter

    assert manager.connection_ids() == [
        "sim-main"
    ]


def test_duplicate_registration_is_rejected() -> None:
    manager = BrokerManager()

    first = SimulatedBrokerAdapter(
        "sim-main",
    )

    second = SimulatedBrokerAdapter(
        "sim-main",
    )

    manager.register(
        first,
    )

    with pytest.raises(
        BrokerAlreadyRegisteredError,
        match="already registered",
    ):
        manager.register(
            second,
        )


def test_registration_can_replace_existing_broker() -> None:
    manager = BrokerManager()

    first = SimulatedBrokerAdapter(
        "sim-main",
    )

    second = SimulatedBrokerAdapter(
        "sim-main",
    )

    first.connect()

    manager.register(
        first,
    )

    manager.register(
        second,
        replace=True,
    )

    assert first.health().connected is False

    assert manager.get(
        "sim-main"
    ) is second

    assert len(manager) == 1


def test_unknown_connection_is_rejected() -> None:
    manager = BrokerManager()

    with pytest.raises(
        BrokerNotRegisteredError,
        match="not registered",
    ):
        manager.get(
            "missing-broker",
        )

    with pytest.raises(
        BrokerNotRegisteredError,
        match="cannot be empty",
    ):
        manager.get(
            "   ",
        )


def test_unregister_disconnects_and_removes_broker() -> None:
    manager = BrokerManager()

    adapter = SimulatedBrokerAdapter(
        "sim-main",
    )

    adapter.connect()

    manager.register(
        adapter,
    )

    removed = manager.unregister(
        "sim-main",
    )

    assert removed is adapter

    assert removed.health().connected is False

    assert manager.contains(
        "sim-main"
    ) is False

    assert len(manager) == 0


def test_list_by_broker_type() -> None:
    manager = BrokerManager()

    first = SimulatedBrokerAdapter(
        "sim-one",
    )

    second = SimulatedBrokerAdapter(
        "sim-two",
    )

    manager.register_many(
        [
            first,
            second,
        ]
    )

    simulated = manager.list_by_broker_type(
        BrokerType.SIMULATED,
    )

    assert len(simulated) == 2

    assert {
        adapter.connection_id
        for adapter in simulated
    } == {
        "sim-one",
        "sim-two",
    }

    assert manager.list_by_broker_type(
        BrokerType.PRIMEXBT_MT5,
    ) == []


def test_clear_disconnects_all_brokers() -> None:
    manager = BrokerManager()

    first = SimulatedBrokerAdapter(
        "sim-one",
    )

    second = SimulatedBrokerAdapter(
        "sim-two",
    )

    first.connect()
    second.connect()

    manager.register_many(
        [
            first,
            second,
        ]
    )

    assert len(manager) == 2

    manager.clear()

    assert len(manager) == 0

    assert first.health().connected is False
    assert second.health().connected is False