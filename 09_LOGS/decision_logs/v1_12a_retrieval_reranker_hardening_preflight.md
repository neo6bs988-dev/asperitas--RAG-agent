# V1.12A Decision Log

Owner: Retrieval Evaluation Release Engineer. Date: 2026-07-13. Issue: #178. Base: `b67598658cd7fb8eb1210fd4fdd05cc702c57e4b`.

Decision: publish a docs-only preflight with three certified session-4 modes (baseline, mvp003, vector); classify hybrid and deterministic-test values as `historical_not_freshly_reverified`; defer their fresh capture to V1.12B.

Leakage classification: `EVALUATION_ORACLE_LEAKAGE / PROMOTION_VALIDITY_DEFECT`. No retrieval improvement is implemented. Rejected: indefinite capture retries, hybrid promotion, reranker tuning before a harness, fixture edits, external reranker, vector DB, LLM judge, or CI changes. Skipped: pytest/full suite; this PR changes docs only. Rollback: revert this documentation commit. Residual risk: no complete fresh six-mode matrix, holdout, or generalization evidence.
