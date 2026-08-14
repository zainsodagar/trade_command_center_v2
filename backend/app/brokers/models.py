from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin, new_uuid


class BrokerConnection(TimestampMixin, Base):
    __tablename__ = "broker_connections"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=new_uuid,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )
    broker_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )
    account_mode: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
    )

    # Reference only. Never store a broker password or API secret in this table.
    secret_ref: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )