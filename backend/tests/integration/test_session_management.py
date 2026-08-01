from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountSession
from app.accounts.session_service import create_session


def create_account(db_session: Session, subject: str) -> Account:
    account = Account(
        auth_issuer="https://identity-provider.test/auth/v1",
        auth_subject=subject,
    )
    db_session.add(account)
    db_session.flush()
    return account


def test_list_sessions_returns_only_authenticated_accounts_sessions(
    client: TestClient,
    db_session: Session,
) -> None:
    account = create_account(db_session, "account-one")
    current = create_session(
        db_session,
        account,
        device_name="Current iPhone",
    )
    other = create_session(
        db_session,
        account,
        device_name="Other iPad",
    )

    another_account = create_account(db_session, "account-two")
    create_session(
        db_session,
        another_account,
        device_name="Someone else's phone",
    )

    response = client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {current.token}"},
    )

    assert response.status_code == 200

    sessions = response.json()["sessions"]
    assert {item["id"] for item in sessions} == {
        str(current.session.id),
        str(other.session.id),
    }
    assert sum(item["is_current"] for item in sessions) == 1
    assert next(
        item for item in sessions if item["is_current"]
    )["device_name"] == "Current iPhone"


def test_delete_current_session_revokes_only_current_device(
    client: TestClient,
    db_session: Session,
) -> None:
    account = create_account(db_session, "current-logout")
    current = create_session(db_session, account)
    other = create_session(db_session, account)

    response = client.delete(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {current.token}"},
    )

    assert response.status_code == 204
    assert response.content == b""
    assert current.session.revoked_at is not None
    assert other.session.revoked_at is None


def test_delete_all_sessions_revokes_every_device_for_account(
    client: TestClient,
    db_session: Session,
) -> None:
    account = create_account(db_session, "all-devices-logout")
    first = create_session(db_session, account)
    second = create_session(db_session, account)

    another_account = create_account(db_session, "unrelated-account")
    unrelated = create_session(db_session, another_account)

    response = client.delete(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {first.token}"},
    )

    assert response.status_code == 204

    db_session.expire_all()
    account_sessions = list(
        db_session.scalars(
            select(AccountSession).where(
                AccountSession.account_id == account.id
            )
        )
    )

    assert len(account_sessions) == 2
    assert all(
        account_session.revoked_at is not None
        for account_session in account_sessions
    )
    assert second.session.id in {
        account_session.id for account_session in account_sessions
    }

    db_session.refresh(unrelated.session)
    assert unrelated.session.revoked_at is None
