from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"

    __table_args__ = (
        UniqueConstraint(
            "auth_issuer",
            "auth_subject",
            name="uq_accounts_auth_identity",
        ),
        CheckConstraint(
            "status IN ('active', 'paused', 'banned', 'deleted')",
            name="ck_accounts_valid_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    auth_issuer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    auth_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
