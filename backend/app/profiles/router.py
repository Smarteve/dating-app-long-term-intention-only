from fastapi import APIRouter

from app.db.session import DatabaseSession
from app.profiles.schemas import PromptResponse
from app.profiles.service import list_active_prompts

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


@router.get("", response_model=list[PromptResponse])
def get_prompts(db: DatabaseSession) -> list[PromptResponse]:
    prompts = list_active_prompts(db)
    return [PromptResponse.model_validate(prompt) for prompt in prompts]
