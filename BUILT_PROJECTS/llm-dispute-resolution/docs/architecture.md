# Architecture Overview

This document provides deeper architectural detail beyond the high-level project README.

## 1. Context Diagram
```mermaid
flowchart LR
Client[Client / Integrator] --> API[FastAPI Layer]
API --> ORCH[Orchestrator]
ORCH --> CLASS[Classifier Agent]
ORCH --> ENRICH[Enrichment]
ORCH --> RECOMM[Recommendation Agent]
ORCH --> AUDIT[(Audit Store)]
ORCH --> METRICS[(Metrics / Prometheus)]
CLASS --> LLM[(LLM Provider)]
RECOMM --> LLM
ENRICH --> DB[(Dispute DB)]
```

## 2. Logical Component Layers
| Layer | Components | Responsibility |
|-------|-----------|----------------|
Interface | FastAPI routers, request validation | Input boundary, auth, rate limit |
Orchestration | Orchestrator controller, step planner | Order & manage agent execution |
Agents | Classifier, Enrichment, Recommendation, Guardrail | Business/ML logic units |
Data | Repositories (cases, transactions, audit) | Persistence abstraction |
Integration | LLM client, external service adapters | External API communication |
Observability | Metrics + Structured Logging + Tracing | Telemetry for reliability |
Security | Auth middleware, sanitizer, secrets mgmt | Protection & compliance |

## 3. Sequence (Dispute Submission)
```mermaid
sequenceDiagram
	autonumber
	participant C as Client
	participant A as API
	participant O as Orchestrator
	participant G as Guardrail
	participant CL as Classifier
	participant E as Enrichment
	participant R as Recommendation
	participant D as DB
	participant AU as Audit
	C->>A: POST /v1/disputes
	A->>O: create_case(request)
	O->>G: sanitize(narrative)
	G-->>O: clean_text
	O->>CL: classify(case_id, narrative)
	CL-->>O: label + confidence
	O->>E: fetch_context(case_id)
	E-->>O: txns + prior_disputes
	O->>R: recommend(label, context)
	R-->>O: action + rationale
	O->>D: persist recommendation
	O->>AU: audit events (steps)
	O-->>A: aggregated response
	A-->>C: 200 OK (classification + recommendation)
```

## 4. Data Model (Simplified ER)
```mermaid
erDiagram
	DISPUTE_CASE ||--o{ AUDIT_EVENT : has
	DISPUTE_CASE ||--o{ TRANSACTION_LEDGER : references
	DISPUTE_CASE ||--o| RECOMMENDATION : produces
	DISPUTE_CASE {
		UUID id
		TEXT external_ref
		UUID customer_id
		UUID merchant_id
		BIGINT amount_cents
		CHAR(3) currency
		TEXT narrative
		TEXT status
		TEXT classification
		NUMERIC classification_confidence
		TIMESTAMPTZ created_at
	}
	RECOMMENDATION {
		UUID id
		UUID dispute_case_id
		TEXT action
		NUMERIC confidence
		JSONB rationale
	}
	AUDIT_EVENT {
		UUID id
		UUID dispute_case_id
		TEXT step
		JSONB payload
		TIMESTAMPTZ created_at
	}
```

## 5. Deployment Topology (MVP)
```mermaid
flowchart TB
subgraph Container
	APIService[FastAPI + Orchestrator]
end
APIService --> PostgreSQL[(SQLite/Postgres)]
APIService --> Redis[(Optional Cache)]
APIService --> LLMProvider[(OpenAI API)]
```

## 6. Cross-Cutting Concerns
| Concern | Strategy |
|---------|----------|
Error Handling | Unified exception -> JSON error model |
Retries | Exponential backoff wrapper around LLM & DB transient errors |
Configuration | 12-factor: env vars with typed loader |
Security | API key (MVP), later OAuth2; prompt sanitization |
Versioning | Prefix /v1; embed `agent_version` in audit |
Resilience | Circuit breaker for LLM latency > threshold |

## 7. Scaling Considerations
| Bottleneck | Mitigation Path | Phase |
|------------|-----------------|-------|
LLM Latency | Async batch / parallelization | P2 |
DB Reads | Connection pooling, read replicas | P3 |
Throughput | Split agents into workers + queue | P3 |
Cost | Model tier routing + caching | P2 |

## 8. Security Notes
Narrative redaction (regex patterns) before LLM. Minimal PII fields in DB; hashed customer identifiers optional. Secrets via environment only.

## 9. Observability Mapping
Instrumentation via decorator attaches span (agent_name) + metrics counters. Structured logs JSON: {ts, level, case_id, step, latency_ms, success}.

## 10. Open Architecture Questions
| ID | Question | Resolution Path |
|----|----------|----------------|
ARCH-01 | Adopt Redis in MVP or defer? | Evaluate benefit vs complexity |
ARCH-02 | Use pgvector early? | Start with plain JSON; add later |

---
Version: 1.0.0 | Owner: Architecture | Status: Draft

