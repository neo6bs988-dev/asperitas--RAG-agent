# MVP-007 Phase 3 Closeout Audit - Reranker Regression Tests

Date: 2026-06-22

Branch: `mvp007-prd-reranker-regression-closeout`

Base: latest `main` including PR #41 merge commit `1b11d00e9885d23c9e9800949ce13f621c0f4d76`.

## Executive Bottom Line

MVP-007 Phase 3 is ready for closeout after PR D if the accompanying regression-test PR passes review and CI.

Phase 3 established an explicit, non-default, candidate-preserving fail-closed reranker policy:

```powershell
--reranker deterministic-test --reranker-policy fail-closed
```

The policy prevents the known deterministic-test source @3 regression by falling back to the base retriever order when runtime source-preservation invariants are violated. This is regression prevention, not evidence that `deterministic-test` improves retrieval quality.

## Phase 3 PR Summary

PR #37 documented the candidate-preserving reranker strategy. It defined the conservative design: preserve `mvp003` as the protected deterministic reference, keep `hybrid` explicit and non-default, and require fail-closed protection before any reranker can be treated as safe.

PR #39 added eval-harness candidate-preservation reporting. It made source @3/@5 changes, candidate dropped/duplicated/introduced counts, metadata preservation violations, and would-fail-closed diagnostics visible without changing retrieval behavior.

PR #41 implemented the explicit fail-closed reranker wrapper. It added `--reranker-policy fail-closed`, runtime structural/provenance validation, fallback to base order, and additive fallback diagnostics.

PR D adds targeted regression coverage and this closeout audit. It does not change retrieval behavior, reranker behavior, scoring, chunking, fixtures, source registry, ingestion, dependencies, defaults, or eval pass/fail semantics.

## Full Fixture Metrics

Dataset: `eval/retrieval_questions.jsonl`

Expected sources: `eval/expected_sources.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 35.5% | 0.0% |
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `vector` | 56.2% | 56.2% | 59.4% | 59.4% | 59.4% | 54.8% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test` | 93.8% | 93.8% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid + deterministic-test` | 100.0% | 87.5% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test + fail-closed` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid + deterministic-test + fail-closed` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Reranker Impact

Direct deterministic-test remains plumbing-only:

| Base mode | Source @3 delta | Source @5 delta | Overall delta | Would fail closed | Main reason |
|---|---:|---:|---:|---:|---|
| `mvp003` | -3.1 pp | +0.0 pp | +0.0 pp | 25/32 | `top3_source_identity_lost` |
| `hybrid` | -9.4 pp | +0.0 pp | +0.0 pp | 23/32 | `top3_source_identity_lost` |

Fail-closed mode prevents the known source @3 regression:

| Base mode | Source @3 delta | Source @5 delta | Priority delta | Evidence delta | Section delta | Path-context delta | Overall delta | Fallback count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `mvp003` | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | 25/32 |
| `hybrid` | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | +0.0 pp | 23/32 |

The high fallback counts are expected because `deterministic-test` is intentionally a plumbing reranker.

## Target-Risk Questions

Target-only temp fixtures were generated outside the tracked repository state for:

- `MVP0025-Q001`
- `MVP0025-Q004`
- `MVP0025-Q010`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 0.0% | 33.3% | 66.7% | 66.7% | 66.7% | 0.0% | 0.0% |
| `mvp003` | 33.3% | 66.7% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `vector` | 33.3% | 33.3% | 33.3% | 33.3% | 33.3% | 0.0% | 100.0% |
| `hybrid` | 100.0% | 66.7% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test` | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `hybrid + deterministic-test` | 100.0% | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test + fail-closed` | 33.3% | 66.7% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `hybrid + deterministic-test + fail-closed` | 100.0% | 66.7% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Target-risk conclusions:

- `MVP0025-Q001` remains protected by fail-closed fallback and still needs hybrid behavior for full pass.
- `MVP0025-Q004` remains protected by fail-closed fallback and still needs hybrid behavior for full pass.
- `MVP0025-Q010` remains protected by path-context semantics and fail-closed fallback.
- Hybrid remains an accepted comparison mode, not the default.
- No fixture semantics were changed.

## Regression Tests Added

PR D adds tests that lock:

- Q001/Q004/Q010 fixture expectations.
- Direct deterministic-test behavior remains capable of changing top-3 source identity.
- Fail-closed policy requires the explicit policy flag.
- Fail-closed mode preserves source @3, source @5, priority, evidence, section, path-context, and overall metrics versus the corresponding base mode.
- Fallback diagnostics remain additive.

Existing PR C tests already cover runtime fallback on:

- reranker exception
- dropped candidate
- duplicated candidate
- introduced candidate
- candidate count change
- top3 source identity loss
- top5 source coverage loss
- grounding metadata mutation

## Guardrail Confirmation

Guardrails preserved:

- No default behavior changed.
- No reranker is default.
- `mvp003` remains the protected deterministic reference.
- `hybrid` remains explicit and non-default.
- `deterministic-test` remains plumbing-only and is not claimed as quality-improving.
- No retrieval scoring, chunking, fixtures, expected answers, source registry, ingestion behavior, dependencies, generated indexes, APIs, model binaries, secrets, or cloud resources changed.
- No source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gate was relaxed.

## Remaining Risks

- Hybrid eval is slow in the local environment; full hybrid runs completed but took several minutes.
- Fail-closed prevents regressions but does not prove reranker quality improvement.
- A real candidate-preserving reranker still requires a separate design, implementation, and full evaluation cycle.
- Runtime fail-closed checks cannot know answer keys; they preserve base candidate/source structure and grounding metadata.

## Recommended Next Phase

Close MVP-007 Phase 3 after PR D passes CI and review.

The next recommended phase is a separate real-reranker evaluation track: define a candidate-preserving reranker strategy that can improve ordering while preserving source @3, source @5, source priority, evidence label, section, path-context, metadata, guardrail, and abstention metrics across full and target-risk fixtures. Do not make any reranker default until repeated full-fixture evidence shows no source-grounding regression.
