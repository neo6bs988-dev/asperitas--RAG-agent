# AI Development Runbook

Status: docs-only operating runbook

Related issue: #96

## Objective

Define the standard AI-assisted development loop for Asperitas work using ChatGPT, Codex, Claude Code, GitHub, and future gstack skills while preserving product runtime behavior and Asperitas truth rules.

## Operating Principles

- Treat ChatGPT and Codex as planning and implementation agents, not source-of-truth authorities.
- Treat gstack as development methodology until installed and verified.
- Preserve `AGENTS.md`, AOS, PRIME, source hierarchy, evidence labels, and compliance gates.
- Keep each task small, reviewable, reversible, and tied to GitHub evidence.
- Do not mutate retrieval, answer generation, source registry, chunks, release artifacts, or tests for docs-only work.

## Standard Loop

Use this loop for meaningful development tasks:

1. ChatGPT scope.
2. `/office-hours`.
3. `/autoplan`.
4. `/plan-eng-review`.
5. Codex implementation.
6. `/review`.
7. `/cso`.
8. `/qa`.
9. `/ship`.
10. `/document-release`.
11. `/retro`.
12. GitHub evidence.

Until gstack is installed, slash-command names are role labels and checklist phases.

## Phase Guide

### 1. ChatGPT Scope

Capture:

- role;
- goal;
- success criteria;
- constraints;
- changed surfaces;
- non-goals;
- validation commands;
- PR and issue link requirements.

For Asperitas, scope must explicitly state whether the task is docs-only, runtime code, retrieval logic, compliance-sensitive, release-related, or public-facing.

### 2. `/office-hours`

Challenge the problem framing before editing.

Expected output:

- user-visible outcome;
- narrowest useful change;
- missing evidence;
- compliance and confidentiality concerns;
- whether the task strengthens Biological Intelligence Factory goals.

### 3. `/autoplan`

Produce a concise implementation plan.

Expected output:

- files expected to change;
- files explicitly out of scope;
- validation plan;
- rollback plan;
- risk and assumption list.

### 4. `/plan-eng-review`

Review the plan as an engineering gate.

Confirm:

- no hidden runtime behavior change;
- no artifact mutation unless requested;
- tests/evals match changed surface;
- source/truth boundary is preserved;
- dependencies and commands are available.

### 5. Codex Implementation

Implement only the approved scope.

Rules:

- read existing files before editing;
- make small focused changes;
- preserve user work;
- add tests for code changes;
- avoid unrelated refactors;
- use docs-only edits for docs-only tasks.

### 6. `/review`

Review the diff before validation.

Check:

- changed files match scope;
- no non-doc runtime files changed for docs-only work;
- links and commands are accurate;
- no overclaim or unsupported status language;
- no secrets, credentials, confidential details, or private personal data added.

### 7. `/cso`

Run a security and compliance review appropriate to the changed surface.

For Asperitas, this includes:

- confidentiality;
- IP and licensing;
- CITES, Nagoya, LMO, biosafety, and biosecurity triggers;
- investor/public communication risk;
- claims of validation, deployment, traction, or production readiness.

### 8. `/qa`

Run the lightest validation that protects the changed surface.

Docs-only minimum:

```bash
git diff --check
python scripts/verify_artifacts.py
```

Source-code minimum:

```bash
python -m pytest
python scripts/verify_artifacts.py
```

Release-readiness escalation:

```bash
python scripts/check_v1_release_readiness.py --json
python scripts/run_v1_rc_smoke.py --json
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
```

Retrieval or answer-generation changes require the retrieval evaluation workflow defined in `docs/QUALITY_GATES.md`.

### 9. `/ship`

Prepare GitHub evidence.

Required PR body sections:

- objective and issue reference;
- changed files;
- commands run;
- validation results;
- retrieval metrics if applicable;
- compliance/source-grounding review;
- risks and rollback;
- GO/NO-GO recommendation.

### 10. `/document-release`

Use this phase only when behavior, release evidence, commands, or user-facing workflows changed.

For docs-only operating-stack tasks, do not update release artifacts unless the task explicitly asks for release-evidence changes.

### 11. `/retro`

Record lessons that improve future agent performance:

- which phase caught the most risk;
- which checks were skipped and why;
- which custom Asperitas skill would have helped;
- whether required mode is still premature.

### 12. GitHub Evidence

Every PR should reference its issue and preserve enough evidence for review:

- branch name;
- diff summary;
- validation output;
- skipped checks;
- risk/rollback;
- next action.

## Gate Selection

Use `docs/QUALITY_GATES.md` as the canonical gate selector.

Docs-only tasks:

- `git diff --check`;
- artifact verification;
- no-runtime-file confirmation;
- PR review.

Retrieval, chunking, metadata, vector DB, reranking, or answer-generation tasks:

- `python -m pytest`;
- `python scripts/verify_artifacts.py`;
- chunk audit;
- retrieval evals;
- before/after metrics.

Release tasks:

- full release-readiness script;
- smoke tests;
- release evidence docs;
- human approval before tag or GitHub release.

## Stop Rules

Stop and escalate when:

- a docs-only task appears to require runtime changes;
- gstack guidance conflicts with Asperitas governance;
- validation cannot run and no safe substitute exists;
- a claim would imply production RAG/KG/eval/compliance/wet-lab completion;
- public or investor-facing claims lack source support.
