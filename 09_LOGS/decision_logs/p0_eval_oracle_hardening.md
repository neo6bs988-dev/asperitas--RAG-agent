# P0 Eval Oracle Hardening Decision Log

Date: 2026-06-22

## Objective

Harden retrieval evaluation oracle scoring so the current 32-question retrieval eval reports both strict exact-source metrics and additive relaxed accepted-source metrics.

This prepares V1 performance measurement. It does not optimize retrieval.

## Audit Findings Used

- Current eval set has 32 questions.
- The prior read-only audit found vector underperformance is mostly real, but exact filename and single-source oracle behavior distorts some metric interpretation.
- Known multi-valid risks include overlapping P0 governance documents, duplicate PTMC copies, duplicate SEED copies, China&AI variants, and broad synthetic biology report overlap.
- Eval expansion to 60-100 questions remains blocked until oracle schema and reporting are reviewed.
- Vector optimization should be a later experiment after oracle hardening.

## Strict Versus Relaxed Oracle Policy

Strict metrics preserve the existing exact `expected_source_file` behavior and remain the threshold/regression source of truth.

Relaxed metrics are additive and separately named. A relaxed source match can pass when a result matches:

- the strict expected source path;
- an `accepted_sources` path;
- an `accepted_source_ids` value;
- a conservative `accepted_aliases` match.

Relaxed metrics must not silently replace strict metrics.

## Scope

Expected files changed by this PR:

- `scripts/run_retrieval_eval.py`
- `tests/test_retrieval_eval.py`
- `eval/retrieval_questions.jsonl`
- `eval/expected_sources.jsonl`
- `docs/EVALS.md`
- `docs/QUALITY_GATES.md`
- `docs/RETRIEVAL_EVAL_THRESHOLDS.md`
- `09_LOGS/decision_logs/p0_eval_oracle_hardening.md`

## Non-Goals

- No retrieval ranking change.
- No chunking change.
- No embedding/vector provider change.
- No `mvp003` semantic change.
- No hybrid default change.
- No reranker behavior change.
- No CI behavior change.
- No ingestion.
- No new eval questions.

## Risks

- Relaxed metrics could be misread as replacing strict regression gates unless reports keep labels clear.
- Accepted aliases can over-broaden if future additions are not tied to registry evidence.
- Duplicate sources with different priority/evidence labels, such as SEED P1 versus P5, should be interpreted carefully.

## Rollback

Revert this PR to restore exact-source-only scoring and fixture schema. Because strict metric keys are preserved, downstream strict threshold gates should remain compatible.

## Next Step

Review strict and relaxed metrics on all retrieval modes. If the oracle behavior is accepted, run metadata integrity hardening next, especially for missing section metadata and duplicate-source interpretation, then expand the golden set to 60-100 questions. Vector optimization should remain blocked until oracle and metadata integrity are both verified.
