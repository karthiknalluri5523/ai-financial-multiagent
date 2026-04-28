"""FastAPI entry point."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="AI-Powered Multi-Agent Financial Analysis & Reporting System",
    version="0.1.0",
    description="LangGraph multi-agent backend for citation-backed financial analysis.",
)

app.include_router(router, prefix="/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
