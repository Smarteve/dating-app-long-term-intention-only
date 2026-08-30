from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.profiles.models import Prompt


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
