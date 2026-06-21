# MVP-007 Phase 3 PR C - Fail-Closed Reranker Wrapper

Date: 2026-06-21

Branch: `mvp007-prc-fail-closed-reranker-wrapper`

Base: `main` after PR #39 merge commit `e000565298cc993d868a695a6f036d5772f4463e`

## Executive Bottom Line

PR C implements an explicit, non-default fail-closed reranker policy:

```powershell
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --reranker-policy fail-closed --limit 5
```

The wrapper allows safe reranker experimentation by returning reranked candidates only when runtime structural and provenance invariants pass. If a reranker violates those invariants, the wrapper falls back to the base retriever order and reports additive diagnostics.

## Scope

Changed areas:

- `src/asperitas_agent/reranking.py`
- `scripts/run_retrieval_eval.py`
- reranking and retrieval-eval tests

Added behavior:

- `--reranker-policy fail-closed`
- runtime candidate/source/metadata validation
- fallback to base order on invariant violation
- additive fallback diagnostics in reranker eval output

## Non-Goals

- No default retrieval behavior change.
- No default reranker.
- No production reranker.
- No runtime fail-open behavior.
- No change to no-reranker behavior.
- No change to existing deterministic-test behavior unless fail-closed policy is explicitly enabled.
- No replacement of `mvp003`.
- No change making `hybrid` default.
- No scoring, chunking, source registry, ingestion, fixture, or eval pass/fail semantic change.
- No dependencies, APIs, vector DBs, generated indexes, secrets, model binaries, or cloud resources.

## Runtime Invariants

The fail-closed wrapper does not use answer keys. It validates only runtime structure and provenance.

Fallback reasons:

- `reranker_exception`
- `candidate_dropped`
- `candidate_duplicated`
- `candidate_introduced`
- `candidate_count_changed`
- `top3_source_identity_lost`
- `top5_source_coverage_lost`
- `grounding_metadata_mutated`

Candidate identity uses existing stable fields:

1. `source_id`
2. `source_file`
3. `content_hash`
4. `chunk_id`

Source identity uses provenance fields only:

1. `source_id`
2. `source_file`

## Diagnostics

When fail-closed policy is active, `reranker_comparison` is extended with:

- `reranker_policy`
- `fallback_count`
- `fallback_reasons`
- `fallback_by_question`

No-reranker JSON and stdout remain unchanged. Existing deterministic-test reranker output remains unchanged unless the fail-closed policy is explicitly enabled.

## Guardrail Check

Guardrails preserved:

- `mvp003` remains the protected deterministic reference.
- `hybrid` remains an explicit comparison mode, not the default.
- `deterministic-test` remains plumbing-only and is not claimed as quality-improving.
- The wrapper prevents unsafe reranker regressions; it is not evidence that the reranker improves quality.
- Fallback uses runtime structural/provenance invariants, not answer keys.
- No source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gate is relaxed.

## Expected Metric Behavior

For `mvp003 + deterministic-test + fail-closed` and `hybrid + deterministic-test + fail-closed`, source @3, source @5, source priority, evidence label, section, path context, and overall pass rate should not regress versus the matching base retriever.

Fallback counts may be high for deterministic-test because it remains a plumbing-only reranker. That is expected and should be interpreted as diagnostic evidence for future candidate-preserving reranker design, not as proof of retrieval-quality improvement.

## Exact Next Action

After PR C review, decide whether PR D should add target-specific regression tests for `MVP0025-Q001`, `MVP0025-Q004`, and `MVP0025-Q010`. Do not make any reranker default without repeated full-fixture evidence showing no source-grounding regression.
