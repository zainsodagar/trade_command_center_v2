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
## Phase 3 — Broker Adapter Foundation

### Checkpoint 3.1 — Normalized Broker Contract ? COMPLETE

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

### Checkpoint 3.2 — Simulated Broker Adapter

### Checkpoint 3.2 — Simulated Broker Integration ? COMPLETE

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

### Phase 3 — Broker Adapter Foundation ? COMPLETE

Phase 3 now provides the permanent broker-independent foundation required for PrimeXBT MT5 and future Binance integration.

Next:

## Phase 4 — PrimeXBT MT5 Demo Read-Only
