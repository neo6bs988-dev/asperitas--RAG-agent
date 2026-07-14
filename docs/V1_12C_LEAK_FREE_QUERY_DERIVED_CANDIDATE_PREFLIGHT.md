# V1.12C Leak-Free Query-Derived Candidate-Mode Preflight

## Executive Bottom Line

V1.12C should implement exactly one opt-in, local, deterministic candidate mode provisionally named `mvp006-query-derived-hybrid`. It must replace the legacy hybrid path's expected-section candidate expansion and section scoring with a bounded query-derived metadata-intent overlay. This preflight implements no code, claims no retrieval improvement, and promotes no mode.

## Confirmed Repository State

- V1.12B is merged by PR #181 at `8e67b8387b6afdcd79a438cf2763775d396c496d`; its exact-head CI run `29298324551` and Quality Gates run `29298324568` succeeded.
- V1.12B adds strict source@1, strict source rank@5, MRR@5, source-level deduplicated nDCG@5, and opt-in per-question diagnostic latency.
- `scripts/run_retrieval_eval.py` projects `EvalQuestion` to `RetrievalQuestion(question_id, user_question)` for baseline, `mvp003`, and vector retrieval.
- Legacy `hybrid` still accepts `EvalQuestion`, calls `collect_hybrid_section_candidates`, and scores `expected_chunk_or_section`; it is evaluation-oracle affected.
- The V1.12B matrix labels legacy hybrid and deterministic-test variants `non_promotable` with `oracle_affected_legacy_hybrid` blockers. `mvp003` remains the protected deterministic reference.

## Source Status and Assumptions

The repository fixtures are public-development evaluation fixtures. They are not protected holdout, qualified human gold, generalization, production-latency, or production-readiness evidence. No protected or private data is required for V1.12C.

## Problem Statement

The legacy hybrid mode improves candidate expansion and metadata scoring with `expected_chunk_or_section`. That field is valid in post-retrieval scoring, but not valid input for retrieval-time candidate generation or ranking. The correct classification is **EVALUATION_ORACLE_LEAKAGE / PROMOTION_VALIDITY_DEFECT**, not a production security breach, exploit, or biosafety incident.

## Existing Oracle-Affected Path

`run_hybrid_retrieval(EvalQuestion, ...)` invokes `collect_hybrid_section_candidates(...)`, which filters rows using `question.expected_chunk_or_section`; `hybrid_section_score(...)` uses the same expected field. The dispatcher intentionally sends only legacy hybrid the gold-bearing object. Baseline, `mvp003`, and vector receive `RetrievalQuestion` instead.

## Selected Minimal Design

`mvp006-query-derived-hybrid` is an opt-in, non-default, deterministic metadata-intent overlay:

1. Accept `RetrievalQuestion` only.
2. Reuse existing oracle-free baseline, `mvp003`, and vector candidate paths.
3. Normalize and tokenize only `user_question`; retain bounded tokens/phrases suitable for matching normal candidate title, section, section heading, and section path metadata.
4. Add a bounded deterministic metadata-intent contribution for query-token overlap. Preserve original score, rank, and score-components fields; record any new contribution separately.
5. Deduplicate by normalized source and chunk identity, retain complete metadata, and order by final score descending, original rank ascending, normalized source identity, then chunk identity.
6. Fail closed on missing identity/required metadata and return no hidden fallback to legacy hybrid.

This is the smallest sufficient design because it replaces only the oracle-derived section behavior while retaining existing offline candidate sources. It adds no LLM, embedding model, provider, network call, vector service, framework, or dependency.

## Input Contract

Allowed retrieval-time inputs are `question_id`, `user_question`, normal registry/chunk metadata, existing oracle-free retrieval results, and deterministic concepts derived from `user_question`.

Forbidden before retrieval output exists are `expected_source_file`, `expected_source_id`, accepted-source fields, `expected_chunk_or_section`, `expected_path_context`, expected priority or label, `oracle_notes`, fixture answers, expected rank, score outcomes, threshold outcomes, and prior evaluation output. Gold fields remain permitted only in post-retrieval scoring.

## Query-Derived Intent Contract

The helper must lowercase/normalize query tokens deterministically, discard empty tokens, and compare them against repository-controlled candidate metadata. It must not contain mappings tailored to fixture questions, IDs, answer text, aliases, or expected sections. Empty/no-intent queries receive zero overlay contribution and retain stable oracle-free base ordering.

## Candidate Generation and Scoring Contract

Candidate generation is the union of oracle-free results from existing paths, not a scan expanded by expected sections. The overlay is bounded, deterministic, and additive only to the new mode's temporary final score. It cannot alter baseline, `mvp003`, vector, legacy hybrid, existing thresholds, or any default selection.

## Stable Ordering and Deduplication

Deduplicate deterministically by normalized source/chunk identity. Identical final scores use original rank, normalized source identity, and chunk identity as stable tie-breakers. Invalid or missing identity fails closed rather than silently creating an unstable candidate.

## Metadata Preservation

Each output must preserve source ID, source file, source priority, evidence label, title, section/heading/path context, content hash, chunk ID, original score, original rank, and existing score components. The overlay may add explicit diagnostic components but must not overwrite provenance or grounding metadata.

## Oracle-Leakage Threat Model

| Threat | Required control |
|---|---|
| Direct or indirect gold-field access | Candidate APIs accept `RetrievalQuestion`, not `EvalQuestion`. |
| Expected-section expansion | Query tokens and ordinary metadata replace expected-section inputs. |
| Fixture alias, ID, or special-case rule | Tests reject expected/oracle fields and hard-coded question handling. |
| Hidden legacy fallback | New mode remains separately named; test that legacy hybrid is never called. |
| Post-score or threshold feedback | Candidate generation has no score-result, threshold, or prior-artifact input. |
| Source/chunk duplication | Deterministic normalized deduplication and stable tie-breaking. |

## Failure-Closed Behavior

Missing required identity or metadata, invalid candidate structure, or an unsupported mode fails explicitly. The implementation must not fall back to legacy hybrid, expected-section matching, fixture-specific logic, or a promoted default.

## Test Contract

The implementation PR must test: `RetrievalQuestion`-only candidate APIs; zero expected/oracle-field access; no legacy-hybrid fallback; deterministic token normalization and tie-breaking; source/chunk deduplication; metadata preservation; missing-identity failure; empty-query behavior; opt-in-only registration; non-promotion; unchanged `mvp003`; and unchanged existing thresholds.

## V1.12D Promotion and Non-Regression Gates

V1.12C cannot promote the candidate. V1.12D must make a fresh promote, defer, reject, or revise decision. It requires non-regression for source@5, source priority, evidence label, section, path context, overall pass rate, metadata completeness, and deterministic reruns; plus at least one improvement signal in source@1, source@3, MRR@5, or source-level nDCG@5, with no source@3 regression. It also requires zero oracle access outside scoring, bounded p50/p95 diagnostic latency, no hidden dependency, passing tests/CI/Quality Gates, rollback availability, and explicit human approval before any default switch.

## Scalability Review

The design is a deterministic helper over existing local candidate outputs. It scales from a small offline comparison mode without creating service, state, provider, or operational burden. A future architecture change requires separate measurable evidence that this smallest pattern is insufficient.

## Moat Review

This does not create a data moat by itself. Its value is validity: it makes future ranking evidence less vulnerable to evaluation leakage while preserving provenance and reproducibility.

## Biosafety / Compliance Review

No biological source, compliance decision, approval state, external communication, wet-lab behavior, or autonomous action changes. Evaluator output remains non-authoritative for legal, regulatory, CITES, Nagoya, LMO, biosafety, biosecurity, IP, or wet-lab approval.

## Rejected Alternatives

Rejected for V1.12C: LLM query classification; agents or agent frameworks; external rerankers or network APIs; new embeddings solely for intent inference; vector databases; autonomous tuning; fixture-derived mappings; per-question hardcoding; changing `mvp003`; replacing legacy hybrid; and default-mode promotion. None is necessary to prove one bounded leak-free deterministic candidate mode.

## Failure Modes

Potential outcomes are no improvement, source@3 regression, metadata loss, unstable ordering, insufficient intent signal, or excess diagnostic latency. Each is evidence for V1.12D to defer, reject, or revise; none is grounds to weaken metrics or alter protected references.

## Rollback

Keep `mvp003` protected and defaults unchanged. Roll back the future opt-in implementation by removing its explicit mode registration; no migration, dependency, service, or stored-state rollback is required.

## Proposed Implementation PR Scope

The next PR must re-inspect the repository and choose the minimum surface. It may need one bounded deterministic helper, `scripts/run_retrieval_eval.py` to expose the opt-in mode, `scripts/run_v1_12b_retrieval_matrix.py` to measure it, and focused tests. This preflight does not pre-authorize every listed file.

## Truth Boundary

This PR implements no code, claims no retrieval improvement, promotes no mode, leaves legacy hybrid oracle-affected and non-promotable, keeps `mvp003` protected, and does not implement protected holdout. Protected holdout remains human-gated. V1.12D owns fresh comparison and promote/defer.

## Next Action

After this Draft preflight is reviewed and merged, create a separate V1.12C implementation task for one opt-in leak-free query-derived candidate mode. Do not start V1.12D in that task.
