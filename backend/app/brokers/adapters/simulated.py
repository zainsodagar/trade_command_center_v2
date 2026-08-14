from datetime import UTC, datetime, timedelta
from math import sin

from backend.app.brokers.adapters.base import (
    BrokerAdapter,
    BrokerInstrumentNotFoundError,
    BrokerNotConnectedError,
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


class SimulatedBrokerAdapter(BrokerAdapter):
    """
    Deterministic read-only broker used to validate Trade Command Center.

    This adapter requires no external broker, credentials, network
    connection, or trading account.
    """

    _CAPABILITIES = BrokerCapabilities(
        supports_cfds=True,
        market_orders=False,
        limit_orders=False,
        stop_orders=False,
        order_modification=False,
        order_cancellation=False,
        position_closing=False,
        partial_closing=False,
        trailing_stop=False,
        order_book=False,
        read_only=True,
    )

    _TIMEFRAMES: dict[str, timedelta] = {
        "M1": timedelta(minutes=1),
        "M5": timedelta(minutes=5),
        "M15": timedelta(minutes=15),
        "M30": timedelta(minutes=30),
        "H1": timedelta(hours=1),
        "H4": timedelta(hours=4),
        "D1": timedelta(days=1),
    }

    def __init__(self, connection_id: str) -> None:
        super().__init__(connection_id)

        self._connected = False
        self._instruments = self._build_instruments()

    @property
    def broker_type(self) -> BrokerType:
        return BrokerType.SIMULATED

    @property
    def capabilities(self) -> BrokerCapabilities:
        return self._CAPABILITIES

    def connect(self) -> BrokerHealth:
        self._connected = True

        return self.health()

    def disconnect(self) -> None:
        self._connected = False

    def health(self) -> BrokerHealth:
        if self._connected:
            message = "Simulated broker connected"
        else:
            message = "Simulated broker disconnected"

        return BrokerHealth(
            connection_id=self.connection_id,
            broker_type=self.broker_type,
            connected=self._connected,
            read_only=True,
            message=message,
            checked_at=datetime.now(UTC),
        )

    def get_account(self) -> BrokerAccount:
        self._require_connected()

        return BrokerAccount(
            connection_id=self.connection_id,
            broker_type=self.broker_type,
            account_id="SIM-DEMO-001",
            account_mode=AccountMode.DEMO,
            server="TCC-SIMULATED",
            company="Trade Command Center",
            currency="USD",
            balance=10_000.00,
            equity=10_000.00,
            margin=0.00,
            free_margin=10_000.00,
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
        self._require_connected()

        instruments = list(self._instruments)

        if search:
            cleaned_search = search.strip().lower()

            instruments = [
                instrument
                for instrument in instruments
                if cleaned_search in instrument.symbol.lower()
                or cleaned_search in instrument.broker_symbol.lower()
                or cleaned_search in instrument.display_name.lower()
                or cleaned_search in instrument.description.lower()
            ]

        if asset_class is not None:
            instruments = [
                instrument
                for instrument in instruments
                if instrument.asset_class == asset_class
            ]

        if tradable_only:
            instruments = [
                instrument
                for instrument in instruments
                if instrument.tradable
            ]

        return instruments

    def get_instrument(
        self,
        symbol: str,
    ) -> Instrument:
        self._require_connected()

        cleaned_symbol = symbol.strip().lower()

        for instrument in self._instruments:
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

        bid, ask = self._quote_prices(instrument.symbol)

        return Quote(
            symbol=instrument.symbol,
            broker_symbol=instrument.broker_symbol,
            bid=bid,
            ask=ask,
            last=(bid + ask) / 2,
            spread=ask - bid,
            timestamp=datetime.now(UTC),
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        count: int = 200,
    ) -> list[Candle]:
        instrument = self.get_instrument(symbol)

        normalized_timeframe = timeframe.strip().upper()

        if normalized_timeframe not in self._TIMEFRAMES:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        if count < 1:
            raise ValueError(
                "count must be at least 1"
            )

        if count > 5000:
            raise ValueError(
                "count cannot exceed 5000"
            )

        quote = self.get_quote(symbol)

        if quote.last is None:
            raise RuntimeError(
                f"Simulated quote has no last price: {symbol}"
            )

        interval = self._TIMEFRAMES[normalized_timeframe]
        now = datetime.now(UTC)

        candle_end = self._align_time(
            now,
            interval,
        )

        volatility = self._candle_volatility(
            instrument.symbol,
        )

        candles: list[Candle] = []

        previous_close = quote.last

        for index in range(count):
            reverse_index = count - index

            timestamp = candle_end - (
                interval * reverse_index
            )

            wave = sin(
                index / 4.0
            )

            drift = wave * volatility

            open_price = previous_close
            close_price = open_price + drift

            high_price = max(
                open_price,
                close_price,
            ) + (volatility * 0.35)

            low_price = min(
                open_price,
                close_price,
            ) - (volatility * 0.35)

            candle = Candle(
                symbol=instrument.symbol,
                broker_symbol=instrument.broker_symbol,
                timeframe=normalized_timeframe,
                timestamp=timestamp,
                open=round(
                    open_price,
                    instrument.digits,
                ),
                high=round(
                    high_price,
                    instrument.digits,
                ),
                low=round(
                    low_price,
                    instrument.digits,
                ),
                close=round(
                    close_price,
                    instrument.digits,
                ),
                volume=float(
                    1000 + (index * 25)
                ),
                spread=quote.spread,
            )

            candles.append(candle)
            previous_close = close_price

        return candles

    def get_positions(self) -> list[BrokerPosition]:
        self._require_connected()

        return []

    def get_open_orders(self) -> list[BrokerOrder]:
        self._require_connected()

        return []

    def _require_connected(self) -> None:
        if not self._connected:
            raise BrokerNotConnectedError(
                "Simulated broker is not connected"
            )

    @staticmethod
    def _align_time(
        value: datetime,
        interval: timedelta,
    ) -> datetime:
        interval_seconds = int(
            interval.total_seconds()
        )

        timestamp = int(
            value.timestamp()
        )

        aligned_timestamp = (
            timestamp // interval_seconds
        ) * interval_seconds

        return datetime.fromtimestamp(
            aligned_timestamp,
            tz=UTC,
        )

    @staticmethod
    def _quote_prices(
        symbol: str,
    ) -> tuple[float, float]:
        prices: dict[str, tuple[float, float]] = {
            "EUR/USD": (
                1.09480,
                1.09495,
            ),
            "GBP/USD": (
                1.28720,
                1.28740,
            ),
            "XAU/USD": (
                2412.30,
                2412.55,
            ),
            "WTI/USD": (
                78.42,
                78.47,
            ),
            "NAS100/USD": (
                19850.20,
                19851.00,
            ),
            "BTC/USD": (
                68450.00,
                68462.00,
            ),
        }

        try:
            return prices[symbol]
        except KeyError as exc:
            raise BrokerInstrumentNotFoundError(
                f"No simulated quote configured for {symbol}"
            ) from exc

    @staticmethod
    def _candle_volatility(
        symbol: str,
    ) -> float:
        volatility: dict[str, float] = {
            "EUR/USD": 0.00015,
            "GBP/USD": 0.00020,
            "XAU/USD": 0.75,
            "WTI/USD": 0.08,
            "NAS100/USD": 7.5,
            "BTC/USD": 35.0,
        }

        try:
            return volatility[symbol]
        except KeyError as exc:
            raise BrokerInstrumentNotFoundError(
                f"No simulated candle configuration for {symbol}"
            ) from exc

    def _build_instruments(
        self,
    ) -> list[Instrument]:
        return [
            Instrument(
                symbol="EUR/USD",
                broker_symbol="EURUSD",
                display_name="Euro vs US Dollar",
                description="Simulated forex CFD",
                broker_type=self.broker_type,
                asset_class=AssetClass.FOREX,
                market_type=MarketType.CFD,
                base_currency="EUR",
                quote_currency="USD",
                profit_currency="USD",
                margin_currency="USD",
                digits=5,
                point=0.00001,
                tick_size=0.00001,
                tick_value=1.0,
                contract_size=100_000.0,
                minimum_quantity=0.01,
                maximum_quantity=100.0,
                quantity_step=0.01,
            ),
            Instrument(
                symbol="GBP/USD",
                broker_symbol="GBPUSD",
                display_name="British Pound vs US Dollar",
                description="Simulated forex CFD",
                broker_type=self.broker_type,
                asset_class=AssetClass.FOREX,
                market_type=MarketType.CFD,
                base_currency="GBP",
                quote_currency="USD",
                profit_currency="USD",
                margin_currency="USD",
                digits=5,
                point=0.00001,
                tick_size=0.00001,
                tick_value=1.0,
                contract_size=100_000.0,
                minimum_quantity=0.01,
                maximum_quantity=100.0,
                quantity_step=0.01,
            ),
            Instrument(
                symbol="XAU/USD",
                broker_symbol="XAUUSD",
                display_name="Gold vs US Dollar",
                description="Simulated precious metal CFD",
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
            ),
            Instrument(
                symbol="WTI/USD",
                broker_symbol="USOIL",
                display_name="WTI Crude Oil",
                description="Simulated energy CFD",
                broker_type=self.broker_type,
                asset_class=AssetClass.ENERGY,
                market_type=MarketType.CFD,
                base_currency="WTI",
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
            ),
            Instrument(
                symbol="NAS100/USD",
                broker_symbol="US100",
                display_name="Nasdaq 100 Index",
                description="Simulated index CFD",
                broker_type=self.broker_type,
                asset_class=AssetClass.INDEX,
                market_type=MarketType.CFD,
                quote_currency="USD",
                profit_currency="USD",
                margin_currency="USD",
                digits=2,
                point=0.01,
                tick_size=0.01,
                tick_value=1.0,
                contract_size=1.0,
                minimum_quantity=0.01,
                maximum_quantity=1000.0,
                quantity_step=0.01,
            ),
            Instrument(
                symbol="BTC/USD",
                broker_symbol="BTCUSD",
                display_name="Bitcoin vs US Dollar",
                description="Simulated cryptocurrency CFD",
                broker_type=self.broker_type,
                asset_class=AssetClass.CRYPTO,
                market_type=MarketType.CFD,
                base_currency="BTC",
                quote_currency="USD",
                profit_currency="USD",
                margin_currency="USD",
                digits=2,
                point=0.01,
                tick_size=0.01,
                tick_value=0.01,
                contract_size=1.0,
                minimum_quantity=0.01,
                maximum_quantity=100.0,
                quantity_step=0.01,
            ),
        ]