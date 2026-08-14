# Broker Adapter Contract

## Purpose

Trade Command Center uses a broker-independent adapter layer so the core application does not depend directly on PrimeXBT MT5, Binance, or any future broker API.

All broker integrations must translate broker-native data into the normalized Trade Command Center schemas.

## Supported Broker Types

Current architecture defines:

- simulated
- primexbt_mt5
- binance

The simulated adapter is implemented first to validate the architecture before any real broker connection is introduced.

## Symbol Normalization

Two symbol identifiers are maintained:

- `symbol` — Trade Command Center normalized symbol
- `broker_symbol` — exact broker-native symbol

Example:

- normalized: `XAU/USD`
- broker-native: `XAUUSD`

This prevents application logic from depending on broker-specific naming conventions.

## Normalized Data Models

The broker layer currently defines normalized models for:

- broker health
- broker account
- instruments
- quotes
- candles
- positions
- open orders

## Broker Adapter Operations

Every broker adapter must provide:

- `connect()`
- `disconnect()`
- `health()`
- `get_account()`
- `get_instruments()`
- `get_instrument()`
- `get_quote()`
- `get_candles()`
- `get_positions()`
- `get_open_orders()`

The permanent contract also defines:

- `place_order()`
- `modify_order()`
- `cancel_order()`
- `close_position()`

Execution operations are disabled by default and raise `BrokerOperationNotSupported`.

Execution-capable adapters must explicitly override these methods during later execution phases.

## Safety Rule

Read-only broker connectivity must never implicitly enable order execution.

Broker capabilities explicitly describe whether execution functionality is available.

The backend remains authoritative for risk validation and future trade authorization.

## Checkpoint 3.1 Result

Checkpoint 3.1 established and tested the normalized broker contract.

Validation result:

- broker contract tests: 7 passed
- full backend suite: 12 passed
- Ruff: all checks passed
