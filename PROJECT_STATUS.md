# Project Status

Last updated: 2026-08-14

## Current phase

Phase 1 - Clean project foundation

## Current checkpoint

Step 4 - Database foundation

## Completed

- Clean V2 monorepo created and committed.
- FastAPI backend environment created and tested.
- V2 repository pushed to GitHub.
- SQLAlchemy database foundation added.
- Alembic migration system added.
- User model added.
- Broker connection model added.
- Trading account model added.
- Risk profile model added.
- Append-only audit event foundation added.
- Execution record foundation added.
- Broker credentials are represented only by `secret_ref`; raw broker secrets are not database fields.
- Execution records include a unique `client_order_id` foundation for idempotency.
- Local SQLite runtime database is excluded from Git.
- Automated database structure/security tests added.
- Execution remains disabled.
- Live trading remains disabled.

## In progress

- Local Step 4 migration and test verification.

## Next checkpoint

Step 5 - Broker adapter contracts and simulated read-only broker.

After that:

Step 6 - PrimeXBT MT5 read-only execution-agent connection.

## Blocked

None.
## Phase 3 � Broker Adapter Foundation

### Checkpoint 3.1 � Normalized Broker Contract ? COMPLETE

Completed:

- Broker capability model
- Normalized broker schemas
- Broker type and account mode normalization
- Asset class and market type normalization
- Normalized instruments, quotes, candles, positions, and orders
- Separation of normalized `symbol` from broker-native `broker_symbol`
- Permanent abstract `BrokerAdapter` contract
- Read-only execution safeguards
- Broker adapter exception hierarchy
- Automated broker contract tests

Validation:

- Broker contract tests: 7 passed
- Full backend suite: 12 passed
- Ruff: all checks passed

Next:

### Checkpoint 3.2 � Simulated Broker Adapter

### Checkpoint 3.2 � Simulated Broker Integration ? COMPLETE

Completed:

- Production SimulatedBrokerAdapter
- Multi-asset simulated instrument catalog
- Forex, metals, energy, indices, and crypto coverage
- Broker connection lifecycle handling
- Dynamic instrument discovery and filtering
- Normalized quotes
- Normalized historical candles
- Read-only positions and orders
- Disconnected broker protection
- BrokerManager central connection registry
- BrokerService application layer
- FastAPI broker API
- Dynamic broker connection count in system status
- HTTP error normalization
- API-level execution safeguards

Read-only API endpoints implemented:

- GET /api/v1/brokers
- POST /api/v1/brokers/simulated
- GET /api/v1/brokers/{connection_id}/health
- POST /api/v1/brokers/{connection_id}/connect
- POST /api/v1/brokers/{connection_id}/disconnect
- DELETE /api/v1/brokers/{connection_id}
- GET /api/v1/brokers/{connection_id}/capabilities
- GET /api/v1/brokers/{connection_id}/account
- GET /api/v1/brokers/{connection_id}/instruments
- GET /api/v1/brokers/{connection_id}/instrument
- GET /api/v1/brokers/{connection_id}/quote
- GET /api/v1/brokers/{connection_id}/candles
- GET /api/v1/brokers/{connection_id}/positions
- GET /api/v1/brokers/{connection_id}/orders

Safety:

- No buy endpoint
- No sell endpoint
- No order placement endpoint
- No trade execution endpoint
- Simulated broker remains read-only
- execution_enabled remains false
- live_trading_enabled remains false

Validation:

- Full backend suite: 51 passed
- Ruff: all checks passed
- One known non-blocking Starlette TestClient/httpx deprecation warning remains

### Phase 3 � Broker Adapter Foundation ? COMPLETE

Phase 3 now provides the permanent broker-independent foundation required for PrimeXBT MT5 and future Binance integration.

Next:

## Phase 4 � PrimeXBT MT5 Demo Read-Only

## Phase 4 — PrimeXBT MT5 Demo Read-Only

### Checkpoint 4.1 — Windows MT5 Agent Foundation ✅ COMPLETE

Completed:

- Independent Windows execution-agent Python package
- Independent execution-agent virtual environment
- Independent dependency requirements and lock file
- Agent configuration layer
- MT5 status model
- FastAPI execution-agent application
- Local-only agent listener on 127.0.0.1:8765
- Health endpoint
- Agent status endpoint
- MT5 status endpoint
- Automated execution-agent tests
- PowerShell agent startup script
- PowerShell execution-agent test script
- Runtime verification through Swagger and PowerShell

Current safety state:

- MT5 enabled: false
- MT5 terminal available: false
- MT5 initialized: false
- Broker account logged in: false
- Execution enabled: false
- Live trading enabled: false

No order placement, buy, sell, modify-order, cancel-order,
close-position, or execution endpoints exist.

Validation:

- Execution-agent tests: 5 passed
- Backend tests: 51 passed
- Ruff: all checks passed
- Live local HTTP runtime verified on 127.0.0.1:8765

Next:

### Checkpoint 4.2 — MT5 Terminal Detection and Read-Only Initialization ✅ COMPLETE

Completed:

- MetaTrader5 Python package installed only in the Windows execution-agent environment
- MetaTrader5 pinned at version 5.0.5735
- PXBT MT5 terminal discovered explicitly
- configured terminal:
  C:\Program Files\PXBT Trading MT5 Terminal\terminal64.exe
- MT5 terminal initialization through explicit terminal path
- controlled MT5 shutdown after every probe
- terminal version/build discovery
- terminal connection-state discovery
- PXBT company and terminal identity detection
- existing logged-in MT5 account detection
- demo/live/contest account-mode detection
- masked account-login reporting
- broker server, company, currency and leverage discovery
- read-only MT5 status exposed through execution-agent API
- automated account-aware MT5 status tests
- live HTTP validation against PXBT MT5 demo terminal

Validated PXBT environment:

- terminal company: PXBT Trading Ltd
- terminal: PXBT Trading MT5 Terminal
- terminal build: 6090
- account mode: demo
- account server: PXBTTrading-1
- account currency: USD
- leverage: 100

Safety state:

- execution enabled: false
- live trading enabled: false
- no mt5.login() call
- no order_send() call
- no order_check() call
- no order-placement API endpoints
- no broker credentials stored in source
- full MT5 account login is not exposed through the API
- MT5 Python connection is shut down after each read-only probe

Validation:

- MT5 account-aware status tests: 6 passed
- execution-agent tests: 11 passed
- execution-agent Ruff: all checks passed
- live /api/v1/mt5/status validation successful
- live /api/v1/agent/status validation successful

Next:

### Checkpoint 4.3 - PrimeXBT MT5 Read-Only Market and Account Data - COMPLETE

Completed:

- dynamic PXBT MT5 instrument discovery
- 207 broker-native instruments discovered
- read-only instrument catalogue API
- read-only quote API
- read-only OHLC/candle API
- detailed read-only account API
- controlled candle timeframes:
  M1, M5, M15, M30, H1, H4, D1
- maximum candle request count limited to 1000
- account balance, equity, profit, credit and margin reporting
- margin call and stop-out reporting
- leverage, currency and account metadata reporting
- masked account login exposed through HTTP
- full MT5 login excluded from HTTP responses
- live PXBT demo validation completed

Validated PXBT instrument catalogue:

- total instruments: 207
- Forex: 99
- Commodities: 36
- Crypto: 35
- Indices: 17
- Shares: 16
- reference symbols: 4
- new-order-allowed symbols: 202
- new-order-disabled symbols: 5
- TONUSDT detected as close-only
- BTCUSD detected as a disabled reference symbol that can still
  provide read-only quote and candle data

Historical-data behavior:

- Trade Command Center never calls mt5.symbol_select()
- historical data is retrieved using copy_rates_from_pos()
- PXBT MT5 may internally change a symbol from
  selected=false to selected=true while loading history
- candle responses record selected_before and selected_after
- visible_before and visible_after are also recorded
- Trade Command Center does not attempt to restore selection because
  doing so would itself mutate terminal state
- candle availability does not imply tradability
- quote availability does not imply tradability
- data availability does not imply freshness

Validated PXBT demo account:

- account mode: demo
- server: PXBTTrading-1
- company: PXBT Trading Ltd
- currency: USD
- leverage: 100
- masked login exposed: yes
- full login exposed: no

Safety state:

- execution enabled: false
- live trading enabled: false
- no mt5.login() call
- no explicit mt5.symbol_select() call
- no mt5.order_send() call
- no mt5.order_check() call
- no order-placement API endpoints
- no broker credentials stored in source
- demo-account read access only
- MT5 Python connection is shut down after controlled probes

Validation:

- execution-agent tests: 80 passed
- backend tests: 51 passed
- total regression tests: 131 passed
- execution-agent Ruff: all checks passed
- backend Ruff: all checks passed
- git diff --check: clean
- forbidden MT5-call search: clean
- live instrument endpoint validation: successful
- live quote endpoint validation: successful
- live candle endpoint validation: successful
- live account endpoint validation: successful
- live agent safety-state validation: successful

## Phase 4 - PrimeXBT MT5 Demo Read-Only - COMPLETE

Phase 4 now provides a controlled Windows execution-agent boundary
for read-only PXBT MT5 terminal status, dynamic instruments, quotes,
historical candles and detailed demo-account data.

No Trade Command Center execution capability has been introduced.

Next:

## Phase 5 - Flutter Windows
