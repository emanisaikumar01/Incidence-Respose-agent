from typing import Any

from pydantic import BaseModel, Field


class RecalledCase(BaseModel):
    memory_id: str
    text: str


class RecommendationRequest(BaseModel):
    incident: dict[str, Any]
    recalled_cases: list[RecalledCase] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    status: str
    summary: str | None = None
    root_cause: str | None = None
    recommendation: str | None = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float | None = None