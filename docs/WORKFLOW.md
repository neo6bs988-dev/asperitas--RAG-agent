# Human + Codex Workflow

## Current Execution Authority (2026-07-11)

Use [`docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) as the authoritative current-status and forward-performance control plane. For files already inside `docs/`, the path refers to `CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` in the same directory.

Latest confirmed baseline before this documentation sync:

- `main`: `1e437c4515cc664f6acdb6e5bb197aaf576d34af`;
- PR #166 guard hardening: merged after CI #250 and Quality Gates #381 succeeded;
- V1.10B diagnostic answer-sample reporting: merged;
- V1.10C preflight: merged;
- V1.10C six-file implementation: preserved locally and pending publication; not on `main`.

If an older status table or “next step” conflicts with the current-state roadmap, treat the older status wording as historical. Preserve its technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

Current mandatory sequence:

```text
V1.10C publication
-> V1.10 closure
-> representative biology/compliance eval reset
-> retrieval and reranker hardening
-> real grounded answer path and diagnostic verifier
-> compliance/security adversarial gates
-> trace, latency, token, and cost control plane
-> internal dogfood
-> approved data flywheel
-> web productization and production-readiness gates
```


Use this workflow for all Asperitas AI RAG Agent changes. The goal is to keep every change small, verifiable, source-grounded, compliance-aware, and aligned with the benchmark-beating performance doctrine in `README.md` and `AGENTS.md`.

## V1.5A Preflight Overlay

For V1.5 and later tasks, perform this preflight before editing:

- Risk level: low, medium, or high.
- Changed surface: docs, templates, CI, source code, retrieval, answer generation, compliance/security, or evals.
- Verification scope: docs sanity, targeted tests, retrieval eval, compliance review, CI review, or release gate.
- Test budget: targeted checks by default; full local suites or broad GitHub Actions expansion only when risk justifies them.
- Metric provenance: label results as `Fresh Run`, `Historical`, or `Not Run`.
- Branch/PR path: use a non-main branch and GitHub PR review for mergeable work.

V1.5A operating loop:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

## 1. Clarify Objective

- State the requested outcome in one sentence.
- Identify whether the task is docs, source code, eval, CI, release, compliance, review, or roadmap.
- Identify the active stage: V1.5 gap closure/performance hardening unless a later merged roadmap says otherwise.
- Identify whether retrieval, answer generation, source registry, chunks, evals, compliance, or public/investor claims are affected.
- Confirm constraints around safety, confidentiality, GitHub writes, and production-status claims.

## 2. Select Context

Read the narrowest relevant context:

- Treat ChatGPT / Asperitas Project Chat as the command tower that distilled Deep Research, PDFs, AOS/PRIME doctrine, benchmark doctrine, user memory, and strategy into the current task prompt.
- `README.md` for mission, truth boundary, benchmark doctrine, roadmap, and tool doctrine.
- `AGENTS.md` for agent behavior, stop rules, testing rules, and report format.
- `docs/AI_DEVELOPMENT_OS.md` for the operating model.
- `docs/QUALITY_GATES.md` for verification scope.
- `docs/AOS_SOURCE_POLICY.md` for source hierarchy and claim rules.
- `docs/V1_5_PERFORMANCE_ROADMAP.md` for current performance priorities.
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
- Do not delete files unless explicitly requested.
- Do not relax gates to make checks pass.
- Do not add dependencies, services, endpoints, secrets, generated indexes, or model binaries without approval.

## 6. Validate

Use `docs/QUALITY_GATES.md`.

Docs-only changes may skip pytest and retrieval eval when they do not affect source code, source registry, chunks, retrieval, ranking, scoring, embeddings, vector DB, reranking, answer generation, or eval fixtures. The PR must state this clearly.

For V1.5A+, run changed-area verification first. Docs/templates-only work normally uses cheap QA: re-read edited files, check headings/links/paths/code fences, inspect the diff, and run `git diff --check`.

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
- next step is clear.

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

After this documentation sync, continue with V1.5 Gap Closure:

1. confirm docs/PR template/quality gates are aligned;
2. add or update issue/milestone templates if missing;
3. split slow validation into targeted CI jobs;
4. implement claim-to-citation verifier planning;
5. define biology-specific golden set scope.
