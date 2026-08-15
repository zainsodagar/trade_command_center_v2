from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Configuration for the Windows MT5 execution agent."""

    model_config = SettingsConfigDict(
        env_prefix="TCC_AGENT_",
        extra="ignore",
    )

    app_name: str = "Trade Command Center MT5 Agent"
    app_env: str = "development"

    host: str = "127.0.0.1"
    port: int = 8765

    mt5_enabled: bool = False
    
    mt5_terminal_path: str | None = None

    execution_enabled: bool = False
    live_trading_enabled: bool = False


@lru_cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()
