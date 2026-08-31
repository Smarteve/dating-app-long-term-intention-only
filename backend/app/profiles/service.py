from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.profiles.models import Profile, ProfilePromptAnswer, Prompt


def list_active_prompts(db: Session) -> list[Prompt]:
    statement = (
        select(Prompt)
        .where(Prompt.is_active.is_(True))
        .order_by(Prompt.slug)
    )

    return list(db.scalars(statement).all())


def get_profile_data(
    account: Account,
    db: Session,
) -> tuple[Profile, list[ProfilePromptAnswer]] | None:
    statement = select(Profile).where(Profile.account_id == account.id)
    profile = db.scalar(statement)
    if profile is None:
        return None

    prompt_answers = get_prompt_answers(profile, db)
    return profile, prompt_answers


def get_prompt_answers(
    profile: Profile,
    db: Session,
) -> list[ProfilePromptAnswer]:
    statement = select(ProfilePromptAnswer).where(
        ProfilePromptAnswer.profile_id == profile.id
    )
    prompt_answers = db.scalars(statement).all()
    return list(prompt_answers)
