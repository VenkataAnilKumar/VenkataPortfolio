# Safety and Rollback

## Policy Gates
- CODEOWNERS/OWNERS approvals; protected branches; critical paths.
- Max churn per PR/module; change windows; freeze periods.

## Validation Steps
- Compile/build; unit/integration tests; static analysis; security scans; coverage checks.

## Rollback Plan
- Per-PR revert script; automatic rollback on failing SLOs within 24–72h.
- Canary rollout for multi-service refactors; feature flags where applicable.

## Auditability
- Record rationale, evidence, and validation results for each change.
- Immutable audit log and traceability to inputs and model versions.
