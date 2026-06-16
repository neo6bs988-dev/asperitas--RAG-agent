# Issue #21 - MVP-004 Follow-up: Failed Retrieval Question Recovery Audit

Date: 2026-06-17

Repository state: `main` at `195ea8144615ea0335ad6a00ef3b492507f92585`

Audit branch: `issue21-mvp004-failed-retrieval-followup`

## Executive Bottom Line

- Can Issue #21 be closed? YES.
- Reason: all three historical failed retrieval questions now have clear, reproducible classifications under current eval semantics and accepted comparison modes.
- No retrieval behavior changed.

`MVP0025-Q001` and `MVP0025-Q004` are `hybrid_only`: `mvp003` still fails section/overall, but accepted `hybrid` passes current source-grounding gates. `MVP0025-Q010` is `fixed_by_eval_semantics`: the old failure was a section/path mismatch, and current `expected_path_context` correctly treats `P1_RND_PROJECTS` as source path provenance.

## Scope

Target questions:

- `MVP0025-Q001`
- `MVP0025-Q004`
- `MVP0025-Q010`

Modes compared:

- `baseline`
- `mvp003`
- `vector`
- `hybrid`
- `mvp003 + deterministic-test reranker`
- `hybrid + deterministic-test reranker`

## Non-Goals

- Did not replace `mvp003`.
- Did not make `hybrid` default.
- Did not relax source priority, evidence-label, section, path-context, metadata, guardrail, or abstention gates.
- Did not add dependencies, external services, vector DBs, APIs, generated indexes, secrets, cloud resources, or model binaries.
- Did not change retrieval scoring, chunking, reranking, metadata matching, guardrail logic, source registry, or ingestion behavior.

## Commands Run

Full repository checks:

```powershell
python scripts\verify_artifacts.py
python -m pytest
```

Results:

- `python scripts\verify_artifacts.py`: OK; 48 registry records; 2,821 chunks; 0 errors; 0 warnings.
- `python -m pytest`: 177 passed.

Target-only retrieval fixture was built from `eval/retrieval_questions.jsonl` and `eval/expected_sources.jsonl` for `MVP0025-Q001`, `MVP0025-Q004`, and `MVP0025-Q010`. The temp files were not committed.

```powershell
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever baseline --limit 5 --json
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever mvp003 --limit 5 --json
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever vector --limit 5 --json
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever hybrid --limit 5 --json
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever mvp003 --reranker deterministic-test --limit 5 --json
python scripts\run_retrieval_eval.py --questions %TEMP%\issue21_target_retrieval_questions.jsonl --expected %TEMP%\issue21_target_expected_sources.jsonl --retriever hybrid --reranker deterministic-test --limit 5 --json
```

## Target Eval Metrics

Dataset: target-only subset of `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 0.0% | 33.3% | 66.7% | 66.7% | 66.7% | 0.0% | 0.0% |
| `mvp003` | 33.3% | 66.7% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `vector` | 33.3% | 33.3% | 33.3% | 33.3% | 33.3% | 0.0% | 100.0% |
| `hybrid` | 100.0% | 66.7% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| `mvp003 + deterministic-test` | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% |
| `hybrid + deterministic-test` | 100.0% | 33.3% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Per-Question Result Matrix

Legend: `PASS` means overall pass. `FAIL` includes the primary failing gate.

| question_id | baseline | mvp003 | vector | hybrid | mvp003 + deterministic-test | hybrid + deterministic-test | final classification | close-impact |
|---|---|---|---|---|---|---|---|---|
| `MVP0025-Q001` | FAIL section; expected source rank 3 | FAIL section; expected source rank 5 | FAIL source; expected source not @5 | PASS; expected source rank 5 | FAIL section; expected source rank 3 | PASS; expected source rank 5 | `hybrid_only` | Close allowed; document `mvp003` weakness |
| `MVP0025-Q004` | FAIL section; expected source rank 4 | FAIL section; expected source rank 1 | FAIL source; expected source not @5 | PASS; expected source rank 2 | FAIL section; expected source rank 1 | PASS; expected source rank 5 | `hybrid_only` | Close allowed; document `mvp003` weakness |
| `MVP0025-Q010` | FAIL source/path; expected source not @5 | PASS; expected source rank 1 | PASS; expected source rank 1 | PASS; expected source rank 1 | PASS; expected source rank 1 | PASS; expected source rank 1 | `fixed_by_eval_semantics` | Close allowed |

## Detailed Findings

### MVP0025-Q001

Current expectation:

- Expected source: `AGENTS.md`
- Expected section: `Source Priority Policy`
- Expected path context: none
- Expected priority: `P0`
- Expected evidence label: `Document-Supported Fact`

Original failure summary: `mvp003` found the expected source in top 5, but source-level de-duplication selected a wrong-section chunk from `AGENTS.md`.

Observed result by mode:

| Mode | Overall | Source @5 | Priority | Evidence | Section | Expected rank | Best expected-source candidate |
|---|---|---|---|---|---|---:|---|
| `baseline` | FAIL | PASS | PASS | PASS | FAIL | 3 | `AGENTS.md`; title `AGENTS`; section `Non-Negotiable Truth Rules` |
| `mvp003` | FAIL | PASS | PASS | PASS | FAIL | 5 | `AGENTS.md`; title `AGENTS`; section `Non-Negotiable Truth Rules` |
| `vector` | FAIL | FAIL | FAIL | FAIL | FAIL | n/a | no expected source in top 5 |
| `hybrid` | PASS | PASS | PASS | PASS | PASS | 5 | `AGENTS.md`; title `AGENTS`; section `Core Documents` |
| `mvp003 + deterministic-test` | FAIL | PASS | PASS | PASS | FAIL | 3 | `AGENTS.md`; title `AGENTS`; section `Non-Negotiable Truth Rules` |
| `hybrid + deterministic-test` | PASS | PASS | PASS | PASS | PASS | 5 | `AGENTS.md`; title `AGENTS`; section `Core Documents` |

Interpretation:

- `expected_path_context` is not involved.
- `hybrid` fixes the question through same-source section substitution while preserving source @5, priority, and evidence gates.
- `deterministic-test` does not fix the `mvp003` section failure.
- Final classification: `hybrid_only`.

Remaining risk: `hybrid` passing can mask the fact that protected `mvp003` remains weaker for section-locality on this question.

### MVP0025-Q004

Current expectation:

- Expected source: `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`
- Expected section: `SINGLE SOURCE OF TRUTH`
- Expected path context: none
- Expected priority: `P0`
- Expected evidence label: `Document-Supported Fact`

Original failure summary: `mvp003` found the expected source at rank 1, but selected a wrong-section chunk.

Observed result by mode:

| Mode | Overall | Source @5 | Priority | Evidence | Section | Expected rank | Best expected-source candidate |
|---|---|---|---|---|---|---:|---|
| `baseline` | FAIL | PASS | PASS | PASS | FAIL | 4 | `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`; section `BIOLOGICAL MONOPOLY ENGINE` |
| `mvp003` | FAIL | PASS | PASS | PASS | FAIL | 1 | `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`; section `BIOLOGICAL MONOPOLY ENGINE` |
| `vector` | FAIL | FAIL | FAIL | FAIL | FAIL | n/a | no expected source in top 5 |
| `hybrid` | PASS | PASS | PASS | PASS | PASS | 2 | `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`; section `MISSION` |
| `mvp003 + deterministic-test` | FAIL | PASS | PASS | PASS | FAIL | 1 | `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`; section `BIOLOGICAL MONOPOLY ENGINE` |
| `hybrid + deterministic-test` | PASS | PASS | PASS | PASS | PASS | 5 | `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`; section `MISSION` |

Interpretation:

- `expected_path_context` is not involved.
- `hybrid` fixes the current eval gate by finding an acceptable same-source section candidate under the accepted hybrid policy.
- `deterministic-test` does not fix the `mvp003` section failure.
- Final classification: `hybrid_only`.

Remaining risk: `hybrid` is an accepted comparison mode, not the default production policy; do not present this as `mvp003` being fixed.

### MVP0025-Q010

Current expectation:

- Expected source: `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx`
- Expected section: none
- Expected path context: `P1_RND_PROJECTS`
- Expected priority: `P1`
- Expected evidence label: `Document-Supported Fact`

Original failure summary: the old fixture treated `P1_RND_PROJECTS` as a section expectation even though it is folder/path provenance, not chunk-local heading text.

Observed result by mode:

| Mode | Overall | Source @5 | Priority | Evidence | Section | Path context | Expected rank | Best expected-source candidate |
|---|---|---|---|---|---|---|---:|---|
| `baseline` | FAIL | FAIL | FAIL | FAIL | n/a | FAIL | n/a | no expected source in top 5 |
| `mvp003` | PASS | PASS | PASS | PASS | n/a | PASS | 1 | `2026 PTMC project.pptx`; blank section metadata |
| `vector` | PASS | PASS | PASS | PASS | n/a | PASS | 1 | `2026 PTMC project.pptx`; blank section metadata |
| `hybrid` | PASS | PASS | PASS | PASS | n/a | PASS | 1 | `2026 PTMC project.pptx`; path provenance in `source_file` |
| `mvp003 + deterministic-test` | PASS | PASS | PASS | PASS | n/a | PASS | 1 | `2026 PTMC project.pptx`; blank section metadata |
| `hybrid + deterministic-test` | PASS | PASS | PASS | PASS | n/a | PASS | 1 | `2026 PTMC project.pptx`; path provenance in `source_file` |

Interpretation:

- `expected_path_context` changed the interpretation correctly.
- The current fixture no longer asks section matching to validate folder provenance.
- No retrieval behavior needed to change for this question under `mvp003`.
- Final classification: `fixed_by_eval_semantics`.

Remaining risk: none for Issue #21 closeout, as long as path context remains separate from chunk-local section semantics.

## Reranker Impact

`deterministic-test` is plumbing-only. It must not be claimed as a quality-improving reranker.

Target-only observations:

- `mvp003 + deterministic-test` keeps overall at 33.3% on the target subset; it does not fix Q001 or Q004 because section match remains false.
- `hybrid + deterministic-test` keeps overall at 100.0% on the target subset, but source @3 drops from 66.7% to 33.3%.

Existing full-fixture MVP-007 Phase 2 evidence also records source @3 regression:

- `mvp003 + deterministic-test`: source @3 delta -3.1 percentage points.
- `hybrid + deterministic-test`: source @3 delta -9.4 percentage points.

Therefore no target question is classified as `fixed_by_reranker`.

## Decision

- Issue #21 close recommendation: YES.
- Reason: all three historical failed questions have clear classifications other than `still_open` or `inconclusive`, supported by reproducible eval output and existing committed MVP-006/MVP-007 reports.
- Follow-up issue needed? NO for Issue #21 closeout.

Recommended close note:

> Issue #21 can close. `MVP0025-Q001` and `MVP0025-Q004` are fixed in accepted `hybrid` comparison mode but remain documented `mvp003` section-locality weaknesses. `MVP0025-Q010` is fixed by current `expected_path_context` semantics. No retrieval behavior or gates were changed.

## Risk / Devil's Advocate

- Risk of overclaiming: high if the result is described as "`mvp003` fixed." It is not. Q001 and Q004 are `hybrid_only`.
- Risk that `hybrid` masks `mvp003` weakness: real. The report separates `mvp003` from `hybrid` and keeps `mvp003` protected.
- Risk that eval semantics are too permissive: low for Q010 because path context is checked only against `source_file`; it does not satisfy section expectations.
- Regression risk: low for this audit because no retrieval code, scoring, chunking, metadata, or eval logic changed.
- Reranker risk: deterministic-test can reorder candidates and hurt source @3. It validates plumbing only and should not be used as a quality-improvement claim.

## Next Action

Close Issue #21 with the decision above. Keep the next substantive retrieval task separate: MVP-007 Phase 3 should define or defer a candidate-preserving reranker strategy that improves ordering without source @3, source @5, section, path-context, priority, evidence-label, or metadata regression.
