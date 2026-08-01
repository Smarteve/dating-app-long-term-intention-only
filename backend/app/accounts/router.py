from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.accounts.account_service import get_or_create_account
from app.accounts.dependencies import (
    BearerCredentials,
    CurrentAccount,
    CurrentSession,
)
from app.accounts.identity_provider import (
    IdentityProvider,
    IdentityVerificationError,
    get_identity_provider,
)
from app.accounts.schemas import (
    ActiveSessionListResponse,
    ActiveSessionResponse,
    SessionExchangeRequest,
    SessionResponse,
)
from app.accounts.session_service import (
    create_session,
    list_active_sessions,
    revoke_account_session,
    revoke_all_sessions,
)
from app.db.session import DatabaseSession


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

IdentityProviderDependency = Annotated[
    IdentityProvider,
    Depends(get_identity_provider),
]


def invalid_identity_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identity token is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/exchange",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def exchange_identity_token(
    request: SessionExchangeRequest,
    db: DatabaseSession,
    credentials: BearerCredentials,
    identity_provider: IdentityProviderDependency,
) -> SessionResponse:
    if credentials is None or not credentials.credentials:
        raise invalid_identity_token()

    try:
        identity = identity_provider.verify_token(
            credentials.credentials
        )
    except IdentityVerificationError:
        raise invalid_identity_token() from None

    account = get_or_create_account(db, identity)

    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is unavailable",
        )

    created = create_session(
        db,
        account,
        device_name=request.device_name,
    )

    return SessionResponse(
        access_token=created.token,
        expires_at=created.session.expires_at,
        session_id=created.session.id,
    )


@router.get("", response_model=ActiveSessionListResponse)
def get_active_sessions(
    authenticated: CurrentSession,
    db: DatabaseSession,
) -> ActiveSessionListResponse:
    sessions = list_active_sessions(
        db,
        authenticated.account.id,
    )

    return ActiveSessionListResponse(
        sessions=[
            ActiveSessionResponse(
                id=account_session.id,
                device_name=account_session.device_name,
                created_at=account_session.created_at,
                last_seen_at=account_session.last_seen_at,
                expires_at=account_session.expires_at,
                is_current=(
                    account_session.id == authenticated.session.id
                ),
            )
            for account_session in sessions
        ],
    )


@router.delete(
    "/current",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_current_session(
    authenticated: CurrentSession,
) -> Response:
    revoke_account_session(authenticated.session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_all_sessions(
    account: CurrentAccount,
    db: DatabaseSession,
) -> Response:
    revoke_all_sessions(db, account.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
