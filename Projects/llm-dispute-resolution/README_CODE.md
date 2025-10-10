# Code Implementation Overview

This folder contains the runnable MVP skeleton for the Multi-Agent Dispute Resolution System described in the design documents.

## Features Implemented
- POST /v1/disputes endpoint executing a synchronous pipeline: classify → enrich (mock) → recommend.
- Mock LLM adapter (deterministic logic) with narrative keyword heuristic.
- Metrics endpoint /v1/metrics (p95 latencies, case counts by label).
- In-memory audit buffer (collected but not yet exposed via API).
- JSON Schemas for classification & recommendation outputs.
- Basic test exercising end-to-end happy path.

## Not Yet Implemented (Design-Ready Seams)
- Persistent storage of disputes & audit events (DB models exist; persistence intentionally deferred to keep skeleton lean).
- Real LLM API calls (would be added inside `LLMAdapter`).
- Pattern clustering / embeddings.
- Cost accounting metrics.
- Audit retrieval endpoint.

## Running Locally
Create virtual environment & install dependencies:
```bash
python -m venv .venv
./.venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000/docs for interactive API.

## Tests
```bash
pytest -q
```

## Next Steps
1. Add DB persistence for dispute + audit events.
2. Implement real LLM call with JSON schema validation & retry.
3. Expose audit retrieval endpoint.
4. Introduce cost tracking & token budgeting.
5. Add clustering (Phase 2) with embedding index.

---
This code is intentionally minimal to emphasize architecture clarity and extensibility.
