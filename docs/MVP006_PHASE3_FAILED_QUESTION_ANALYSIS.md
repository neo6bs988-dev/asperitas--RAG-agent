# MVP-006 Phase 3 Failed Question Analysis

Date: 2026-06-16

Related issue: #24

## Decision

Implement a hybrid-only targeted improvement and keep `hybrid` experimental.

`hybrid` now beats the `mvp003` reference on overall and section match without changing `baseline`, `mvp003`, or `vector` behavior.

## Implemented Change

Hybrid now supports same-source section substitution:

- Start from the protected `mvp003` top-k source set.
- Add section-matching chunk candidates from those same protected sources.
- Only allow a substitution when the same-source section candidate has at least 90% of the protected chunk's raw `mvp003` score.
- Preserve source ID, source file, source priority, evidence label, section fields, heading context, embedding metadata, and content hash.

This lets `hybrid` improve section accuracy while preserving source-grounding gates.

## Failed Questions Inspected

| Question ID | Expected source | Expected section | Finding |
|---|---|---|---|
| `MVP0025-Q001` | `AGENTS.md` | `Source Priority Policy` | `mvp003` found `AGENTS.md` in top 5 but selected a wrong-section chunk. Same-source section candidates existed. |
| `MVP0025-Q004` | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf` | `SINGLE SOURCE OF TRUTH` | `mvp003` found the expected source at rank 1 but selected a wrong-section chunk. Same-source section candidates existed. |
| `MVP0025-Q010` | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | `P1_RND_PROJECTS` | Expected source, priority, and evidence were correct at rank 1, but the expected source chunks have no matching section metadata. |

## Failure Taxonomy

`MVP0025-Q001`:

- Candidate collection issue: `mvp003` returns one chunk per source, so `AGENTS.md` was represented by the highest-scoring wrong-section chunk.
- Source registry/path alias issue: multiple P0 prompt/governance sources strongly match source-priority language.
- Safe fix: implemented same-source section substitution in `hybrid`.

`MVP0025-Q004`:

- Candidate collection issue: the expected source ranked first, but source-level de-dup selected a different high-scoring section.
- Scoring weight issue: raw metadata/alias scoring outweighed section locality.
- Safe fix: implemented same-source section substitution in `hybrid`.

`MVP0025-Q010`:

- Chunking/section metadata issue: PPTX chunks from the expected source have blank section metadata.
- Eval fixture ambiguity: `P1_RND_PROJECTS` is a source path/folder signal, not a chunk section.
- Decision: defer. Fixing this through retrieval scoring would weaken the section gate. The safer next step is fixture or metadata review.

## Eval Metrics

Dataset: `eval/retrieval_questions.jsonl`

Top-k: 5

| Mode | Before overall | After overall | Before section | After section |
|---|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 34.4% | 34.4% |
| mvp003 | 90.6% | 90.6% | 90.6% | 90.6% |
| vector | 53.1% | 53.1% | 53.1% | 53.1% |
| hybrid | 90.6% | 96.9% | 90.6% | 96.9% |

Full after metrics:

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector | 53.1% | 56.2% | 59.4% | 59.4% | 59.4% | 53.1% |
| hybrid | 96.9% | 96.9% | 100.0% | 100.0% | 100.0% | 96.9% |

Remaining failed question:

- `MVP0025-Q010`

## Quality Gates

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Results:

- `python -m pytest`: 161 passed
- `python scripts/verify_artifacts.py`: ok; 48 registry records; 2821 chunks; 0 errors; 0 warnings

## Regression Check

No regression in `baseline`, `mvp003`, or `vector`.

Hybrid improved:

- Overall: +6.3 percentage points
- Section match: +6.3 percentage points

Hybrid preserved:

- Source @5: 100.0%
- Source priority: 100.0%
- Evidence label: 100.0%

## Next Task

MVP-006 Phase 4: resolve `MVP0025-Q010` through fixture or metadata review. Decide whether folder/path expectations such as `P1_RND_PROJECTS` should be represented as chunk section metadata, heading context, or a separate path-context eval field.
