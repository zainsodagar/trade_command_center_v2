from datetime import UTC, datetime

import pytest

from backend.app.brokers.adapters.base import (
    BrokerAdapter,
    BrokerInstrumentNotFoundError,
    BrokerOperationNotSupported,
)
from backend.app.brokers.capabilities import BrokerCapabilities
from backend.app.brokers.schemas import (
    AccountMode,
    AssetClass,
    BrokerAccount,
    BrokerHealth,
    BrokerOrder,
    BrokerPosition,
    BrokerType,
    Candle,
    Instrument,
    MarketType,
    Quote,
)

NOW = datetime(2026, 8, 14, tzinfo=UTC)


class DummyReadOnlyAdapter(BrokerAdapter):
    @property
    def broker_type(self) -> BrokerType:
        return BrokerType.SIMULATED

    @property
    def capabilities(self) -> BrokerCapabilities:
        return BrokerCapabilities()

    def connect(self) -> BrokerHealth:
        return BrokerHealth(
            connection_id=self.connection_id,
            broker_type=self.broker_type,
            connected=True,
            read_only=True,
            message="Dummy broker connected",
            checked_at=NOW,
        )

    def disconnect(self) -> None:
        return None

    def health(self) -> BrokerHealth:
        return self.connect()

    def get_account(self) -> BrokerAccount:
        return BrokerAccount(
            connection_id=self.connection_id,
            broker_type=self.broker_type,
            account_id="SIM-001",
            account_mode=AccountMode.DEMO,
            currency="USD",
            balance=10_000.0,
            equity=10_000.0,
            margin=0.0,
            free_margin=10_000.0,
            margin_level=None,
            leverage=100,
            trade_allowed=False,
            expert_trading_allowed=False,
        )

    def get_instruments(
        self,
        *,
        search: str | None = None,
        asset_class: AssetClass | None = None,
        tradable_only: bool = True,
    ) -> list[Instrument]:
        instrument = Instrument(
            symbol="XAU/USD",
            broker_symbol="XAUUSD",
            display_name="Gold vs US Dollar",
            description="Simulated gold CFD",
            broker_type=self.broker_type,
            asset_class=AssetClass.METAL,
            market_type=MarketType.CFD,
            base_currency="XAU",
            quote_currency="USD",
            profit_currency="USD",
            margin_currency="USD",
            digits=2,
            point=0.01,
            tick_size=0.01,
            tick_value=1.0,
            contract_size=100.0,
            minimum_quantity=0.01,
            maximum_quantity=100.0,
            quantity_step=0.01,
            tradable=True,
        )

        instruments = [instrument]

        if search:
            cleaned_search = search.strip().lower()

            instruments = [
                item
                for item in instruments
                if cleaned_search in item.symbol.lower()
                or cleaned_search in item.broker_symbol.lower()
                or cleaned_search in item.display_name.lower()
            ]

        if asset_class is not None:
            instruments = [
                item
                for item in instruments
                if item.asset_class == asset_class
            ]

        if tradable_only:
            instruments = [
                item
                for item in instruments
                if item.tradable
            ]

        return instruments

    def get_instrument(
        self,
        symbol: str,
    ) -> Instrument:
        cleaned_symbol = symbol.strip().lower()

        for instrument in self.get_instruments(
            tradable_only=False,
        ):
            if cleaned_symbol in {
                instrument.symbol.lower(),
                instrument.broker_symbol.lower(),
            }:
                return instrument

        raise BrokerInstrumentNotFoundError(
            f"Instrument not found: {symbol}"
        )

    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        instrument = self.get_instrument(symbol)

        return Quote(
            symbol=instrument.symbol,
            broker_symbol=instrument.broker_symbol,
            bid=2400.00,
            ask=2400.20,
            last=2400.10,
            spread=0.20,
            timestamp=NOW,
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        count: int = 200,
    ) -> list[Candle]:
        instrument = self.get_instrument(symbol)

        return [
            Candle(
                symbol=instrument.symbol,
                broker_symbol=instrument.broker_symbol,
                timeframe=timeframe,
                timestamp=NOW,
                open=2399.00,
                high=2401.00,
                low=2398.50,
                close=2400.00,
                volume=1000.0,
                spread=0.20,
            )
            for _ in range(count)
        ]

    def get_positions(self) -> list[BrokerPosition]:
        return []

    def get_open_orders(self) -> list[BrokerOrder]:
        return []


def test_adapter_requires_connection_id() -> None:
    with pytest.raises(
        ValueError,
        match="connection_id cannot be empty",
    ):
        DummyReadOnlyAdapter("   ")


def test_read_only_adapter_contract() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    health = adapter.connect()
    account = adapter.get_account()
    instruments = adapter.get_instruments()

    assert health.connected is True
    assert health.read_only is True

    assert account.account_mode == AccountMode.DEMO
    assert account.trade_allowed is False

    assert len(instruments) == 1
    assert instruments[0].symbol == "XAU/USD"
    assert instruments[0].broker_symbol == "XAUUSD"


def test_instrument_filtering() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    results = adapter.get_instruments(
        search="gold",
        asset_class=AssetClass.METAL,
    )

    assert len(results) == 1

    no_results = adapter.get_instruments(
        asset_class=AssetClass.CRYPTO,
    )

    assert no_results == []


def test_get_instrument_accepts_normalized_and_broker_symbol() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    normalized = adapter.get_instrument("XAU/USD")
    native = adapter.get_instrument("XAUUSD")

    assert normalized == native
    assert normalized.symbol == "XAU/USD"


def test_unknown_instrument_is_rejected() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    with pytest.raises(BrokerInstrumentNotFoundError):
        adapter.get_instrument("UNKNOWN")


def test_quote_and_candles_use_normalized_schema() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    quote = adapter.get_quote("XAUUSD")

    candles = adapter.get_candles(
        "XAU/USD",
        "M5",
        count=5,
    )

    assert quote.symbol == "XAU/USD"
    assert quote.broker_symbol == "XAUUSD"

    assert len(candles) == 5
    assert all(candle.timeframe == "M5" for candle in candles)


def test_execution_is_disabled_by_default() -> None:
    adapter = DummyReadOnlyAdapter("simulated-main")

    assert adapter.capabilities.read_only is True
    assert adapter.capabilities.market_orders is False
    assert adapter.capabilities.limit_orders is False

    with pytest.raises(BrokerOperationNotSupported):
        adapter.place_order(
            {
                "symbol": "XAUUSD",
                "side": "buy",
                "quantity": 0.01,
            }
        )

    with pytest.raises(BrokerOperationNotSupported):
        adapter.modify_order(
            "ORDER-001",
            {
                "stop_loss": 2390.0,
            },
        )

    with pytest.raises(BrokerOperationNotSupported):
        adapter.cancel_order("ORDER-001")

    with pytest.raises(BrokerOperationNotSupported):
        adapter.close_position("POSITION-001")
        