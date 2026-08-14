from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin, new_uuid


class RiskProfile(TimestampMixin, Base):
    __tablename__ = "risk_profiles"

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
    risk_per_trade_pct: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        nullable=False,
    )
    daily_loss_limit_pct: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        nullable=False,
    )
    max_open_positions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    max_total_exposure_pct: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )