---
name: mvp-release-manager
description: Use when closing an MVP stage, preparing a release note, or deciding the next MVP task for asperitas-agent.
---

# MVP Release Manager

## When To Use

- Closing an MVP stage.
- Preparing release notes.
- Deciding whether the next task should stay in the current MVP or move forward.
- Summarizing tests, evals, risks, and acceptance criteria for a milestone.

## When Not To Use

- Small implementation tasks that do not affect milestone status.
- Raw retrieval metric analysis before eval interpretation.
- Compliance review before risk classification is complete.

## Required Inputs

- Current MVP stage.
- Roadmap entry.
- Changed files and feature summary.
- Test and eval results.
- Known risks, blockers, and deferred work.
- Acceptance criteria.

## Workflow Steps

1. Identify current MVP and target release state.
2. Compare completed work against acceptance criteria.
3. Verify tests, retrieval evals, citation checks, and compliance checks.
4. List open risks and deferred tasks.
5. Decide release status: ready, conditional, or blocked.
6. Draft release note.
7. Recommend next MVP task.

## Quality Gates

- Acceptance criteria are explicit.
- Tests and evals are summarized.
- Compliance and source-grounding status are included.
- Deferred work is not hidden.
- Release decision is clear.

## Report Format

- MVP:
- Release decision:
- Completed:
- Verification:
- Metrics:
- Risks:
- Deferred:
- Release note:
- Next MVP task:

## Failure Conditions

- MVP is marked complete without acceptance criteria.
- Metrics or validation are claimed without evidence.
- Compliance or source-grounding gaps are ignored.
- Deferred work is described as complete.

## Next-Step Recommendation Format

- Next MVP:
- Next task:
- Acceptance criterion:
- Required gate:

