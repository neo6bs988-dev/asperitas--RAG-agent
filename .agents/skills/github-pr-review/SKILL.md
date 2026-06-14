---
name: github-pr-review
description: Use before commits, pushes, pull requests, and merge decisions in the asperitas-agent repository.
---

# GitHub PR Review

## When To Use

- Before commit, push, PR creation, PR update, or merge decision.
- When reviewing changed files for scope, tests, evals, secrets, or governance fit.
- When preparing a PR summary.

## When Not To Use

- Early design brainstorming before files change.
- Retrieval metric analysis that needs the retrieval-eval-quality-gate skill first.
- Compliance analysis that needs the compliance-biosafety-review skill first.

## Required Inputs

- Branch name and target branch.
- Changed files.
- Diff summary.
- Test and eval results.
- Known risks and skipped checks.

## Workflow Steps

1. Inspect `git status`.
2. Inspect changed files and diff.
3. Confirm scope matches the objective.
4. Confirm source code was not changed for docs-only tasks.
5. Confirm tests, evals, docs, and compliance gates are complete.
6. Check for secrets, credentials, or confidential content.
7. Prepare commit message and PR summary.

## Quality Gates

- Diff is reviewed.
- Unrelated files are excluded.
- Required tests and evals are reported.
- No destructive or secret-bearing change is included.
- PR summary states risks and next review focus.

## Report Format

- Branch:
- Changed files:
- Scope check:
- Tests/evals:
- Risk check:
- Commit message:
- PR summary:
- Merge recommendation:

## Failure Conditions

- Diff contains unrelated changes.
- Source code changed during docs-only work.
- Tests or evals are missing without explanation.
- Secrets or confidential data are present.
- Merge recommendation ignores known failures.

## Next-Step Recommendation Format

- Next GitHub action:
- Target branch:
- Required reviewer focus:
- Blocker:

