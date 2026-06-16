# MVP-007 Reranker Contract

Date: 2026-06-16

Related issue: #12

## Objective

Add the smallest reranker boundary that can reorder retrieval candidates without changing existing retriever modes or weakening source-grounding metadata.

## Current Retrieval Policy

| Mode | Policy |
|---|---|
| `baseline` | CLI eval default remains unchanged. |
| `mvp003` | Protected deterministic reference retriever. |
| `vector` | Secondary eval signal. |
| `hybrid` | Accepted eval comparison mode, not default. |

Reranking must not replace `mvp003`, make `hybrid` default, or silently alter any existing mode.

## Interface

The reranker boundary is row-based so it can work with `baseline`, `mvp003`, `vector`, or `hybrid` result dictionaries:

```python
class Reranker(Protocol):
    reranker_name: str
    reranker_version: str
    deterministic: bool

    def rerank(
        self,
        query: str,
        candidates: Sequence[Mapping[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        ...
```

Use `rerank_candidates(...)` as the enable/disable boundary:

- `reranker=None` returns a deep-copied original candidate order.
- An explicit reranker may reorder candidates.
- `top_k` can truncate returned rows.
- Negative `top_k` is rejected.

## Deterministic Test Reranker

`DeterministicTestReranker` is an offline test double only.

Behavior:

- scores candidates by deterministic lexical overlap between the query and candidate title, source file, section fields, heading context, and text;
- preserves original retrieval `rank`, `score`, and `score_components`;
- adds `reranker_metadata` with input rank, reranked rank, reranker name, version, deterministic flag, and reranker score;
- uses stable tie-breaking by original rank and input order;
- makes no network calls and requires no external model or service.

This reranker is not a production relevance model.

## Required Metadata Preservation

Rerankers must not drop or mutate these fields when they are present on input rows:

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

Path-context expectations continue to depend on `source_file`, so rerankers must preserve `source_file` exactly.

Existing retrieval scores and ranks must remain available. A reranker may add metadata, but it must not overwrite `rank`, `score`, or `score_components` unless a later issue explicitly defines a migration.

## Phase 1 Boundary

Phase 1 adds:

- reranker protocol;
- disabled-by-default rerank helper;
- deterministic offline test reranker;
- metadata preservation checks and unit tests;
- this contract and eval plan.

Phase 1 does not add a CLI eval flag and does not run reranking inside `scripts/run_retrieval_eval.py`. That prevents accidental metric changes before the eval contract is approved.

## Eval Plan For Issue #13

Issue #13 should add explicit eval plumbing, for example:

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5
```

Acceptance criteria for a real reranker eval mode:

- default eval output is unchanged when no reranker is enabled;
- reranked mode is explicit in command output;
- source file match @5 does not regress versus the selected base retriever;
- source priority does not regress;
- evidence label does not regress;
- section match does not regress unless the regression is explicitly accepted and explained;
- path-context match does not regress;
- required source-grounding metadata survives reranking;
- `mvp003` remains the protected reference baseline.

## Rollback Path

If reranking regresses source-grounding metrics or drops metadata:

1. Disable the reranker flag.
2. Keep `baseline`, `mvp003`, `vector`, and `hybrid` unchanged.
3. Keep the interface and tests if useful, but do not expose reranking in default evals.
4. Record the regression and reranker failure mode before retrying.

## Next Task

MVP-007 Phase 2 / Issue #13: add explicit reranker eval plumbing and compare no-rerank versus reranked outputs for `mvp003` and `hybrid`.

