from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PromptResponse(BaseModel):
    id: UUID
    slug: str
    text: str

    model_config = ConfigDict(from_attributes=True)


class PromptAnswerResponse(BaseModel):
    prompt_id: UUID
    answer: str


    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    id: UUID
    account_id: UUID
    display_name: str | None
    date_of_birth: date | None
    bio: str | None
    city: str | None
    height_cm: int | None
    is_discoverable: bool
    published_at: datetime | None
    prompt_answers: list[PromptAnswerResponse]

    model_config = ConfigDict(from_attributes=True)
