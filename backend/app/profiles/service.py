from sqlalchemy import select
from sqlalchemy.orm import Session

from app.profiles.models import Prompt


def list_active_prompts(db: Session) -> list[Prompt]:
    statement = (
        select(Prompt)
        .where(Prompt.is_active.is_(True))
        .order_by(Prompt.slug)
    )

    return list(db.scalars(statement).all())
