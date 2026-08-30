from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PromptResponse(BaseModel):
    id: UUID
    slug: str
    text: str

    model_config = ConfigDict(from_attributes=True)
