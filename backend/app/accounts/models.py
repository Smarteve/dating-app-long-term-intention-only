from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
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


class AccountSession(TimestampMixin, Base):
    __tablename__ = "sessions"

    __table_args__ = (
        UniqueConstraint(
            "token_hash",
            name="uq_sessions_token_hash",
        ),
        CheckConstraint(
            "length(token_hash) = 64",
            name="ck_sessions_token_hash_length",
        ),
        CheckConstraint(
            "expires_at > created_at",
            name="ck_sessions_expiry_after_creation",
        ),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_sessions_revocation_after_creation",
        ),
        Index(
            "ix_sessions_account_id",
            "account_id",
        ),
        Index(
            "ix_sessions_expires_at",
            "expires_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    device_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )