"""Analyst agent — drafts findings and citations using GPT-4o.

Findings are returned as structured JSON (validated by Pydantic) so the
critic can fact-check claim-by-claim against the retrieved docs.
"""
from __future__ import annotations

import json

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.models import Finding, GraphState

ANALYST_PROMPT = """You are a senior financial analyst. Using ONLY the provided sources,
draft an analysis for the user's question. Every claim MUST cite a source_id from the
provided documents. If a claim cannot be supported, omit it.

Return strict JSON:
{{
  "answer": "<concise prose, 3-6 sentences>",
  "findings": [
    {{"claim": "...", "source_id": "...", "confidence": 0.0-1.0}}
  ]
}}

Question: {question}
Tickers: {tickers}
Sources:
{sources}

If the critic gave feedback, address it: {critic_notes}
"""


def _llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        api_key=settings.openai_api_key,
        timeout=60,
    )


def _format_sources(state: GraphState) -> str:
    return "\n\n".join(f"[{d.id}] {d.title}\n{d.text[:1200]}" for d in state.docs)


async def analyst_node(state: GraphState) -> dict:
    prompt = ANALYST_PROMPT.format(
        question=state.question,
        tickers=", ".join(state.tickers) or "none",
        sources=_format_sources(state),
        critic_notes="; ".join(state.critic_review.notes) or "none",
    )
    response = await _llm().ainvoke(prompt)
    payload = json.loads(response.content)
    return {
        "draft_answer": payload["answer"],
        "findings": [Finding(**f) for f in payload["findings"]],
        "model_calls": state.model_calls + 1,
        "critic_loops": state.critic_loops + (1 if state.critic_review.notes else 0),
    }
