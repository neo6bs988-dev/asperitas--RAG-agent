# Asperitas Agent Development Workflow Playbook

Status: active operating playbook
Repository: `asperitas--RAG-agent`

## Executive Bottom Line

Use one core repository first. Separate agents as modules, configs, tests, and docs. Do not create a separate repository for every agent until the agent becomes independently deployed or needs a separate release boundary.

## Default Workflow

1. ChatGPT: architecture, requirements, agent boundaries, repository structure, implementation prompt, final review.
2. Codex: implementation, tests, verification, evaluation when affected, documentation updates, report.
3. Claude Code: refactor, performance improvement, maintainability, bottleneck removal, follow-up verification.
4. GitHub: code, docs, decision logs, issues, pull requests, and release records.

## Repository Strategy

Shared core modules stay centralized:

- source registry
- metadata schema
- ingestion pipeline
- chunking
- retrieval
- citation handling
- evidence labels
- review gates
- evals
- artifact verification
- decision logs

Agent-specific work is separated by role, config, tests, and docs while reusing the shared core.

## Standard Development Sequence

### A. Architecture Gate

Define objective, MVP stage, agent boundary, expected files, non-goals, tests, evals, verification, and report format.

### B. Codex Gate

Codex must read `AGENTS.md`, inspect existing files before editing, make the smallest safe change, preserve compatibility, add tests for source-code changes, run verification, run retrieval evals if retrieval or chunking changes, and update docs if behavior changes.

### C. Claude Code Gate

Claude Code improves speed, maintainability, modularity, error handling, typing, edge cases, test clarity, and bottlenecks after a working implementation exists.

### D. Final Review Gate

ChatGPT reviews architecture, risk, source-grounding, next MVP, and release readiness.

## Codex Prompt Template

```text
Use AGENTS.md and relevant .agents/skills instructions.

Task:
[precise task]

Context:
- Current repo: asperitas--RAG-agent
- Current MVP stage: [MVP-###]
- Target files: inspect first unless listed below
- Agent boundary: [shared core / workflow / role contract / module]

Constraints:
- Do not delete files.
- Make the smallest safe change.
- Preserve backward compatibility.
- Reuse shared source registry, metadata, RAG, eval, and decision-log modules.
- Add or update tests for source-code changes.
- Run pytest for source-code changes.
- Run artifact verification.
- Run retrieval eval if retrieval, chunking, scoring, metadata, embedding, or answer generation changes.
- Update docs if behavior changes.

Report:
1. objective
2. files changed
3. agent boundary
4. shared modules reused
5. tests run
6. artifact verification
7. retrieval metrics before/after
8. source-grounding review
9. risks/skipped checks
10. next action
```

## Split-to-New-Repository Trigger

Only split an agent into a new repository when independent deployment, external partner use, release divergence, dependency conflict, or monorepo ownership burden makes it necessary.
