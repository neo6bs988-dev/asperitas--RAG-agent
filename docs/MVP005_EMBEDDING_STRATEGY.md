# MVP-005 Embedding Strategy

Date: 2026-06-15

Related issue: #6

## Decision

Improve embedding quality before selecting an external vector backend. The current vector mode proves the adapter and eval plumbing, but it does not prove semantic retrieval quality.

## Current State

- `EmbeddingRecord` exists and preserves source-grounding metadata.
- `EmbeddingProvider` exists.
- `DeterministicOfflineEmbeddingProvider` exists for offline CI and repeatable tests.
- `InMemoryVectorStore` exists for local adapter tests.
- `python scripts/run_retrieval_eval.py --retriever vector --limit 5` is measurable.
- Current vector overall pass rate is 31.2%, below baseline at 34.4% and far below `mvp003` at 90.6%.

## Strategy

1. Keep the deterministic hash provider as a test double only.
2. Add a local semantic embedding provider behind `EmbeddingProvider`.
3. Do not call external embedding APIs.
4. Do not commit model binaries, generated indexes, API keys, endpoints, or cloud credentials.
5. Preserve embedding provenance in every record:
   - `embedding_model`
   - `embedding_dim`
   - `embedding_version`
   - `content_hash`
6. Keep `mvp003` as the reference retriever until vector or hybrid retrieval passes eval.

## Provider Requirements

Any next provider must:

- run offline and deterministically in tests;
- validate positive embedding dimensions;
- return stable vectors for unchanged text and model version;
- expose explicit model name and version;
- support cache invalidation by `content_hash`, `embedding_model`, `embedding_dim`, and `embedding_version`;
- preserve all `EmbeddingRecord` metadata fields;
- avoid network access in default test mode.

## Evaluation Requirements

Run these commands for every embedding strategy change:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

Track:

- overall pass rate;
- source file match @3 and @5;
- source priority match;
- evidence label match;
- section match;
- failed question IDs;
- top result source file for failures.

## Backend Trigger

Prototype Qdrant only after one of these is true:

- semantic vector mode beats baseline overall;
- semantic vector mode materially improves recall for questions where baseline fails;
- MVP-006 hybrid retrieval needs payload-filtered vector storage for a measured experiment.

Until then, the vector backend decision remains deferred.

## Phase 5 Update

Issue #22 added `LexicalSemanticOfflineEmbeddingProvider`, a pure-Python local provider behind `EmbeddingProvider`.

Measured result:

- previous vector overall: 31.2%
- Phase 5 vector overall: 53.1%
- baseline overall remains 34.4%
- mvp003 overall remains 90.6%

Decision: keep the Phase 5 provider for vector eval, keep `mvp003` as the reference retriever, and defer external vector DB installation until hybrid retrieval or backend-prototype work has a separate measured gate.
