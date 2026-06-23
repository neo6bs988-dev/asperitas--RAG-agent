---
name: docs-only-governance-update
description: Use for additive governance, workflow, prompt, or skill updates that must not change source, tests, eval fixtures, CI, registry, chunks, or generated artifacts.
---

# Docs-Only Governance Update

## When To Use

- The task is limited to docs, governance, workflow, prompts, or skills.
- The user forbids source, test, eval, CI, registry, chunk, embedding, vector, or generated artifact changes.
- You need to add reusable operating instructions.

## When Not To Use

- Source code behavior must change.
- Tests or eval fixtures must change.
- CI behavior must change.
- Generated artifacts must be regenerated.

## Required Inputs

- Mode and scope.
- Files allowed and files forbidden.
- Whether fresh metrics, tests, or retrieval evals are required.
- Stop rule.
- Required report format.

## Workflow Steps

1. Inspect `git status --short --branch`.
2. Read existing docs and skills before editing.
3. Start from a clean branch or explicitly isolate pre-existing dirty governance edits before staging.
4. Make additive, focused changes only.
5. Do not rewrite `AGENTS.md` wholesale.
6. Re-read every changed file.
7. Run `git diff --check` and inspect `git diff --stat`.
8. Confirm forbidden file classes were not touched.
9. Report skipped tests and evals as skipped because the task was docs/skills-only.

## Quality Gates

- Changed files are limited to allowed docs or skill paths.
- No source, tests, eval fixtures, CI, registry, chunk, embedding, vector data, or generated artifacts changed.
- New skills include YAML frontmatter.
- Instructions are operational, specific, and reusable.
- Governance PRs are not mixed with retrieval, performance, fixture, or generated-artifact changes.

## Report Format

- Executive bottom line:
- Files changed:
- What changed:
- Verification performed:
- Tests/evals skipped:
- Risks:
- Next recommended step:

## Failure Conditions

- Source, tests, eval fixtures, CI, registry, chunks, embeddings, vector data, or generated artifacts changed.
- A historical metric is described as a fresh run.
- Tests or evals are claimed without being run.
- Governance text creates a new behavior requirement that conflicts with existing constraints.

## Next-Step Recommendation Format

- Next task:
- Mode:
- Scope:
- Required gates:
- Stop rule:
