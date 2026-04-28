"""HTTP routes."""
from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from app.core.graph import GRAPH
from app.core.models import AnalyzeRequest, AnalyzeResponse, GraphState

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    start = time.perf_counter()
    try:
        state = GraphState(question=req.question, tickers=req.tickers)
        result = await GRAPH.ainvoke(state)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AnalyzeResponse(
        answer=result["final_answer"],
        findings=result["findings"],
        critic_review=result["critic_review"],
        model_calls=result["model_calls"],
        latency_ms=int((time.perf_counter() - start) * 1000),
    )
