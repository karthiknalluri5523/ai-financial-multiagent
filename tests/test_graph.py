"""Smoke test for the LangGraph wiring.

Mocks the four agent nodes so the test runs without API keys.
"""
from __future__ import annotations

import pytest

from app.core.graph import build_graph
from app.core.models import CriticReview, Document, Finding, GraphState


@pytest.fixture
def patched_graph(monkeypatch):
    async def fake_retriever(state: GraphState):
        return {"docs": [Document(id="src1", title="t", text="Azure grew 30%.")]}

    async def fake_analyst(state: GraphState):
        return {
            "draft_answer": "Azure cloud grew strongly.",
            "findings": [Finding(claim="Azure grew 30%.", source_id="src1", confidence=0.9)],
            "model_calls": state.model_calls + 1,
        }

    async def fake_critic(state: GraphState):
        return {
            "critic_review": CriticReview(issues_found=0, notes=[], passes=True),
            "model_calls": state.model_calls + 1,
        }

    async def fake_reporter(state: GraphState):
        return {"final_answer": state.draft_answer + "\n[ok]"}

    # Patch at the IMPORT SITE (app.core.graph), not the source modules.
    # graph.py used `from app.agents.X import Y_node`, which copied those names
    # into its own namespace — so patching the sources has no effect on the
    # references graph.py holds. Patch where the names are actually looked up.
    monkeypatch.setattr("app.core.graph.retriever_node", fake_retriever)
    monkeypatch.setattr("app.core.graph.analyst_node", fake_analyst)
    monkeypatch.setattr("app.core.graph.critic_node", fake_critic)
    monkeypatch.setattr("app.core.graph.reporter_node", fake_reporter)
    return build_graph()


@pytest.mark.asyncio
async def test_graph_runs_end_to_end(patched_graph):
    result = await patched_graph.ainvoke(GraphState(question="How is Azure doing?"))
    assert "[ok]" in result["final_answer"]
    assert result["critic_review"].passes
    assert result["model_calls"] >= 2
