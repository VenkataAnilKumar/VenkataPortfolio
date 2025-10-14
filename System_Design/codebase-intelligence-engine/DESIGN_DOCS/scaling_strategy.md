# Scaling Strategy

## Workload Partitioning
- Shard by repo/service/module; prioritize hotspots and recent churn.

## Execution Model
- Queue-based workers for ingestion, parsing, analysis, and planning.
- Caching for intermediate artifacts (ASTs, embeddings, graph segments).

## Storage
- Object storage for artifacts; relational for metadata; graph DB for relations.

## Performance Tuning
- Incremental diffs; file-level and module-level caching; bloom filters to skip unchanged paths.

## Multi-tenancy
- Namespace isolation; per-tenant rate limits and resource quotas.
