from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin, new_uuid


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=new_uuid,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class TradingAccount(TimestampMixin, Base):
    __tablename__ = "trading_accounts"
    __table_args__ = (
        UniqueConstraint(
            "broker_connection_id",
            "broker_account_id",
            name="uq_trading_accounts_connection_account",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=new_uuid,
    )
    broker_connection_id: Mapped[str] = mapped_column(
        ForeignKey("broker_connections.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    broker_account_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    server: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    currency: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )