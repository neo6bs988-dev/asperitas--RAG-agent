---
name: read-only-audit
description: Use for inspection-only tasks where Codex must analyze repo state, metrics, issues, PRs, or risks without changing files.
---

# Read-Only Audit

## When To Use

- The task asks to inspect, audit, compare, triage, or decide without implementation.
- The user explicitly says read-only, audit-only, no file changes, or no code changes.
- You need to verify repo state before a follow-up implementation task.

## When Not To Use

- The user asks to create or edit files.
- A bugfix or implementation is already authorized.
- A release closeout requires new documentation.

## Required Inputs

- Audit objective.
- Mode, scope, allowed files, forbidden files, and stop rule.
- Required commands, if any.
- Issue, PR, branch, or metric baseline to inspect.

## Workflow Steps

1. Read `AGENTS.md` and the narrowest relevant skill.
2. Inspect `git status --short --branch`.
3. Read only the files needed for the objective.
4. Run only approved read-only commands.
5. Label every metric as `Fresh Run`, `Historical`, or `Not Run`.
6. Report findings, risks, and the next safe action.

## Quality Gates

- No file content is changed.
- No source, test, eval fixture, registry, chunk, CI, or generated artifact is modified.
- Findings cite files, commands, issues, PRs, or observed outputs.
- Historical metrics are not presented as fresh.
- Audit decisions do not silently authorize implementation, fixture edits, generated artifacts, or branch mutation.

## Report Format

- Objective:
- Files inspected:
- Commands run:
- Metrics:
- Findings:
- Risks:
- Decision:
- Next action:

## Failure Conditions

- Any file is edited during a read-only task.
- A metric is reported without a Fresh Run / Historical / Not Run label.
- The audit depends on a missing file, issue, PR, or command and the blocker is not reported.

## Next-Step Recommendation Format

- Recommended mode:
- Target scope:
- Files allowed:
- Stop rule:
