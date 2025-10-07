# backend/app/models/schemas.py

from typing import Any

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    resume_text: str = Field(..., min_length=1, description="Plain text resume")
    jd_text: str = Field(..., min_length=1, description="Plain text job description")
    params: dict[str, Any] | None = None


class RunResponse(BaseModel):
    run_id: str
    status: str


class ArtifactMeta(BaseModel):
    name: str
    kind: str
    mime: str


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    error: str | None = None
    artifacts: list[ArtifactMeta] = []
