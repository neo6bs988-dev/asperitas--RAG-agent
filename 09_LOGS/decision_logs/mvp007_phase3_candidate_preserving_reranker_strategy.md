# MVP-007 Phase 3 - Candidate-Preserving Reranker Strategy

Date: 2026-06-17

Repository state: `main` at `472c3b4f4657ea179f64b6533dc79fe4ceee0ebd`

Audit branch: `mvp007-phase3-candidate-preserving-reranker-strategy`

Related work:

- MVP-007 Phase 1 reranker contract
- MVP-007 Phase 2 reranker eval plumbing
- Issue #21 closeout audit for `MVP0025-Q001`, `MVP0025-Q004`, and `MVP0025-Q010`

## Executive Bottom Line

MVP-007 Phase 3 should design and then implement a conservative, explicit, non-default reranker wrapper that preserves candidate coverage and fails closed to the base retriever order whenever source-grounding metrics would regress.

The deterministic-test reranker is useful only as plumbing validation. It must not be described as a retrieval-quality improvement: current full-fixture eval shows source @3 regression for both protected `mvp003` and accepted comparison `hybrid`.

Recommended next implementation strategy:

1. Keep `mvp003` as the protected deterministic reference.
2. Keep `hybrid` as an accepted comparison mode, not the default.
3. Add no production reranker in this PR.
4. In a later PR, add a guardrail-preserving fail-closed wrapper behind an explicit non-default flag.
5. Permit candidate reordering only when source identity coverage, source priority, evidence label, section, path context, and metadata gates are preserved.

## Scope

This document covers design only:

- current reranker architecture
- deterministic-test source @3 regression cause
- candidate-preserving strategy options
- recommended Phase 3 path
- acceptance criteria, eval protocol, and test plan
- proposed PR breakdown before any production reranker work

## Non-Goals

- Do not implement a production reranker.
- Do not change retrieval behavior.
- Do not replace `mvp003`.
- Do not make `hybrid` default.
- Do not relax source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gates.
- Do not change retrieval scoring, chunking, metadata matching, source registry, ingestion, or eval semantics.
- Do not add dependencies, vector DBs, APIs, secrets, model binaries, generated indexes, cloud resources, or network access.
- Do not start MVP-008 or MVP-009.

## Current Architecture Summary

Reranking is row-based and lives behind `src/asperitas_agent/reranking.py`.

- `Reranker` is a protocol with `rerank(query, candidates, top_k=None)`.
- `rerank_candidates(...)` is the enable/disable boundary.
- `reranker=None` returns a deep-copied original candidate order.
- `DeterministicTestReranker` is explicit and offline-only.
- The eval runner supports `--reranker none` and `--reranker deterministic-test`.
- Reranked eval runs compare base and reranked summaries, including ordering changes and metric deltas.

The current metadata preservation check rejects rerankers that mutate required grounding fields:

- `source_id`
- `source_file`
- `source_priority`
- `evidence_label`
- `section`
- `section_heading`
- `section_path`
- `heading_context`
- `embedding_model`
- `embedding_dim`
- `embedding_version`
- `content_hash`

This is necessary but not sufficient: preserving metadata values does not guarantee preserving the right candidates in the right top-k bands.

## Why Deterministic-Test Regressed Source @3

`deterministic-test` scores candidates by lexical overlap over title, source file, section fields, heading context, and text. It preserves metadata, rank, score, and score components, but it is not gate-aware.

The regression mechanism is simple:

1. Base retrieval may place an expected source in the top 3.
2. The reranker may reorder copied candidates based on lexical overlap alone.
3. A non-expected source can move above an expected source.
4. Source @5 can remain intact while source @3 falls.

Current full-fixture evidence:

- `mvp003 + deterministic-test`: source @3 drops from 96.9% to 93.8%.
- `hybrid + deterministic-test`: source @3 drops from 96.9% to 87.5%.
- Source @5 and overall do not drop in these runs, but that is not enough to call the reranker quality-improving.

## Strategy Options

| Option | Description | Expected benefit | Complexity | Regression risk | Required tests | Required eval metrics | Allowed before MVP-008/009? | Changes retrieval behavior? | Explicit non-default flag? |
|---|---|---|---|---|---|---|---|---|---|
| A. Guardrail-preserving reranker wrapper | Run base retrieval, run reranker on copied candidates, validate result against grounding invariants, and fall back to base order on violation. | Strongest safety boundary; makes regressions observable and recoverable. | Medium | Low if fail-closed. | Wrapper fallback, metadata preservation, unchanged disabled path, eval delta assertions. | Source @3, source @5, priority, evidence, section, path context, overall, metadata. | Yes | Only when explicit flag is used. | Yes |
| B. Source-preserving rerank constraint | Preserve base top-3 source identities and base top-5 source coverage while allowing limited intra-source or intra-band reordering. | Directly targets source @3/@5 regression. | Medium | Low to medium; can reduce useful reordering. | Source identity lock tests, duplicate-source handling, missing-source edge cases. | Source @3/@5 deltas, per-source coverage, overall. | Yes | Only when explicit flag is used. | Yes |
| C. Top-k locked candidate bands | Lock top 3 and optionally top 5 bands; allow reranking inside each band only. | Simple, predictable, easy to reason about. | Low | Low; may blunt reranker impact. | Band-order tests, top-k truncation tests, stable tie tests. | Top-1 changes, top-3/top-5 changes, source @3/@5. | Yes | Only when explicit flag is used. | Yes |
| D. Metadata-aware tie-breaker reranker | Use reranker only as a tie-breaker when base scores or bands are effectively tied and grounding metadata remains equal. | Minimal disruption; useful for deterministic ordering polish. | Low to medium | Low | Tie threshold tests, unchanged non-ties, metadata-equal constraints. | Ordering changes, all grounding gates, score-component preservation. | Yes | Only when explicit flag is used. | Yes |
| E. Hybrid-first candidate generation plus conservative rerank | Use `hybrid` as candidate generator and apply constrained rerank after hybrid protection. | Builds on the strongest current comparison mode. | Medium to high | Medium; could be mistaken for making hybrid default. | Explicit-mode tests, hybrid-not-default tests, guardrail fallback. | Hybrid baseline deltas, source @3/@5, section/path context. | Yes, only as comparison mode | Only when explicit hybrid flag is used. | Yes |
| F. Fail-closed reranker mode | Treat any exception, metadata mutation, missing candidate, source coverage loss, or metric regression as a reason to return base order. | Robust operational safety. | Medium | Low; may hide weak reranker value unless logged. | Exception fallback, violation logging, deterministic output, no partial mutation. | Violation counts, fallback counts, all grounding gates. | Yes | Only when explicit flag is used. | Yes |

## Recommended Strategy

Adopt Option A plus Option F, with Option B as the primary invariant set:

`guardrail-preserving fail-closed reranker wrapper`

The wrapper should work with both `mvp003` and `hybrid`, remain non-default, and run only when the caller opts in.

Proposed flow:

1. Run the selected base retriever.
2. Score or summarize the base results.
3. Run the reranker on copied candidates.
4. Validate reranked output before returning it.
5. If validation fails, return the original base order and record a fallback reason.

Eval-time validation can use answer-key metrics:

- no source @3 regression
- no source @5 regression
- no source priority regression
- no evidence-label regression
- no section regression
- no path-context regression
- no metadata preservation regression
- no overall pass-rate regression

Runtime validation must not depend on answer keys. Runtime invariants should use base-result structure instead:

- preserve base top-3 source identities unless an explicit constrained policy allows same-source movement only
- preserve base top-5 source coverage
- never drop or mutate grounding metadata fields
- preserve original rank, score, and score components
- allow reordering only within locked bands or metadata-safe tie-breaks
- fail closed to base order on any exception or invariant violation

## Acceptance Criteria

A future implementation PR may proceed only when all of the following are true:

- `mvp003` default/no-reranker output remains byte-for-byte or semantically unchanged.
- `hybrid` remains explicit and non-default.
- Reranker use remains explicit and non-default.
- Disabled reranker path still deep-copies and preserves original order.
- Metadata preservation checks still cover all required grounding fields.
- Reranker wrapper falls back to base order on candidate loss, metadata mutation, exception, or source coverage regression.
- Full-fixture eval shows no regression in source @3, source @5, priority, evidence, section, path context, or overall for the protected modes under test.
- Target eval for Q001/Q004/Q010 remains no worse than current accepted behavior.

## Eval Protocol

Required full-fixture commands:

```powershell
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5
```

Required target-risk eval:

- Build temp fixtures outside the repo from `eval/retrieval_questions.jsonl` and `eval/expected_sources.jsonl`.
- Include only `MVP0025-Q001`, `MVP0025-Q004`, and `MVP0025-Q010`.
- Run the same six modes with `--json`.
- Do not commit temp files.

Required repository checks:

```powershell
python scripts/verify_artifacts.py
python -m pytest
git diff --check
```

## Test Plan

Future code PRs should add focused tests for:

- explicit reranker flag selection
- disabled reranker preserving base order
- metadata mutation rejection
- unknown candidate rejection
- top-k band preservation
- base top-3 source identity preservation
- base top-5 source coverage preservation
- fail-closed fallback on exception
- fail-closed fallback on candidate drop
- fail-closed fallback on source coverage regression
- deterministic fallback reason reporting
- no default-mode behavior change for `baseline`, `mvp003`, `vector`, or `hybrid`

## Proposed PR Breakdown

1. PR A: this design document and decision log only.
2. PR B: eval harness additions only, including explicit candidate-preservation delta reporting.
3. PR C: candidate-preserving fail-closed wrapper behind a non-default flag.
4. PR D: targeted regression tests for Q001/Q004/Q010 and reranker source @3/source @5 preservation.
5. PR E: optional conservative default decision only after repeated metrics prove no source-grounding regression. This is not part of MVP-007 Phase 3.

## Current Metrics Observed

Dataset: full `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 35.5% | 0.0% |
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `vector` | 56.2% | 56.2% | 59.4% | 59.4% | 59.4% | 54.8% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test` | 93.8% | 93.8% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid + deterministic-test` | 100.0% | 87.5% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Reranker ordering effects:

| Base mode | Top-1 changed | Top-3 changed | Top-5 changed | Source @3 delta | Source @5 delta | Overall delta |
|---|---:|---:|---:|---:|---:|---:|
| `mvp003` | 7/32 | 27/32 | 27/32 | -3.1 pp | +0.0 pp | +0.0 pp |
| `hybrid` | 8/32 | 27/32 | 27/32 | -9.4 pp | +0.0 pp | +0.0 pp |

## Known-Risk Target Metrics

Dataset: temp target-only subset for `MVP0025-Q001`, `MVP0025-Q004`, and `MVP0025-Q010`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 0.0% | 33.3% | 66.7% | 66.7% | 66.7% | 0.0% | 0.0% |
| `mvp003` | 33.3% | 66.7% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `vector` | 33.3% | 33.3% | 33.3% | 33.3% | 33.3% | 0.0% | 100.0% |
| `hybrid` | 100.0% | 66.7% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test` | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `hybrid + deterministic-test` | 100.0% | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Target question expectations:

| Question | Expected source | Expected section or path context | Current classification |
|---|---|---|---|
| `MVP0025-Q001` | `AGENTS.md` | `Source Priority Policy`; `evidence hierarchy` | `hybrid_only` |
| `MVP0025-Q004` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf` | `SINGLE SOURCE OF TRUTH`; `approval` | `hybrid_only` |
| `MVP0025-Q010` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | `P1_RND_PROJECTS`; `PTMC` | `fixed_by_eval_semantics` |

Target reranker impact:

- `mvp003 + deterministic-test` changes all target top-3/top-5 orderings and still fails Q001/Q004 overall because section remains wrong.
- `hybrid + deterministic-test` keeps all three target questions overall-pass, but source @3 drops from 66.7% to 33.3%.
- Therefore deterministic-test remains plumbing-only even when target overall pass rate is unchanged.

## Guardrail And Regression Check

This design does not change code or behavior.

Guardrails preserved:

- `mvp003` remains the protected deterministic reference.
- `hybrid` remains an accepted comparison mode, not the default.
- `deterministic-test` remains plumbing-only.
- No retrieval behavior changed.
- No source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gate was relaxed.
- No fixture, chunk, index, source registry, ingestion, or dependency file was changed.

## Risks And Devil's Advocate Objections

- A strict source-preserving wrapper can make a reranker look useless if it is only allowed to reorder within narrow bands.
- Runtime preservation cannot know expected answers, so it must protect base candidate structure rather than eval truth labels.
- Source @3 may be a stricter signal than overall pass rate; preserving only overall pass would miss the exact regression observed in Phase 2.
- Hybrid-first reranking is attractive because hybrid is strongest today, but it risks being interpreted as a default-policy shift.
- Fail-closed fallback can hide weak reranker value unless fallback reasons are reported in eval output.
- A metadata-preserving reranker can still harm grounding by moving the right source out of the most useful rank band.

## Exact Next Action

Open PR B as an eval-harness-only change that reports candidate-preservation invariants and fallback reasons without changing retrieval behavior. Do not implement a production reranker until those eval diagnostics are in place and passing.
