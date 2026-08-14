from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin, new_uuid


class ExecutionRecord(TimestampMixin, Base):
    __tablename__ = "execution_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=new_uuid,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    broker_connection_id: Mapped[str] = mapped_column(
        ForeignKey("broker_connections.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    trading_account_id: Mapped[str | None] = mapped_column(
        ForeignKey("trading_accounts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # Generated client-side/backend idempotency identity.
    client_order_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    broker_order_id: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )
    side: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    order_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    requested_quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 10),
        nullable=False,
    )
    approved_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 10),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        index=True,
        nullable=False,
    )

    risk_snapshot_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )
    request_snapshot_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )
    broker_response_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )