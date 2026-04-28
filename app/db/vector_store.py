"""Thin pgvector wrapper.

For brevity this is an in-memory fallback. Wire the real Postgres
client in by reading DATABASE_URL from settings and using `psycopg`
with the `pgvector` extension enabled.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _StoredDoc:
    id: str
    title: str
    text: str


_SEED: list[_StoredDoc] = [
    _StoredDoc(
        id="msft-10k-2024-p47",
        title="Microsoft 10-K FY2024, p.47",
        text=(
            "Intelligent Cloud revenue increased 20% in FY24, driven by Azure and "
            "other cloud services growth of 30% in Q4. Server products and cloud "
            "services revenue increased 22%."
        ),
    ),
    _StoredDoc(
        id="msft-10q-q3-2024",
        title="Microsoft 10-Q Q3 FY2024",
        text=(
            "Operating income grew 23% YoY. Capital expenditures, including "
            "finance leases, increased to support cloud and AI offerings."
        ),
    ),
]


class VectorStore:
    """In-memory store; replace with pgvector queries in production."""

    def __init__(self) -> None:
        self._docs = list(_SEED)

    async def search(self, query: str, k: int = 8) -> list[dict]:
        # Naive keyword overlap — good enough as a placeholder. Real impl
        # should embed the query and run cosine search in Postgres.
        q = query.lower()
        scored = []
        for d in self._docs:
            score = sum(tok in d.text.lower() for tok in q.split()) / max(len(q.split()), 1)
            if score > 0:
                scored.append({"id": d.id, "title": d.title, "text": d.text, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]
