# Functional Requirements

## Ingestion & Parsing
- Connect to Git providers; support full and incremental scans.
- Language-aware parsing for top ecosystems; collect ASTs, symbols, types, comments.
- Normalize artifacts into a Code Intelligence Graph.

## Analysis
- Detect code smells, duplication, hotspots, dependency cycles, architectural drift.
- Compute risk and stability scores per module.
- Identify test coverage gaps and critical paths.

## Planning & Refactoring
- Generate candidate refactorings with rationale and impact.
- Batch into dependency-safe plans; produce diffs/PRs.
- Provide rollback plans per step.

## Safety & Governance
- Policy-based gating (owners, critical files, maximum churn, freeze windows).
- CI integration: build, tests, lint, security, coverage.
- Manual approvals and stage gates.

## Developer Experience
- PR annotations with explanations and links to evidence.
- IDE hints and dashboard visualizations (graph, hotspots, risk trends).

## APIs
- Project onboarding, scan triggers, results retrieval, plan generation, and feedback capture.
