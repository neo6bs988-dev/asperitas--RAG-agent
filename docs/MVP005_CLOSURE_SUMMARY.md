# MVP-005 Closure Summary

Date: 2026-06-15

## Decision

MVP-005 is complete. Proceed to MVP-006 hybrid retrieval design.

## Completed Scope

MVP-005 established the vector retrieval foundation without external services or vector database dependencies.

Completed phases:

- Issue #2: `EmbeddingRecord` schema and metadata-preservation tests.
- Issue #3: offline deterministic embedding provider boundary.
- Issue #4: local in-memory vector store adapter.
- Issue #5: vector retrieval eval mode.
- Issue #6: vector backend decision and embedding strategy.
- Issue #22: local lexical-semantic embedding provider.

## Final MVP-005 Metrics

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector before Phase 5 | 31.2% | 34.4% | 40.6% | 40.6% | 40.6% | 31.2% |
| vector after Phase 5 | 53.1% | 56.2% | 59.4% | 59.4% | 59.4% | 53.1% |

Vector overall improved by 21.9 percentage points over the Phase 4 vector baseline and now beats the TF-IDF baseline overall. It still underperforms `mvp003`, which remains the reference retriever.

## Final Architecture State

- `EmbeddingRecord` preserves source-grounding metadata.
- `EmbeddingProvider` boundary exists.
- `DeterministicOfflineEmbeddingProvider` remains the CI/test double.
- `LexicalSemanticOfflineEmbeddingProvider` is the MVP-005 local vector provider.
- `InMemoryVectorStore` is the default local vector store adapter.
- `scripts/run_retrieval_eval.py --retriever vector --limit 5` is supported.
- External vector DB adoption is deferred.
- Qdrant remains the provisional future prototype candidate after hybrid retrieval or backend-gated eval justifies it.

## Non-Negotiables Going Into MVP-006

- Do not replace `mvp003`.
- Keep `baseline`, `mvp003`, and `vector` modes separately callable.
- Preserve source IDs, source file, source priority, evidence labels, section metadata, heading context, embedding model, embedding dimension, embedding version, and content hash.
- Do not add external vector DB dependencies until a separate backend prototype gate justifies it.
- Treat vector as a useful signal, not the sole retriever.

## Next Task

Start MVP-006 Issue #10: design hybrid retrieval scoring contract that combines `mvp003` metadata-aware retrieval with the improved local vector signal.