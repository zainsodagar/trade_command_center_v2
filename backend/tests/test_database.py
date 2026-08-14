from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from backend.app.database.base import Base
from backend.app.database.models import MODEL_CLASSES


def make_test_engine():
    _ = MODEL_CLASSES
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_expected_database_tables_exist() -> None:
    engine = make_test_engine()
    Base.metadata.create_all(engine)

    table_names = set(inspect(engine).get_table_names())

    assert table_names == {
        "users",
        "broker_connections",
        "trading_accounts",
        "risk_profiles",
        "audit_events",
        "execution_records",
    }


def test_broker_connection_does_not_store_raw_credentials() -> None:
    engine = make_test_engine()
    Base.metadata.create_all(engine)

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("broker_connections")
    }

    forbidden = {
        "password",
        "api_key",
        "api_secret",
        "secret_key",
        "private_key",
        "mt5_password",
    }

    assert columns.isdisjoint(forbidden)
    assert "secret_ref" in columns


def test_execution_record_has_idempotency_identity() -> None:
    engine = make_test_engine()
    Base.metadata.create_all(engine)

    indexes = inspect(engine).get_indexes("execution_records")
    unique_constraints = inspect(engine).get_unique_constraints("execution_records")

    indexed_columns = {
        column
        for index in indexes
        for column in index["column_names"]
    }
    unique_columns = {
        column
        for constraint in unique_constraints
        for column in constraint["column_names"]
    }

    assert "client_order_id" in indexed_columns or "client_order_id" in unique_columns