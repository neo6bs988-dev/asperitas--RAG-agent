# Human + Codex Workflow

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This workflow document defines durable execution rules. It must not duplicate mutable phase names, commit SHAs, or next-step claims. Older phase references in historical documents remain historical and cannot override the canonical roadmap.

Use this workflow for all Asperitas AI RAG Agent changes. The goal is to keep every change small, verifiable, source-grounded, compliance-aware, and aligned with the benchmark-beating performance doctrine in `README.md` and `AGENTS.md`.

## Current Execution Preflight

Before editing, record:

- Risk level: low, medium, or high.
- Changed surface: docs, templates, CI, source code, retrieval, answer generation, compliance/security, evals, trace/logging, schema, or deployment.
- Active phase: read from the canonical current-state roadmap rather than from this file.
- Verification scope: docs sanity, targeted tests, retrieval eval, compliance review, CI review, or release gate.
- Test budget: targeted checks by default; full local suites or broad GitHub Actions expansion only when risk justifies them.
- Metric provenance: label results as `Fresh Run`, `Historical`, or `Not Run`.
- Branch/PR path: use a non-main branch and GitHub PR review for mergeable work.

Operating loop:

```text
Scope Lock
-> Source and Risk Preflight
-> Contract Design
-> Minimal Implementation
-> Cheap QA
-> Targeted Verification
-> GitHub PR
-> GitHub Actions
-> Human Review
-> Merge
-> Evidence Log
-> Learn Back
```

## 1. Clarify Objective

- State the requested outcome in one sentence.
- Identify whether the task is docs, source code, eval, CI, release, compliance, review, roadmap, or productization.
- Read the active stage and immediate next action from the canonical current-state roadmap.
- Identify whether retrieval, answer generation, source registry, chunks, evals, compliance, security, or public/investor claims are affected.
- Confirm constraints around safety, confidentiality, GitHub writes, and production-status claims.

## 2. Select Context

Read the narrowest relevant context:

- ChatGPT / Asperitas Project Chat for distilled Deep Research, PDFs, AOS/PRIME doctrine, benchmark doctrine, user memory, and strategy.
- `README.md` for mission, truth boundary, benchmark doctrine, and architecture direction.
- `AGENTS.md` for agent behavior, stop rules, testing rules, and report format.
- `docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` for live status and next phase.
- `docs/AI_DEVELOPMENT_OS.md` for the operating model.
- `docs/QUALITY_GATES.md` for verification scope.
- `docs/AOS_SOURCE_POLICY.md` for source hierarchy and claim rules.
- Relevant `.agents/skills/*/SKILL.md` for specialized workflows.

Do not request all PDFs or Deep Research files by default. Ask only for exact missing source text when source ingestion, source registry status, citation-level evidence, or PDF-derived content is directly required.

If multiple rules apply, use the stricter gate.

## 3. Inspect Before Editing

- Read existing files before modifying them.
- Check tests, eval scripts, docs, current PRs/issues, and `git status`.
- Identify the smallest cohesive diff and its blast radius.
- Preserve user changes and unrelated worktrees.
- Confirm rollback before mutation.

## 4. Implement the Smallest Sufficient Change

Use this architecture ladder:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

Do not add frameworks, services, dependencies, vector backends, KGs, agent runtimes, or autonomous execution without a documented simpler-pattern failure, expected metric gain, security/cost impact, evaluation evidence, and rollback.

## 5. Verify by Risk

- Docs-only: path/link checks, Markdown fences, stale-status scan, secret scan, and `git diff --check`.
- Tests/schema/eval: targeted tests, contract checks, deterministic outputs, artifact verification, and compile checks.
- Retrieval/ranking: before/after retrieval metrics, metadata preservation, leakage review, latency/token impact, and rollback.
- Runtime/answer/compliance/security: targeted and adversarial tests, trace/eval evidence, human approval boundaries, and expanded CI as justified.
- Release or core pipeline: full suite or equivalent clean-environment GitHub gate when risk warrants it.

Skipped checks must include rationale and residual risk.

## 6. Publish and Merge

```text
branch
-> targeted local validation
-> commit and push
-> Draft PR
-> exact-head GitHub Actions
-> review
-> ready-for-review
-> merge
-> post-merge verification
-> decision/release log
```

Do not merge when pass/fail status is unclear. Do not bypass required review, required checks, branch protection, or security/compliance gates.

## 7. Evidence Contract

Every significant final report must include:

- changed files;
- validation commands and results;
- skipped tests and rationale;
- metric provenance;
- security/confidentiality review;
- residual risks;
- rollback path;
- PR and merge SHAs;
- exactly one next action from the canonical roadmap.
