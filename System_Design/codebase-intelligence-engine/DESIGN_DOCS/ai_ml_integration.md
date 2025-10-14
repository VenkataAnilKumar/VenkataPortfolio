# AI / ML Integration

## Models
- Static analysis: rule-based and learned detectors.
- Embeddings for semantic search and clone detection.
- Classifiers for risk scoring; regressors for effort estimation.

## Training data
- Public repos, internal histories, code review outcomes, defect logs.

## Inference flow
1. Extract features from AST, graph topology, historical changes.
2. Embed code/comments for semantic similarity.
3. Aggregate signals to produce findings and scores.

## Guardrails
- Explainability for each recommendation.
- Safety filters: never suggest changes in forbidden paths; cap churn.
- Human-in-the-loop approvals; feedback loops to down-rank bad suggestions.

## Offline evaluation
- Benchmarks against known refactors and defect histories.
- A/B test with shadow suggestions before enabling PR creation.
