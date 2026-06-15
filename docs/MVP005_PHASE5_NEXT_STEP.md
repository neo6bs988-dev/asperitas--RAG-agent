# MVP-005 Phase 5 Next Step

Date: 2026-06-15

Related issue: #6

## Decision From Issue #6

External vector backend adoption is deferred. Qdrant is the provisional future prototype candidate, but embedding quality must improve first.

## Why

The current vector mode is measurable but weak:

- baseline overall: 34.4%
- mvp003 overall: 90.6%
- vector overall: 31.2%

The weakness comes from deterministic hash-derived vectors and missing metadata-aware scoring boosts, not from vector storage.

## Next Implementation Step

Add and evaluate a local semantic embedding provider behind `EmbeddingProvider`.

## Required Constraints

- Keep `DeterministicOfflineEmbeddingProvider` as the CI/test double.
- Do not call external APIs.
- Do not commit model binaries, generated indexes, secrets, endpoints, or cloud credentials.
- Keep `mvp003` as the reference retriever.
- Preserve all `EmbeddingRecord` fields.
- Run baseline, mvp003, and vector eval after any semantic-provider change.

## Acceptance Direction

The next provider should improve vector retrieval over the current 31.2% overall vector score or clearly show why MVP-006 hybrid retrieval is needed before backend installation.