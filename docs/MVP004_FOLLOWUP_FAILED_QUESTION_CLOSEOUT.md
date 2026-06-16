# MVP-004 Follow-up Failed Question Closeout

Date: 2026-06-17

Related issue: #21

## Decision

Issue #21 can be closed after this closeout report is reviewed.

The historical MVP-003 failed retrieval questions now have explicit dispositions:

- `MVP0025-Q001`: fixed only in accepted `hybrid` eval mode.
- `MVP0025-Q004`: fixed only in accepted `hybrid` eval mode.
- `MVP0025-Q010`: fixed by the path-context eval semantics correction.

This does not mean `mvp003` has been replaced or silently changed. `mvp003` remains the protected deterministic reference retriever and still shows its known section-selection limitations for Q001 and Q004. `hybrid` remains an accepted comparison mode, not the default.

## Files Inspected

- `AGENTS.md`
- `.agents/skills/asperitas-rag-development/SKILL.md`
- `.agents/skills/retrieval-eval-quality-gate/SKILL.md`
- `.agents/skills/source-grounding-citation/SKILL.md`
- `.agents/skills/performance-optimization-gate/SKILL.md`
- `.agents/skills/mvp-release-manager/SKILL.md`
- `.agents/skills/github-pr-review/SKILL.md`
- `eval/retrieval_questions.jsonl`
- `scripts/run_retrieval_eval.py`
- `docs/MVP006_PHASE3_FAILED_QUESTION_ANALYSIS.md`
- `docs/MVP006_PHASE4_PATH_CONTEXT_DECISION.md`
- `docs/MVP006_PHASE5_HYBRID_GRADUATION_DECISION.md`
- `docs/MVP007_PHASE2_RERANKER_EVAL_REPORT.md`
- GitHub Issue #21 latest handoff comment

## Quality Gates

| Command | Result |
|---|---|
| `python -m pytest` | Passed: 177 tests |
| `python scripts/verify_artifacts.py` | Passed: 48 registry records, 2821 chunks, 0 warnings, 0 errors |
| `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` | Completed |
| `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` | Completed |
| `python scripts/run_retrieval_eval.py --retriever vector --limit 5` | Completed |
| `python scripts/run_retrieval_eval.py --retriever hybrid --limit 5` | Timed out once, then returned no output once; captured rerun completed |
| `python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5` | Returned no output once; captured rerun completed |
| `python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5` | Completed |

The no-output runs did not leave stale Python processes after cleanup. The captured reruns used the same eval command with stdout/stderr capture and produced the metrics below.

## Metrics By Retriever

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 35.5% | 0.0% |
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `vector` | 56.2% | 56.2% | 59.4% | 59.4% | 59.4% | 54.8% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Reranker Eval Impact

`deterministic-test` remains a plumbing-only reranker. It must not be claimed as a quality-improving reranker.

| Base mode | Reranker | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `mvp003` | `deterministic-test` | 93.8% | 93.8% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid` | `deterministic-test` | 100.0% | 87.5% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Ordering impact:

| Base mode | Top-1 changed | Top-3 changed | Top-5 changed | Source @3 delta | Source @5 delta | Overall delta |
|---|---:|---:|---:|---:|---:|---:|
| `mvp003` | 7/32 | 27/32 | 27/32 | -3.1 pp | +0.0 pp | +0.0 pp |
| `hybrid` | 8/32 | 27/32 | 27/32 | -9.4 pp | +0.0 pp | +0.0 pp |

## Historical Failed Question Status

### MVP0025-Q001

Expected source: `AGENTS.md`

Expected section/path context: `Source Priority Policy`

Accepted closeout status: fixed only in `hybrid`.

| Mode | Top result source | Source @5 | Priority | Evidence | Section/path | Overall |
|---|---|---|---|---|---|---|
| `mvp003` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_AOS_v10_3_Universal_AI_Tool_Master_Prompt.md` | Pass | Pass | Pass | Fail | Fail |
| `hybrid` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_AOS_v10_3_Universal_AI_Tool_Master_Prompt.md` | Pass | Pass | Pass | Pass | Pass |
| `mvp003 + deterministic-test` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_Codex_Master_Constitution_DB_Integration_Guide_v1_2.pdf` | Pass | Pass | Pass | Fail | Fail |
| `hybrid + deterministic-test` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_AOS_v10_3_Universal_AI_Tool_Master_Prompt.md` | Pass | Pass | Pass | Pass | Pass |

Interpretation: `mvp003` finds the expected source in top 5 but selects the wrong section. `hybrid` passes because it can add same-source section candidates without relaxing source priority or evidence gates.

### MVP0025-Q004

Expected source: `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`

Expected section/path context: `SINGLE SOURCE OF TRUTH`

Accepted closeout status: fixed only in `hybrid`.

| Mode | Top result source | Source @5 | Priority | Evidence | Section/path | Overall |
|---|---|---|---|---|---|---|
| `mvp003` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf` | Pass | Pass | Pass | Fail | Fail |
| `hybrid` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_Codex_Master_Constitution_DB_Integration_Guide_v1_2.pdf` | Pass | Pass | Pass | Pass | Pass |
| `mvp003 + deterministic-test` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf` | Pass | Pass | Pass | Fail | Fail |
| `hybrid + deterministic-test` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_AOS_v10_3_Master_Format_Advanced_Prompt_Constitution.pdf` | Pass | Pass | Pass | Pass | Pass |

Interpretation: `mvp003` has the expected source at rank 1 but not the expected section. `hybrid` passes by locating a section-matching candidate from the expected source inside top 5.

### MVP0025-Q010

Expected source: `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx`

Expected section/path context: `expected_path_context = P1_RND_PROJECTS`

Accepted closeout status: fixed by fixture/eval semantics.

| Mode | Top result source | Source @5 | Priority | Evidence | Section/path | Overall |
|---|---|---|---|---|---|---|
| `mvp003` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | Pass | Pass | Pass | Pass | Pass |
| `vector` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | Pass | Pass | Pass | Pass | Pass |
| `hybrid` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | Pass | Pass | Pass | Pass | Pass |
| `mvp003 + deterministic-test` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | Pass | Pass | Pass | Pass | Pass |
| `hybrid + deterministic-test` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | Pass | Pass | Pass | Pass | Pass |

Interpretation: `P1_RND_PROJECTS` is folder/path provenance, not chunk-local section structure. The separate `expected_path_context` field fixes the fixture semantics without turning folder names into fake headings.

## Regression Check

- No source code changed.
- No eval fixture changed.
- No retrieval mode changed.
- `baseline`, `mvp003`, `vector`, and `hybrid` remain separately callable.
- `mvp003` remains the protected deterministic reference retriever.
- `hybrid` remains accepted comparison mode, not default.
- No source priority, evidence-label, section, path-context, or metadata gate was relaxed.
- No external dependency, vector DB, API, secret, generated index, model binary, endpoint, or cloud resource was added.

## Risks

- `hybrid` reaches 100.0% on the current 32-question fixture, but the fixture remains small.
- Q001 and Q004 are still useful as reminders that `mvp003` is source-grounded but not always section-optimal.
- The deterministic test reranker preserves source @5 and overall, but lowers source @3. It should remain plumbing-only.
- Future reranker work should not claim improvement unless it beats `mvp003` and `hybrid` without source @3, source @5, priority, evidence, section, path-context, or metadata regression.

## Next Task

MVP-007 Phase 3: define a candidate-preserving reranker strategy or acceptance threshold that can improve top-k ordering without source-grounding regression.

