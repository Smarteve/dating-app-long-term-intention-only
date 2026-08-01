from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.identity_provider import VerifiedIdentity
from app.accounts.models import Account


def get_or_create_account(
    db: Session,
    identity: VerifiedIdentity,
) -> Account:
    statement = select(Account).where(
        Account.auth_issuer == identity.issuer,
        Account.auth_subject == identity.subject,
    )
    account = db.scalar(statement)

    if account is not None:
        return account

    account = Account(
        auth_issuer=identity.issuer,
        auth_subject=identity.subject,
    )
    db.add(account)
    db.flush()

    return account
