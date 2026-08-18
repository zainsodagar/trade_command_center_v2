# Architecture Decisions

## ADR-001: Canonical project

The canonical development project is:

`D:\dev\projects\trade_command_center_v2`

The previous project remains at:

`D:\dev\projects\trade_command_center`

The previous project is reference-only and must not be modified during the V2 rebuild.

## ADR-002: Repository layout

The project uses one monorepo for Flutter applications, FastAPI backend, Windows execution agent, tests, scripts, infrastructure, and documentation.

## ADR-003: Broker rollout

1. PrimeXBT MT5 demo
2. PrimeXBT MT5 real
3. Binance

## ADR-004: Risk authority

The backend is the sole authority for final position sizing, margin validation, exposure limits, and trade approval.

## ADR-005: Execution isolation

The Flutter application does not connect directly to MetaTrader 5 and does not store broker credentials. MT5 execution is performed through a separate Windows execution agent.

## ADR-006: AI boundary

AI modules may analyze markets and create proposed trade plans. They cannot bypass deterministic risk controls or directly send broker orders.

## ADR-007: Instrument support

The system supports all instruments exposed by connected PrimeXBT MT5 and Binance accounts. Broker symbol catalogues are loaded dynamically.

## Broker Adapter Abstraction

Decision: Trade Command Center core services must never communicate directly with PrimeXBT MT5, Binance, or another broker implementation.

All broker integrations must implement the common `BrokerAdapter` contract and convert broker-native data into normalized Trade Command Center schemas.

Normalized symbols and broker-native symbols are stored separately.

Execution methods exist in the permanent interface but remain disabled unless explicitly implemented by an execution-capable adapter.

This allows read-only connectivity, risk controls, simulated execution, PrimeXBT MT5, and Binance to share a common application architecture.

## Broker Service Boundary

Decision: FastAPI routes must not interact with concrete broker adapters directly.

The broker application flow is:

FastAPI -> BrokerService -> BrokerManager -> BrokerAdapter

BrokerManager owns adapter registration and lookup by connection ID.

BrokerService provides application-level broker operations and currently exposes read-only functionality only.

Execution methods are intentionally not exposed through BrokerService or FastAPI during the broker foundation and read-only broker phases.

The simulated broker is used to prove the architecture before introducing PrimeXBT MT5.

## Separate Windows MT5 Agent

Decision: MetaTrader 5 integration must run behind a separate
Windows execution-agent boundary rather than being imported directly
inside the main FastAPI backend.

Architecture:

Backend -> Windows MT5 Agent -> MT5 Terminal -> PrimeXBT

Reasons:

- isolate Windows-specific MT5 dependencies
- keep the main backend broker-independent
- prevent broker terminal failures from directly affecting the backend
- create an explicit security boundary before execution is introduced
- allow the main backend and future mobile clients to remain platform-independent

The agent initially binds only to 127.0.0.1.

Checkpoint 4.1 contains no trading endpoints and defaults all execution
and live-trading settings to false.
## MT5 Account Discovery Without Stored Credentials

Decision: During PrimeXBT MT5 read-only integration, Trade Command Center inspects the account already authenticated inside the configured PXBT MT5 terminal.

The application does not call mt5.login() and does not store the MT5 account password in source code, environment configuration, or database fields during this phase.

The execution agent detects the account using account_info() only after successfully initializing the explicitly configured PXBT terminal.

The account trade mode must be exposed so the application can distinguish demo, contest, real, and unknown accounts.

During Phase 4, only demo-account read access is intended.

The full MT5 login number is not exposed through the execution-agent API. A masked representation may be returned for operator identification.

Broker or terminal permissions such as trade_allowed or trade_expert do not override Trade Command Center safety gates. TCC execution_enabled and live_trading_enabled remain independent controls and are both false during Phase 4.

## MT5 Historical Data and Implicit Symbol Selection

Decision: Trade Command Center must not explicitly call
`mt5.symbol_select()` during the Phase 4 read-only integration.

Historical-rate requests use `copy_rates_from_pos()` against the
broker-native symbol.

PXBT MT5 has been observed to internally change a symbol from
`selected=false` to `selected=true` when historical rates are loaded,
even though Trade Command Center did not call `symbol_select()`.

The execution agent therefore records symbol state before and after
historical retrieval.

It does not attempt to restore the original selection state because
calling `symbol_select(..., False)` would itself introduce an explicit
terminal-state mutation.

Instrument selection and visibility are not treated as indicators of
tradability.

Quote or candle availability is also not treated as proof that new
orders are allowed.

## MT5 Read-Only Account Data Boundary

Decision: Detailed MT5 financial account state may be exposed by the
Windows execution agent during Phase 4 only when:

- MT5 integration is enabled
- the authenticated account is a demo account
- `execution_enabled=false`
- `live_trading_enabled=false`

Permitted read-only account data includes:

- balance
- credit
- profit
- equity
- margin
- free margin
- margin level
- margin call level
- stop-out level
- leverage
- account currency
- account mode
- broker server
- broker company
- related read-only MT5 account metadata

The internal MT5 login may remain available inside the execution agent
for account identity validation.

HTTP responses expose only the masked account login.

The full MT5 login must not be returned by the account API.

Broker-side values such as `trade_allowed` and `trade_expert` are
informational only and cannot override Trade Command Center safety
gates.

These account-data permissions do not authorize trade execution.
