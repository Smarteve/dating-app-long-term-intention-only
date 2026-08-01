from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.identity_provider import (
    IdentityProvider,
    IdentityVerificationError,
    VerifiedIdentity,
    get_identity_provider,
)
from app.accounts.models import Account, AccountSession
from app.accounts.session_tokens import hash_session_token


class FakeIdentityProvider:
    def verify_token(self, token: str) -> VerifiedIdentity:
        if token != "valid-supabase-token":
            raise IdentityVerificationError("invalid test token")

        return VerifiedIdentity(
            issuer="https://identity-provider.test/auth/v1",
            subject="supabase-user-123",
            email="user@example.com",
        )


def test_exchange_creates_account_and_first_party_session(
    client: TestClient,
    test_app: FastAPI,
    db_session: Session,
) -> None:
    test_app.dependency_overrides[get_identity_provider] = lambda: cast(
        IdentityProvider,
        FakeIdentityProvider(),
    )

    response = client.post(
        "/api/v1/sessions/exchange",
        headers={"Authorization": "Bearer valid-supabase-token"},
        json={"device_name": "Test iPhone"},
    )

    assert response.status_code == 201

    body = response.json()
    assert body["token_type"] == "bearer"

    account = db_session.scalar(
        select(Account).where(
            Account.auth_subject == "supabase-user-123"
        )
    )
    assert account is not None

    account_session = db_session.scalar(
        select(AccountSession).where(
            AccountSession.account_id == account.id
        )
    )
    assert account_session is not None
    assert account_session.device_name == "Test iPhone"
    assert account_session.token_hash == hash_session_token(
        body["access_token"]
    )
    assert account_session.token_hash != body["access_token"]


def test_exchange_rejects_invalid_identity_token(
    client: TestClient,
    test_app: FastAPI,
) -> None:
    test_app.dependency_overrides[get_identity_provider] = lambda: cast(
        IdentityProvider,
        FakeIdentityProvider(),
    )

    response = client.post(
        "/api/v1/sessions/exchange",
        headers={"Authorization": "Bearer invalid-token"},
        json={},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Identity token is invalid"}
