from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.accounts.models import Account
from app.accounts.session_service import (
    AuthenticatedSession,
    authenticate_session,
)
from app.db.session import DatabaseSession


bearer_scheme = HTTPBearer(auto_error=False)

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


def unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_authenticated_session(
    db: DatabaseSession,
    credentials: BearerCredentials,
) -> AuthenticatedSession:
    if credentials is None:
        raise unauthorized_exception()

    token = credentials.credentials

    if not token:
        raise unauthorized_exception()

    authenticated = authenticate_session(
        db,
        token,
    )

    if authenticated is None:
        raise unauthorized_exception()

    return authenticated


CurrentSession = Annotated[
    AuthenticatedSession,
    Depends(get_authenticated_session),
]


def get_current_account(
    authenticated: CurrentSession,
) -> Account:
    return authenticated.account


CurrentAccount = Annotated[
    Account,
    Depends(get_current_account),
]



