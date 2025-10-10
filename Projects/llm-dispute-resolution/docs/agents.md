# Agent Specifications & Pre-Implementation Readiness Checklist

This document defines each planned agent, their contracts, failure semantics, operational SLOs, and cross‑cutting readiness items that must be satisfied before writing substantial production code.

---
## 1. Readiness Dimensions (Engineering Checklist)
| Dimension | Key Questions | Status | Notes |
|-----------|---------------|--------|-------|
Problem Framing | Are success thresholds (precision, latency, cost) numerically defined? | DONE | KPIs & targets in blueprint §11 |
Data Availability | Representative dispute narratives & historical outcomes? | PARTIAL | Synthetic set planned (≥200); not yet committed |
Security & Compliance | PII classification, redaction strategy, logging policy? | PARTIAL | Redaction + minimal PII defined; retention decision pending |
Model Strategy | Which tasks need higher vs cheaper models vs rules? | DONE | Dual-tier strategy & mock fallback defined |
Fallback Paths | Rule-based backup or escalate documented? | DONE | Classification heuristic + recommendation ESCALATE_REVIEW |
Cost Guardrails | Max $/case & token limits documented? | DONE | ≤$0.55 MVP; ≤$0.45 Phase 2; token cap 6000 |
Observability | Metrics, logs, traces, run ledger schema locked? | IN PROGRESS | Metrics + audit buffer; trace & persistent audit TBD |
Versioning | Prompt + agent contract version strategy? | DONE | Semantic version + envelope fields |
Data Retention | Narrative & rationale storage duration? | PENDING | Decision: 180 days (to ratify) |
Privacy Reviews | DPIA / privacy review? | N/A | Portfolio context; document rationale only |
Threat Modeling | Injection, leakage, abuse cases addressed? | PARTIAL | Prompt injection mitigation; abuse scenarios backlog |
Performance | p95 concurrency & latency modeling? | IN PROGRESS | Targets set; load test not executed |
Change Management | Promotion path for prompt/agent updates? | PLANNED | Manual review + version bump checklist |
Testing Assets | Golden labeled dataset present? | PARTIAL | Unit/integration tests exist; golden set WIP |
Rollback Plan | Fast disable/feature flag per agent? | PLANNED | To add env-driven agent disable switches |

---
## 2. Agent Inventory Overview
| Agent | Category | Purpose | Criticality | Invocation Mode | Scaling Pattern |
|-------|----------|---------|------------|-----------------|-----------------|
ClassifierAgent | NLP / LLM | Assign dispute type label + confidence | HIGH | Synchronous (Step 1) | CPU bound (LLM latency) |
EnrichmentAgent (Transaction) | Data Fetch | Retrieve last N transactions | MEDIUM | Parallel (fan-out) | I/O bound |
EnrichmentAgent (History Summary) | Summarization | Summarize prior disputes & risk flags | MEDIUM | Parallel | LLM + cache |
RecommendationAgent | Reasoning | Consolidate evidence & propose action | HIGH | Sequential after enrichment | LLM reasoning |
PatternSeedAgent (MVP deferred) | Analytics | Produce candidate feature vectors | LOW | Async batch | Vector ops |
AuditAgent | System | Persist step record + rationale | HIGH | Wrapped around every step | Lightweight write |
MetricsAgent | System | Emit per-step timing & counters | HIGH | Wrapper | In-memory + push |
GuardrailAgent | Validation | Sanitize inputs / detect injection or PII leakage | HIGH | Inline pre/post LLM | Fast regex + policies |

---
## 3. Global Contract Conventions
All agent IO MUST:
1. Conform to JSON schema (enumerated below)
2. Include `agent_version` & `timestamp`
3. Use idempotent `run_id` to support replay
4. Avoid embedding raw PII beyond allowed fields
5. Provide `confidence` when producing probabilistic output

Unified envelope:
```json
{
	"agent": "ClassifierAgent",
	"agent_version": "1.0.0",
	"run_id": "uuid",
	"input": { /* task specific */ },
	"output": { /* task specific */ },
	"meta": {"latency_ms": 842, "model": "gpt-4", "token_usage": {"prompt": 512, "completion": 128}},
	"timestamp": "2025-10-08T10:15:22Z"
}
```

---
## 4. Detailed Agent Contracts

### 4.1 ClassifierAgent
Purpose: Map narrative + minimal structured fields to a dispute type taxonomy.

Taxonomy (v1): `FRAUD_UNAUTHORIZED`, `MERCHANT_ERROR`, `SERVICE_NOT_RECEIVED`, `FRIENDLY_FRAUD_RISK`, `OTHER`.

Input Schema:
```json
{
	"narrative": "string (<=2000 chars)",
	"amount_cents": 2599,
	"currency": "USD",
	"customer_profile": {"prior_disputes": 2, "account_age_days": 430},
	"merchant_profile": {"dispute_rate": 0.014}
}
```
Output Schema:
```json
{
	"label": "FRAUD_UNAUTHORIZED",
	"confidence": 0.91,
	"rationale": "Concise justification citing narrative patterns",
	"features": {"keywords": ["not", "authorize"]}
}
```
SLO: p95 latency < 2500ms; precision ≥ 0.90 on golden set.
Retries: 1 retry on transient HTTP / 429 with exponential backoff (500ms, jitter).
Fallback: Rule-based heuristic (keyword + amount constraints) if LLM fails.
Guardrails: Regex filtering of PAN fragments; narrative truncation > 2000 chars.

### 4.2 EnrichmentAgent (Transaction)
Purpose: Retrieve last N (config default=5) transactions for customer & merchant pair.
Input:
```json
{"customer_id": "c_123", "merchant_id": "m_456", "limit": 5}
```
Output:
```json
{
	"transactions": [
		{"id": "t1", "amount_cents": 2599, "currency": "USD", "ts": "2025-10-08T09:00:00Z"}
	],
	"count_prior_disputes": 2
}
```
SLO: p95 latency < 400ms.
Retries: 2 (DB connectivity).
Fallback: Return empty list + flag `partial=true`.

### 4.3 EnrichmentAgent (History Summary)
Purpose: LLM summarization of pattern across prior disputes.
Input:
```json
{"prior_disputes": [{"label": "FRAUD_UNAUTHORIZED", "age_days": 33}], "recent_transactions": 5}
```
Output:
```json
{"summary": "Customer has 2 prior fraud disputes in last 90d", "risk_indicators": ["repeat_fraud"], "confidence": 0.72}
```
SLO: p95 latency < 1800ms.
Retries: 1.
Fallback: Keyword template summary (non-LLM) if timeout.

### 4.4 RecommendationAgent
Purpose: Combine classifier output + enrichment to propose action: `REFUND`, `ESCALATE_REVIEW`, `REQUEST_INFO`.
Input:
```json
{
	"classification": {"label": "FRAUD_UNAUTHORIZED", "confidence": 0.91},
	"enrichment": {"count_prior_disputes": 2, "recent_txn_count": 5},
	"history_summary": {"risk_indicators": ["repeat_fraud"]}
}
```
Output:
```json
{
	"action": "REFUND",
	"confidence": 0.83,
	"rationale": "High-confidence unauthorized pattern with repeat prior disputes",
	"policy_refs": ["POLICY:FRAUD/CHARGEBACK/REFUND_THRESHOLD_V1"]
}
```
SLO: p95 latency < 2500ms.
Retries: 1 (model-level); fallback action: `ESCALATE_REVIEW` with rationale.

### 4.5 PatternSeedAgent (Deferred)
Stub in code returning `{"status":"disabled"}` until enabled. Avoids later interface churn.

### 4.6 AuditAgent (Wrapper)
Intercepts before & after each agent; persists envelope minus sensitive input fields.
Output Example:
```json
{"step":"ClassifierAgent.post","case_id":"dsp_123","latency_ms":2140,"success":true}
```

### 4.7 MetricsAgent (Wrapper)
Increments counters & histograms. Exposes process-level gauges (CPU, mem) if feasible.

### 4.8 GuardrailAgent
Pre-process narrative: remove emails, mask card-like digit sequences, refuse processing if injection attempt probability > threshold (heuristic + optional moderation API).

---
## 5. Failure & Degradation Matrix
| Agent | Failure Mode | Detection | Degradation Path | Escalation |
|-------|--------------|-----------|------------------|------------|
Classifier | LLM timeout | Request timer | Use rule-based fallback | Log WARN + metric increment |
Enrichment Txn | DB timeout | Query timeout | Return empty array partial=true | Mark case ENRICH_PARTIAL |
History Summary | LLM error | Non-200 | Provide template summary | Flag low_rationale_quality |
Recommendation | Hallucinated policy id | Policy ID validation | Strip invalid refs, still return action | Metric: invalid_policy_ref_count |
Audit | DB write fail | Exception | Retry once in-memory queue | Alert if queue > threshold |

---
## 6. Versioning Strategy
- Semantic version each agent contract (MAJOR change on schema, MINOR on optional field, PATCH on internal logic only).
- Persist `agent_version` in audit for replay comparability.
- Maintain `/v1/agents/contracts` endpoint (static JSON) for external consumers.

---
## 7. Observability Mapping
| Metric | Labels | Source |
|--------|--------|--------|
agent_latency_ms | agent_name | Wrapper timer |
agent_failures_total | agent_name, failure_type | Exception handler |
llm_token_usage_total | agent_name, model | LLM client wrapper |
classification_precision | model_version | Offline eval job |
recommendation_override_rate | n/a | Analyst feedback (future) |

Traces: span per agent invocation (`trace_id = case_id`).

---
## 8. Security Controls Recap
- Input sanitization (GuardrailAgent)
- Output policy reference validation
- PII masking before persistence (narrative hashed + salted optional)
- Principle of least privilege DB roles (writer vs reader)
- Config-driven model API keys (no hardcoding)

---
## 9. Open Questions (Track Before Build)
| ID | Question | Owner | Resolution Due |
|----|----------|-------|----------------|
Q1 | Do we require PCI scope reduction for narratives with partial PAN? | Security | TBD |
Q2 | Is SQLite acceptable for MVP or mandate Postgres from start? | Eng Lead | TBD |
Q3 | How large is golden labeled set for classifier eval? | Data | TBD |
Q4 | Budget per month for LLM usage? | Product | TBD |
Q5 | Need multi-tenant isolation now or later? | Architecture | TBD |

---
## 10. Implementation Gating Criteria
Development can commence when all of: (a) success metrics baseline defined; (b) golden dataset assembled; (c) model + fallback selection ratified; (d) audit schema frozen; (e) cost guardrails documented; (f) open questions Q1–Q5 resolved or consciously deferred.

---
Prepared at a senior engineering depth to minimize rework and accelerate safe iteration.
