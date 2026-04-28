"""Reporter agent — formats final user-facing answer with inline citations."""
from __future__ import annotations

from app.core.models import GraphState


async def reporter_node(state: GraphState) -> dict:
    """Lightweight formatter — no LLM call needed; deterministic templating."""
    bullets = "\n".join(f"- {f.claim}  [{f.source_id}]" for f in state.findings)
    final = (
        f"{state.draft_answer.strip()}\n\n"
        f"Key findings:\n{bullets if bullets else '- (no supported findings)'}"
    )
    return {"final_answer": final}
