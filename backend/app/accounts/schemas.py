from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SessionExchangeRequest(BaseModel):
    device_name: str | None = Field(
        default=None,
        max_length=120,
    )


class SessionResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    session_id: UUID


class ActiveSessionResponse(BaseModel):
    id: UUID
    device_name: str | None
    created_at: datetime
    last_seen_at: datetime | None
    expires_at: datetime
    is_current: bool


class ActiveSessionListResponse(BaseModel):
    sessions: list[ActiveSessionResponse]
