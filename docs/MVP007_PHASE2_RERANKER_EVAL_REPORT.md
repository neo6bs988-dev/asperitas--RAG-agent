# MVP-007 Phase 2 Reranker Eval Report

Date: 2026-06-16

Related issue: #13

## Decision

Keep reranker eval explicit and keep default retrieval behavior unchanged.

`--reranker deterministic-test` is accepted as reranker plumbing validation, not as a recommended retrieval-quality improvement. It preserves source @5 and overall pass rate for `mvp003` and `hybrid`, but it lowers source @3 for both.

## Commands

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5
```

## Baseline Metrics

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 35.5% | 0.0% |
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `vector` | 56.2% | 56.2% | 59.4% | 59.4% | 59.4% | 54.8% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Reranker Metrics

| Base mode | Reranker | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `mvp003` | `deterministic-test` | 93.8% | 93.8% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid` | `deterministic-test` | 100.0% | 87.5% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Ordering Effects

| Base mode | Top-1 changed | Top-3 changed | Top-5 changed | Source @3 delta | Source @5 delta | Overall delta |
|---|---:|---:|---:|---:|---:|---:|
| `mvp003` | 7/32 | 27/32 | 27/32 | -3.1 pp | +0.0 pp | +0.0 pp |
| `hybrid` | 8/32 | 27/32 | 27/32 | -9.4 pp | +0.0 pp | +0.0 pp |

## Metadata Preservation

Reranker eval preserves:

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
- original retrieval `rank`
- original retrieval `score`
- original retrieval `score_components`

Reranker-specific fields are added under `reranker_metadata`.

## Regression Check

No default retrieval behavior changed.

No reranked run regressed:

- source file match @5;
- source priority;
- evidence label;
- section match;
- path-context match;
- overall pass rate.

Both reranked runs regressed source file match @3. This makes `deterministic-test` useful for plumbing validation but not suitable as a recommended reranker.

## Risks

- The deterministic test reranker is lexical and intentionally simple.
- It can reorder many candidates without improving source-grounded ranking.
- Because it lowers source @3, do not use it as a default or quality-improvement claim.
- A production reranker strategy needs a stronger scoring contract and acceptance threshold before MVP-008 answer generation.

## Next Task

MVP-007 Phase 3: decide whether to tune deterministic reranking rules, add a guarded candidate-preserving reranker, or defer production reranking until a stronger local reranker strategy is defined.

