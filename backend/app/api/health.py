from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db.engine import database_is_ready


class HealthResponse(BaseModel):
    status: Literal["ok"]


DatabaseReady = Annotated[bool, Depends(database_is_ready)]

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
def readiness(is_database_ready: DatabaseReady) -> HealthResponse:
    if not is_database_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        )

    return HealthResponse(status="ok")
