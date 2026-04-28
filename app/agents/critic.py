"""Critic agent — fact-checks the analyst's findings against the source docs.

Uses Anthropic Claude as a different family of model from the analyst (GPT-4o)
to reduce shared-mode failures. Verifies each finding's source_id exists and
that the claim is plausibly supported by the source text.
"""
from __future__ import annotations

import json

from langchain_anthropic import ChatAnthropic

from app.core.config import settings
from app.core.models import CriticReview, GraphState

CRITIC_PROMPT = """You are a meticulous fact-checker reviewing a financial analyst's draft.
For each finding, verify:
  1. source_id exists in the provided documents
  2. the claim is plausibly supported by that source's text
  3. there is no overreach (e.g., predicting future performance from historical-only data)

Return strict JSON:
{{
  "issues_found": <int>,
  "notes": ["<one short note per issue>"],
  "passes": <true if 0 issues else false>
}}

Documents:
{sources}

Findings:
{findings}
"""


def _llm() -> ChatAnthropic:
    return ChatAnthropic(
        model="claude-3-5-sonnet-latest",
        temperature=0.0,
        api_key=settings.anthropic_api_key,
        timeout=60,
    )


async def critic_node(state: GraphState) -> dict:
    sources = "\n\n".join(f"[{d.id}] {d.title}\n{d.text[:800]}" for d in state.docs)
    findings = "\n".join(
        f"- ({f.source_id}) {f.claim}  conf={f.confidence}" for f in state.findings
    )
    prompt = CRITIC_PROMPT.format(sources=sources, findings=findings)
    response = await _llm().ainvoke(prompt)
    payload = json.loads(response.content)
    review = CriticReview(**payload)
    return {
        "critic_review": review,
        "model_calls": state.model_calls + 1,
    }
