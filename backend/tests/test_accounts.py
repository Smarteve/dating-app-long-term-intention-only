from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account


def test_account_can_be_persisted(db_session: Session) -> None:
    account = Account(
        auth_issuer="test",
        auth_subject="user-123",
    )

    db_session.add(account)
    db_session.flush()

    saved_account = db_session.scalar(
        select(Account).where(Account.id == account.id)
    )

    assert saved_account is not None
    assert saved_account.auth_issuer == "test"
    assert saved_account.auth_subject == "user-123"
    assert saved_account.status == "active"