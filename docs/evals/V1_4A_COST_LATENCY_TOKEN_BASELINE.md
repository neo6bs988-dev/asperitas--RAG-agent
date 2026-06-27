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
- Total retrieved-context approximate tokens: 13215
- Duplicate evidence count: 0
- Duplicate source count: 0
- Ask-agent latency mean/p50/p95/max ms: 717.292 / 0.142 / 2809.697 / 2871.656
- Retrieval/evidence assembly latency mean/max ms: 2795.827 / 3095.102

## Top cost/token drivers

- GOLDEN-001 (golden_eval): 877 context tokens
- GOLDEN-002 (golden_eval): 877 context tokens
- GOLDEN-003 (golden_eval): 877 context tokens
- GOLDEN-004 (golden_eval): 877 context tokens
- GOLDEN-006 (golden_eval): 877 context tokens

## Highest-latency cases

- v1_3c_status_truth_boundary (v1_3c_answer_contract): 2871.656 ms
- GOLDEN-003 (golden_eval): 2809.697 ms
- GOLDEN-002 (golden_eval): 2791.62 ms
- GOLDEN-001 (golden_eval): 2738.984 ms
- v1_3c_compliance_gate (v1_3c_answer_contract): 2738.682 ms

## Scope lock

- measurement_only: True
- answer_behavior_changed: False
- retrieval_scoring_changed: False
- source_artifacts_mutated: False

## Safe V1.4B candidates

- Reduce duplicated evidence from repeated source paths before answer generation, with citation contract tests preserved.
- Compress retrieved context excerpts after retrieval scoring and before answer assembly, without changing ranking.
- Trim boilerplate in deterministic answer sections only after locking answer-contract/router tests.
- Cache registry/chunk reads in evaluation harnesses; keep production behavior separate from baseline claims.

## Truth boundary

This baseline measures deterministic local cost, latency, token/context size, evidence duplication, and output length. It is not an optimization, deployment claim, legal clearance, regulatory clearance, biological validation, or answer-quality proof beyond the referenced fixtures.
