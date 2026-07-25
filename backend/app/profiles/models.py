from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Profile(TimestampMixin, Base):
    __tablename__ = "profiles"

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            name="uq_profiles_account_id",
        ),
        CheckConstraint(
            "display_name IS NULL OR length(trim(display_name)) > 0",
            name="ck_profiles_display_name_not_blank",
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm > 0",
            name="ck_profiles_positive_height",
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

    display_name: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    height_cm: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    is_discoverable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Prompt(TimestampMixin, Base):
    __tablename__ = "prompts"

    __table_args__ = (
        UniqueConstraint(
            "slug",
            name="uq_prompts_slug",
        ),
        CheckConstraint(
            "length(trim(text)) > 0",
            name="ck_prompts_text_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=true(),
    )


class ProfilePromptAnswer(TimestampMixin, Base):
    __tablename__ = "profile_prompt_answers"

    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "prompt_id",
            name="uq_profile_prompt_answers_profile_prompt",
        ),
        CheckConstraint(
            "length(trim(answer)) > 0",
            name="ck_profile_prompt_answers_answer_not_blank",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )

    profile_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    prompt_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("prompts.id", ondelete="RESTRICT"),
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
