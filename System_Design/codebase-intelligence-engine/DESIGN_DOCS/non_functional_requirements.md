# Non-Functional Requirements

## Reliability & Availability
- 99.9% availability target for API; resumable scans; idempotent operations.

## Performance
- Incremental analysis under 10 minutes for medium repos; daily full scans for large monorepos.

## Scalability
- Horizontal workers for parsing/analysis; partition by repo/service/module.

## Security & Privacy
- Least-privilege tokens; in-repo secrets never exfiltrated; PII redaction.
- Support self-hosting and air-gapped deployments.

## Observability
- OpenTelemetry tracing; Prometheus metrics; structured logs; audit events.

## Compliance
- Retention policies, tamper-evident logs; SOC2-friendly controls.

## Cost
- Per-project and per-scan cost budgets; autoscaling; spot instances for batch work.
