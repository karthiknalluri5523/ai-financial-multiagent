"""LangGraph wiring: retriever -> analyst -> critic -> reporter, with critic loop-back."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.analyst import analyst_node
from app.agents.critic import critic_node
from app.agents.reporter import reporter_node
from app.agents.retriever import retriever_node
from app.core.config import settings
from app.core.models import GraphState


def _route_after_critic(state: GraphState) -> str:
    """If critic flags issues and we have loops left, send back to analyst."""
    if state.critic_review.passes:
        return "reporter"
    if state.critic_loops >= settings.app_max_critic_loops:
        return "reporter"
    return "analyst"


def build_graph():
    g = StateGraph(GraphState)
    g.add_node("retriever", retriever_node)
    g.add_node("analyst", analyst_node)
    g.add_node("critic", critic_node)
    g.add_node("reporter", reporter_node)

    g.set_entry_point("retriever")
    g.add_edge("retriever", "analyst")
    g.add_edge("analyst", "critic")
    g.add_conditional_edges(
        "critic",
        _route_after_critic,
        {"analyst": "analyst", "reporter": "reporter"},
    )
    g.add_edge("reporter", END)
    return g.compile()


GRAPH = build_graph()
