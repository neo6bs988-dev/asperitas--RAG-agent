# V1.12A Retrieval/Reranker Hardening Preflight

## Executive Bottom Line

V1.12A is a measurement-contract and leakage-boundary preflight. It implements no retrieval or reranker improvement. `mvp003` remains the protected reference; legacy hybrid is comparison-only; the deterministic-test reranker is plumbing-only. Durable all-mode capture moves to V1.12B.

## Source Status and Evidence

Confirmed fresh session-4 evidence at `b67598658cd7fb8eb1210fd4fdd05cc702c57e4b`: 32-question public development fixture, 14 multi-valid-source questions, clean repository status, and certified command durations.

| mode | duration s | source@3 | source@5 | priority | evidence | section | path | overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 11.852 | 0.3125 | 0.40625 | 0.40625 | 0.40625 | 0.38710 | 0.0 | 0.375 |
| mvp003 | 219.501 | 0.9375 | 1.0 | 1.0 | 1.0 | 0.96774 | 1.0 | 0.96875 |
| vector | 17.760 | 0.5625 | 0.59375 | 0.59375 | 0.59375 | 0.54839 | 1.0 | 0.5625 |

Hybrid and both deterministic-test reranker results are `historical_not_freshly_reverified`; their fresh runs are `pending_v1_12b_measurement_harness`. These command durations are diagnostic only, not per-query p50/p95.

## Leakage Audit

`EvalQuestion` carries expected, accepted, and oracle fields. `run_hybrid_retrieval`, `collect_hybrid_section_candidates`, and `hybrid_section_score` consume `expected_chunk_or_section`; same-source section substitution can use that oracle-derived score. This is `EVALUATION_ORACLE_LEAKAGE / PROMOTION_VALIDITY_DEFECT`, not a production security vulnerability, breach, exploit, or biosafety incident. Gold fields are allowed in scoring only and forbidden to future leak-free retrieval, candidate generation, reranking, and query-intent inference.

## Dataset and Protected Reference

The fixture is public development data, not protected holdout, and cannot prove generalization. Protected holdout requires human-approved private access and governance. `mvp003` remains unchanged and callable; baseline and vector remain separately callable; rollback remains `mvp003`.

## Future Metric and Promotion Contract

V1.12B will implement strict source@1/@3/@5, MRR@5 (first strict expected source rank reciprocal, zero if absent), and source-level deduplicated nDCG@5 so repeated chunks cannot inflate gain. Strict and relaxed metrics remain separate. Promotion remains opt-in unless source@5, priority, evidence, section, path, and overall do not regress; source@3 or MRR/nDCG improves without source@3 regression; oracle access is zero outside scoring; metadata and candidate preservation pass; latency/context are bounded; tests and CI pass; and rollback is trivial.

## PR Decomposition and Boundary

V1.12B: durable all-mode harness, ranking/latency metrics, leakage-guard tests. V1.12C: one opt-in leak-free query-derived candidate mode. V1.12D: fresh comparison and promote/defer decision. No retrieval/reranker improvement, complete fresh six-mode baseline, holdout, generalization, real answer quality, runtime verifier, production vector DB/KG, approval, wet-lab validation, autonomous execution, production readiness, or foundation-model capability is proven.

## Next Action

Implement V1.12B durable measurement harness, ranking metrics, latency capture, and leakage-guard tests in a separate PR after V1.12A is merged.
