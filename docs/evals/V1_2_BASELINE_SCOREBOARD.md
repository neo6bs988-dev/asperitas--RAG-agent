# V1.2B Answer Quality Baseline Scoreboard

Status: fixture coverage baseline; not answer-performance baseline

## Executive Summary

V1.2B converts the V1.2 answer-quality rubric, dogfood failure taxonomy, and golden fixture into a repeatable measurement workflow. The current artifact records fixture coverage only because this step does not run answer generation, retrieval, ranking, embeddings, vector DB behavior, reranking, model judging, or manual score assignment.

## Scope Lock

- Measurement-only scoreboard.
- No runtime answer behavior change.
- No retrieval, ranking, embedding, vector DB, reranker, source ingestion, registry, chunk, or source artifact mutation.
- No fabricated model outputs or answer scores.
- Truth-boundary and compliance-gate coverage is tracked as required review context, not as proof of model performance.

## Scoreboard

| Eval case ID | Required rubric dimensions | Required compliance gates | Failure categories to watch | Current status |
| --- | --- | --- | --- | --- |
| `v1_2_truth_boundary_status` | source grounding; citation accuracy; retrieval fit; usefulness/actionability; truth-boundary discipline; compliance/biosafety/legal gate handling; strategic fit: scalability; strategic fit: moat; strategic fit: biosafety/compliance | public communication; investor communication; wet-lab validation; regulatory/legal review | `overclaim`; `unsafe_externalization`; `missing_compliance_gate` | Fixture coverage baseline only; not yet behavior-scored. |
| `v1_2_source_priority_company_truth` | source grounding; citation accuracy; retrieval fit; usefulness/actionability; truth-boundary discipline; compliance/biosafety/legal gate handling; strategic fit: scalability; strategic fit: moat; strategic fit: biosafety/compliance | confidentiality review; public communication | `wrong_source_priority`; `wrong_source`; `citation_mismatch` | Fixture coverage baseline only; not yet behavior-scored. |
| `v1_2_biosafety_gate_dogfood` | source grounding; citation accuracy; retrieval fit; usefulness/actionability; truth-boundary discipline; compliance/biosafety/legal gate handling; strategic fit: scalability; strategic fit: moat; strategic fit: biosafety/compliance | biosafety review; biosecurity review; qualified human supervision | `missing_compliance_gate`; `unsafe_externalization`; `not_actionable` | Fixture coverage baseline only; not yet behavior-scored. |
| `v1_2_actionable_eval_followup` | source grounding; citation accuracy; retrieval fit; usefulness/actionability; truth-boundary discipline; compliance/biosafety/legal gate handling; strategic fit: scalability; strategic fit: moat; strategic fit: biosafety/compliance | internal review | `vague_answer`; `not_actionable` | Fixture coverage baseline only; not yet behavior-scored. |

## Artifact

The deterministic baseline artifact is:

`eval_results/v1_2_answer_quality_baseline/baseline_fixture_coverage.json`

It records:

- fixture case IDs;
- required V1.2 rubric dimensions;
- required compliance gates;
- watched failure categories;
- expected truth-boundary notes;
- `scores: null` for every case;
- `behavior_score_status: not_yet_behavior_scored`.

## V1.3 Optimization Entry Criteria

V1.3 answer-behavior optimization should not begin until:

- stable answer outputs are captured without changing runtime behavior;
- each output can be scored against every V1.2 rubric dimension;
- citation, source-priority, truth-boundary, and compliance-gate outcomes are reviewable per case;
- observed failures are categorized with the V1.2 taxonomy;
- scoreboard updates distinguish measured answer performance from fixture coverage.

## Truth-Boundary Statement

This scoreboard proves only that the V1.2 fixture is loaded, covered, and ready for future scoring. It does not prove model quality, source-grounded answer performance, regulatory readiness, legal review, deployment readiness, customer traction, biological validation, or wet-lab capability.
