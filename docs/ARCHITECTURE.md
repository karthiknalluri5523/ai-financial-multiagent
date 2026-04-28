# Architecture

## Why a graph instead of a chain?

A linear chain (`retrieve -> analyze -> respond`) cannot self-correct. Adding a critic that can loop back to the analyst (bounded) gives us measurable hallucination drops without manual review.

## Graph

- **retriever**: pgvector + lightweight keyword overlap. Returns up to 8 docs.
- **analyst** (GPT-4o, t=0.1): structured-JSON output of `{answer, findings[]}`. Each finding includes a `source_id` that must exist in the retrieved docs.
- **critic** (Claude 3.5 Sonnet, t=0.0): independent fact-checker. Different model family from analyst to reduce shared-mode failures.
- **reporter**: pure-Python formatter — no LLM call.

Loop bound: at most `APP_MAX_CRITIC_LOOPS` (default 2) re-runs of the analyst.

## Observability

- LangChain callbacks routed to **Langfuse** for trace-level inspection.
- FastAPI middleware emits Prometheus metrics: `requests_total`, `latency_seconds`, `model_calls_total`.

## Eval

A 50-question benchmark lives in `tests/eval/` (not committed in this skeleton). Each run records:

- citation coverage (fraction of claims with a valid `source_id`)
- hallucination rate (manual judge, from a held-out set)
- token usage and latency

## Production hardening checklist

- [ ] Wire real Postgres + pgvector (replace `VectorStore` in-memory fallback)
- [ ] Add request-level rate limiting + auth
- [ ] Cache analyst outputs by `(question, doc_ids)` hash
- [ ] Migrate JSON parsing to `langchain-core.output_parsers.PydanticOutputParser`
- [ ] Add streaming `text/event-stream` endpoint for UI
