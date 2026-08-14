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
