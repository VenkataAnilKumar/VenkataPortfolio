# Requirements Detail

Canonical numbered requirements (FR = Functional Requirement, NFR = Non‑Functional Requirement). Each includes Priority (P0 critical, P1 important, P2 later), Acceptance Criteria (AC), and Traceability note (Design / Code artifact mapping).

## 1. Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria (excerpt) | Traceability | Impl Status | Notes |
|----|-------------|----------|-------------------------------|--------------|-------------|-------|
FR-01 | System shall accept dispute submission via POST /v1/disputes | P0 | Returns 201 + body with case id | API Spec §1 | DONE | Implemented (`/v1/disputes`) |
FR-02 | Narrative length > limit shall be truncated with notice | P0 | Response indicates `truncated=true` | Ingestion module | DONE | Truncation at 2000 chars |
FR-03 | System shall classify dispute into taxonomy (≥5 labels) | P0 | ≥85% precision MVP; ≥90% Phase 2 | Classifier Agent | PARTIAL | Only FRAUD_UNAUTHORIZED / OTHER implemented; expand taxonomy |
FR-04 | On classifier failure, rule-based fallback applied | P0 | Fallback path executed; audit record present | Agents Spec §4.1 | PARTIAL | Heuristic classification; explicit failure path TBD |
FR-05 | Enrichment shall fetch last N (≤5) transactions | P0 | Response shows array length ≤ N | Enrichment module | PARTIAL | Mock returns fixed count; DB integration pending |
FR-06 | System shall count prior disputes for customer | P0 | Count matches seeded dataset | DB query layer | PARTIAL | Static value; real query needed |
FR-07 | Recommendation shall output action + confidence + rationale | P0 | JSON fields present & confidence ∈ [0,1] | Recommendation Agent | DONE | Mock adapter returns structured output |
FR-08 | Recommendation fallback to ESCALATE_REVIEW on failure | P0 | Failure simulation returns fallback | Agents Spec §4.4 | PARTIAL | Always returns path; explicit exception fallback to add |
FR-09 | All agent steps shall be logged to audit_event table | P0 | 100% steps produce audit rows | Audit layer | PARTIAL | In-memory buffer only; DB persistence missing |
FR-10 | GET /v1/disputes/{id} returns classification & recommendation | P0 | Fields match stored state | API Spec §2 | TODO | Endpoint stub returns 404 |
FR-11 | GET /v1/metrics returns JSON counters | P0 | Keys present: total_cases, latency | Metrics module | DONE | Implemented `/v1/metrics` |
FR-12 | System shall expose model version in audit entries | P1 | Audit JSON has model field | LLM wrapper | TODO | Not yet captured |
FR-13 | API key authentication optional toggle | P1 | Requests w/o key rejected when enabled | Middleware | PARTIAL | Settings support; header extraction minimal |
FR-14 | System shall support mock LLM mode (no external call) | P1 | Env flag forces deterministic output | LLM adapter | DONE | `MOCK_LLM` env implemented |
FR-15 | Error responses standardized (code, message, correlation id) | P1 | 4xx/5xx examples match schema | API Spec §4 | TODO | Using default FastAPI error model |
FR-16 | Partial enrichment does not block recommendation | P1 | Simulated outage still yields action | Orchestrator | TODO | Need error injection + continue logic |
FR-17 | System shall compute cost estimate per case (tokens→USD) | P2 | Metric `cost_per_case_usd` present | Metrics pipeline | TODO | Placeholder=0.0 |
FR-18 | Pattern clustering job (batch) | P2 | Clusters persisted; endpoint lists | Pattern module | DEFERRED | Phase 2 future |

## 2. Non-Functional Requirements
| ID | Requirement | Priority | Target | Verification | Impl Status | Notes |
|----|-------------|----------|--------|-------------|-------------|-------|
NFR-01 | Classification latency p95 | P0 | <3s (Phase 2) | Load test report | TODO | Measure once persistence added |
NFR-02 | End-to-end POST latency p95 (MVP) | P0 | <8s | Load test | PARTIAL | Likely met (mock) but unmeasured |
NFR-03 | Availability (core APIs) | P1 | 99.5% Phase 2 | Uptime monitor | DEFERRED | Portfolio only |
NFR-04 | Audit completeness | P0 | 100% steps logged | Audit sampling | PARTIAL | In-memory only |
NFR-05 | Security: PII redaction before model | P0 | No raw PAN/email in prompts | Prompt inspection | TODO | Redaction code not implemented |
NFR-06 | Cost per dispute | P1 | ≤$0.45 | Cost dashboard | TODO | Accounting not built |
NFR-07 | Scalability baseline | P1 | 10k disputes/day | Load bench | DEFERRED | Out of scope MVP |
NFR-08 | Observability instrumentation coverage | P0 | ≥95% agent invocations traced | Trace sampling | PARTIAL | Metrics yes; tracing no |
NFR-09 | Data retention (audit) | P1 | ≥180 days | Policy & DB config | PENDING | Need persistence decision |
NFR-10 | Prompt / agent version traceability | P0 | Each audit includes versions | Audit check | TODO | Envelope lacks version fields |
NFR-11 | Test coverage critical paths | P1 | ≥80% orchestrator & agents | Coverage tooling | PARTIAL | Single flow test present |
NFR-12 | Mean recovery time (transient failure) | P2 | <5 min | Chaos drill | DEFERRED | Future resilience phase |

## 3. Data Requirements
| ID | Requirement | Priority | Detail | Status |
|----|-------------|----------|--------|--------|
DR-01 | Synthetic labeled dataset for classifier eval | P0 | ≥200 cases, balanced labels | TODO |
DR-02 | Transaction ledger seed data | P0 | ≥5 tx per test customer | TODO |
DR-03 | Prior dispute history dataset | P0 | For enrichment accuracy checks | TODO |
DR-04 | Policy reference catalogue | P1 | JSON mapping id→description | DEFERRED |

## 4. Compliance & Security Requirements
| ID | Requirement | Priority | Detail | Status |
|----|-------------|----------|--------|--------|
CSR-01 | Least privilege DB roles | P0 | Separate read vs write user | TODO |
CSR-02 | Secrets management | P0 | Env variables; no secrets in repo | PARTIAL | Using env; no secret scanner |
CSR-03 | Input sanitization (prompt injection guard) | P0 | Guardrail regex + heuristics | TODO |
CSR-04 | Audit immutability | P1 | Append-only table / soft lock | DEFERRED |

## 5. Acceptance Test Matrix (Sample)
| Requirement | Test Case | Expected | Status |
|-------------|-----------|----------|--------|
FR-03 | Classify labeled narrative | Returns label & confidence > threshold | TODO |
FR-08 | Force recommendation failure | ESCALATE_REVIEW fallback | TODO |
FR-09 | Submit dispute | Audit rows count >= 3 (steps) | PARTIAL (in-memory) |
NFR-01 | Load 100 concurrent POSTs | p95 classify latency < target | TODO |
NFR-05 | Submit narrative w/ email | Prompt has masked token | TODO |

## 6. Traceability Map
| Requirement Range | Design Reference | Implementation Artifact (planned) | Status |
|-------------------|------------------|----------------------------------|--------|
FR-01..FR-05 | README §5,8; blueprint §§6-8 | api/routers/disputes.py; services/classifier.py | PARTIAL |
FR-06..FR-09 | README §5,8,11; agents.md | services/enrichment.py; telemetry/audit.py | PARTIAL |
FR-10..FR-15 | README §9; api.md | api/routers/disputes.py (& future) | TODO |
NFR-* | README §12; blueprint §11 | telemetry/metrics.py; future tracing | PARTIAL |

## 7. Open Items
| ID | Description | Owner | Due | Status |
|----|-------------|-------|-----|--------|
OI-01 | Decide SQLite vs Postgres for MVP | Eng | TBD | DECIDED (SQLite) |
OI-02 | Acquire initial labeled narrative set | Eng | TBD | OPEN |
OI-03 | Select cost monitoring approach | Eng | TBD | OPEN |
OI-04 | Implement audit persistence | Eng | TBD | OPEN |

---
Version: 1.0.0 | Owner: Engineering | Status: Draft (iterative)

