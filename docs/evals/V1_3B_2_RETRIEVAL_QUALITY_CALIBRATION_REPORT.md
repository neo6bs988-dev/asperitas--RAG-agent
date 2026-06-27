# V1.3B-2 Retrieval Quality Calibration Report

## Executive Bottom Line

V1.3B-2 calibrates current `mvp003` retrieval after V1.3B-1 fixed source coverage. The calibration is small and deterministic: it adds metadata-only boosts for direct source references, section/heading overlap, and narrowly scoped V1 status/readiness governance docs.

This is retrieval calibration only. It is not answer-quality proof, deployment evidence, legal approval, regulatory approval, biological validation, or wet-lab capability.

## Scope Lock

- No answer-generation behavior change.
- No prompt or answer-contract change.
- No source ingestion.
- No external sources.
- No registry/chunk artifact mutation.
- No embedding, vector DB, or reranker change.
- No fabricated improvement claims.

## Calibration Behavior

The retrieval change is limited to `src/asperitas_agent/retrieval_mvp003.py`:

- `direct_source_reference_bonus`: boosts records whose path, filename, stem, or title is explicitly named in the query.
- `section_heading_bonus`: boosts chunks whose section metadata overlaps query tokens.
- `v1_status_readiness_bonus`: boosts existing V1 status/readiness docs for queries about production, deployment, validation, legal/regulatory approval, readiness, limitations, or eval status.

The default retriever remains `mvp003`; no reranker or semantic/vector path is introduced.

## Before/After Retrieval Metrics

Measured by `eval_results/v1_3b_retrieval_quality_calibration/retrieval_quality_before_after.json`.

Measured deltas after calibration:

- Expected-source hit@1 cases: 1 to 4.
- Expected-source hit@3 cases: 2 to 4.
- Expected-source hit@5 cases: 3 to 4.
- Total expected-source hits in top 5: 4 to 9.
- Retrieval miss flags: 8 to 3.
- Wrong-source proxy flags: 16 to 11.
- Citation candidate availability: 4 of 4 cases before and after.
- Section metadata availability in retrieved rows: unchanged at 19 rows.

Per-case movement:

- `v1_2_truth_boundary_status`: 0 to 3 expected sources in top 5; best expected rank moved from none to 1.
- `v1_2_source_priority_company_truth`: stayed at 1 expected source in top 5.
- `v1_2_biosafety_gate_dogfood`: 1 to 2 expected sources in top 5; best expected rank moved from 5 to 1.
- `v1_2_actionable_eval_followup`: 2 to 3 expected sources in top 5; best expected rank moved from 2 to 1.

Any answer-level outcome remains out of scope for this report.

## Verification

Expected commands:

```bash
python scripts/calibrate_v1_3b_retrieval_quality.py --overwrite --json
python scripts/backfill_v1_3b_source_coverage.py --overwrite --json
python scripts/diagnose_v1_3a_retrieval_quality.py --overwrite --json
python scripts/verify_artifacts.py
python scripts/check_v1_release_readiness.py --json
python scripts/check_v1_2_answer_quality_baseline.py
python scripts/run_v1_2_answer_quality_eval.py --overwrite --json
python scripts/run_golden_agent_eval.py
python -m pytest
```

## Truth Boundary

This calibration improves retrieval ranking/selection diagnostics only. It does not prove answer quality, production readiness, regulatory or legal approval, biological validation, or wet-lab execution readiness.

## Risks/Rollback

Risk: metadata boosts may change the retrieval candidate ordering for governance/status queries. This is intentional and measured here, but it should remain narrow until V1.3C can evaluate answer contracts separately.

Rollback: revert this commit to remove the calibration script/report/tests and restore the prior `mvp003` scoring components.

## Next Step

V1.3C Answer Contract Upgrade should use the calibrated retriever and separately improve how retrieved evidence is converted into answer obligations, limitations, and citations.
