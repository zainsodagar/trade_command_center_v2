from dataclasses import dataclass
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


class MT5Client:
    """
    Controlled read-only MetaTrader 5 client.

    Phase 4 permits terminal and account inspection only.
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
            leverage=account_info.leverage,
            trade_allowed=account_info.trade_allowed,
            trade_expert=account_info.trade_expert,
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
