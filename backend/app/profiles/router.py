from sqlalchemy import select
from fastapi import APIRouter

from app.db.session import DatabaseSession
from app.profiles.models import Prompt
from app.profiles.schemas import PromptResponse

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])

@router.get("", response_model=list[PromptResponse])
def get_prompts(db: DatabaseSession) -> list[PromptResponse]:
    statement = (
        select(Prompt)
        .where(Prompt.is_active.is_(True))
        .order_by(Prompt.slug)
    )

    prompts = db.scalars(statement).all()
    return [PromptResponse.model_validate(prompt) for prompt in prompts]
