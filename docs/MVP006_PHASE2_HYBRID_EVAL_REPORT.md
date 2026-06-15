# MVP-006 Phase 2 Hybrid Eval Report

Date: 2026-06-15

Related issue: #11

## Decision

Keep `hybrid` as an explicit experimental eval mode.

Hybrid now matches the `mvp003` reference metrics at top-k 5 while preserving the existing `baseline`, `mvp003`, and `vector` modes. It does not yet beat `mvp003`, so `mvp003` remains the reference retriever.

## Implementation

Added `--retriever hybrid` with mode label:

```text
mvp006-hybrid-metadata-vector
```

Hybrid behavior:

- Collect candidates from `mvp003` top-N and vector top-N, where N is at least `max(limit * 4, 20)`.
- Merge candidates by `chunk_id`.
- Normalize raw `mvp003` scores by the max candidate score.
- Normalize vector cosine scores with the Phase 1 contract.
- Combine scores through `combine_hybrid_score(...)`.
- Include `score_components` and raw `mvp003_score_raw` / `vector_score_raw`.
- Preserve `mvp003` top-k candidates as a reference guard so vector-only candidates cannot regress source @5, source priority, or evidence label accuracy.

## Metadata Preservation

Hybrid rows preserve or derive:

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

`mvp003`-only candidates receive embedding metadata from the existing `EmbeddingRecord` builder before final ranking output.

## Quality Gates

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Results:

- `python -m pytest`: 159 passed
- `python scripts/verify_artifacts.py`: ok; 48 registry records; 2821 chunks; 0 errors; 0 warnings

## Eval Metrics

Dataset: `eval/retrieval_questions.jsonl`

Top-k: 5

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector | 53.1% | 56.2% | 59.4% | 59.4% | 59.4% | 53.1% |
| hybrid | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |

## Regression Check

No final metric regression versus `mvp003`.

Failed question IDs are unchanged versus `mvp003`:

- `MVP0025-Q001`
- `MVP0025-Q004`
- `MVP0025-Q010`

An earlier hybrid sorting pass allowed vector-only candidates to reduce source @5, priority, and evidence to 96.9%. The final implementation fixes that with the `mvp003` top-k reference guard.

## Risks

- Hybrid does not yet improve over `mvp003`; it is useful as a safe experimental mode, not a replacement.
- The reference guard limits vector-only recall in top-k 5. Future phases should evaluate controlled relaxation only when metrics prove no source-grounding regression.
- Runtime remains CPU-heavy because `hybrid` runs both `mvp003` and local vector candidate generation.

## Next Task

MVP-006 Phase 3: analyze failed questions and test targeted hybrid improvements that can beat `mvp003` without relaxing source-priority, evidence-label, or metadata preservation gates.
