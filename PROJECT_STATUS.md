# Project Status

Last updated: 2026-08-25

## Current phase

Phase 6 - Risk Engine - COMPLETE

## Current checkpoint

Checkpoint 6.6 - Final Phase 6 Validation and Closure - COMPLETE

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

- Final repository closure for Phase 6.

## Next checkpoint

Phase 7 - Simulated Execution.

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

### Checkpoint 5.1 - Flutter Windows Foundation - COMPLETE

Completed:

- Flutter Windows project created under:
  apps/trade_command_center
- Flutter project name:
  trade_command_center
- Windows desktop platform generated
- Windows x64 desktop target validated
- Visual Studio Windows toolchain validated
- Windows SDK validated
- generated Flutter dependencies resolved successfully
- default Flutter counter application removed
- permanent Trade Command Center application entry point created
- permanent application theme foundation created
- Windows desktop application shell created
- desktop NavigationRail foundation created
- Dashboard destination created
- Markets destination created
- Account destination created
- Settings destination created
- persistent DEMO indicator added
- persistent READ ONLY indicator added
- execution state shown as disabled
- no broker credentials stored in Flutter
- no execution functionality introduced
- no broker API connectivity introduced yet

Current Flutter structure:

    apps/trade_command_center/
        lib/
            main.dart
            app/
                app.dart
                app_theme.dart
            features/
                shell/
                    presentation/
                        app_shell.dart
        test/
            widget_test.dart
        windows/
        pubspec.yaml

Validated desktop behavior:

- application launches successfully on Windows
- application remains stable while running
- Dashboard navigation works
- Markets navigation works
- Account navigation works
- Settings navigation works
- DEMO state remains visually visible
- READ ONLY state remains visually visible

Validation:

- Flutter version: 3.44.7
- Dart version: 3.12.2
- flutter analyze: no issues
- flutter tests: 2 passed
- Windows release build: successful
- Windows debug build: successful
- Windows runtime validation: successful
- release executable generated:
  trade_command_center.exe

Safety boundary:

- Flutter contains no broker execution code
- Flutter contains no MT5 dependency
- Flutter does not communicate directly with MT5
- Flutter contains no broker credentials
- execution remains disabled
- live trading remains disabled
- Phase 4 execution-agent safety boundary remains unchanged

Next:

### Checkpoint 5.2 - Desktop Application Structure and Navigation - COMPLETE

Completed:

- original Flutter desktop shell refactored from a monolithic file
- app_shell.dart reduced from 451 lines to approximately 103 lines
- permanent feature-based application structure introduced
- reusable core presentation widgets extracted
- Dashboard moved to its permanent feature module
- Markets moved to its permanent feature module
- Account moved to its permanent feature module
- Settings moved to its permanent feature module
- application mark extracted into a reusable shell widget
- top application bar extracted into a reusable shell widget
- DEMO and READ ONLY badges extracted into reusable shell widgets
- NavigationRail remains the primary Windows desktop navigation
- responsive NavigationRail behavior introduced
- compact navigation used below the desktop extension breakpoint
- extended navigation used on wide desktop windows
- navigation state is preserved through IndexedStack
- no networking dependency introduced
- no broker execution functionality introduced

Permanent presentation structure now includes:

    lib/
        core/
            widgets/
                empty_state.dart
                metric_card.dart
                page_frame.dart
        features/
            account/
                presentation/
                    account_page.dart
            dashboard/
                presentation/
                    dashboard_page.dart
            markets/
                presentation/
                    markets_page.dart
            settings/
                presentation/
                    settings_page.dart
            shell/
                presentation/
                    app_shell.dart
                    widgets/
                        app_mark.dart
                        status_badge.dart
                        top_bar.dart

Responsive desktop behavior:

- compact NavigationRail below 1200 logical pixels
- extended NavigationRail at 1200 logical pixels and above
- compact mode retains visible destination labels
- extended mode displays icon-and-label desktop navigation
- navigation remains operational during window resizing
- Dashboard navigation validated
- Markets navigation validated
- Account navigation validated
- Settings navigation validated
- DEMO indicator remains permanently visible
- READ ONLY indicator remains permanently visible
- no runtime layout overflow observed during validation

Test coverage:

- application starts on Dashboard
- DEMO state is verified
- READ ONLY state is verified
- execution disabled state is verified
- Markets navigation is verified
- Account navigation is verified
- Settings navigation is verified
- return navigation to Dashboard is verified
- safety state remains visible across navigation
- compact NavigationRail behavior is verified
- extended NavigationRail behavior is verified

Validation:

- dart format: successful
- flutter analyze: no issues
- flutter tests: 7 passed
- Windows release build: successful
- Windows runtime compact-layout validation: successful
- Windows runtime wide-layout validation: successful
- responsive navigation runtime validation: successful
- all four navigation destinations validated
- git diff --check: clean
- release executable generated:
  trade_command_center.exe

Safety boundary:

- Flutter remains read-only
- Flutter contains no order-entry controls
- Flutter contains no execution API
- Flutter contains no MT5 package dependency
- Flutter does not communicate directly with MT5
- Flutter contains no broker credentials
- execution remains disabled
- live trading remains disabled
- PrimeXBT MT5 real activation has not occurred
- Phase 4 execution-agent safety boundary remains unchanged

Next:

### Checkpoint 5.4 - Instrument Browser and Read-Only Market Data UI - COMPLETE

Completed:

- Flutter HTTP dependency added using `http 1.6.0`
- permanent API configuration layer added
- backend base URL configurable through:
  `TCC_BACKEND_BASE_URL`
- execution-agent base URL configurable through:
  `TCC_AGENT_BASE_URL`
- safe localhost defaults retained for Windows development
- permanent API endpoint constants added
- GET-only HTTP transport implemented
- HTTP transport supports:
  - JSON object responses
  - JSON list responses
  - empty successful responses
  - FastAPI error detail extraction
  - invalid JSON detection
  - connection-error handling
  - request timeout handling
- reusable `ApiException` model added
- typed backend system-status model added
- typed execution-agent status model added
- detailed typed MT5 status model added
- strict required JSON-field validation added
- strict nullable JSON-field validation added
- date-time response validation added
- `BackendApi` service added
- `AgentApi` service added
- detailed `getMt5Status()` support added
- Flutter communicates only with the local FastAPI backend and
  local Windows execution agent
- Flutter does not communicate directly with MT5
- standalone Dart live-status diagnostic probe added
- real Dart-to-backend connectivity validated
- real Dart-to-agent connectivity validated
- real Dart-to-PXBT-MT5 read-only status validation completed

Validated live PXBT demo status:

- backend: online
- agent: online
- MT5 enabled: true
- MT5 connected: true
- MT5 account logged in: true
- account mode: demo
- account login exposed only in masked form
- masked account login: ***7959
- account server: PXBTTrading-1
- account currency: USD
- account leverage: 100
- backend execution enabled: false
- backend live trading enabled: false
- agent execution enabled: false
- agent live trading enabled: false
- MT5 execution enabled: false
- MT5 live trading enabled: false
- Dart backend read-only safety state: true
- Dart agent read-only safety state: true
- detailed MT5 read-only safety state: true
- detailed MT5 operational read-only state: true

Dashboard integration:

- live backend status connected to Dashboard
- live Windows execution-agent status connected to Dashboard
- live PXBT MT5 demo status connected to Dashboard
- Dashboard networking isolated behind `DashboardStatusService`
- Dashboard presentation does not perform direct HTTP requests
- `DashboardStatus` aggregate safety model added
- `DashboardStatusLoader` abstraction added
- safe dependency injection added for automated widget tests
- Dashboard supports initial loading state
- Dashboard supports connected read-only-safe state
- Dashboard supports initial connection-error state
- Dashboard supports explicit unsafe state
- Dashboard supports manual refresh
- failed refresh preserves the last successfully loaded status
- any unsafe backend, agent, or MT5 layer makes the aggregate
  Dashboard state unsafe
- non-demo MT5 account is treated as not operational read-only
- disconnected MT5 is treated as not operational read-only
- persistent DEMO indicator remains visible
- persistent READ ONLY indicator remains visible
- execution state remains visibly disabled
- masked account login displayed
- account server displayed
- account currency displayed
- account leverage displayed
- live-trading state displayed
- read-only safety state displayed

Automated Flutter test coverage:

- GET-only API transport tests: 7
- backend and agent status service tests: 6
- detailed MT5 status API tests: 3
- Dashboard aggregate safety tests: 5
- Dashboard state widget tests: 6
- application shell and responsive navigation tests: 7
- total Flutter tests: 34 passed

Dashboard widget states verified:

- loading
- connected read-only safe
- initial connection failure
- unsafe execution state
- successful manual refresh
- failed-refresh fallback preserving last known good status

Windows runtime validation:

- Windows desktop application launches successfully
- real local backend connectivity successful
- real local execution-agent connectivity successful
- real PXBT MT5 demo status displayed
- Dashboard displays:
  - Backend: Online
  - MT5 Agent: Connected
  - Account Mode: DEMO
  - Execution: Disabled
  - Login: ***7959
  - Server: PXBTTrading-1
  - Currency: USD
  - Leverage: 1:100
  - Live Trading: Disabled
  - Safety: Read-only safe
- Dashboard refresh works against live services
- Dashboard navigation remains operational
- Markets navigation remains operational
- Account navigation remains operational
- Settings navigation remains operational
- returning to Dashboard preserves the real connected status
- DEMO remains visible across navigation
- READ ONLY remains visible across navigation
- no runtime layout overflow observed

Validation:

- Flutter version: 3.44.7
- Dart version: 3.12.2
- dart format: successful
- flutter analyze: no issues
- Flutter tests: 34 passed
- Windows release build: successful
- release executable generated:
  `trade_command_center.exe`
- real Dart backend status probe: successful
- real Dart execution-agent status probe: successful
- real Dart detailed MT5 status probe: successful
- `DART READ-ONLY API CLIENT CONFIRMED`
- `DART DETAILED MT5 READ-ONLY STATUS CONFIRMED`
- HTTP write-method source search: clean
- prohibited execution-mechanism source search: clean
- git diff --check: clean
- Windows live runtime validation: successful

Flutter network safety boundary:

- Flutter HTTP transport exposes GET only
- no POST implementation exists
- no PUT implementation exists
- no PATCH implementation exists
- no DELETE implementation exists
- no order API exists
- no execution API exists
- no buy control exists
- no sell control exists
- no order-entry control exists
- no `mt5.login()` call exists in Flutter
- no `mt5.symbol_select()` call exists in Flutter
- no `mt5.order_send()` call exists in Flutter
- no `mt5.order_check()` call exists in Flutter
- Flutter contains no MetaTrader5 package dependency
- Flutter does not communicate directly with MT5
- Flutter contains no broker credentials
- account login remains masked
- execution remains disabled
- live trading remains disabled
- PrimeXBT MT5 real activation has not occurred
- Phase 4 Windows execution-agent safety boundary remains unchanged

## Checkpoint 5.3 - COMPLETE

The Flutter Windows application now has a permanent, tested,
GET-only networking layer for Trade Command Center backend,
Windows execution-agent, and detailed PXBT MT5 demo status.

The Windows Dashboard displays real local connectivity and
read-only safety information while keeping execution and live
trading disabled.

No trading or order-execution capability has been introduced.

Next:

### Checkpoint 5.4 - Instrument Browser and Read-Only Market Data UI - COMPLETE

Completed:

- Flutter typed `Mt5Instrument` model added
- all 20 broker-native MT5 instrument fields preserved
- strict JSON schema validation retained
- instrument safety metadata preserved:
  - `trade_mode`
  - `new_order_allowed`
  - `reference_only`
  - `visible`
  - `selected`
- derived read-only availability states added:
  - Available
  - Reference only
  - Close only
  - New orders disabled
- `AgentApi.getMt5Instruments()` added
- live agent response handled as the actual bare JSON array
- no artificial object wrapper introduced
- complete broker catalogue returned without truncation
- malformed catalogue responses rejected safely
- malformed instrument entries rejected safely

Live PXBT MT5 catalogue validation:

- total instruments: 207
- Forex: 99
- Commodities: 36
- Crypto: 35
- Indices: 17
- Shares: 16
- RefSymbols: 4
- full trade mode: 202
- disabled trade mode: 4
- close-only trade mode: 1
- new orders allowed: 202
- new orders blocked: 5
- reference-only instruments: 4
- BTCUSD validated as:
  - RefSymbols
  - disabled
  - reference only
  - new orders blocked
- TONUSDT validated as:
  - Crypto
  - close only
  - new orders blocked
- standalone Dart live catalogue probe completed successfully
- `DART LIVE PXBT INSTRUMENT CATALOGUE CONFIRMED`

Markets domain and data layer:

- dynamic `InstrumentCatalog` added
- `InstrumentCatalogLoader` abstraction added
- `InstrumentCatalogService` added
- Markets presentation does not call `AgentApi` directly
- broker groups discovered dynamically from live catalogue
- no fixed gold-only or single-asset workflow introduced
- search supports:
  - broker symbol
  - description
  - broker path
  - broker group
- dynamic broker-group filtering added
- availability filtering added for:
  - all
  - new orders available
  - new orders blocked
  - reference only
  - close only
- catalogue summary counts added
- unknown/future broker groups remain supported dynamically

Markets Windows UI:

- static Markets placeholder replaced with live read-only instrument browser
- Markets catalogue loads lazily on first navigation
- Dashboard startup is not forced to load the complete instrument catalogue
- Markets state remains preserved after first activation
- initial loading state added
- initial connection-error state added
- Retry action added
- Refresh action added
- failed refresh preserves last successful catalogue
- live instrument-count metric cards added
- dynamic broker-group chips added
- availability-filter chips added
- search field added
- live filtered-result counts added
- read-only instrument cards added
- availability badges added
- broker metadata displayed without execution actions
- persistent DEMO indicator remains visible
- persistent READ ONLY indicator remains visible
- no Buy control added
- no Sell control added
- no Place Order control added
- no Open Position control added
- no execution control added

Search-input defect correction:

- original Markets search field incorrectly recreated
  `TextEditingController` on every state rebuild
- this caused text to appear in reverse order
- cursor focus could disappear after Backspace
- Markets now owns one persistent `TextEditingController`
- controller created once in `initState`
- controller disposed correctly in `dispose`
- typing direction validated in Windows runtime
- Backspace cursor behavior validated
- continued typing after Backspace validated
- dedicated regression test added

Live Windows runtime validation:

- Dashboard remains connected and read-only safe
- Backend displays Online
- MT5 Agent displays Connected
- account mode displays DEMO
- Execution displays Disabled
- live trading remains Disabled
- masked account login remains displayed
- Markets displays 207 instruments
- dynamic broker-group counts validated
- BTCUSD displays Reference only
- TONUSDT displays Close only
- Blocked filter returns 5
- Reference only filter returns 4
- Close only filter returns 1
- Refresh succeeds against real PXBT MT5 catalogue
- search operates correctly
- search Backspace/cursor behavior operates correctly
- navigation preserves Markets state
- returning to Dashboard preserves connected safety state
- no runtime layout overflow observed
- no execution controls observed

Automated Flutter test coverage:

- previous Checkpoint 5.3 suite: 34 tests
- MT5 instrument model tests added
- MT5 instrument API tests added
- InstrumentCatalog domain tests added
- InstrumentCatalogService tests added
- Markets browser widget tests added
- Markets search-input regression test added
- application shell tests updated for safe Markets loader injection
- total Flutter tests: 59 passed

Final validation:

- dart format: successful
- flutter analyze: no issues
- Flutter tests: 59 passed
- Windows debug runtime: successful
- Windows release build: successful
- release executable generated:
  `build\windows\x64\runner\Release\trade_command_center.exe`
- real Dart instrument-catalogue probe: successful
- HTTP write-method source search: clean
- only GET HTTP transport remains
- prohibited execution-mechanism source search: clean
- execution-control UI source search: clean
- git diff --check: clean
- known Windows LF-to-CRLF warnings remain non-blocking

Flutter safety boundary remains unchanged:

- Flutter HTTP transport exposes GET only
- no POST implementation exists
- no PUT implementation exists
- no PATCH implementation exists
- no DELETE implementation exists
- no order API exists
- no execution API exists
- no direct MetaTrader5 dependency exists in Flutter
- no `mt5.login()` call exists in Flutter
- no `mt5.symbol_select()` call exists in Flutter
- no `mt5.order_send()` call exists in Flutter
- no `mt5.order_check()` call exists in Flutter
- Flutter communicates with MT5 only through the local Windows execution agent
- Flutter contains no broker credentials
- account login remains masked
- execution remains disabled
- live trading remains disabled
- PrimeXBT real activation has not occurred

## Checkpoint 5.4 - COMPLETE

Trade Command Center Windows now contains a tested,
broker-native, multi-asset PXBT MT5 instrument browser.

The catalogue is dynamically sourced from the connected broker
and currently exposes 207 instruments across Forex,
Commodities, Crypto, Indices, Shares, and reference symbols.

Search, broker-group filters, availability filters, refresh,
error handling, and navigation-state preservation are operational.

No trading or execution capability has been introduced.

Next:

### Checkpoint 5.5 - Quotes and Historical Candles UI - COMPLETE

Completed:

- typed `Mt5Quote` model added
- typed `Mt5Candle` model added
- typed `Mt5CandleSeries` model added
- nullable date-time JSON parsing support added
- strict quote and candle schema validation retained
- `AgentApi.getMt5Quote()` added
- `AgentApi.getMt5Candles()` added
- all Flutter market-data networking remains GET-only
- `MarketDataLoader` abstraction added
- `MarketDataService` added
- Markets presentation remains separated from direct HTTP transport
- standalone live MT5 market-data Dart probe added
- live PXBT quote parsing validated
- live PXBT candle parsing validated
- `history_stale` remains a safe non-data state rather than being
  presented as valid candle history

Read-only instrument market-data UI:

- instrument cards are selectable
- selected instrument state is visually indicated
- selecting an instrument loads:
  - live read-only quote
  - 100 historical candles
- initial historical timeframe is M1
- supported timeframe controls:
  - M1
  - M5
  - M15
  - M30
  - H1
  - H4
  - D1
- changing timeframe reloads candles only
- changing timeframe does not unnecessarily reload the quote
- quote values displayed:
  - Bid
  - Ask
  - Spread
  - Spread Points
  - Tick Time
  - Quote Status
- historical values displayed:
  - Timeframe
  - Candle Count
  - Oldest Candle
  - Latest Candle
  - History Status
- unavailable quote/history states remain explicit
- stale history does not display stale candles as valid data

Historical charting:

- dependency-free Flutter candlestick chart added
- chart implemented with `CustomPainter`
- OHLC wick and candle-body rendering added
- bullish and bearish candle rendering added
- price-grid labels added
- chart uses broker-native instrument digits
- first and latest candle time labels added
- safe empty-history chart state added
- `history_stale` renders the safe empty-history state
- chart widget automated tests added

Instrument/timeframe state correction:

- an instrument-selection regression was found during live Windows testing
- previously, selecting a second instrument inherited the timeframe
  chosen for the previous instrument
- every newly selected instrument now resets to M1
- timeframe changes remain local to the currently selected instrument
- dedicated automated regression coverage added
- regression verifies:
  - first instrument can change from M1 to H1
  - selecting another instrument resets to M1
  - the new instrument receives a fresh quote request
  - the new instrument receives an M1 candle request
  - M1 becomes selected
  - H1 is no longer selected

Live PXBT MT5 validation:

- BTCUSDT live quote successfully displayed
- BTCUSDT M1 historical candles successfully displayed
- BTCUSDT H1 historical candles successfully displayed
- live candlestick rendering validated
- candle count of 100 validated
- oldest and latest candle timestamps validated
- history status `Available` validated
- XAUUSD exposed the cross-instrument timeframe-state defect
- defect reproduced and corrected
- after correction, XAUUSD opened directly at M1
- XAUUSD displayed 100 M1 candles
- XAUUSD oldest candle timestamp populated
- XAUUSD latest candle timestamp populated
- XAUUSD history status displayed `Available`
- XAUUSD candlestick chart rendered successfully
- DEMO indicator remained visible
- READ ONLY indicator remained visible

Automated Flutter validation:

- Markets page widget tests: 12 passed
- complete Markets feature suite: 27 passed
- full Flutter test suite: 84 passed
- flutter analyze: no issues
- Windows release build: successful
- release executable generated:
  `build\windows\x64\runner\Release\trade_command_center.exe`

Final safety validation:

- Flutter HTTP transport still exposes GET only
- no POST calls found
- no PUT calls found
- no PATCH calls found
- no DELETE calls found
- no `order_send` mechanism found
- no `order_check` mechanism found
- no `mt5.login` mechanism found
- no `symbol_select` mechanism found in Flutter
- no place-order mechanism found
- no trade-execution mechanism found
- Flutter contains no MetaTrader5 dependency
- Flutter does not communicate directly with MT5
- execution remains disabled
- live trading remains disabled
- PXBT account remains demo
- persistent DEMO and READ ONLY UI boundaries remain in place
- git diff --check contains no whitespace errors
- known Windows LF-to-CRLF warnings remain non-blocking

## Checkpoint 5.5 - COMPLETE

Trade Command Center Windows now provides live, read-only,
broker-native quote and historical OHLC visualization for the
dynamic PXBT MT5 instrument catalogue.

Instrument selection, timeframe selection, typed quote/candle
models, stale-history handling, candlestick charting, error states,
and cross-instrument timeframe reset behavior are covered by
automated tests and live Windows validation.

No order entry, trading, broker mutation, or execution capability
has been introduced.

## Phase 5 - Flutter Windows - COMPLETE

Phase 5 now provides the Windows desktop application foundation,
responsive navigation, live read-only system status, dynamic
multi-asset broker instrument discovery, live quotes, historical
candles, and candlestick visualization.

The Flutter application remains behind the local FastAPI backend
and Windows execution-agent architecture and does not communicate
directly with MT5.

Next:

## Phase 6 - Risk Engine

### Checkpoint 6.1 - Deterministic Risk Contract & Core Types - COMPLETE

Completed:

- immutable `RiskSchema` foundation added
- risk-domain models reject unknown fields
- risk-domain models are immutable
- deterministic `RiskDecision` contract added:
  - `allow`
  - `block`
- stable machine-readable `RiskViolationCode` values added
- deterministic `RiskViolation` model added
- deterministic `RiskCheckResult` model added
- ALLOW results cannot contain violations
- BLOCK results require at least one violation
- `RiskLimits` added using `Decimal` for risk percentages
- non-finite Decimal risk limits are rejected
- risk-per-trade percentage validation added
- daily-loss-limit percentage validation added
- maximum-open-position validation added
- total-exposure limit validation added
- total-exposure percentage may exceed 100 percent for leveraged markets
- broker-independent `TradeSide` contract added
- immutable `AccountRiskState` added
- immutable `RiskInstrumentSpec` added
- immutable `TradeRiskCandidate` added
- immutable `RiskEvaluationInput` added
- normalized symbol identity must match between trade and instrument
- broker-native symbol identity must match between trade and instrument
- runtime broker/client objects are rejected by the risk input contract
- account, instrument, and trade numeric risk inputs use `Decimal`
- quantity range validation added
- finite-value validation added for risk calculation inputs

Risk-engine boundary decisions:

- non-positive account equity is accepted by the schema so the
  deterministic engine can return `INVALID_ACCOUNT_EQUITY`
- invalid stop-loss geometry is accepted by the schema so the
  deterministic engine can return `INVALID_STOP_LOSS`
- schema validation remains separate from deterministic risk decisions
- candidate trade objects describe proposals only
- candidate trade objects cannot submit or execute orders

Automated validation:

- complete targeted risk schema and input-contract suite passed
- full backend regression suite passed
- full backend Ruff check passed
- `git diff --check` passed
- repository integrity check passed

Safety validation:

- risk domain contains no `MetaTrader5` dependency
- risk domain contains no `order_send`
- risk domain contains no `order_check`
- risk domain contains no `mt5.login`
- risk domain contains no `symbol_select`
- risk domain contains no HTTP client mechanism
- risk domain contains no broker client mechanism
- backend remained stopped during Checkpoint 6.1 development
- execution agent remained stopped during Checkpoint 6.1 development
- execution remains disabled
- live trading remains disabled
- no broker mutation or execution capability was introduced

Checkpoint 6.1 establishes the deterministic, broker-independent data
contract that later risk calculations will consume.

Next:

### Checkpoint 6.2 - Position Sizing Engine - COMPLETE

Completed:

- deterministic position-sizing engine added
- all position-sizing calculations use `Decimal`
- position sizing is derived from:
  - account equity
  - configured risk-per-trade percentage
  - entry price
  - stop-loss price
  - broker tick size
  - broker loss tick value
  - broker minimum quantity
  - broker maximum quantity
  - broker quantity step
- deterministic risk budget calculation added
- deterministic stop-distance calculation added
- deterministic stop-tick calculation added
- deterministic loss-per-quantity calculation added
- deterministic raw-quantity calculation added
- deterministic normalized-quantity calculation added
- estimated monetary loss at stop is exposed
- calculation diagnostics are retained in the result contract
- sizing result contract is immutable
- machine-readable unavailable reasons added

Safety-first sizing behavior:

- position quantity is always rounded DOWN to the broker quantity step
- quantity normalization never rounds upward into additional risk
- normalized estimated stop loss cannot exceed the configured risk budget
- broker maximum quantity is enforced
- non-step-aligned maximum quantities are reduced to the largest safe
  zero-anchored grid quantity
- calculated quantities below broker minimum are rejected safely
- non-positive account equity returns a deterministic unavailable result
- invalid BUY stop-loss geometry is rejected
- invalid SELL stop-loss geometry is rejected
- missing broker `tick_value_loss` returns a safe unavailable result
- `contract_size` is not used to guess missing tick-value risk
- unsupported or ambiguous quantity grids return
  `invalid_quantity_grid`
- misaligned minimum quantity and quantity step are rejected rather
  than guessed
- quantity grids with no positive executable step are rejected
- no broker-native quantity convention is silently inferred

Deterministic formula:

- risk budget =
  equity multiplied by risk-per-trade percentage divided by 100
- stop distance =
  absolute difference between entry price and stop-loss price
- stop ticks =
  stop distance divided by tick size
- loss per quantity =
  stop ticks multiplied by broker loss tick value
- raw quantity =
  risk budget divided by loss per quantity
- normalized quantity =
  raw quantity rounded DOWN to broker quantity step
- estimated stop loss =
  normalized quantity multiplied by loss per quantity

Key safety validation:

- a raw quantity requiring normalization from above 0.14 but below 0.15
  was normalized to 0.14
- quantity 0.15 would have produced estimated loss of 105 against
  risk budget 100
- engine instead selected 0.14
- resulting estimated loss was 98 against risk budget 100
- automated assertion confirmed normalized risk did not exceed
  configured risk

Automated validation:

- targeted position-sizing suite: 31 passed
- combined risk-domain suite: 104 passed
- full backend regression suite passed
- full backend Ruff check passed
- `git diff --check` passed
- repository integrity check passed
- known Starlette/httpx test warning remains non-blocking

Safety validation:

- risk domain contains no `MetaTrader5` dependency
- risk domain contains no `order_send`
- risk domain contains no `order_check`
- risk domain contains no `mt5.login`
- risk domain contains no `symbol_select`
- risk domain contains no HTTP client mechanism
- risk domain contains no broker client mechanism
- backend remained stopped during Checkpoint 6.2 development
- execution agent remained stopped during Checkpoint 6.2 development
- execution remains disabled
- live trading remains disabled
- no broker mutation capability was introduced
- no order submission capability was introduced
- no execution capability was introduced

Checkpoint 6.2 establishes deterministic, auditable, safety-first
position sizing without any broker communication or execution behavior.

Next:

### Checkpoint 6.3 - Trade and Portfolio Guardrails - COMPLETE

Completed:

- pure deterministic trade and portfolio guardrail engine added
- guardrails consume immutable `RiskEvaluationInput`
- guardrails consume finalized deterministic position sizing
- instrument tradability guard added
- defensive positive-equity guard added
- BUY and SELL stop-loss geometry is independently validated
- broker minimum-quantity guard added
- broker maximum-quantity guard added
- broker quantity-step guard added
- ambiguous or malformed quantity grids are independently blocked
- maximum-open-position guard added
- risk-per-trade monetary guard added
- daily-loss guard added
- projected daily-loss guard added
- maximum-total-exposure guard added
- normalized gross exposure data contract added
- missing normalized exposure data blocks safely
- multiple simultaneous violations are accumulated deterministically

Exposure contract:

- `gross_exposure_per_quantity` added to the broker-independent
  instrument risk specification
- exposure is represented in the account risk currency
- exposure values use `Decimal`
- exposure value must be positive and finite when supplied
- `contract_size` does not imply or substitute for normalized exposure
- the deterministic risk engine does not guess account-currency exposure
- missing normalized exposure returns
  `exposure_data_unavailable`

Daily-loss behavior:

- when the current daily loss has already reached the configured limit,
  additional trades are blocked
- when the proposed trade could push daily loss above the configured limit,
  the trade is blocked
- projected daily loss exactly equal to the configured limit is permitted
  when the limit has not already been reached

Exposure behavior:

- proposed exposure is calculated from finalized quantity multiplied by
  normalized `gross_exposure_per_quantity`
- proposed exposure is added to current account gross exposure
- projected exposure above the configured limit is blocked
- projected exposure exactly equal to the configured limit is permitted
- no broker-specific exposure formula is silently inferred

Guardrail hardening:

- monetary stop risk is independently reproduced from the current
  `RiskEvaluationInput`
- guardrails do not trust supplied sizing monetary diagnostics
- current entry price, stop-loss price, tick size, and loss tick value
  determine authoritative stop risk
- stale or tampered sizing diagnostics return
  `position_sizing_mismatch`
- forged available sizing cannot bypass missing current tick-risk data
- invalid stop geometry is blocked independently of position sizing
- invalid quantity grids are blocked independently of position sizing
- authoritative risk-per-trade decisions use current evaluation data
- authoritative daily-loss decisions use current evaluation data
- finalized quantity remains subject to broker min/max/step defenses

Machine-readable guardrail reasons include:

- `invalid_account_equity`
- `invalid_stop_loss`
- `risk_per_trade_exceeded`
- `daily_loss_limit_reached`
- `max_open_positions_reached`
- `max_total_exposure_exceeded`
- `exposure_data_unavailable`
- `instrument_not_tradable`
- `position_sizing_mismatch`
- `invalid_quantity_grid`
- `position_size_below_minimum`
- `position_size_above_maximum`
- `position_size_step_mismatch`

Automated validation:

- hardened guardrail suite: 27 passed
- complete deterministic risk suite passed
- full backend regression suite passed
- full backend Ruff check passed
- `git diff --check` passed
- exact working-tree integrity check passed
- required hardening fragments verified
- known Starlette/httpx test warning remains non-blocking

Safety validation:

- risk domain contains no `MetaTrader5` dependency
- risk domain contains no `order_send`
- risk domain contains no `order_check`
- risk domain contains no `mt5.login`
- risk domain contains no `symbol_select`
- risk domain contains no HTTP client mechanism
- risk domain contains no broker client mechanism
- guardrail evaluation performs no persistence
- guardrail evaluation performs no order submission
- guardrail evaluation performs no execution
- backend remained stopped during Checkpoint 6.3 development
- execution agent remained stopped during Checkpoint 6.3 development
- execution remains disabled
- live trading remains disabled

Checkpoint 6.3 establishes deterministic portfolio safety boundaries
around finalized position sizing and independently verifies the monetary
risk information used for those decisions.

Next:

### Checkpoint 6.4 - Risk Evaluation Service - COMPLETE

Completed:

- deterministic risk-evaluation orchestration service added
- `RiskEvaluationInput` is the single input contract
- deterministic position sizing runs first
- unavailable position sizing fails closed immediately
- unavailable sizing does not enter trade or portfolio guardrails
- available sizing is passed to deterministic guardrail evaluation
- final sizing diagnostics are preserved for auditability
- final ALLOW/BLOCK decision is exposed through `RiskEvaluationResult`
- final violation collection is exposed through `RiskEvaluationResult`
- orchestration contains no duplicated position-sizing formula
- orchestration contains no duplicated guardrail calculation

Sizing-failure mapping:

- `invalid_account_equity`
  maps to `invalid_account_equity`
- `invalid_stop_loss`
  maps to `invalid_stop_loss`
- `missing_tick_value_loss`
  maps to `missing_tick_value_loss`
- `invalid_quantity_grid`
  maps to `invalid_quantity_grid`
- `position_size_below_minimum`
  maps to `position_size_below_minimum`
- unknown or unmapped future sizing failures fail closed to
  `position_sizing_mismatch`

Risk-evaluation hardening:

- `RiskEvaluationResult` is immutable
- unavailable position sizing cannot coexist with an ALLOW decision
- contradictory final result construction is rejected by model validation
- sizing failure short-circuits guardrail execution
- available sizing invokes guardrail evaluation exactly once
- guardrail BLOCK results are preserved without reinterpretation
- missing exposure remains a guardrail failure rather than a sizing failure
- sizing-reason mappings are tested against the complete current enum
- missing mapping entries fail closed rather than fail open
- repeated evaluation is deterministic
- risk evaluation does not mutate its input

Auditability:

- the complete `PositionSizingResult` is retained in the final result
- normalized quantity remains available for inspection
- estimated monetary stop loss remains available for inspection
- machine-readable sizing failure reason remains available
- final machine-readable risk violations remain available
- final risk decision remains explicitly ALLOW or BLOCK

Automated validation:

- risk-schema suite: 84 passed
- position-sizing suite: 31 passed
- hardened guardrail suite: 27 passed
- hardened risk-evaluation suite: 16 passed
- deterministic risk suite total: 158 passed
- full backend regression suite passed
- full backend Ruff check passed
- deterministic risk-suite collection passed
- `git diff --check` passed
- exact working-tree integrity check passed
- required Checkpoint 6.4 orchestration fragments verified
- known Starlette/httpx test warning remains non-blocking

Safety validation:

- risk domain contains no `MetaTrader5` dependency
- risk domain contains no `order_send`
- risk domain contains no `order_check`
- risk domain contains no `mt5.login`
- risk domain contains no `symbol_select`
- risk domain contains no HTTP client mechanism
- risk domain contains no broker client mechanism
- risk evaluation contains no persistence mechanism
- risk evaluation contains no AI mechanism
- risk evaluation contains no order submission mechanism
- risk evaluation contains no execution mechanism
- backend remained stopped during Checkpoint 6.4 development
- execution agent remained stopped during Checkpoint 6.4 development
- execution remains disabled
- live trading remains disabled

Checkpoint 6.4 establishes one deterministic orchestration boundary that
combines position sizing and portfolio guardrails into a single auditable
risk decision without introducing broker communication or execution.

Next:

### Checkpoint 6.5 - Read-only Risk Preview API - COMPLETE

Completed:

- read-only risk-preview HTTP adapter added
- deterministic risk engine remains separated from FastAPI
- risk-preview router registered with the main FastAPI application
- public endpoint added at `POST /api/v1/risk/preview`
- structured `RiskEvaluationInput` JSON is accepted as the request body
- deterministic `evaluate_risk()` remains the authoritative evaluation service
- HTTP adapter contains no duplicated sizing or guardrail logic
- response preserves complete deterministic risk-evaluation diagnostics

Read-only response contract:

- `read_only` is always `true`
- `execution_enabled` is always `false`
- `live_trading_enabled` is always `false`
- final ALLOW/BLOCK result is returned
- finalized position-sizing diagnostics are returned
- machine-readable risk violations are returned
- missing sizing inputs continue to fail closed
- guardrail failures continue to return deterministic BLOCK results

Public API behavior:

- OpenAPI exposes exactly one `/api/v1/risk` endpoint
- the endpoint supports POST only
- GET requests are rejected
- valid candidate returns deterministic ALLOW
- valid example normalizes quantity to `0.10`
- untradable instrument returns deterministic BLOCK
- missing `tick_value_loss` returns deterministic sizing BLOCK
- malformed risk inputs return HTTP 422
- request bodies cannot override execution or live-trading safety flags
- repeated identical previews return identical results
- preview requests do not mutate system status

Automated validation:

- risk-preview API suite: 9 passed
- risk-schema suite: 84 passed
- position-sizing suite: 31 passed
- guardrail suite: 27 passed
- risk-evaluation suite: 16 passed
- deterministic risk plus API suite total: 167 passed
- full backend regression suite passed
- full backend Ruff check passed
- deterministic risk plus API test collection passed
- `git diff --check` passed
- exact working-tree integrity check passed
- known Starlette/httpx TestClient warning remains non-blocking
- known Windows LF-to-CRLF Git warning remains non-blocking

Architecture and safety validation:

- deterministic risk core remains HTTP-free
- deterministic risk core remains persistence-free
- deterministic risk core remains broker-independent
- deterministic risk core remains execution-free
- existing `risk/models.py` persistence model remains unchanged
- risk-preview HTTP adapter contains no broker client
- risk-preview HTTP adapter contains no MT5 mechanism
- risk-preview HTTP adapter contains no persistence mechanism
- risk-preview HTTP adapter contains no background execution mechanism
- risk-preview HTTP adapter contains no subprocess or socket mechanism
- backend remained stopped during Checkpoint 6.5 development
- execution agent remained stopped during Checkpoint 6.5 development
- execution remains disabled
- live trading remains disabled

Checkpoint 6.5 establishes a safe read-only HTTP boundary around the
deterministic risk engine without adding order creation, persistence,
broker mutation, or execution capability.

Next:

### Checkpoint 6.6 - Final Phase 6 Validation and Closure - COMPLETE

Final Phase 6 regression:

- repository started from the frozen Checkpoint 6.5 commit
- local HEAD matched `origin/main`
- working tree was clean before validation
- backend remained stopped
- execution agent remained stopped
- full backend test suite passed
- full backend Ruff check passed
- deterministic risk plus API suite passed
- deterministic risk plus API collection remained exactly 167 tests
- `git diff --check` passed
- validation left the working tree unchanged

Final deterministic risk and API counts:

- risk schemas: 84
- position sizing: 31
- trade and portfolio guardrails: 27
- risk evaluation service: 16
- read-only risk preview API: 9
- deterministic risk plus API total: 167

Cross-system safety audit:

- execution-agent full test suite passed
- execution agent exposes exactly seven approved GET-only routes
- execution-agent effective `execution_enabled` remained false
- execution-agent effective `live_trading_enabled` remained false
- no `mt5.order_send()` call exists
- no `mt5.order_check()` call exists
- no `mt5.login()` call exists
- no explicit `mt5.symbol_select()` call exists
- backend risk API remains exactly one POST-only preview endpoint
- backend execution flag remains false
- backend live-trading flag remains false
- deterministic risk core remains isolated from HTTP
- deterministic risk core remains isolated from persistence
- deterministic risk core remains broker-independent
- deterministic risk core remains isolated from MT5
- deterministic risk core remains execution-free
- risk-preview HTTP adapter remains calculation-only
- Flutter analyze completed with no issues
- Flutter test suite: 84 passed
- Flutter networking remains GET-only
- Flutter contains no trade-execution or order-entry methods
- Flutter contains no direct MT5 integration
- backend remained stopped after the audit
- execution agent remained stopped after the audit
- final working tree remained clean

Phase 6 safety state:

- deterministic sizing is authoritative
- deterministic guardrails are authoritative
- unavailable sizing fails closed
- stale or inconsistent sizing diagnostics fail closed
- risk limits cannot be bypassed by the preview API
- preview API performs no persistence
- preview API performs no broker mutation
- preview API performs no order creation
- preview API performs no execution
- AI has no execution authority
- execution remains disabled
- live trading remains disabled

Phase 6 deliverables completed:

- Checkpoint 6.1 - Deterministic Risk Contract and Core Types
- Checkpoint 6.2 - Position Sizing Engine
- Checkpoint 6.3 - Trade and Portfolio Guardrails
- Checkpoint 6.4 - Risk Evaluation Service
- Checkpoint 6.5 - Read-only Risk Preview API
- Checkpoint 6.6 - Final Phase 6 Validation and Closure

Phase 6 - Risk Engine is COMPLETE.

The system now has a frozen deterministic risk boundary before any
simulated or broker execution work begins.

Next:

### Phase 7 - Simulated Execution
