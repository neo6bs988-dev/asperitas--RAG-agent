---
name: pr-closeout
description: Use after a scoped change is complete to prepare a PR body, closeout note, decision log, and verification summary.
---

# PR Closeout Skill

## Purpose

Turn a completed change into an auditable GitHub PR package.

## Required Inputs

- objective;
- changed files;
- test commands and results;
- eval commands and results if applicable;
- docs or decision logs added;
- risks and skipped checks;
- next recommended MVP.

## Closeout Checklist

1. Confirm changed files are intentional.
2. Confirm no unrelated files were modified.
3. Confirm no destructive changes occurred.
4. Confirm tests are reported.
5. Confirm retrieval metrics are reported or marked not applicable.
6. Confirm source-grounding and no-overclaim review is included.
7. Confirm residual risks and skipped checks are explicit.
8. Confirm next step is concrete.

## PR Body Template

```markdown
## Objective

## Architecture Impact

## Files Modified

## Tests Executed

## Metrics Before

## Metrics After

## Compliance / Source-Grounding Review

## Risks

## Remaining Gaps

## Recommended Next MVP
```

## Decision Log Rule

Add a decision log when the change affects architecture, MVP status, source governance, eval policy, audit behavior, security behavior, or development workflow.
