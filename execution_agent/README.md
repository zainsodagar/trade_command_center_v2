# Trade Command Center — Windows MT5 Agent

The Windows MT5 Agent is the controlled boundary between the
Trade Command Center backend and MetaTrader 5.

## Architecture

Trade Command Center Backend
    |
Windows MT5 Agent
    |
MetaTrader 5 Terminal
    |
PrimeXBT

The main backend does not communicate directly with MetaTrader 5.

## Current Phase

Phase 4 - PrimeXBT MT5 Demo Read-Only - COMPLETE

Checkpoint 4.3 completes the controlled read-only PXBT MT5
integration for:

- terminal status
- dynamic instrument discovery
- quotes
- historical candles
- detailed demo-account information

No Trade Command Center execution capability has been introduced.

Next development phase:

Phase 5 - Flutter Windows

## Current Endpoints

- GET /health
- GET /api/v1/agent/status
- GET /api/v1/mt5/status
- GET /api/v1/mt5/instruments
- GET /api/v1/mt5/quote
- GET /api/v1/mt5/candles
- GET /api/v1/mt5/account

## Network Binding

The development agent listens only on:

127.0.0.1:8765

It is therefore not exposed to other machines on the network.

## Safety Defaults

- MT5 enabled: false
- terminal available: false
- initialized: false
- account logged in: false
- execution enabled: false
- live trading enabled: false

No trading endpoints currently exist.

## Run

Start:

    .\scripts\start_execution_agent.ps1

Test:

    .\scripts\run_execution_agent_tests.ps1

Swagger:

    http://127.0.0.1:8765/docs

## Development Environment

Dependencies:

    execution_agent\requirements.txt

Pinned dependency versions:

    execution_agent\requirements-lock.txt

Virtual environment:

    execution_agent\.venv

The virtual environment is excluded from Git.
## MT5 Read-Only Integration

Checkpoint 4.2 adds controlled read-only MetaTrader 5 connectivity.

The execution agent uses the explicitly configured PXBT terminal path rather than relying on implicit terminal discovery.

Environment setting:

    TCC_AGENT_MT5_TERMINAL_PATH

Read-only MT5 integration can be enabled with:

    TCC_AGENT_MT5_ENABLED=true

Execution remains separately disabled:

    TCC_AGENT_EXECUTION_ENABLED=false
    TCC_AGENT_LIVE_TRADING_ENABLED=false

The current implementation can inspect:

- MT5 package version
- terminal version and build
- terminal connection state
- broker company
- terminal identity
- currently authenticated account presence
- masked account login
- account mode
- broker server
- account currency
- leverage
- account trading capability flags

The implementation does not perform MT5 login and does not contain order-placement functionality.

Each status probe initializes the configured terminal connection, performs read-only inspection, and shuts down the Python MT5 connection before returning.

## Checkpoint 4.3 Read-Only Market and Account Data

The PXBT instrument catalogue is loaded dynamically from MetaTrader 5
rather than maintained as a hard-coded product list.

The validated PXBT demo environment exposed 207 broker-native symbols
across Forex, Commodities, Crypto, Indices, Shares and reference
symbols.

Market Watch visibility and selection state are not treated as
tradability rules.

Read-only instrument data is available through:

    GET /api/v1/mt5/instruments

Read-only quote data is available through:

    GET /api/v1/mt5/quote

Historical OHLC data is available through:

    GET /api/v1/mt5/candles

Supported candle timeframes:

    M1
    M5
    M15
    M30
    H1
    H4
    D1

Maximum candle request size:

    1000 bars

Trade Command Center never explicitly calls:

    mt5.symbol_select()

PXBT MT5 may nevertheless internally change:

    selected=false

to:

    selected=true

while historical data is loaded with:

    copy_rates_from_pos()

The candle response therefore reports:

    visible_before
    selected_before
    visible_after
    selected_after

Trade Command Center does not attempt to restore the original MT5
selection state because doing so would itself mutate terminal state.

Quote availability and candle availability are independent from
tradability.

Detailed read-only demo-account information is available through:

    GET /api/v1/mt5/account

The account endpoint exposes financial and margin state including:

- balance
- credit
- profit
- equity
- margin
- margin free
- margin level
- margin call level
- stop-out level
- leverage
- currency
- account mode
- broker server
- broker company

Only the masked MT5 login is exposed through HTTP.

The full MT5 login is not returned by the account endpoint.

Phase 4 safety requirements remain:

    TCC_AGENT_EXECUTION_ENABLED=false
    TCC_AGENT_LIVE_TRADING_ENABLED=false

The Phase 4 implementation does not call:

    mt5.login()
    mt5.symbol_select()
    mt5.order_send()
    mt5.order_check()

No order-placement API endpoints exist.

Final Phase 4 validation:

- execution-agent tests: 80 passed
- backend tests: 51 passed
- total regression tests: 131 passed
- execution-agent Ruff: clean
- backend Ruff: clean
- forbidden MT5-call search: clean
