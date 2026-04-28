"""Retriever agent — pulls relevant docs from pgvector + simple keyword overlap."""
from __future__ import annotations

from app.core.models import Document, GraphState
from app.db.vector_store import VectorStore

# Module-level store; in tests this is monkey-patched.
_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store


async def retriever_node(state: GraphState) -> dict:
    query = state.question
    if state.tickers:
        query = f"{query} ({', '.join(state.tickers)})"
    hits = await get_store().search(query, k=8)
    docs = [Document(id=h["id"], title=h["title"], text=h["text"], score=h["score"]) for h in hits]
    return {"docs": docs}
