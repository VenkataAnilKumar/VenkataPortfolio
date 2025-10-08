# Multi-Agent Dispute Resolution System

## 1. Problem Identification
Financial platforms (banks, issuers, PSPs, card programs, BNPL, wallets) process millions of transactions. Disputes (fraud claims, chargebacks, merchant errors, service/product dissatisfaction) are:
- Expensive (manual handling cost $15–$75 per case; downstream chargeback penalties)
- Slow (multi-hop investigation; SLAs missed → compliance risk)
- Error-prone (inconsistent classification → lost representment opportunities)
- Reactive (little proactive pattern recognition for emerging fraud or merchant issues)

### Current Pain Points
| Area | Pain | Impact |
|------|------|--------|
Case Intake | Free‑text + attachments manually triaged | High FTE load, backlog growth |
Classification | Heuristics / static rules | Misrouted cases, higher handling time |
Data Gathering | Siloed systems (ledger, KYC, fraud engine, CRM) | Context switching, delays |
Decision Quality | Inconsistent reasoning trail | Compliance / audit exposure |
Fraud Pattern Discovery | Slow recognition of coordinated attacks | Financial loss escalates |
Customer Communication | Generic / delayed updates | Poor CX, churn risk |

## 2. Vision / Elevator Pitch
An intelligent, auditable, multi-agent LLM–orchestrated dispute platform that: auto‑intakes, classifies, enriches, reasons, recommends resolution paths, and continuously learns from outcomes—reducing handling time, increasing recovery, and improving compliance traceability.

## 3. Goals & Non‑Goals
| Goals (Phase 1–2) | Non‑Goals (For Now) |
|-------------------|---------------------|
Automated case parsing & classification (≥90% precision) | Building a full ledger or payment switch |
Multi-agent evidence gathering & enrichment | Training foundation LLM models from scratch |
Decision recommendation with rationale & policy citation | Full automation of final human sign-off (keep human-in-loop initially) |
Fraud pattern surfacing (cluster & anomaly signals) | Chargeback representment document generation (future phase) |
Complete audit trail & explainability | Replacing existing fraud platform entirely |
Operational metrics & observability | Real-time risk scoring for all live transactions |

## 4. Stakeholders / Personas
| Persona | Needs | Success Metric |
|---------|-------|---------------|
Dispute Analyst | Fast, enriched case context, rationale suggestions | Reduced handling time/case |
Fraud Investigator | Cross-case link analysis, emerging pattern alerts | Earlier detection lead time |
Compliance Officer | Immutable audit logs, policy mapping | Fewer audit findings |
Ops Manager | Throughput + SLA dashboards | Backlog reduction, SLA adherence |
Product Owner | Roadmap clarity, feature impact | Adoption & NPS |
Customer | Transparent status updates | Faster resolution, fewer escalations |

## 5. High-Level Requirements
### Functional
1. Ingest dispute submissions (API, batch, manual UI placeholder) with metadata & attachments
2. Parse narrative & extract structured fields (merchant, amount, suspected reason)
3. Classify dispute type (fraud-first, merchant error, service not received, friendly fraud risk, misc)
4. Enrichment: fetch transaction history, customer KYC flags, prior disputes, fraud scores, merchant risk indicators
5. Recommend resolution path & confidence with cited internal policy sections
6. Fraud pattern detection: cluster similar disputes & surface anomalies
7. Human-in-loop review workflow (accept / modify / reject recommendation)
8. Generate structured case timeline & reasoning log
9. Emit metrics (classification precision, cycle time, override rate)
10. Provide secure audit & compliance export

### Non-Functional
| Attribute | Target |
|----------|--------|
Latency (classification) | < 3s p95 |
Enrichment completion | < 8s p95 (parallelized) |
Uptime (core APIs) | 99.5% Phase 2 |
Explainability | 100% decisions traceable to sources & policy references |
Security | PII encryption at rest + field-level access control |
Scalability | 10k new disputes/day initial; design for 10x |
Cost | ≤ $0.45 per processed dispute (LLM + infra) target |

## 6. Domain Model (Concepts)
Entities: DisputeCase, Party (Customer, Merchant), Transaction, EvidenceItem, EnrichmentTask, PatternCluster, Recommendation, AuditEvent, PolicyReference.

### Draft Schema Snippets (Logical)
```sql
-- Dispute case
dispute_case(id UUID PK, external_ref TEXT, customer_id UUID, merchant_id UUID, amount_cents BIGINT,
	currency CHAR(3), submitted_at TIMESTAMPTZ, narrative TEXT, status TEXT, classification TEXT,
	classification_confidence NUMERIC, recommendation_id UUID NULL, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ);

recommendation(id UUID PK, dispute_case_id UUID FK, summary TEXT, action TEXT, confidence NUMERIC,
	rationale JSONB, policy_refs JSONB, created_at TIMESTAMPTZ);

evidence_item(id UUID PK, dispute_case_id UUID FK, source TEXT, kind TEXT, content JSONB,
	fetched_at TIMESTAMPTZ, agent_run_id UUID);

pattern_cluster(id UUID PK, cluster_key TEXT, feature_vector VECTOR, size INT, first_seen TIMESTAMPTZ, last_seen TIMESTAMPTZ, risk_score NUMERIC);
```

## 7. Architecture Overview
LLM-centric multi-agent orchestration orchestrates discrete specialized agents via a controller. Async enrichment & retrieval feed an evidence graph; recommendation engine constructs a reasoning chain & explanation artifact.

```
Client/API -> Ingestion Service -> Case Store
										 |-> Orchestrator -> (Classifier Agent -> Evidence Agents -> Pattern Agent -> Recommendation Agent)
										 |-> Metrics/Events -> Observability
										 |-> Audit Log
```

### Component Summary
| Component | Responsibility | Tech (Initial) |
|-----------|----------------|----------------|
API Gateway / FastAPI | REST endpoints, auth, rate limit | Python FastAPI + OAuth2/JWT |
Orchestrator Service | Agent plan creation, parallel task scheduling | Python (asyncio), LangChain / custom planner |
Classifier Agent | Narrative embedding + label selection | OpenAI GPT-4 + few-shot prompt |
Evidence Agents | Pull data from transaction DB, KYC, fraud service, merchant DB | Python workers + Redis task queue |
Recommendation Agent | Consolidate evidence, reason, propose action | GPT-4 w/ structured JSON schema |
Pattern Detection | Vector clustering / anomaly detection | Python + FAISS + scheduled job |
Audit / Event Log | Append-only operations trail | PostgreSQL + CDC (future Kafka) |
Vector Store | Narrative & evidence embeddings | Chroma/FAISS (later pgvector) |
Cache | Short-lived enrichment results | Redis |
Metrics & Tracing | Performance & agent tracing | OpenTelemetry + Prometheus + Grafana |

## 8. Multi-Agent Orchestration Design
1. Orchestrator constructs task graph: classify → parallel evidence tasks → aggregate → recommend → optional pattern update.
2. Each agent has: contract (inputs, outputs JSON schema), timeout, retry policy, fallback (# of attempts, degrade path).
3. Controller stores intermediate artifacts in a run table for full replay.
4. Circuit breakers: escalate to human if classification confidence < threshold or enrichment deadline exceeded.

### Agent Contract Template (JSON Schema Excerpt)
```json
{
	"agent": "classification",
	"input": {"narrative": "string", "amount": 2599, "currency": "USD"},
	"output": {"label": "FRAUD_UNAUTHORIZED", "confidence": 0.93, "rationale": "..."}
}
```

## 9. API (Initial Surface)
| Method | Path | Purpose |
|--------|------|---------|
POST | /v1/disputes | Submit new dispute (async processing) |
GET | /v1/disputes/{id} | Retrieve case + classification + rec |
GET | /v1/disputes/{id}/evidence | List enriched evidence items |
POST | /v1/disputes/{id}/decision | Analyst final decision + overrides |
GET | /v1/patterns | List active clusters / anomalies |

### Sample Dispute Submission
```json
POST /v1/disputes
{
	"external_ref": "CASE-12345",
	"customer_id": "c-789",
	"merchant_id": "m-456",
	"amount": 2599,
	"currency": "USD",
	"narrative": "I did not authorize this transaction at StoreXYZ yesterday."
}
```

## 10. Sequence (Happy Path)
1. Case ingested (status=RECEIVED)
2. Orchestrator triggers classifier (status=CLASSIFYING)
3. Classification stored (status=ENRICHING)
4. Parallel evidence agents complete; evidence aggregated (status=RECOMMENDING)
5. Recommendation agent produces action + rationale (status=PENDING_REVIEW)
6. Analyst approves (status=RESOLVED) OR overrides (status=RESOLVED_MANUAL)
7. Metrics + audit event appended

## 11. Failure / Edge Cases
| Scenario | Handling |
|----------|----------|
LLM timeout | Retry up to N with exponential backoff; fallback smaller model; escalate if still failing |
Low confidence | Flag manual review path early |
Evidence source unavailable | Partial evidence with degraded risk scoring; mark gap in rationale |
Pattern job drift | Backfill feature vectors & re-cluster overnight batch |
Prompt injection in narrative | Sanitize/strip system tokens; apply content moderation pre-filter |

## 12. Observability & Metrics
Key metrics: classification_latency_ms, enrichment_parallel_fanout_time, recommendation_confidence_hist, analyst_override_rate, cost_per_case_usd, fraud_pattern_time_to_detection, dispute_cycle_time.
Tracing: span per agent run, correlation id = dispute_case_id.
Logging: structured JSON (level, case_id, agent, run_id, event_type).

## 13. Security & Compliance
PII tokenization for customer identifiers. Field-level encryption for narrative (potential PII). RBAC: roles (ANALYST, INVESTIGATOR, ADMIN, AUDITOR). Audit log immutable (WORM retention). Prompt content filtered (no full PAN). Data residency: region‑scoped vector store & DB.

## 14. Tech Stack Rationale
Python FastAPI for rapid iteration; async orchestrator; Redis for short-lived task queue/caching; PostgreSQL for relational & audit needs; FAISS/Chroma for vector similarity; OpenAI GPT‑4 for high reasoning quality (with option to downgrade to cost-effective model for enrichment summarization). Modular agents allow polyglot future rewrite (e.g., Go for performance-critical enrichment).

## 15. Phased Delivery Plan
| Phase | Scope | Exit Criteria |
|-------|-------|---------------|
P0 (Spike) | Prototype classifier + basic enrichment + recommendation skeleton | Demo on synthetic 50 cases |
P1 | Full ingestion, classification, enrichment, recommendation, audit log | 90% precision, <3s classify p95 |
P2 | Pattern detection, dashboards, override analytics | 20% reduction handling time |
P3 | Semi-automation of low-risk categories, active learning loop | 30% manual workload reduction |
P4 | Representment package generation, expansion to new dispute types | Cost/case maintained ≤ target |

## 16. Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
LLM hallucination in rationale | Constrain output schema; cross-check policy IDs exist |
Cost creep | Tier models by task; cache embeddings; monitor cost_per_case |
Data leakage | Strict prompt templates; redact sensitive fields before send |
Cold start latency | Warm LLM sessions; connection pooling |
Low adoption by analysts | Include human-in-loop UI feedback; measure override reasons |

## 17. KPIs / Success Metrics
- Avg handling time ↓ ≥30%
- Analyst override rate < 20% after Phase 2
- Classification precision ≥90%, recall ≥88%
- Fraud pattern lead time improvement ≥25%
- Cost per dispute ≤ $0.45
- Audit exceptions = 0 critical

## 18. Testing Strategy
| Layer | Approach |
|-------|----------|
Unit | Pure functions (classification wrapper, parsing, policy mapping) |
Contract | OpenAPI schema tests; JSON schema validation for agent IO |
Integration | End-to-end orchestrator run on fixture disputes |
LLM Evaluation | Golden set with expected labels + rationales (BLEU / semantic similarity) |
Load | Parallel dispute ingestion simulation (locust/k6) |
Chaos | Inject timeouts in evidence agents; validate circuit breakers |

## 19. Future Extensions
1. Active learning loop (analyst override → fine-tune adapter / prompt adjustments)
2. Representment document auto-generation
3. Graph-based merchant linking & collusion detection
4. Multi-lingual dispute narrative handling
5. Real-time streaming early-fraud warnings into upstream prevention stack

## 20. Diagram Placeholders
Add diagrams under `docs/`:
| File | Intent |
|------|--------|
architecture-overview.mmd | High-level component + data flows |
sequence-happy-path.mmd | Detailed agent orchestration sequence |
data-model.mmd | ER-style logical model |
agents-context.mmd | Agent interaction graph |

---
Prepared as a senior-level foundational design document. Iterate as real constraints & empirical metrics emerge.
