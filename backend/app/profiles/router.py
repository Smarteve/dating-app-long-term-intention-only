from fastapi import APIRouter, HTTPException

from app.accounts.dependencies import CurrentAccount
from app.db.session import DatabaseSession
from app.profiles.schemas import (
    ProfileResponse,
    PromptAnswerResponse,
    PromptResponse,
)
from app.profiles.service import get_profile_data, list_active_prompts

router = APIRouter(prefix="/api/v1")


@router.get("/prompts", response_model=list[PromptResponse], tags=["prompts"])
def get_prompts(db: DatabaseSession) -> list[PromptResponse]:
    prompts = list_active_prompts(db)
    return [PromptResponse.model_validate(prompt) for prompt in prompts]


@router.get("/me/profile", response_model=ProfileResponse, tags=["profiles"])
def get_profile(
    account: CurrentAccount,
    db: DatabaseSession,
) -> ProfileResponse:
    result = get_profile_data(account, db)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )
    profile, prompt_answers = result

    return ProfileResponse(
        id=profile.id,
        account_id=profile.account_id,
        display_name=profile.display_name,
        date_of_birth=profile.date_of_birth,
        bio=profile.bio,
        city=profile.city,
        height_cm=profile.height_cm,
        is_discoverable=profile.is_discoverable,
        published_at=profile.published_at,
        prompt_answers=[
            PromptAnswerResponse.model_validate(answer)
            for answer in prompt_answers
        ],
    )
