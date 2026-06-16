# Regression Tracking Ledger

## Purpose

This ledger tracks historical failed retrieval questions, closeout status, and future regression risk without changing eval fixture semantics.

Do not edit `eval/retrieval_questions.jsonl` or expected-source fixtures from this ledger. Use this file to record interpretation, follow-up, and issue status only.

## Status Legend

| Status | Meaning |
|---|---|
| open | unresolved failure or risk |
| fixed-default | fixed in the protected/default path |
| fixed-comparison | fixed only in comparison mode such as `hybrid` |
| fixed-semantics | fixed by correcting eval semantics or expected path context |
| accepted-limitation | known limitation accepted for current MVP |
| regression | previously passing behavior failed again |

## Historical Failed Questions

| Question ID | Related issue | Expected source | Current disposition | Protected-reference status | Follow-up |
|---|---|---|---|---|---|
| MVP0025-Q001 | #21 | `AGENTS.md` | fixed-comparison | `mvp003` still section-limited; `hybrid` passes | preserve as section-selection regression sentinel |
| MVP0025-Q004 | #21 | `01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf` | fixed-comparison | `mvp003` source pass but section/path fail; `hybrid` passes | preserve as source-vs-section sentinel |
| MVP0025-Q010 | #21 | `01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx` | fixed-semantics | path-context provenance accepted | protect against fake-heading regression |

## Regression Entry Template

| Date | PR | Commit | Question ID | Mode | Before | After | Status | Action |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Rules

- A target-only pass does not prove global retrieval improvement.
- A comparison-mode fix does not mean the protected reference was fixed.
- A fixture semantics correction must explain why the old expectation was wrong.
- Any reappearance of a closed failure should be marked `regression` and linked to a new issue.
- Keep `hybrid` comparison success separate from `mvp003` protected-reference behavior.
