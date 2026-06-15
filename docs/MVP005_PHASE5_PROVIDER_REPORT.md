# MVP-005 Phase 5 Provider Report

Date: 2026-06-15

Related issue: #22

## Objective

Add and evaluate a local semantic embedding provider behind the existing `EmbeddingProvider` boundary before installing any external vector database backend.

## Provider Strategy

Implemented a pure-Python lexical-semantic offline provider:

- provider: `LexicalSemanticOfflineEmbeddingProvider`
- model label: `offline-lexical-semantic-hash`
- version: `mvp005-phase5-lexical-semantic`
- vector eval mode label: `mvp005-offline-lexical-semantic-vector`
- vector eval dimension: `1024`

The provider uses local token normalization, simple English stemming, short phrase features, deterministic feature hashing, and L2 normalization. It falls back to the existing deterministic offline hash provider for featureless text.

This is not a production semantic model. It is a safe local step that improves vector retrieval quality without adding dependencies, APIs, model binaries, indexes, endpoints, credentials, or cloud resources.

## Dependency And Security Review

No dependency was added.

No Qdrant, Chroma, FAISS, Weaviate, LangChain, LlamaIndex, model package, external API, secret, endpoint, generated index, or binary model artifact was added.

`DeterministicOfflineEmbeddingProvider` remains available as the CI/test double.

## Metadata Preservation

Vector records still use `EmbeddingRecord` and preserve:

- `chunk_id`
- `source_id`
- `source_file`
- `source_priority`
- `evidence_label`
- `section`
- `section_heading`
- `section_path`
- `heading_context`
- `embedding_model`
- `embedding_dim`
- `embedding_version`
- `content_hash`

Vector eval embeds chunk text plus source-registry metadata for ranking, but returned rows keep the original source-grounding fields intact.

## Eval Results

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Before Overall | After Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector | 31.2% | 53.1% | 56.2% | 59.4% | 59.4% | 59.4% | 53.1% |

Vector overall improved by 21.9 percentage points over the Phase 4 vector baseline and now exceeds the TF-IDF baseline overall by 18.7 percentage points. It still underperforms `mvp003` by 37.5 percentage points overall.

## Commands Run

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

Verification results:

- `python -m pytest`: 147 passed
- `python scripts/verify_artifacts.py`: `ok: true`, 48 registry records, 2821 chunks, no errors or warnings

## Decision

Keep the lexical-semantic offline provider as the MVP-005 Phase 5 vector provider.

Do not replace `mvp003`. The metadata-aware deterministic retriever remains the reference retrieval path.

Do not install Qdrant or another external vector backend yet. The next step should test hybrid retrieval or semantic-vector candidate behavior while preserving `mvp003` as a fallback.

## Next Step

Start the next issue: design MVP-006 hybrid retrieval that can combine `mvp003` metadata-aware scoring with the improved local vector signal.

