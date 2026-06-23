# Codex Task Prompts

Use these prompts to keep Codex work small, verifiable, and aligned with the repository operating system.

## Mandatory Task Header

Use this header for future Codex implementation, audit, closeout, and governance tasks.

```text
Mode:
Scope:
Files allowed:
Files forbidden:
Fresh metrics required: yes/no
Tests required: yes/no
Retrieval eval required: yes/no
Clean branch/worktree required: yes/no
Decision log required: yes/no
Stop rule:
```

Default governance stance: source-grounded, deterministic where possible, JSON-auditable for machine-read logs, and fail-closed for quality gates that protect source priority, evidence labels, section/path-context, metadata, compliance, or safety.

## Compact Recurring Templates

### Read-Only Audit

```text
Use AGENTS.md and .agents/skills/read-only-audit/SKILL.md.

Mode: read-only audit
Scope: [repo area / issue / PR / metric]
Files allowed: none
Files forbidden: all file modifications
Fresh metrics required: yes/no
Tests required: no
Retrieval eval required: yes/no
Stop rule: stop after findings, risks, decision, and next action.

Task:
[audit objective]

Report:
1. Objective
2. Files inspected
3. Commands run
4. Metrics labeled Fresh Run / Historical / Not Run
5. Findings
6. Risks
7. Decision
8. Next action
```

### Implementation Task

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Mode: implementation
Scope: [smallest safe behavior change]
Files allowed: [explicit file list or "inspect first"]
Files forbidden: [source/test/eval/CI/artifacts as applicable]
Fresh metrics required: yes/no
Tests required: yes/no
Retrieval eval required: yes/no
Stop rule: stop if required precondition, file, test, or eval gate is missing.

Task:
[implementation objective]

Report:
1. Objective
2. Files changed
3. Tests run
4. Artifact verification
5. Retrieval metrics, if required
6. Regression check
7. Risks
8. Next task
```

### Retrieval Regression

```text
Use AGENTS.md and .agents/skills/retrieval-regression-closeout/SKILL.md.

Mode: retrieval regression closeout
Scope: [question IDs / retriever modes]
Files allowed: docs/report only unless implementation is explicitly approved
Files forbidden: source/test/eval fixtures unless the task authorizes them
Fresh metrics required: yes
Tests required: no unless code changes
Retrieval eval required: yes
Stop rule: do not relax source priority, evidence-label, section, path-context, or metadata gates.

Task:
[regression closeout objective]

Report:
1. Commands run
2. Metrics by retriever
3. Question status
4. Failure taxonomy
5. Regression check
6. Decision
7. Next action
```

### Artifact Verification

```text
Use AGENTS.md and docs/QUALITY_GATES.md.

Mode: artifact verification
Scope: [artifact paths]
Files allowed: none unless the task explicitly permits corrections
Files forbidden: source, tests, eval fixtures, CI, registry, chunks, generated artifacts
Fresh metrics required: no
Tests required: no
Retrieval eval required: no
Stop rule: stop after existence, path, schema, and risk checks.

Task:
Verify the requested artifacts and report drift or missing files.

Report:
1. Artifacts inspected
2. Verification method
3. Findings
4. Risks
5. Next action
```

### Bugfix

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Mode: bugfix
Scope: [specific failing behavior]
Files allowed: [affected source and tests]
Files forbidden: unrelated source, eval fixtures, CI, registry, chunks, generated artifacts
Fresh metrics required: yes if behavior is measured
Tests required: yes
Retrieval eval required: yes if retrieval, metadata, reranking, or answer evidence selection changes
Stop rule: stop if the failure cannot be reproduced or the safe fix scope is unclear.

Task:
[bug and expected behavior]

Report:
1. Root cause
2. Files changed
3. Tests added/updated
4. Commands run
5. Regression check
6. Risks
7. Next action
```

### PR Closeout

```text
Use AGENTS.md, .agents/skills/github-pr-review/SKILL.md, and .agents/skills/pr-closeout-report/SKILL.md.

Mode: PR closeout
Scope: [branch / issue / PR]
Files allowed: none unless final docs correction is explicitly needed
Files forbidden: unrelated source, tests, eval fixtures, CI, registry, chunks, generated artifacts
Fresh metrics required: yes/no
Tests required: yes/no
Retrieval eval required: yes/no
Stop rule: stop if changed files, commands, metrics, or skipped gates cannot be verified.

Task:
Prepare closeout report for review.

Report:
1. Executive bottom line
2. Branch
3. Files changed
4. Commands run
5. Metrics labeled Fresh Run / Historical / Not Run
6. Skipped checks
7. Risks
8. Review focus
9. Next action
```

### Failure Taxonomy Update

```text
Use AGENTS.md and the relevant quality-gate skill.

Mode: failure taxonomy update
Scope: [failure IDs / affected gate]
Files allowed: docs/report only unless explicitly approved
Files forbidden: source, tests, eval fixtures, CI, registry, chunks, generated artifacts
Fresh metrics required: no unless reclassifying active behavior
Tests required: no unless code changes
Retrieval eval required: yes if retrieval behavior is being reclassified from fresh runs
Stop rule: do not relabel a failure as fixed without evidence.

Task:
[taxonomy update objective]

Report:
1. Failure IDs
2. Evidence inspected
3. Classification
4. Metrics provenance
5. Risks
6. Decision
7. Next action
```

### Docs-Only Update

```text
Use AGENTS.md and .agents/skills/docs-only-governance-update/SKILL.md.

Mode: docs-only / skills-only / governance update
Scope: [docs and skill files]
Files allowed: docs/**, .agents/skills/**
Files forbidden: source, tests, eval fixtures, registry, chunks, embeddings, vector data, generated artifacts, CI
Fresh metrics required: no
Tests required: no
Retrieval eval required: no
Clean branch/worktree required: yes
Decision log required: yes if the task closes an MVP, PR, performance phase, or quality-gate decision
Stop rule: stop if a source, test, eval, CI, registry, chunk, or generated artifact change is needed.

Task:
[docs-only objective]

Report:
1. Executive bottom line
2. Files changed
3. What changed
4. Verification performed
5. Tests/evals skipped and why
6. Risks
7. Next recommended step
```

## Decision Log Schema Note

Future decision entries must include date, task, issue/PR, files changed or inspected, commands, metrics, risks, decision, and next action. Each metric must be labeled `Fresh Run`, `Historical`, or `Not Run`.

Decision logs are append-only and should be JSON-auditable when the log target supports structured records. Do not overwrite historical logs. `00_ADMIN/decision_log.md` currently has a binary-content signature; flag that anomaly as a risk, but do not delete, rewrite, convert, or repair it unless explicitly approved.

## Universal Task Prompt

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
[write the exact objective]

Context:
- Current repo: asperitas--RAG-agent
- Current MVP stage: [MVP-004 / MVP-005 / etc.]
- Target files: [list if known; otherwise inspect first]

Constraints:
- Do not delete files.
- Make the smallest safe change.
- Preserve backward compatibility.
- Add or update tests for source code changes.
- Run pytest for source code changes.
- Run artifact verification for generated artifacts.
- Run retrieval eval if retrieval/chunking/scoring/answer generation is affected.
- Update docs if behavior, commands, or workflow changes.

Report:
1. Objective
2. Files changed
3. Tests run
4. Artifact verification
5. Retrieval metrics before/after
6. Compliance/source-grounding impact
7. Risks or skipped checks
8. Next recommended task
```

## Docs-Only Governance Prompt

```text
Use AGENTS.md and .agents/skills/github-pr-review/SKILL.md.

Task:
Update governance or workflow documentation only.

Constraints:
- Do not modify source code.
- Do not modify tests.
- Do not claim that a pipeline is implemented unless an executable file exists.
- Re-read every edited document before reporting done.

Report:
- Files changed
- What changed
- Verification performed
- Skipped checks and why
- Next operational improvement
```

## MVP-004 Retrieval/Chunking Prompt

```text
Use AGENTS.md, .agents/skills/asperitas-rag-development/SKILL.md, and .agents/skills/retrieval-eval-quality-gate/SKILL.md.

Task:
[describe MVP-004 chunking/retrieval objective]

Required commands:
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5

Acceptance:
- No test failure.
- Artifact verification is ok.
- No unexplained source/evidence regression.
- Section metadata behavior is explicitly reported.

Report using docs/MVP004_BASELINE_METRICS.md format.
```

## Source-Grounded Answer Prompt

```text
Use AGENTS.md and .agents/skills/source-grounding-citation/SKILL.md.

Task:
Implement or review source-grounded answer behavior.

Constraints:
- Every material claim must trace to a source ID.
- Unsupported claims must be removed or labeled.
- Evidence labels and source priority must survive formatting.
- Insufficient evidence must produce an explicit uncertainty response.

Report:
- Affected answer path
- Citation behavior
- Unsupported-claim handling
- Tests/checks
- Residual hallucination risk
```

## Compliance/Biosafety Prompt

```text
Use AGENTS.md and .agents/skills/compliance-biosafety-review/SKILL.md.

Task:
Review the change for biological, biodiversity, regulatory, privacy, IP, legal, investor, or public-communication risk.

Report:
- Risk domain
- Severity
- Evidence reviewed
- Missing approvals
- Decision: clear / mitigate / block / escalate
- Safe next action
- Human approval needed
```

## MVP Release Prompt

```text
Use AGENTS.md and .agents/skills/mvp-release-manager/SKILL.md.

Task:
Decide whether [MVP-X] can close.

Inputs:
- Roadmap entry
- Changed files
- Commands run
- Test/eval results
- Acceptance criteria
- Known risks

Report:
- Release decision: ready / conditional / blocked
- Completed work
- Verification evidence
- Metrics
- Deferred tasks
- Release note
- Next MVP task
```

## Recovery Prompt After Codex Stops

```text
Resume the previous Codex task in this repository.

First:
1. Inspect git status and changed files.
2. Read AGENTS.md and relevant skills.
3. Identify whether the previous task was docs, source code, eval, compliance, or release.
4. Do not continue blindly.

Then report:
- What appears complete
- What appears incomplete
- Whether source code changed
- Which checks must run next
- The safest next command or patch
```
