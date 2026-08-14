# Changelog

## Unreleased

### Added

- Clean V2 monorepo structure.
- Initial architecture documentation.
- Project status and decision tracking.
- Secure default `.gitignore`.
- FastAPI backend application.
- Backend environment configuration.
- `/health` endpoint.
- `/api/v1/system/status` endpoint.
- Backend automated tests.
- Ruff linting configuration.
- Backend development scripts.
- SQLAlchemy database foundation.
- Alembic migrations.
- User, broker connection, trading account, risk profile, audit event, and execution record models.
- Database security tests preventing raw broker credential fields.
- Unique execution `client_order_id` foundation for idempotency.