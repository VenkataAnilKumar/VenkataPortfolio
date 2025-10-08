# MVP Scope: Multi-Agent Dispute Resolution System

This document defines a lean, demonstrable Minimum Viable Product (MVP) that can be built quickly with constrained resources while still credibly showcasing architecture, multi-agent orchestration concepts, and measurable value.

---
## 1. MVP Objectives
| Objective | Rationale | Evidence of Success |
|-----------|-----------|---------------------|
| Automate initial dispute classification | Reduces analyst triage load | >= 85% precision on labeled sample |
| Provide basic enrichment (transaction + prior dispute fetch) | Shows contextual reasoning | Enrichment latency < 5s p95 |
| Generate recommendation (accept / escalate / request info) with rationale | Demonstrates LLM structured reasoning | Analyst override rate < 30% on test set |
| Persist full audit trail of steps | Compliance & explainability story | 100% steps logged per case |
| Expose 3 core APIs | Usability + integration signal | Working Postman collection / OpenAPI |
| Basic metrics (classification count, latency) | Observability baseline | Dashboard / simple JSON metrics endpoint |

---
## 2. Cut Lines (Must / Should / Could / Won't – MVP)
| Priority | Item | Decision |
|----------|------|----------|
| MUST | Dispute ingestion (POST /v1/disputes) | In scope |
| MUST | Basic classification (fraud vs. non-fraud / other) | In scope |
| MUST | Enrichment: last N transactions + count of prior disputes | In scope |
| MUST | Recommendation (3-way outcome + confidence) | In scope |
| MUST | Simple orchestrator (sequential + small parallel segment) | In scope |
| MUST | JSON audit log per step | In scope |
| MUST | SQLite/PostgreSQL minimal schema | In scope |
| SHOULD | Retry wrapper for LLM calls | Simple single retry |
| SHOULD | Embedding-based similarity (optional pgvector / FAISS) | Stretch |
| SHOULD | Basic auth (API key header) | Simple decorator |
| COULD | Pattern clustering | Deferred |
| COULD | Multi-agent parallel evidence fan-out | Use sequential stub |
| COULD | Policy citation mapping | Replace with hard-coded placeholder |
| WON'T (MVP) | Full pattern anomaly subsystem | Future phase |
| WON'T (MVP) | Dashboard UI | Out of scope |
| WON'T (MVP) | Representment package generation | Future phase |
| WON'T (MVP) | Multi-language narratives | Future phase |

---
## 3. Simplified Architecture (MVP)
```
FastAPI (API Layer)
  -> Orchestrator (Python service module)
       1. Classification Step (LLM or rules fallback)
       2. Enrichment Step (DB queries)
       3. Recommendation Step (LLM JSON schema)
  -> Persistence (SQLite or Postgres)
  -> Audit Logger (table + appended JSON events)
  -> Metrics (in-memory counters + /metrics JSON endpoint)
```

### Why This Slice Works
- Vertical slice: ingest -> classify -> enrich -> recommend -> retrieve
- Replaceable components (classification agent can later swap to dedicated microservice)
- Minimal complexity (no queue; synchronous request/response + background thread if needed)

---
## 4. Data Model (Trimmed)
Tables:
- dispute_case(id, external_ref, customer_id, merchant_id, amount_cents, currency, narrative, status, classification, classification_confidence, recommendation_action, recommendation_confidence, created_at)
- audit_event(id, dispute_case_id, step, payload_json, created_at)
- transaction_ledger(id, customer_id, merchant_id, amount_cents, currency, occurred_at)

No pattern_cluster or evidence_item table in MVP (enrichment fields stored inline in audit or aggregated response).

---
## 5. Agent Simplification
| Agent (Full Design) | MVP Realization |
|---------------------|-----------------|
| Classifier Agent | Single function: call GPT-4 (or gpt-3.5) with few-shot; fallback regex/rule |
| Evidence Agents (multiple) | One enrichment function: fetch last 5 transactions + prior dispute count |
| Recommendation Agent | Single prompt producing JSON {action, confidence, rationale} |
| Pattern Agent | Omitted |
| Controller / Orchestrator | Python module executing steps in order with timing + logging |

---
## 6. LLM Cost Control (MVP)
| Use Case | Model | Frequency | Notes |
|----------|-------|-----------|-------|
| Classification | gpt-3.5-turbo (or cheaper) | 1 per case | Temperature low (0.1) |
| Recommendation | gpt-4-mini / gpt-4o | 1 per case | Higher reasoning; keep concise |
| Future Caching | Narrative embeddings | Later | Not required now |

Token budget: enforce max narrative length (truncate with notice). Provide developer flag to switch to mock mode.

---
## 7. API Surface (MVP)
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/disputes | Create & process a new dispute synchronously (returns classification + recommendation) |
| GET | /v1/disputes/{id} | Retrieve stored case & recommendation |
| GET | /v1/metrics | Basic counters (total_cases, avg_latency_ms) |

Status progression simplified: RECEIVED -> PROCESSING -> COMPLETED

### Sample Response (POST /v1/disputes)
```json
{
  "id": "dsp_123",
  "classification": {"label": "FRAUD_UNAUTHORIZED", "confidence": 0.88},
  "recommendation": {"action": "REFUND", "confidence": 0.81, "rationale": "Transaction pattern inconsistent with customer history."},
  "latency_ms": 1270
}
```

---
## 8. Metrics (Minimal First)
- total_cases
- classification_latency_ms (rolling avg)
- recommendation_latency_ms
- cases_by_label{label}
- overrides (future when analyst review added)

Expose as JSON now; Prometheus exporter later.

---
## 9. Testing Strategy (MVP)
| Layer | Focus |
|-------|-------|
| Unit | Classification function (mock LLM), recommendation parser |
| Integration | POST /v1/disputes full flow with in-memory DB |
| Prompt Eval | 20 labeled synthetic narratives to track precision |
| Load | 100 concurrent dispute POSTs (measure p95 latency) |

---
## 10. Implementation Order (Suggested Sprints)
**Sprint 0 (Setup)**: Repo layout, FastAPI skeleton, schema migration script, health endpoint.  
**Sprint 1**: Dispute ingestion + DB persistence + simple classification (rule-based placeholder).  
**Sprint 2**: LLM classification + enrichment + recommendation prompt + audit events.  
**Sprint 3**: Metrics endpoint + basic tests + prompt refinement set.  
**Sprint 4**: Hardening (timeouts, retries), cost logging, minimal docs & demo script.  

---
## 11. Demo Storyboard
1. Submit 3 synthetic disputes (fraud, merchant error, ambiguous).  
2. Show API JSON responses.  
3. Query metrics endpoint.  
4. Display audit log rows for one case (classification + enrichment + recommendation).  
5. (Optional) Switch model=mock and replay for fast CI run.  

---
## 12. How to Present in Portfolio
- Include this `mvp.md` + trimmed architecture diagram (docs/architecture.md).  
- Add example prompt + response (redacted) in README.  
- Provide metrics screenshot (simulated) in docs/.  
- Focus narrative: "Reduced manual triage by X% with explainable automated classification + recommendation pipeline."  

---
## 13. Post-MVP Growth Path
1. Introduce evidence_item table + multi-source fan-out.  
2. Add pattern clustering job + vector store.  
3. Implement decision override endpoint + analyst feedback loop.  
4. Optimize cost with model tier routing + summarization pre-steps.  
5. Introduce streaming ingestion & asynchronous processing.  

---
**MVP defined.** Keep scope disciplined—optimize for demonstrable value + architectural credibility, not feature breadth.
