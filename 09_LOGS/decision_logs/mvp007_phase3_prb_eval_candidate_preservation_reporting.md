# MVP-007 Phase 3 PR B - Eval Candidate-Preservation Reporting

Date: 2026-06-19

Branch: `mvp007-prb-eval-candidate-preservation-reporting`

Base: `main` after PR #37 merge commit `2bc21706467fd7e180f2a967b2c5832e8ee9dbd1`

## Executive Bottom Line

PR B adds eval-harness visibility for reranker candidate-preservation risk. It does not implement the fail-closed runtime wrapper and does not change retrieval, scoring, chunking, reranking, fixture, or pass/fail semantics.

The deterministic-test reranker remains plumbing-only. The new reporting makes candidate-preservation risk visible so a later PR can decide whether and how to fail closed without guessing.

## Scope

Changed area:

- `scripts/run_retrieval_eval.py`
- retrieval eval tests

Added reporting when a reranker is active:

- top-1/top-3/top-5 ordering changes
- base top-3 source identity preservation
- base top-5 source coverage preservation
- dropped candidates
- duplicated candidates
- introduced candidates
- grounding metadata preservation violations
- would-fail-closed count
- would-fail-closed reason breakdown
- source @3/@5, priority, evidence, section, path-context, and overall regression visibility

## Non-Goals

- No production reranker wrapper.
- No fail-closed runtime behavior.
- No retrieval behavior change.
- No scoring, chunking, metadata, source registry, ingestion, fixture, or eval semantic change.
- No default reranker.
- No replacement of `mvp003`.
- No change making `hybrid` default.
- No dependency, API, vector DB, generated index, secret, model binary, or cloud resource.

## Identity Policy

Candidate-preservation reporting uses stable existing fields and does not mutate candidates.

Candidate identity prefers a composite of:

1. `source_id`
2. `source_file`
3. `content_hash`
4. `chunk_id`

Source identity for top-k preservation uses:

1. `source_id`
2. `source_file`

This keeps source-preservation reporting tied to existing provenance fields while avoiding new schema requirements.

## Reporting Semantics

The existing `reranker_comparison` JSON object is preserved and extended additively.

New fields:

- `top3_source_identity_preserved_count`
- `top5_source_coverage_preserved_count`
- `candidate_dropped_count`
- `candidate_duplicated_count`
- `candidate_introduced_count`
- `metadata_preservation_violation_count`
- `would_fail_closed_count`
- `would_fail_closed_reasons`

`would_fail_closed_reasons` is a reason-to-question-count map. It is reporting-only; it does not alter the returned retrieval results.

Supported reasons:

- `candidate_dropped`
- `candidate_duplicated`
- `candidate_introduced`
- `top3_source_identity_lost`
- `top5_source_coverage_lost`
- `grounding_metadata_mutated`
- `source_at3_regression`
- `source_at5_regression`
- `priority_regression`
- `evidence_label_regression`
- `section_regression`
- `path_context_regression`
- `overall_regression`

## Compatibility

Existing stdout summary lines are preserved.

When a reranker is active, stdout now includes an additional `Candidate preservation:` section.

Existing JSON fields are not removed or renamed. No-reranker JSON output remains unchanged and does not include `reranker_comparison`.

## Guardrail Check

This PR is allowed because it is eval/reporting-only.

Guardrails preserved:

- `mvp003` remains the protected deterministic reference.
- `hybrid` remains an explicit comparison mode.
- `deterministic-test` remains plumbing-only.
- No pass/fail semantic gate is relaxed.
- No source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gate is relaxed.

## Exact Next Action

After this PR, open PR C only if the team accepts the reporting shape and wants to implement a non-default candidate-preserving fail-closed wrapper using these diagnostics.
