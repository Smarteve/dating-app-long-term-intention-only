from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.accounts.session_service import create_session
from app.profiles.models import Profile, ProfilePromptAnswer, Prompt


def create_account(db_session: Session, subject: str) -> Account:
    account = Account(
        auth_issuer="https://identity-provider.test/auth/v1",
        auth_subject=subject,
    )
    db_session.add(account)
    db_session.flush()
    return account


def test_get_prompts_returns_active_prompts_sorted_by_slug(
    client: TestClient,
    db_session: Session,
) -> None:
    active_later = Prompt(
        id=uuid4(),
        slug="z-activity",
        text="What activity do you enjoy?",
        is_active=True,
    )
    active_first = Prompt(
        id=uuid4(),
        slug="a-value",
        text="What value matters most to you?",
        is_active=True,
    )
    inactive = Prompt(
        id=uuid4(),
        slug="hidden-prompt",
        text="This prompt should not be returned.",
        is_active=False,
    )
    db_session.add_all([active_later, inactive, active_first])
    db_session.flush()

    response = client.get("/api/v1/prompts")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(active_first.id),
            "slug": "a-value",
            "text": "What value matters most to you?",
        },
        {
            "id": str(active_later.id),
            "slug": "z-activity",
            "text": "What activity do you enjoy?",
        },
    ]


def test_get_my_profile_returns_profile_and_prompt_answers(
    client: TestClient,
    db_session: Session,
) -> None:
    account = create_account(db_session, "profile-owner")
    session = create_session(db_session, account)
    prompt = Prompt(
        id=uuid4(),
        slug="ideal-sunday",
        text="What does your ideal Sunday look like?",
        is_active=True,
    )
    profile = Profile(
        id=uuid4(),
        account_id=account.id,
        display_name="Alex",
        date_of_birth=date(1995, 4, 12),
        bio="Enjoys hiking and cooking.",
        city="London",
        height_cm=180,
    )
    answer = ProfilePromptAnswer(
        id=uuid4(),
        profile_id=profile.id,
        prompt_id=prompt.id,
        answer="A slow morning and dinner with friends.",
    )
    db_session.add_all([prompt, profile, answer])
    db_session.flush()

    response = client.get(
        "/api/v1/me/profile",
        headers={"Authorization": f"Bearer {session.token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(profile.id),
        "account_id": str(account.id),
        "display_name": "Alex",
        "date_of_birth": "1995-04-12",
        "bio": "Enjoys hiking and cooking.",
        "city": "London",
        "height_cm": 180,
        "is_discoverable": False,
        "published_at": None,
        "prompt_answers": [
            {
                "prompt_id": str(prompt.id),
                "answer": "A slow morning and dinner with friends.",
            }
        ],
    }


def test_get_my_profile_returns_not_found_when_profile_is_missing(
    client: TestClient,
    db_session: Session,
) -> None:
    account = create_account(db_session, "profile-missing")
    session = create_session(db_session, account)

    response = client.get(
        "/api/v1/me/profile",
        headers={"Authorization": f"Bearer {session.token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Profile not found"}


def test_get_my_profile_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/me/profile")

    assert response.status_code == 401
