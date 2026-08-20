import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import MetaTrader5 as mt5

from execution_agent.app.core.config import AgentSettings, get_agent_settings


class MT5ClientError(RuntimeError):
    """Base error raised by the MT5 client."""


class MT5ConfigurationError(MT5ClientError):
    """Raised when MT5 configuration is missing or invalid."""


class MT5InitializationError(MT5ClientError):
    """Raised when the MT5 terminal cannot be initialized."""


@dataclass(frozen=True)
class MT5TerminalSnapshot:
    package_version: str

    terminal_version: int
    terminal_build: int
    terminal_build_date: str

    connected: bool
    trade_allowed: bool
    trade_api_disabled: bool
    dlls_allowed: bool

    company: str
    terminal_name: str

    terminal_path: str
    data_path: str


@dataclass(frozen=True)
class MT5AccountSnapshot:
    login: int
    masked_login: str

    trade_mode: str

    server: str
    company: str
    currency: str

    leverage: int

    trade_allowed: bool
    trade_expert: bool

    currency_digits: int = 0
    limit_orders: int = 0
    fifo_close: bool = False

    margin_mode: int = 0
    margin_so_mode: int = 0

    balance: float = 0.0
    credit: float = 0.0
    profit: float = 0.0
    equity: float = 0.0

    margin: float = 0.0
    margin_free: float = 0.0
    margin_level: float = 0.0

    margin_so_call: float = 0.0
    margin_so_so: float = 0.0

    margin_initial: float = 0.0
    margin_maintenance: float = 0.0

    assets: float = 0.0
    liabilities: float = 0.0
    commission_blocked: float = 0.0


@dataclass(frozen=True)
class MT5InstrumentSnapshot:
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

@dataclass(frozen=True)
class MT5QuoteSnapshot:
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


MT5_TIMEFRAMES: dict[str, int] = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

MT5_TIMEFRAME_SECONDS: dict[str, int] = {
    "M1": 60,
    "M5": 5 * 60,
    "M15": 15 * 60,
    "M30": 30 * 60,
    "H1": 60 * 60,
    "H4": 4 * 60 * 60,
    "D1": 24 * 60 * 60,
}

MAX_CANDLE_COUNT = 1000

CANDLE_HISTORY_SYNC_ATTEMPTS = 4
CANDLE_HISTORY_SYNC_DELAY_SECONDS = 1.0


@dataclass(frozen=True)
class MT5CandleSnapshot:
    bar_time: datetime

    open: float
    high: float
    low: float
    close: float

    tick_volume: int
    spread: int
    real_volume: int


@dataclass(frozen=True)
class MT5CandleSeriesSnapshot:
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

    candles: tuple[MT5CandleSnapshot, ...]

    unavailable_reason: str | None

    error_code: int | None
    error_message: str | None


class MT5Client:
    """
    Controlled read-only MetaTrader 5 client.

    Phase 4 permits terminal, account, and market-data inspection only.
    No order-placement or execution methods exist here.
    """

    def __init__(
        self,
        settings: AgentSettings | None = None,
    ) -> None:
        self.settings = (
            settings
            if settings is not None
            else get_agent_settings()
        )

        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def validate_configuration(self) -> Path:
        terminal_path = self.settings.mt5_terminal_path

        if not terminal_path:
            raise MT5ConfigurationError(
                "MT5 terminal path is not configured"
            )

        path = Path(terminal_path)

        if not path.is_file():
            raise MT5ConfigurationError(
                f"MT5 terminal not found: {path}"
            )

        if self.settings.execution_enabled:
            raise MT5ConfigurationError(
                "Read-only MT5 client requires "
                "execution_enabled=false"
            )

        if self.settings.live_trading_enabled:
            raise MT5ConfigurationError(
                "Read-only MT5 client requires "
                "live_trading_enabled=false"
            )

        return path

    def initialize(self) -> None:
        if self._initialized:
            return

        terminal_path = self.validate_configuration()

        initialized = mt5.initialize(
            path=str(terminal_path),
        )

        if not initialized:
            error_code, error_message = mt5.last_error()

            raise MT5InitializationError(
                "MT5 initialization failed: "
                f"{error_code} - {error_message}"
            )

        self._initialized = True

    def shutdown(self) -> None:
        if not self._initialized:
            return

        mt5.shutdown()

        self._initialized = False

    def get_terminal_snapshot(
        self,
    ) -> MT5TerminalSnapshot:
        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        version = mt5.version()

        if version is None:
            raise MT5ClientError(
                "MT5 terminal version is unavailable"
            )

        terminal_info = mt5.terminal_info()

        if terminal_info is None:
            error_code, error_message = mt5.last_error()

            raise MT5ClientError(
                "MT5 terminal information is unavailable: "
                f"{error_code} - {error_message}"
            )

        terminal_version, build, build_date = version

        return MT5TerminalSnapshot(
            package_version=mt5.__version__,
            terminal_version=terminal_version,
            terminal_build=build,
            terminal_build_date=build_date,
            connected=terminal_info.connected,
            trade_allowed=terminal_info.trade_allowed,
            trade_api_disabled=terminal_info.tradeapi_disabled,
            dlls_allowed=terminal_info.dlls_allowed,
            company=terminal_info.company,
            terminal_name=terminal_info.name,
            terminal_path=terminal_info.path,
            data_path=terminal_info.data_path,
        )

    def get_account_snapshot(
        self,
    ) -> MT5AccountSnapshot:
        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        account_info = mt5.account_info()

        if account_info is None:
            error_code, error_message = mt5.last_error()

            raise MT5ClientError(
                "MT5 account information is unavailable: "
                f"{error_code} - {error_message}"
            )

        trade_modes = {
            mt5.ACCOUNT_TRADE_MODE_DEMO: "demo",
            mt5.ACCOUNT_TRADE_MODE_CONTEST: "contest",
            mt5.ACCOUNT_TRADE_MODE_REAL: "real",
        }

        trade_mode = trade_modes.get(
            account_info.trade_mode,
            "unknown",
        )

        login_text = str(account_info.login)

        if len(login_text) > 4:
            masked_login = (
                "*" * (len(login_text) - 4)
                + login_text[-4:]
            )
        else:
            masked_login = "****"

        return MT5AccountSnapshot(
            login=account_info.login,
            masked_login=masked_login,
            trade_mode=trade_mode,
            server=account_info.server,
            company=account_info.company,
            currency=account_info.currency,
            currency_digits=account_info.currency_digits,
            limit_orders=account_info.limit_orders,
            fifo_close=account_info.fifo_close,
            margin_mode=account_info.margin_mode,
            margin_so_mode=account_info.margin_so_mode,
            balance=account_info.balance,
            credit=account_info.credit,
            profit=account_info.profit,
            equity=account_info.equity,
            margin=account_info.margin,
            margin_free=account_info.margin_free,
            margin_level=account_info.margin_level,
            margin_so_call=account_info.margin_so_call,
            margin_so_so=account_info.margin_so_so,
            margin_initial=account_info.margin_initial,
            margin_maintenance=account_info.margin_maintenance,
            assets=account_info.assets,
            liabilities=account_info.liabilities,
            commission_blocked=account_info.commission_blocked,
            leverage=account_info.leverage,
            trade_allowed=account_info.trade_allowed,
            trade_expert=account_info.trade_expert,
        )

    def get_instrument_snapshots(
        self,
    ) -> tuple[MT5InstrumentSnapshot, ...]:
        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        symbols = mt5.symbols_get()

        if symbols is None:
            error_code, error_message = mt5.last_error()

            raise MT5ClientError(
                "MT5 instrument catalogue is unavailable: "
                f"{error_code} - {error_message}"
            )

        trade_modes = {
            mt5.SYMBOL_TRADE_MODE_DISABLED: "disabled",
            mt5.SYMBOL_TRADE_MODE_LONGONLY: "long_only",
            mt5.SYMBOL_TRADE_MODE_SHORTONLY: "short_only",
            mt5.SYMBOL_TRADE_MODE_CLOSEONLY: "close_only",
            mt5.SYMBOL_TRADE_MODE_FULL: "full",
        }

        new_order_modes = {
            mt5.SYMBOL_TRADE_MODE_LONGONLY,
            mt5.SYMBOL_TRADE_MODE_SHORTONLY,
            mt5.SYMBOL_TRADE_MODE_FULL,
        }

        snapshots: list[MT5InstrumentSnapshot] = []

        for symbol in symbols:
            broker_path = symbol.path or ""

            broker_group = (
                broker_path.split("\\", 1)[0]
                if broker_path
                else "Unknown"
            )

            trade_mode = trade_modes.get(
                symbol.trade_mode,
                f"unknown_{symbol.trade_mode}",
            )

            new_order_allowed = (
                symbol.trade_mode
                in new_order_modes
            )

            reference_only = (
                broker_group == "RefSymbols"
                and symbol.trade_mode
                == mt5.SYMBOL_TRADE_MODE_DISABLED
            )

            snapshots.append(
                MT5InstrumentSnapshot(
                    broker_symbol=symbol.name,
                    broker_path=broker_path,
                    broker_group=broker_group,
                    description=symbol.description or "",
                    currency_base=symbol.currency_base or "",
                    currency_profit=symbol.currency_profit or "",
                    currency_margin=symbol.currency_margin or "",
                    digits=symbol.digits,
                    point=symbol.point,
                    contract_size=symbol.trade_contract_size,
                    volume_min=symbol.volume_min,
                    volume_max=symbol.volume_max,
                    volume_step=symbol.volume_step,
                    trade_mode=trade_mode,
                    trade_calc_mode=symbol.trade_calc_mode,
                    order_mode=symbol.order_mode,
                    new_order_allowed=new_order_allowed,
                    reference_only=reference_only,
                    visible=symbol.visible,
                    selected=symbol.select,
                )
            )

        return tuple(
            sorted(
                snapshots,
                key=lambda instrument: instrument.broker_symbol,
            )
        )

    def probe(
        self,
    ) -> MT5TerminalSnapshot:
        """
        Initialize, inspect the terminal, and always disconnect the
        Python integration afterward.
        """

        try:
            self.initialize()

            return self.get_terminal_snapshot()

        finally:
            self.shutdown()

    def probe_account(
        self,
    ) -> MT5AccountSnapshot:
        """
        Initialize, inspect the currently logged-in account, and
        always disconnect the Python integration afterward.

        This method never performs login or order execution.
        """

        try:
            self.initialize()

            return self.get_account_snapshot()

        finally:
            self.shutdown()

    def get_instrument_snapshot(
        self,
        broker_symbol: str,
    ) -> MT5InstrumentSnapshot:
        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        wanted_symbol = broker_symbol.strip()

        if not wanted_symbol:
            raise MT5ClientError(
                "MT5 broker symbol is required"
            )

        instruments = self.get_instrument_snapshots()

        for instrument in instruments:
            if instrument.broker_symbol == wanted_symbol:
                return instrument

        raise MT5ClientError(
            f"MT5 symbol not found: {wanted_symbol}"
        )

    def get_quote_snapshot(
        self,
        broker_symbol: str,
    ) -> MT5QuoteSnapshot:
        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        instrument = self.get_instrument_snapshot(
            broker_symbol
        )

        if not instrument.selected:
            return MT5QuoteSnapshot(
                broker_symbol=instrument.broker_symbol,
                broker_path=instrument.broker_path,
                broker_group=instrument.broker_group,
                digits=instrument.digits,
                point=instrument.point,
                trade_mode=instrument.trade_mode,
                new_order_allowed=(
                    instrument.new_order_allowed
                ),
                reference_only=instrument.reference_only,
                visible=instrument.visible,
                selected=instrument.selected,
                quote_available=False,
                tick_time=None,
                tick_time_msc=None,
                bid=None,
                ask=None,
                last=None,
                volume=None,
                volume_real=None,
                flags=None,
                spread=None,
                spread_points=None,
                unavailable_reason="symbol_not_selected",
                error_code=None,
                error_message=None,
            )

        tick = mt5.symbol_info_tick(
            instrument.broker_symbol
        )

        if tick is None:
            error_code, error_message = mt5.last_error()

            return MT5QuoteSnapshot(
                broker_symbol=instrument.broker_symbol,
                broker_path=instrument.broker_path,
                broker_group=instrument.broker_group,
                digits=instrument.digits,
                point=instrument.point,
                trade_mode=instrument.trade_mode,
                new_order_allowed=(
                    instrument.new_order_allowed
                ),
                reference_only=instrument.reference_only,
                visible=instrument.visible,
                selected=instrument.selected,
                quote_available=False,
                tick_time=None,
                tick_time_msc=None,
                bid=None,
                ask=None,
                last=None,
                volume=None,
                volume_real=None,
                flags=None,
                spread=None,
                spread_points=None,
                unavailable_reason="tick_unavailable",
                error_code=error_code,
                error_message=error_message,
            )

        tick_time = (
            datetime.fromtimestamp(
                tick.time,
                tz=UTC,
            )
            if tick.time > 0
            else None
        )

        spread = None
        spread_points = None

        if tick.bid > 0 and tick.ask > 0:
            spread = tick.ask - tick.bid

            if instrument.point > 0:
                spread_points = round(
                    spread / instrument.point,
                    10,
                )

        return MT5QuoteSnapshot(
            broker_symbol=instrument.broker_symbol,
            broker_path=instrument.broker_path,
            broker_group=instrument.broker_group,
            digits=instrument.digits,
            point=instrument.point,
            trade_mode=instrument.trade_mode,
            new_order_allowed=instrument.new_order_allowed,
            reference_only=instrument.reference_only,
            visible=instrument.visible,
            selected=instrument.selected,
            quote_available=True,
            tick_time=tick_time,
            tick_time_msc=tick.time_msc,
            bid=tick.bid,
            ask=tick.ask,
            last=tick.last,
            volume=tick.volume,
            volume_real=tick.volume_real,
            flags=tick.flags,
            spread=spread,
            spread_points=spread_points,
            unavailable_reason=None,
            error_code=None,
            error_message=None,
        )


    def get_candle_series_snapshot(
        self,
        broker_symbol: str,
        timeframe: str,
        count: int,
    ) -> MT5CandleSeriesSnapshot:
        """
        Return read-only MT5 OHLC history for one broker symbol.

        TCC makes no explicit Market Watch selection call.
        MT5 itself may internally mark a symbol as selected while
        loading historical rates.
        """

        if not self._initialized:
            raise MT5InitializationError(
                "MT5 client is not initialized"
            )

        instrument = self.get_instrument_snapshot(
            broker_symbol
        )

        wanted_timeframe = timeframe.strip().upper()

        if not wanted_timeframe:
            raise MT5ClientError(
                "MT5 timeframe is required"
            )

        if wanted_timeframe not in MT5_TIMEFRAMES:
            supported = ", ".join(
                MT5_TIMEFRAMES
            )

            raise MT5ClientError(
                "Unsupported MT5 timeframe: "
                f"{wanted_timeframe}. "
                f"Supported timeframes: {supported}"
            )

        if isinstance(count, bool):
            raise MT5ClientError(
                "MT5 candle count must be an integer"
            )

        if count < 1 or count > MAX_CANDLE_COUNT:
            raise MT5ClientError(
                "MT5 candle count must be between "
                f"1 and {MAX_CANDLE_COUNT}"
            )

        rates = None
        history_stale = False

        for attempt in range(
            CANDLE_HISTORY_SYNC_ATTEMPTS
        ):
            rates = mt5.copy_rates_from_pos(
                instrument.broker_symbol,
                MT5_TIMEFRAMES[wanted_timeframe],
                0,
                count,
            )

            history_stale = False

            if rates is not None and len(rates) > 0:
                tick = mt5.symbol_info_tick(
                    instrument.broker_symbol
                )

                if (
                    tick is not None
                    and tick.time > 0
                ):
                    latest_rate_time = max(
                        int(rate["time"])
                        for rate in rates
                    )

                    maximum_age_seconds = (
                        MT5_TIMEFRAME_SECONDS[
                            wanted_timeframe
                        ]
                        * 2
                    )

                    history_stale = (
                        int(tick.time)
                        - latest_rate_time
                        > maximum_age_seconds
                    )

            if not history_stale:
                break

            if (
                attempt + 1
                < CANDLE_HISTORY_SYNC_ATTEMPTS
            ):
                time.sleep(
                    CANDLE_HISTORY_SYNC_DELAY_SECONDS
                )

        instrument_after = mt5.symbol_info(
            instrument.broker_symbol
        )

        visible_after = (
            bool(instrument_after.visible)
            if instrument_after is not None
            else instrument.visible
        )

        selected_after = (
            bool(instrument_after.select)
            if instrument_after is not None
            else instrument.selected
        )

        if history_stale:
            return MT5CandleSeriesSnapshot(
                broker_symbol=instrument.broker_symbol,
                broker_path=instrument.broker_path,
                broker_group=instrument.broker_group,
                digits=instrument.digits,
                point=instrument.point,
                trade_mode=instrument.trade_mode,
                new_order_allowed=(
                    instrument.new_order_allowed
                ),
                reference_only=instrument.reference_only,
                visible_before=instrument.visible,
                selected_before=instrument.selected,
                visible_after=visible_after,
                selected_after=selected_after,
                timeframe=wanted_timeframe,
                count_requested=count,
                candles_available=False,
                candle_count=0,
                oldest_candle_time=None,
                latest_candle_time=None,
                candles=(),
                unavailable_reason="history_stale",
                error_code=None,
                error_message=None,
            )

        if rates is None:
            error_code, error_message = mt5.last_error()

            return MT5CandleSeriesSnapshot(
                broker_symbol=instrument.broker_symbol,
                broker_path=instrument.broker_path,
                broker_group=instrument.broker_group,
                digits=instrument.digits,
                point=instrument.point,
                trade_mode=instrument.trade_mode,
                new_order_allowed=(
                    instrument.new_order_allowed
                ),
                reference_only=instrument.reference_only,
                visible_before=instrument.visible,
                selected_before=instrument.selected,
                visible_after=visible_after,
                selected_after=selected_after,
                timeframe=wanted_timeframe,
                count_requested=count,
                candles_available=False,
                candle_count=0,
                oldest_candle_time=None,
                latest_candle_time=None,
                candles=(),
                unavailable_reason="rates_unavailable",
                error_code=error_code,
                error_message=error_message,
            )

        candles = tuple(
            sorted(
                (
                    MT5CandleSnapshot(
                        bar_time=datetime.fromtimestamp(
                            int(rate["time"]),
                            tz=UTC,
                        ),
                        open=float(rate["open"]),
                        high=float(rate["high"]),
                        low=float(rate["low"]),
                        close=float(rate["close"]),
                        tick_volume=int(
                            rate["tick_volume"]
                        ),
                        spread=int(rate["spread"]),
                        real_volume=int(
                            rate["real_volume"]
                        ),
                    )
                    for rate in rates
                ),
                key=lambda candle: candle.bar_time,
            )
        )

        if not candles:
            return MT5CandleSeriesSnapshot(
                broker_symbol=instrument.broker_symbol,
                broker_path=instrument.broker_path,
                broker_group=instrument.broker_group,
                digits=instrument.digits,
                point=instrument.point,
                trade_mode=instrument.trade_mode,
                new_order_allowed=(
                    instrument.new_order_allowed
                ),
                reference_only=instrument.reference_only,
                visible_before=instrument.visible,
                selected_before=instrument.selected,
                visible_after=visible_after,
                selected_after=selected_after,
                timeframe=wanted_timeframe,
                count_requested=count,
                candles_available=False,
                candle_count=0,
                oldest_candle_time=None,
                latest_candle_time=None,
                candles=(),
                unavailable_reason="no_rates",
                error_code=None,
                error_message=None,
            )

        return MT5CandleSeriesSnapshot(
            broker_symbol=instrument.broker_symbol,
            broker_path=instrument.broker_path,
            broker_group=instrument.broker_group,
            digits=instrument.digits,
            point=instrument.point,
            trade_mode=instrument.trade_mode,
            new_order_allowed=instrument.new_order_allowed,
            reference_only=instrument.reference_only,
            visible_before=instrument.visible,
            selected_before=instrument.selected,
            visible_after=visible_after,
            selected_after=selected_after,
            timeframe=wanted_timeframe,
            count_requested=count,
            candles_available=True,
            candle_count=len(candles),
            oldest_candle_time=candles[0].bar_time,
            latest_candle_time=candles[-1].bar_time,
            candles=candles,
            unavailable_reason=None,
            error_code=None,
            error_message=None,
        )

    def probe_candles(
        self,
        broker_symbol: str,
        timeframe: str,
        count: int,
    ) -> MT5CandleSeriesSnapshot:
        """
        Return read-only broker OHLC history and always disconnect
        the Python MT5 integration afterward.

        TCC never calls symbol_select(). MT5 may internally
        change symbol selection while loading historical rates.
        """

        try:
            self.initialize()

            return self.get_candle_series_snapshot(
                broker_symbol,
                timeframe,
                count,
            )

        finally:
            self.shutdown()

    def probe_instruments(
        self,
    ) -> tuple[MT5InstrumentSnapshot, ...]:
        """
        Return the broker instrument catalogue and always disconnect
        the Python MT5 integration afterward.

        This method does not modify Market Watch selection.
        """

        try:
            self.initialize()

            return self.get_instrument_snapshots()

        finally:
            self.shutdown()

    def probe_quote(
        self,
        broker_symbol: str,
    ) -> MT5QuoteSnapshot:
        """
        Return the latest available broker tick without modifying
        Market Watch selection.

        An unselected symbol is reported as unavailable rather than
        being automatically selected.
        """

        try:
            self.initialize()

            return self.get_quote_snapshot(
                broker_symbol
            )

        finally:
            self.shutdown()

    def __enter__(
        self,
    ) -> "MT5Client":
        self.initialize()

        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.shutdown()
