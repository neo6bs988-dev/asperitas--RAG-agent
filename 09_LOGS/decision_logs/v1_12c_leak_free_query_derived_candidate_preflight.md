# V1.12C Leak-Free Query-Derived Candidate Preflight Decision

Date: 2026-07-14

Owner: Retrieval Evaluation Release Engineer

Base: post-PR #183 `main` at `41266165a2313aef48ffe3a2904ecec22acf7ca7`.

## Evidence

- V1.12B merged in PR #181 at `8e67b8387b6afdcd79a438cf2763775d396c496d` after exact-head CI `29298324551` and Quality Gates `29298324568` succeeded.
- V1.12B provides strict source@1, MRR@5, source-level nDCG@5, diagnostic latency, an oracle-free `RetrievalQuestion` boundary for baseline/`mvp003`/vector, and non-promotable legacy-hybrid matrix classification.

## Decision

Prepare one deterministic, opt-in, local `mvp006-query-derived-hybrid` mode. It will use a query-derived metadata-intent overlay over oracle-free candidate paths and will not change defaults or promotion state.

This preflight implements no code and claims no retrieval improvement. Protected holdout remains unimplemented, not proven by public-development fixtures, and human-gated.

## Oracle Boundary

Candidate generation may accept only `RetrievalQuestion(question_id, user_question)`, ordinary candidate metadata, and oracle-free results. Expected-source, expected-section/path/priority/label, accepted-source, alias, oracle-note, fixture-answer, threshold, scoring-outcome, and prior-artifact fields are forbidden before scoring. Classification: `EVALUATION_ORACLE_LEAKAGE / PROMOTION_VALIDITY_DEFECT`.

## Selected Architecture

Normalize user-query tokens; match only normal title/section/path metadata; add a bounded explicit overlay; preserve original ranking metadata; deduplicate normalized source/chunk identity; use stable score/rank/source/chunk tie-breakers; fail closed on invalid identity; never fall back to legacy hybrid.

## Rejected Alternatives

LLM or agent planning, external reranker/API, network use, new vector database or embedding model, autonomous tuning, fixture-specific mapping, per-question hardcoding, changing `mvp003`, replacing legacy hybrid, and default promotion are rejected because none is required for the bounded test.

## Recommended Implementation Scope

Re-inspect before implementation. Minimum likely surface: one helper, evaluator mode exposure if necessary, matrix registration if necessary, and focused tests. No dependency, fixture, registry, chunk, threshold, workflow, or default change is authorized by this decision.

## Validation Plan

Test the safe type boundary, absence of oracle fields, no legacy fallback, deterministic normalization/tie-breaking/deduplication, metadata preservation, fail-closed invalid identity, empty-query behavior, opt-in status, unchanged `mvp003`, and non-promotable legacy hybrid. V1.12D must then run fresh comparison, non-regression, latency, CI, and Quality Gates before a human promote/defer decision.

## Rollback and Residual Risk

Rollback is removal of the future explicit opt-in mode; defaults and `mvp003` remain unchanged. Residual risk: query-derived intent may not improve ranking, may regress source@3 or section/path metrics, or may add latency. Public-development fixtures do not prove protected-holdout generalization.

## Next Human Gate

Review this preflight before authorizing the separate V1.12C implementation PR. V1.12D owns comparison and promote/defer.
