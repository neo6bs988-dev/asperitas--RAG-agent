# Pipeline Automation

This document upgrades the Asperitas RAG workflow from static governance into executable quality gates.

## Automation Layers

| Layer | Purpose | Current Mechanism |
|---|---|---|
| Local developer loop | Fast feedback before commit | shell commands from `docs/MVP004_BASELINE_METRICS.md` |
| Codex task loop | Make agents follow repo rules | `AGENTS.md` + `.agents/skills/*/SKILL.md` |
| CI quality gate | Run repeatable checks on push/PR | `.github/workflows/quality-gates.yml` |
| PR review gate | Make review scope explicit | `.github/pull_request_template.md` |
| MVP release gate | Decide whether to close a milestone | `.agents/skills/mvp-release-manager/SKILL.md` |

## Local Quality Pipeline

Run this before committing source-code, retrieval, chunking, schema, or eval changes:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Docs-only changes do not need pytest or retrieval eval, but they must satisfy artifact verification by human review: correct path, required sections, no broken governance references, no false implementation claims.

## CI Quality Pipeline

The GitHub Actions workflow should run on:

- push to `main`
- pull request to `main`
- manual dispatch

The CI gate must install the project, run unit tests, run artifact verification, audit chunk sections, and run deterministic retrieval evals.

CI is not a substitute for human review. It only confirms that the executable gates still run.

## PR Review Pipeline

Before merge, reviewers must check:

1. Scope matches objective.
2. Source code changes include tests.
3. Retrieval or chunking changes include eval output.
4. Biological/compliance changes include risk classification.
5. Docs match implemented behavior.
6. No secrets, credentials, private contact data, or unapproved confidential content were added.

## MVP Release Pipeline

Use the MVP release manager skill when closing a milestone.

Required release evidence:

- changed files
- acceptance criteria
- commands run
- test result
- artifact verification result
- retrieval metrics if applicable
- compliance/source-grounding review
- deferred risks
- next MVP task

## Escalation Rules

Escalate to human decision if:

- compliance risk is unclear;
- a metric regresses but the model suggests proceeding;
- source hierarchy or evidence labels are changed;
- a task requires deletion of source, tests, evals, registry, or governance files;
- a generated claim would be investor-facing, partner-facing, public, or regulatory-facing.

## Next Automation Targets

1. Add machine-readable eval output artifacts in CI.
2. Add a threshold checker that fails CI on hard regressions.
3. Add release notes under `09_LOGS/decision_logs/` for each MVP closure.
4. Add branch protection so `main` requires the quality-gates workflow.
5. Add separate workflows for heavy embeddings/vector DB checks when MVP-005 begins.