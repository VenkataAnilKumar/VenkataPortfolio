# Benchmarks

## Dataset Candidates
- Open-source monorepos (e.g., kubernetes, vscode) for public evaluation.
- Internal repos with anonymized metrics.

## Tasks
- Clone detection; smell detection; architectural drift identification; safe rename/move/refactor.

## Protocol
- Shadow mode (no PR creation) → human assessment → gated PR creation.
- Track precision/recall for findings; review time; revert rate; coverage deltas.

## Reporting
- Monthly trend dashboards; per-project comparisons; cost per improvement.
