# Database Model

Trade Command Center V2 uses SQLAlchemy ORM models and Alembic migrations.

## Initial tables

- `users`
- `broker_connections`
- `trading_accounts`
- `risk_profiles`
- `audit_events`
- `execution_records`

## Credential rule

`broker_connections.secret_ref` is only an opaque reference to an approved secret store.

The database must not contain raw:

- MT5 passwords
- Binance API secrets
- private keys
- JWT signing secrets

## Execution identity

`execution_records.client_order_id` is unique. It is the database foundation for later duplicate-order/idempotency protection.

## Development database

The local development database is:

`backend/runtime/trade_command_center_dev.db`

It is ignored by Git. Database structure is preserved through Alembic migration files, not by committing SQLite database files.