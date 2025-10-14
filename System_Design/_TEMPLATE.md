# System Design Title

Brief one-liner positioning the system (what it does, for whom, and why it matters).

---

## 1) Problem & Goals
- Problem statement: what specific pain this solves
- Primary goals (3–6 bullets)
- Non-goals (clarify what’s intentionally out of scope)

## 2) Requirements
- Functional requirements
- Non-functional requirements (SLOs, latency, throughput, availability, durability)
- Compliance and governance

## 3) High-level Architecture
Describe the overall architecture and key subsystems.

Diagram (ASCII):

```
[Client/UI] -> [API Gateway] -> [Service/Coordinator] -> [Workers/Engines]
                  |                    |                    |
                  v                    v                    v
              [AuthZ/IAM]          [Cache/DB]           [External APIs]
```

## 4) Core Components
- Component A: responsibilities, inputs/outputs, scaling, failure modes
- Component B: responsibilities, inputs/outputs, scaling, failure modes
- ...

## 5) Data Model
- Key entities and relationships
- Example schemas (IDs, timestamps, status fields)
- Indexing and partitioning strategy

## 6) API/Interfaces
- External API endpoints (inputs/outputs, status codes)
- Internal interfaces and contracts
- Versioning and backward compatibility

## 7) Workflows & Sequences
- Typical request flow (step-by-step)
- Error paths and retries
- Idempotency strategy

## 8) Scaling & Performance
- Horizontal vs vertical scaling
- Caching layers and invalidation
- Backpressure and rate limiting

## 9) Reliability, Safety, and Observability
- Failure domains and redundancy
- Circuit breakers, timeouts, retries, DLQs
- Tracing, metrics, logs, audits
- Guardrails and policy enforcement

## 10) Security
- AuthN/AuthZ, least privilege, key management
- Data encryption (at-rest/in-transit)
- Threat model and mitigations

## 11) Trade-offs & Alternatives
- Key choices with pros/cons
- Considered alternatives and why rejected

## 12) Deployment & Operations
- Environments and rollouts
- Migrations
- Disaster recovery and RTO/RPO

## 13) Open Questions & Next Steps
- Known unknowns
- Iteration plan

---

Acceptance criteria
- Clear functional coverage and interfaces
- SLOs and safety controls defined
- Operable with metrics and runbooks