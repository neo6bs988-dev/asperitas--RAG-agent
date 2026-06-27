# V1.4A Cost Latency Token Baseline

## Executive bottom line

V1.4A adds deterministic measurement only. It records answer length, approximate token/context size, evidence and citation counts, duplicate evidence/source counts, latency, retrieval/evidence assembly latency where isolated, and answer/router section counts without changing answer behavior or retrieval scoring.

## Baseline commits

- v1_3e_merge_sha: `fd0c93c7a7155f4054266b1b93512c5fe9396231`
- v1_3d_merge_sha: `635db3186f3538b12934f170a314bbe50c1a1d30`
- v1_3c_merge_sha: `65a200cc7736bb946bbf1ead7d71a5129bff7c61`
- pr_102_merge_sha: `9c3d8ee7d9cb6885540aa9f67a8ecff297d468ec`

## Results summary

- Cases measured: 27
- Suite counts: `{"golden_eval": 6, "retrieval_eval_sample": 8, "v1_3c_answer_contract": 7, "v1_3d_truth_compliance_router": 6}`
- Total answer approximate tokens: 9432
- Total retrieved-context approximate tokens: 7983
- Duplicate evidence count: 0
- Duplicate source count: 0
- Ask-agent latency mean/p50/p95/max ms: 845.862 / 0.212 / 3328.692 / 3504.915
- Retrieval/evidence assembly latency mean/max ms: 3268.116 / 3688.785

## Top cost/token drivers

- GOLDEN-001 (golden_eval): 527 context tokens
- GOLDEN-002 (golden_eval): 527 context tokens
- GOLDEN-003 (golden_eval): 527 context tokens
- GOLDEN-004 (golden_eval): 527 context tokens
- GOLDEN-006 (golden_eval): 527 context tokens

## Highest-latency cases

- GOLDEN-004 (golden_eval): 3504.915 ms
- v1_3c_status_truth_boundary (v1_3c_answer_contract): 3328.692 ms
- v1_3c_compliance_gate (v1_3c_answer_contract): 3277.873 ms
- GOLDEN-003 (golden_eval): 3222.134 ms
- GOLDEN-006 (golden_eval): 3217.259 ms

## Scope lock

- measurement_only: True
- answer_behavior_changed: False
- retrieval_scoring_changed: False
- source_artifacts_mutated: False

## Safe V1.4B candidates

- Context compression after retrieval scoring and before answer assembly, without changing ranking.
- Answer-section and boilerplate trimming under V1.3C answer-contract and V1.3D router tests.
- Eval harness caching for registry/chunk reads; keep production behavior separate from baseline claims.

## Not Currently Prioritized

- Duplicate evidence reduction is not currently prioritized because measured duplicate evidence and duplicate source counts are zero.

## Truth boundary

This baseline measures deterministic local cost, latency, token/context size, evidence duplication, and output length. It is not an optimization, deployment claim, legal clearance, regulatory clearance, biological validation, or answer-quality proof beyond the referenced fixtures.
