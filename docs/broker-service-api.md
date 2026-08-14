# Broker Service and API

## Purpose

Checkpoint 3.2 validates the complete broker-independent read path before connecting Trade Command Center to a real broker.

The current architecture is:

FastAPI
    |
BrokerService
    |
BrokerManager
    |
BrokerAdapter
    |
Concrete Broker Adapter

Current concrete adapter:

- SimulatedBrokerAdapter

Future adapters:

- PrimeXBT MT5
- Binance

## Simulated Broker

The simulated broker provides deterministic read-only data without requiring:

- network access
- broker credentials
- MT5
- PrimeXBT
- Binance
- real funds

It currently exposes six representative instruments across multiple asset classes:

- EUR/USD
- GBP/USD
- XAU/USD
- WTI/USD
- NAS100/USD
- BTC/USD

The catalog deliberately proves that Trade Command Center is not a gold-only application.

## BrokerManager

BrokerManager maintains the registry of broker adapter instances by connection ID.

Application code does not construct or locate concrete adapters directly.

Example future registry:

- sim-main -> SimulatedBrokerAdapter
- primexbt-demo -> PrimeXBT MT5 adapter
- primexbt-live -> PrimeXBT MT5 adapter
- binance-main -> Binance adapter

## BrokerService

BrokerService provides the application-facing read-only broker interface.

It currently supports:

- connection lifecycle
- connection health
- capabilities
- account information
- instruments
- individual instrument lookup
- quotes
- candles
- positions
- open orders

BrokerService intentionally contains no order placement API during the read-only phases.

## FastAPI Broker Interface

The broker API exposes normalized broker information through HTTP.

Normalized symbols are supplied through query parameters where appropriate so symbols containing `/` do not interfere with URL routing.

Examples:

GET /api/v1/brokers/sim-main/quote?symbol=XAU/USD

GET /api/v1/brokers/sim-main/candles?symbol=BTC/USD&timeframe=H1&count=100

Broker-native symbols such as XAUUSD and BTCUSD are also accepted by adapters that support them.

## System Status

The system endpoint now reports the actual number of registered broker connections instead of a hard-coded value.

Execution remains explicitly disabled:

- execution_enabled = false
- live_trading_enabled = false

## Safety Boundary

Checkpoint 3.2 exposes no HTTP route for:

- buying
- selling
- placing an order
- modifying an order
- cancelling an order
- closing a position
- executing a trade

Execution will be introduced only in later controlled phases.

## Validation

Checkpoint 3.2 validation:

- 51 backend tests passed
- Ruff passed across the entire backend
- read-only broker HTTP workflow validated end-to-end
