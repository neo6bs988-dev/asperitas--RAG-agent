---
name: pr-closeout-report
description: Use before closing a PR or handing off for review so files, commands, metrics, skipped gates, risks, and next action are explicit.
---

# PR Closeout Report

## When To Use

- Before creating, updating, or handing off a PR.
- Before reporting a branch as ready for review.
- When a task needs a concise closeout with changed files, checks, risks, and next action.

## When Not To Use

- Early exploration before the change scope is known.
- Read-only audit with no PR or branch handoff.
- Release decision that needs the MVP release manager first.

## Required Inputs

- Branch and target branch.
- Issue or PR number.
- Changed files and diff summary.
- Commands run and results.
- Metrics labeled Fresh Run / Historical / Not Run.
- Skipped checks and reasons.

## Workflow Steps

1. Inspect `git status --short --branch`.
2. Inspect `git diff --stat` and the changed file list.
3. Confirm the diff matches the requested mode and scope.
4. Confirm forbidden file classes were not changed.
5. Confirm governance-only PRs are isolated from source, retrieval, performance, fixture, CI, and generated-artifact changes.
6. Summarize tests, evals, artifact checks, and skipped gates.
7. State risks, rollback path if relevant, and next action.

## Quality Gates

- Scope matches the task.
- Required commands are reported.
- Skipped gates are explicit.
- No source code changed for docs-only PRs.
- No secrets, endpoints, generated indexes, or confidential content are added.
- Metrics are labeled `Fresh Run`, `Historical`, or `Not Run`.

## Report Format

- Executive bottom line:
- Branch:
- Issue/PR:
- Files changed:
- Commands run:
- Metrics:
- Skipped checks:
- Risk check:
- Review focus:
- Next action:

## Failure Conditions

- PR closeout omits changed files or commands.
- A metric is reported without provenance.
- Skipped tests/evals are hidden.
- The diff includes unrelated or forbidden files.

## Next-Step Recommendation Format

- Recommended PR action:
- Required reviewer focus:
- Merge blocker:
- Follow-up issue:
