"""Pydantic schemas — request/response and shared graph state."""
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

# ---------- API I/O ----------

class AnalyzeRequest(BaseModel):
    question: str = Field(..., min_length=4, max_length=2000)
    tickers: list[str] = Field(default_factory=list, max_length=10)


class Finding(BaseModel):
    claim: str
    source_id: str
    confidence: float = Field(ge=0, le=1, default=0.8)


class CriticReview(BaseModel):
    issues_found: int = 0
    notes: list[str] = Field(default_factory=list)
    passes: bool = True


class AnalyzeResponse(BaseModel):
    answer: str
    findings: list[Finding]
    critic_review: CriticReview
    model_calls: int = 0
    latency_ms: int = 0


# ---------- Graph state ----------

class Document(BaseModel):
    id: str
    title: str
    text: str
    score: float = 0.0


class GraphState(BaseModel):
    """Shared state passed between agents."""
    question: str
    tickers: list[str] = Field(default_factory=list)
    docs: list[Document] = Field(default_factory=list)
    draft_answer: str = ""
    findings: list[Finding] = Field(default_factory=list)
    critic_review: CriticReview = Field(default_factory=CriticReview)
    final_answer: str = ""
    model_calls: int = 0
    critic_loops: Annotated[int, "incremented each time critic re-runs analyst"] = 0
