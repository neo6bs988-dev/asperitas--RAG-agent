# Human + Codex Workflow

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This workflow defines durable execution rules. It must not duplicate mutable phase names, commit SHAs, or next-step claims. If an older status table or “next step” conflicts with the canonical roadmap, treat the older wording as historical while preserving its scoped technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

Use this workflow for all Asperitas AI RAG Agent changes. The goal is to keep every change small, verifiable, source-grounded, compliance-aware, and aligned with the benchmark-beating performance doctrine in `README.md` and `AGENTS.md`.

## Current Preflight Overlay

Before editing:

- Risk level: low, medium, or high.
- Changed surface: docs, templates, CI, source code, retrieval, answer generation, compliance/security, evals, trace/logging, schema, or deployment.
- Verification scope: docs sanity, targeted tests, retrieval eval, compliance review, CI review, or release gate.
- Test budget: targeted checks by default; full local suites or broad GitHub Actions expansion only when risk justifies them.
- Metric provenance: label results as `Fresh Run`, `Historical`, or `Not Run`.
- Branch/PR path: use a non-main branch and GitHub PR review for mergeable work.
- Active phase and next action: read from the canonical current-state roadmap and live GitHub evidence.

Operating loop:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

## 1. Clarify Objective

- State the requested outcome in one sentence.
- Identify whether the task is docs, source code, eval, CI, release, compliance, review, or roadmap.
- Identify the active stage from the canonical current-state roadmap rather than from historical phase labels in this file.
- Identify whether retrieval, answer generation, source registry, chunks, evals, compliance, or public/investor claims are affected.
- Confirm constraints around safety, confidentiality, GitHub writes, and production-status claims.

## 2. Select Context

Read the narrowest relevant context:

- Treat ChatGPT / Asperitas Project Chat as the command tower that distilled Deep Research, PDFs, AOS/PRIME doctrine, benchmark doctrine, user memory, and strategy into the current task prompt.
- `README.md` for mission, truth boundary, benchmark doctrine, roadmap, and tool doctrine.
- `AGENTS.md` for agent behavior, stop rules, testing rules, and report format.
- `docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` for live status, bottlenecks, phase order, and next action.
- `docs/AI_DEVELOPMENT_OS.md` for the operating model.
- `docs/QUALITY_GATES.md` for verification scope.
- `docs/AOS_SOURCE_POLICY.md` for source hierarchy and claim rules.
- Historical phase roadmaps only for their scoped contracts and acceptance criteria.
- Relevant `.agents/skills/*/SKILL.md` for specialized workflows.

Do not request all PDFs or Deep Research files by default. Ask only for exact missing source text when source ingestion, source registry status, citation-level evidence, or PDF-derived content is directly required.

If multiple rules apply, use the stricter gate.

## 3. Inspect Before Editing

- Read existing files before modifying them.
- Check tests, eval scripts, docs, and current PR/issue context.
- Identify protected baselines and non-negotiable artifacts.
- Confirm whether the change is docs-only or behavior-changing.
- If the workspace or branch contains unrelated changes, do not stage or overwrite them.

## 4. Plan The Smallest Safe Change

The plan must include:

- files to change;
- files not to change;
- expected behavior impact;
- validation commands or next-best checks;
- retrieval/eval impact;
- compliance/source-grounding impact;
- risk and rollback path.

Avoid source code changes during docs/governance tasks.

## 5. Implement

- Change only files required by the objective.
- Preserve existing behavior unless behavior change is the objective.
- Prefer additive, scoped, reversible changes.
- Do not delete files unless explicitly requested and reference impact is checked.
- Do not relax gates to make checks pass.
- Do not add dependencies, services, endpoints, secrets, generated indexes, or model binaries without approval.

## 6. Validate

Use `docs/QUALITY_GATES.md`.

Docs-only changes may skip pytest and retrieval eval when they do not affect source code, source registry, chunks, retrieval, ranking, scoring, embeddings, vector DB, reranking, answer generation, or eval fixtures. The PR must state this clearly.

Run changed-area verification first. Docs/templates-only work normally uses cheap QA: re-read edited files, check headings/links/paths/code fences, inspect the diff, and run `git diff --check`.

Behavior changes require targeted tests and relevant evals.

## 7. Retrieval And Answer Eval Rules

Run retrieval eval when the change affects:

- ingestion;
- chunking;
- metadata filtering;
- scoring;
- embeddings;
- vector DB behavior;
- hybrid retrieval;
- reranking;
- answer evidence selection;
- answer generation.

Run answer/citation checks when the change affects:

- answer contract;
- citation rendering;
- evidence labels;
- truth/compliance router;
- refusal/escalation behavior;
- unsupported-claim handling.

## 8. Report Metrics

Report only measured metrics. Do not infer wins without evidence.

Required metric report when relevant:

- dataset or fixture;
- command;
- mode or retriever;
- top-k settings;
- before/after metric;
- pass/fail count;
- regressions;
- skipped checks and why;
- decision: pass / conditional pass / fail.

Cache hits are not latency wins unless net runtime improves.

## 9. GitHub PR Flow

- Use a branch, not direct `main`, unless explicitly authorized.
- Review the diff before commit/PR.
- Commit only intended files.
- Use `.github/pull_request_template.md`.
- Keep PRs narrow.
- State truth boundary and validation.
- If CI disconnects or times out, split validation and recover exact evidence.
- Merge only when scope, checks, and residual risks are clear.

Default branch naming:

```text
codex/{short-description}
```

## 10. Merge Decision

A PR may merge when:

- changed files match the objective;
- no unrelated changes are included;
- checks are appropriate for the changed surface;
- no false production-status claim is introduced;
- source-grounding and compliance risks are labeled;
- skipped checks have rationale;
- next step is clear and sourced from the canonical roadmap.

A PR must not merge when:

- pass/fail status is unclear;
- retrieval or answer behavior changed without relevant evals;
- source IDs, priorities, evidence labels, or provenance are dropped;
- docs claim implementation that does not exist;
- secrets, credentials, endpoints, generated indexes, or model binaries are added unexpectedly;
- compliance risk is hidden.

## Required Final Report

Every task must end with:

```text
Changed files:
Verification:
Retrieval metrics:
Compliance/source-grounding review:
Risks or skipped checks:
Recommended next step:
```

## Current Default Next Step

Read the canonical current-state roadmap's `Immediate Next Action` and verify it against live GitHub evidence. Do not use historical issue numbers or phase labels in this workflow as an execution command.
