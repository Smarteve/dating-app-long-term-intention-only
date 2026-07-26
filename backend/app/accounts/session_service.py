from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountSession
from app.accounts.session_tokens import (
    generate_session_token,
    hash_session_token,
)


SESSION_LIFETIME = timedelta(days=30)
LAST_SEEN_UPDATE_INTERVAL = timedelta(minutes=15)


@dataclass(frozen=True)
class CreatedSession:
    token: str
    session: AccountSession


@dataclass(frozen=True)
class AuthenticatedSession:
    account: Account
    session: AccountSession


def create_session(
    db: Session,
    account: Account,
    *,
    device_name: str | None = None,
    now: datetime | None = None,
) -> CreatedSession:
    current_time = now or datetime.now(UTC)
    token = generate_session_token()

    normalized_device_name = (
        device_name.strip()
        if device_name is not None and device_name.strip()
        else None
    )

    account_session = AccountSession(
        account_id=account.id,
        token_hash=hash_session_token(token),
        expires_at=current_time + SESSION_LIFETIME,
        last_seen_at=current_time,
        device_name=normalized_device_name,
    )

    db.add(account_session)
    db.flush()

    return CreatedSession(
        token=token,
        session=account_session,
    )


def authenticate_session(
    db: Session,
    token: str,
    *,
    now: datetime | None = None,
) -> AuthenticatedSession | None:
    current_time = now or datetime.now(UTC)

    statement = (
        select(AccountSession, Account)
        .join(
            Account,
            Account.id == AccountSession.account_id,
        )
        .where(
            AccountSession.token_hash == hash_session_token(token),
            AccountSession.revoked_at.is_(None),
            AccountSession.expires_at > current_time,
            Account.status == "active",
        )
    )

    row = db.execute(statement).one_or_none()

    if row is None:
        return None

    account_session, account = row

    if (
        account_session.last_seen_at is None
        or account_session.last_seen_at
        <= current_time - LAST_SEEN_UPDATE_INTERVAL
    ):
        account_session.last_seen_at = current_time

    return AuthenticatedSession(
        account=account,
        session=account_session,
    )


def revoke_session(
    db: Session,
    token: str,
    *,
    now: datetime | None = None,
) -> bool:
    current_time = now or datetime.now(UTC)

    statement = select(AccountSession).where(
        AccountSession.token_hash == hash_session_token(token),
    )
    account_session = db.scalar(statement)

    if account_session is None:
        return False

    if account_session.revoked_at is None:
        account_session.revoked_at = current_time

    return True


def revoke_all_sessions(
    db: Session,
    account_id: UUID,
    *,
    now: datetime | None = None,
) -> None:
    current_time = now or datetime.now(UTC)

    statement = (
        update(AccountSession)
        .where(
            AccountSession.account_id == account_id,
            AccountSession.revoked_at.is_(None),
        )
        .values(revoked_at=current_time)
    )

    db.execute(statement)