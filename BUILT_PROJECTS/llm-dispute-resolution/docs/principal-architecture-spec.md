# Architecture Specification (Superseded)

This document has been superseded by `docs/blueprint.md`, which now serves as the single authoritative source. Retained for historical comparison. Refer to the blueprint for current decisions, scope, and architecture. The original content remains below unmodified for archival purposes.

---
# (Original) Architecture Specification: Multi-Agent Dispute Resolution System

Version: 1.0.0  | Owner: Engineering  | Status: Draft (Historical)  
Scope: Portfolio-grade implementation blueprint optimized for a single engineer while demonstrating production-quality architectural rigor.

---
## 1. Problem Identification & Validation
### 1.1 Core Problem & Beneficiaries
Financial platforms expend excessive analyst time (12–18 mins/case) on early dispute triage (classification + basic context gathering). This creates SLA risk, inconsistent outcomes, and lost recovery opportunities. Primary beneficiaries: Dispute Analysts, Fraud Investigators, Compliance Officers; secondary: Product & Finance (cost), Customers (faster resolution).

### 1.2 Inadequate Current Solutions
| Category | Limitation |
|----------|-----------|
Rule-based Triage | Static, brittle; poor recall on emerging fraud patterns |
Generic Case Management Tools | Workflow-centric, not reasoning/LLM-aware |
Standalone Fraud Scoring APIs | Score single transactions; no multi-artifact rationale |
Ad-hoc Analyst Procedures | Non-repeatable, low observability, variable quality |

### 1.3 Technical Challenges
| Challenge | Why Hard |
|-----------|----------|
Unstructured Narrative Understanding | Requires robust classification with explainability & confidence |
Context Aggregation | Multiple data dimensions (transactions, prior disputes) fused under latency budget |
Explainable Recommendations | LLM outputs must be deterministic-enough + schema-bounded |
Cost Control | LLM token usage variability vs per-case budget ceiling |
Auditability | Need reconstructible rationale chain for compliance |
Incremental Extendability | Must evolve to vector similarity & pattern clustering without core refactor |

### 1.4 10x Better Criteria
| Dimension | Baseline | Target (10x) | Mechanism |
|----------|----------|--------------|-----------|
Handling Time | 12–18 mins | 3–7 mins (↓≥60%) | Automated classification + enrichment |
Consistency | Human variance | Stable taxonomy (≥90% precision) | Structured LLM prompts + fallback rules |
Explainability | Ad-hoc notes | Structured JSON rationale + policy refs | Schema & audit events |
Early Fraud Signal | Days lag | <24h cluster surfacing | Embedding + anomaly pipeline (Phase 2+) |
Cost | High FTE cost | Predictable ≤$0.45/case variable compute | Model tier routing + caching |
Compliance | Manual hunts | Immutable audit ledger | Append-only structured events |

Validation Path (Portfolio): Use synthetic labeled dataset (≥200 examples) + reproducible evaluation scripts to evidence precision, latency, and audit completeness.

---
## 2. Project Overview & Value Proposition
### 2.1 Executive Summary
LLM-orchestrated multi-agent service that ingests disputes, classifies, enriches context, generates explainable recommendations, and logs an immutable audit trail—achieving lower handling time, improved consistency, and enhanced fraud pattern readiness.

### 2.2 Differentiators
1. Contract-bound LLM agent outputs (JSON schema enforcement).  
2. Fallback multi-tier reasoning (LLM → rule heuristic → escalate).  
3. Audit-first design: every agent step persisted.  
4. Cost guardrails baked into orchestrator (token budgeting + model tier selection).  
5. Extensible path to vector similarity & clustering without architectural rewrite.  

### 2.3 Success Metrics / KPIs
| KPI | MVP Target | Phase 2 Target |
|-----|------------|----------------|
Classification Precision | ≥85% | ≥90% |
Avg Handling Time Reduction | Synthetic demonstration | ≥30% illustrative scenario |
Recommendation Override Rate | <30% | <20% |
Audit Completeness | 100% steps | 100% |
Cost per Case | ≤$0.55 | ≤$0.45 |
LLM Timeout Escalations | <5% calls | <2% |

---
## 3. Comprehensive Scope Definition
### 3.1 In Scope (Phase 1 MVP)
- Dispute ingestion API (POST /v1/disputes) synchronous pipeline.
- Classification (LLM + fallback rule set).
- Basic enrichment (recent transactions + prior dispute count).
- Recommendation (action + rationale + confidence).
- Structured audit logging (per step).
- Metrics endpoint (JSON): counts, latency, label distribution.
- Deterministic mock mode (no external LLM) for CI & cost-free demos.

### 3.2 Phase 2 Enhancements
- Analyst decision override endpoint.
- Audit event query API.
- Embedding generation & similarity (vector store introduction).
- Pattern clustering batch job + anomaly surfacing.
- Cost attribution metrics, simple Prometheus exporter.

### 3.3 Phase 3 Production Hardening
- Asynchronous processing path (enqueue & poll).
- Circuit breaker + adaptive timeout logic.
- Advanced security (API key rotation, request signing, role claims).
- Incremental learning loop (override feedback dataset).
- Optional multi-tenancy boundaries.

### 3.4 Explicitly Out of Scope (Now)
- Full analyst UI / web portal.
- Chargeback representment document generator.
- Real-time streaming ingestion.
- Multi-language narrative handling.
- Full enterprise IAM / SSO integration.

### 3.5 Constraints & Resource Acknowledgment
Single engineer, limited time; prefer Python monolith (modular packages) over microservices; reduce moving parts; optional components stubbed with seam interfaces; infrastructure minimized (SQLite → Postgres optional; skip container orchestration initially).

---
## 4. Detailed Requirements Analysis
### 4.1 Representative User Stories (Subset)
| ID | Story | Acceptance Criteria |
|----|-------|--------------------|
US-01 | As an integrator, I submit a dispute and receive classification + recommendation in one call. | POST returns 201 JSON: id, classification.label/confidence, recommendation.action/confidence/rationale. |
US-02 | As an analyst, I need the rationale and confidence score for traceability. | Response includes rationale + numeric confidence 0–1, audit row persists same. |
US-03 | As compliance, I must reconstruct processing steps. | GET audit (Phase 2) lists ordered steps with timestamps + success flags. |
US-04 | As engineering, I can run locally without incurring LLM cost. | MOCK_LLM=1 produces deterministic canned outputs; tests pass offline. |
US-05 | As product, I need to know cost per case. | Metric cost_per_case_usd computed (Phase 2). |

### 4.2 Functional Requirements (Condensed)
See `requirements.md` (FR-01..FR-18). Critical P0: FR-01..FR-11.

### 4.3 API Specification
Refer `api.md`. MVP endpoints: POST /v1/disputes, GET /v1/disputes/{id}, GET /v1/metrics.

### 4.4 Data Model & Schemas
Core tables (MVP): dispute_case, recommendation (may inline fields initially), audit_event, transaction_ledger. See `architecture.md` ER diagram.

### 4.5 Non-Functional Requirements
Latency: classify p95 <3s (Phase 2). End-to-end p95 <8s MVP. Audit completeness 100%. Cost ≤$0.45 Phase 2. See `requirements.md` NFR-01..NFR-12.

### 4.6 Security & Privacy
Prompt sanitization (mask email, card-like patterns). API key optional. Minimal PII persisted. Future: hashed customer ids for anonymization.

---
## 5. System Architecture & Design
### 5.1 Conceptual Diagram
Client → API Layer → Orchestrator → (Classifier → Enrichment → Recommendation) → Persistence (DB + Audit) → Metrics.

### 5.2 Component Decomposition
| Component | Responsibility | Notes |
|-----------|----------------|-------|
API Router | Request validation, model invocation | FastAPI dependencies |
Orchestrator | Step coordination, timing, error paths | Implements run() pipeline |
Classifier Agent | LLM classification with rule fallback | JSON schema constrained |
Enrichment Service | Fetch last N transactions + prior disputes count | Single DB repo function |
Recommendation Agent | LLM reasoning: action & rationale | Structured JSON output |
Audit Logger | Append step events | Interceptor / decorator |
Metrics Collector | Counters & latency histograms | In-memory + snapshot endpoint |
LLM Client Adapter | Abstract OpenAI vs mock | Fallback + token budgeting |

### 5.3 Data Flow (MVP)
Request → Validate → Persist case (RECEIVED) → classify() → update classification → enrich() → recommend() → persist recommendation → emit audit events → aggregate response.

### 5.4 State Management
Dispute state machine (simplified): RECEIVED → PROCESSING → COMPLETED (error path: FAILED + reason).

### 5.5 Interface Contracts
LLM Adapter: classify(prompt_ctx) → {label, confidence, rationale}; recommend(ctx) → {action, confidence, rationale}. Contracts typed (Pydantic models) + JSONSchema export.

### 5.6 Deployment Architecture (Portfolio)
Single container (optional) or local process: FastAPI app + SQLite DB file. Environment variables: OPENAI_API_KEY (optional), MOCK_LLM, DB_URL.

---
## 6. Technical Specification
### 6.1 Technology Stack & Trade-offs
| Layer | Choice | Justification | Trade-off |
|-------|--------|--------------|----------|
Language | Python 3.11+ | Mature ecosystem, FastAPI, async I/O | Lower raw perf vs Go/Rust |
Web Framework | FastAPI | Type hints, auto OpenAPI | Learning overhead minimal |
DB | SQLite (MVP) / Postgres upgrade path | Zero setup locally → easier portfolio use | Concurrency limits (SQLite) |
ORM / Models | SQLModel or SQLAlchemy + Pydantic | Declarative, schema generation | Some overhead |
LLM Access | OpenAI SDK (pluggable adapter) | Quick integration | External dependency / cost |
Vector Store (Phase 2) | FAISS or Chroma (optional) | Simple local index | Memory footprint |
Task Queue (Deferred) | None (synchronous) | Simplicity | Limits async scaling |

### 6.2 Database Decisions
MVP: SQLite with WAL mode for moderate concurrency. Migration scripts (Alembic) from day 1 to avoid friction upgrading to Postgres.

### 6.3 Communication Patterns
In-process function calls; no message broker initially. Future: add Redis queue for parallel enrichment & pattern jobs.

### 6.4 Security Architecture
Boundary: API key (header). Sanitizer pre-LLM. Sensitive fields excluded from logs. Secrets via env only; no code-embedded tokens.

### 6.5 Monitoring & Observability
Instrumentation decorator adds: start_ts, end_ts, latency_ms, success, failure_type. Expose metrics via GET /v1/metrics. Logging: structured JSON to stdout. Optional: span id seeded from case id for correlation.

### 6.6 Cost Management
Token budget per case (hard limit). Model tier selection (classification cheaper vs recommendation higher). Mock mode default for CI / tests.

---
## 7. Implementation Roadmap
### Phase 1 (Weeks 1–4/6): MVP
Deliverables:
- FastAPI skeleton + health + config loader.
- DB schema & migrations (dispute_case, audit_event, transaction_ledger seed script).
- LLM adapter (real + mock) + classifier prompt + rule fallback.
- Enrichment function.
- Recommendation prompt + schema validator.
- Orchestrator pipeline + audit & metrics.
- Unit + integration tests (≥70% orchestrator, agents).
- OpenAPI spec snapshot + README usage.
Success Criteria: FR-01..FR-11 pass tests; precision evaluation script runs; end-to-end latency <8s p95 (synthetic).

### Phase 2 (Weeks 5–8/9): Enhanced Capabilities
Deliverables:
- Analyst decision endpoint.
- Audit retrieval endpoint.
- Embedding generation + vector similarity (FAISS index) for pattern seed.
- Pattern clustering batch script (nightly simulation).
- Prometheus-ready metrics exporter.
- Cost per case computation.
Success Criteria: Classification precision ≥90%; cost metrics visible; vector similarity endpoint returns neighbors.

### Phase 3 (Weeks 9–11/12): Production Readiness Layer
Deliverables:
- Asynchronous ingestion mode (queue abstraction stub or background task).
- Circuit breaker + adaptive timeout wrapper.
- Override feedback capture & dataset generation.
- Hardening: retry/backoff config, graceful shutdown, structured error codes.
- Extended test suite (load test script + chaos simulation stub).
Success Criteria: System sustains 100 concurrent synthetic disputes with acceptable latency; breaker triggers gracefully under forced LLM delays.

---
## 8. Risk Analysis & Mitigation
| Risk | Category | Impact | Likelihood | Mitigation |
|------|----------|--------|-----------|------------|
LLM Cost Spike | Technical/Cost | Budget overrun | Medium | Mock mode default; token cap; caching (Phase 2) |
Latency Variability | Performance | Breach SLO | Medium | Timeout + fallback tier model |
Schema Drift (Prompts) | Architectural | Break downstream parsing | Medium | JSON schema validation + pinned prompt versions |
SQLite Concurrency Limits | Architectural | Lock contention | Low | Early Alembic readiness for Postgres switch |
Over-scoping Features | Resource | Delay demonstration | Medium | Phase gating + cut-line doc |
Low Classification Precision | Quality | Weak value proposition | Medium | Few-shot tuning + training set iteration |
Prompt Injection | Security | Data leakage | Low | Sanitizer + allowlist output schema |

### 8.1 Validation & Testing Strategy
See `requirements.md` §5 & `mvp.md` test plan. Adds chaos injection (timeout simulation) + golden dataset evaluation script producing precision/recall JSON artifact.

---
## 9. Evaluation Framework
### 9.1 System Performance
Metrics gathered per run: classification_latency_ms, recommendation_latency_ms, total_case_latency_ms, error_rate%. Report script aggregates p50/p95.

### 9.2 Dispute Resolution Quality
| Metric | Method |
|--------|-------|
Precision / Recall | Evaluate classifier labels vs golden set |
Override Rate | (overrides / total recommendations) Phase 2+ |
Rationale Quality (subjective) | Template rubric + semantic similarity (optional) |

### 9.3 User Satisfaction (Portfolio Approximation)
Proxy: Simulated analyst override logs + qualitative rubric; documented in README narrative.

### 9.4 Technical Benchmarks
| Benchmark | Target |
|-----------|-------|
Cold Start Launch | <2s app startup |
Memory Footprint | <300MB baseline (no vector index) |
Throughput (Synthetic) | 100 concurrent POST sustained |

### 9.5 Reporting Artifacts
- metrics_snapshot.json (script output)
- evaluation_report.json (precision/recall)
- cost_report.json (token usage aggregation)

---
## 10. Implementation Skeleton (Planned Directories)
```
app/
  api/routers/disputes.py
  core/config.py
  core/logging.py
  domain/models.py
  services/orchestrator.py
  services/classifier.py
  services/enrichment.py
  services/recommendation.py
  services/llm_adapter.py
  infra/db.py
  infra/migrations/
  telemetry/metrics.py
tests/
  test_dispute_flow.py
scripts/
  seed_transactions.py
  eval_classifier.py
```

---
## 11. Decision Log (Key Architectural Decisions)
| ID | Decision | Rationale | Revisit When |
|----|----------|-----------|--------------|
ADR-01 | Monolith (modular) | Simplicity for single engineer | Load > design threshold |
ADR-02 | SQLite first | Zero infra friction | Concurrency pressure |
ADR-03 | JSON-schema bounded LLM IO | Reliability & parsing safety | Model evolves or adds streaming |
ADR-04 | No queue MVP | Faster delivery | Async scaling needed |
ADR-05 | Dual model tier (cheap classify, premium recommend) | Cost optimization | Cost anomalies observed |

---
## 12. Open Questions
| ID | Question | Current Stance | Resolution Trigger |
|----|----------|----------------|--------------------|
Q-01 | Use embeddings in MVP? | Defer | When pattern clustering prioritized |
Q-02 | Introduce Redis early? | Defer | Need async fan-out / caching for latency |
Q-03 | Add RBAC roles? | Defer | Analyst UI emerges |
Q-04 | Multi-tenancy requirements? | Assume single tenant | Evidence of portfolio audience need |

---
## 13. Exit Statement
This specification balances production-minded rigor with pragmatic scoping for a single engineer. The design emphasizes: deterministic agent orchestration, minimal surface area, audit & cost visibility, and clean extensibility for advanced analytics.

---
References: `README.md`, `docs/overview.md`, `docs/requirements.md`, `docs/architecture.md`, `docs/api.md`, `docs/agents.md`, `docs/mvp.md`.
