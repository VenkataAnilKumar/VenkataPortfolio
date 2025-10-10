# Multi-Agent Dispute Resolution System – Unified Engineering Blueprint

Version: 1.0.0  | Owner: Engineering  | Status: Authoritative Source-of-Truth (supersedes overlapping prior docs)  
Consumption Guide: This single blueprint consolidates problem framing, scope, architecture, requirements, agents, APIs, roadmap, and evaluation. Other docs (overview, requirements, architecture, agents, api, mvp, principal-architecture-spec) now act as focused extracts—this file governs when discrepancies occur.

---
## 1. Executive Summary
An LLM‑orchestrated, audit-first service that ingests financial disputes, classifies them, enriches with contextual data, and produces explainable, cost‑controlled recommendations—reducing manual triage time and improving consistency while laying an extensible foundation for fraud pattern detection.

## 2. Problem Definition
| Pain | Impact | Root Driver | Actionable Opportunity |
|------|--------|------------|-----------------------|
High manual triage effort | SLA risk, cost | Fragmented context & unstructured narrative | Automate classification + enrichment (MVP) |
Inconsistent classification | Lost recovery, rework | Human variance, stale rules | Schema‑bounded LLM + fallback rules (MVP) |
Weak explainability | Compliance exposure | Unstructured analyst notes | Structured rationale + audit ledger (MVP) |
Unpredictable unit cost | Budget friction | Unbounded token usage | Tiered model strategy + cap (MVP) |

Note: Fraud pattern recognition and clustering are deferred to future phases, not in MVP scope due to resource limits.

Success for MVP: Demonstrate automated, explainable, cost-controlled classification and recommendation for disputes, with audit traceability, using only core modules/services.

## 3. Value Proposition & Differentiators
| Differentiator | Why It Matters | Implementation Mechanism |
|----------------|----------------|--------------------------|
Contract‑bounded agent IO | Reliability & parsing safety | JSONSchema + Pydantic validators (core) |
Cost guardrails native | Predictable per-case economics | Token budget + model tier routing (core) |
Audit-first design | Compliance & replay | Append-only structured events (core) |
Mock deterministic mode | Low friction dev/demo | LLM adapter strategy pattern (core) |

Note: Extensible vector seam and clustering are not MVP; focus is on core, resource-feasible differentiators.

## 4. Personas & Objectives
| Persona | Core Objective | Metric |
|---------|----------------|--------|
Analyst | Faster high-confidence recommendation | Handling time ↓ |
Compliance | Traceable decision lineage | 100% audit completeness |
Fraud Investigator | Earlier anomaly awareness | Lead time improvement |
Product/Finance | Cost efficiency | Cost/case within target |

## 5. Scope & Phasing
| Phase | Scope | Excluded (Deliberate) | Exit Criteria |
|-------|-------|----------------------|---------------|
MVP (P1) | Ingestion, classification, enrichment (basic), recommendation, audit, metrics (JSON) | UI portal, clustering, async queue, pattern detection | FR-01..11 pass; p95 classify <8s; ≥85% precision |
Enhanced (P2+) | Decision override, audit retrieval, embeddings + similarity, cost metrics, clustering batch | Streaming ingestion, advanced RBAC | ≥90% precision; pattern endpoint returns clusters |

Explicit Out-of-Scope (MVP): Pattern clustering, representment docs, multilingual narratives, enterprise IAM, real-time streaming, UI dashboard, advanced analytics.

## 6. High-Level Architecture (Conceptual)
Client → FastAPI (API) → Orchestrator → Agents (Classifier, Enrichment, Recommendation, Guardrail, Audit Wrapper) → Persistence (DB + Audit) → Metrics.

Note: Only core modules/services are implemented for MVP. Optional extensions (Embedding Index, Pattern Job) are deferred.

## 7. Component Responsibility Matrix
| Component | Responsibilities | Key Interfaces | Failure Modes |
|-----------|-----------------|----------------|---------------|
API Layer | Validation, auth, request id, OpenAPI | Routers, Schemas | 400 validation errors |
Orchestrator | Step sequencing, timing, error path, cost guard | Agent contracts, Audit, Metrics | Timeout, budget breach |
Classifier Agent | Map narrative → label + confidence | LLM Adapter, Rules Fallback | LLM error / low confidence |
Enrichment Service | Retrieve transactions & prior dispute count | DB Repository | DB timeout |
Recommendation Agent | Synthesize action + rationale | LLM Adapter | Hallucination / invalid schema |
Audit Logger | Persist envelope of each step | DB Audit Table | Write failure |
Metrics Collector | Counters & latency histograms | In-memory store | None (reset risk) |
LLM Adapter | Unify real vs mock vs multi-tier | OpenAI SDK (optional) | Rate limit / network |

Note: Embedding/Pattern components are not part of MVP; only core modules/services are implemented.

## 8. Data Model (MVP Logical)
Tables: dispute_case, audit_event, transaction_ledger, (recommendation fields inline vs separate table optional). Phase 2 adds: embedding_cache, pattern_cluster.

Field Principles: Minimal PII, add classification_confidence & action_confidence for analytics, store prompt & prompt_version hashed reference (not full raw content) for reproducibility.

## 9. Agent Contracts (Abbreviated)
| Agent | Input Core | Output Core | SLO p95 | Fallback |
|-------|-----------|-------------|---------|----------|
Classifier | narrative, amount, prior_disputes | label, confidence, rationale | 2500ms | Rules heuristic |
Enrichment | case_id | txns[], prior_dispute_count | 400ms | Empty partial flag |
Recommendation | classification + enrichment summary | action, confidence, rationale | 2500ms | ESCALATE_REVIEW |
Guardrail | raw narrative | sanitized narrative | 50ms | Reject if high risk |

All outputs validated against JSONSchema; violation → fallback or escalation.

## 10. API Surface (Authoritative Summary)
| Method | Path | Purpose | Phase |
|--------|------|---------|-------|
POST | /v1/disputes | Submit + process synchronously | MVP |
GET | /v1/disputes/{id} | Retrieve case snapshot | MVP |
GET | /v1/metrics | Metrics JSON | MVP |
GET | /v1/disputes/{id}/audit | Step events | P2 |
POST | /v1/disputes/{id}/decision | Analyst override / finalization | P2 |
GET | /v1/patterns | Clusters / anomalies | P2 |

Error Model: { error: { code, message, request_id, details } }.

## 11. Non-Functional Targets
| Category | Metric | MVP | P2 | P3 |
|----------|--------|-----|----|----|
Latency | POST classify p95 | <8s E2E | <6s | <4s |
Precision | Classification | ≥85% | ≥90% | ≥90% |
Audit | Completeness | 100% | 100% | 100% |
Cost | $/case | ≤0.55 | ≤0.45 | ≤0.40 |
Throughput | Concurrent cases sustained | 30 | 60 | 100 |
Availability* | Core endpoints | Dev best-effort | 99.5% (illustrative) | 99.5% |
(*Portfolio simulation, not SLA contract.)

## 12. Security & Privacy
Controls: Input sanitization (regex/email/card), minimal PII fields, API key header (optional), hashed IDs optional, no raw secrets in code, prompt redaction. Threat surfaces prioritized: prompt injection, model leakage, malformed JSON attacks.

## 13. Observability & Cost Management
Metrics: total_cases, classification_latency_ms_hist, recommendation_latency_ms_hist, cases_by_label, error_counts{type}, token_usage_total, cost_per_case_usd.  
Logging: Structured JSON (ts, level, request_id, case_id, step, latency_ms, success, error_type).  
Cost: Token accounting (prompt + completion) * per-model pricing table persisted in memory; outlier detection if cost/case > threshold → warn log.

## 14. Performance & Scaling Strategy
Initial synchronous pipeline (no queue). Parallelism via async I/O for LLM + DB. Scaling levers: (1) consolidate multiple calls (classification & recommendation share sanitized narrative), (2) add caching layer for frequent merchant metadata, (3) introduce worker queue once concurrency > ~100. SQLite → Postgres migration path with unchanged repository interface.

## 15. Implementation Roadmap (Condensed)
| Phase | Weeks | Key Deliverables | Exit Checks |
|-------|-------|------------------|-------------|
P1 | 1–4 | API, DB schema, LLM adapter (mock+real), classifier, enrichment, recommendation, audit, metrics, tests, OpenAPI snapshot | FR-01..11 green; eval precision report |
P2 | 5–8 | Override + audit APIs, embeddings, clustering batch, cost metrics, exporter | Precision ≥90%; pattern endpoint returns clusters |
P3 | 9–11 | Async pipeline, circuit breaker, feedback dataset, resilience tests | Latency stable under load; breaker triggers gracefully |

## 16. Testing & Evaluation Framework
| Layer | Tooling | Representative Tests |
|-------|--------|----------------------|
Unit | pytest | classifier fallback, schema validation |
Integration | pytest + test client | POST → full pipeline path |
Prompt Eval | script (eval_classifier.py) | precision/recall JSON output |
Load | locust/k6 (optional) | 100 concurrent POST p95 latency |
Chaos (P3) | fault injection wrapper | Simulate LLM timeout -> fallback |

Artifacts: metrics_snapshot.json, evaluation_report.json, cost_report.json.

## 17. Risk Register (Active)
| ID | Risk | Impact | Mitigation | Trigger to Revisit |
|----|------|--------|-----------|--------------------|
R1 | Elevated token costs | Budget blow | Token cap + cheap model tier | Cost/case > target |
R2 | Low classifier precision | Weak value | Few-shot tuning + dataset expand | Precision < target |
R3 | Schema break by model | Parsing failure | Strict JSONSchema & retry fallback | Validation error spikes |
R4 | DB lock contention (SQLite) | Latency | Early Postgres migration path | Concurrent writes > threshold |
R5 | Over-scope drift | Delivery slip | Phase gate reviews | Slip >1 week |

## 18. Decision Log (Snapshot)
ADR-01 Monolith modular over microservices (single engineer efficiency).  
ADR-02 SQLite first; migrations prepared for Postgres.  
ADR-03 JSONSchema‑bounded LLM outputs for deterministic parsing.  
ADR-04 No queue MVP (simplicity > theoretical parallelism).  
ADR-05 Dual-model tier (cheap classify, higher reasoning recommend) for cost discipline.

## 19. Open Questions
| ID | Question | Current Assumption | Resolution Path |
|----|----------|-------------------|----------------|
Q1 | Include embeddings MVP? | Defer | Add in P2 after core stability |
Q2 | API key mandatory? | Optional toggle | Make default ON in P2 |
Q3 | Policy reference mapping depth? | Minimal stub | Expand with catalog JSON if time |
Q4 | Multi-tenant isolation? | Single tenant | Defer until portfolio feedback |

## 20. Glossary
| Term | Definition |
|------|-----------|
Agent | Self-contained function/module performing a discrete reasoning or data task |
Audit Event | Immutable log entry of a pipeline step with timing & outcome |
Fallback | Degraded deterministic path when LLM call fails or times out |
Pattern Cluster | Grouping of similar disputes via vector similarity |

## 21. Portfolio Narrative Snippet
“Designed and built a contract‑bounded, cost‑aware multi-agent LLM dispute resolution pipeline achieving high classification precision with full audit traceability and a clear extensibility path to fraud pattern intelligence.”

## 22. Implementation Skeleton (Authoritative)
```
app/
  api/routers/disputes.py
  core/{config.py, logging.py}
  domain/{models.py, schemas.py}
  services/{orchestrator.py, classifier.py, enrichment.py, recommendation.py, llm_adapter.py}
  infra/{db.py, migrations/}
  telemetry/{metrics.py, audit.py}
  tests/{test_flow.py, test_classifier.py}
scripts/{seed_transactions.py, eval_classifier.py}
schemas/{classification.schema.json, recommendation.schema.json}
```

## 23. Execution Principles
1. Ship vertical slice early (end-to-end happy path before optimization).  
2. Keep agent interfaces stable; hide prompt iteration inside adapter.  
3. Instrument first, optimize second (measure before refactor).  
4. Enforce schema validation at all external boundaries (API & LLM).  
5. Maintain single source-of-truth (this blueprint) to avoid doc divergence.

---
Single authoritative blueprint complete.
