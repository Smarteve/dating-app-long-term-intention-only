from typing import Literal
from pydantic import BaseModel
from fastapi import APIRouter

class HealthResponse(BaseModel):
    status: Literal["ok"]



router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok")