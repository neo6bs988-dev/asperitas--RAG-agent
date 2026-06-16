# Codex OPS Prompt Templates

## 1. Preflight Only

Use this before any workflow, audit, or behavior-sensitive implementation.

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
Preflight the requested task. Do not edit files yet.

Context:
- Repository: neo6bs988-dev/asperitas--RAG-agent
- Default branch: main
- Current task:
- Related issue/PR:

Hard constraints:
- Do not change retrieval behavior unless explicitly authorized.
- Do not change scoring, chunking, reranking, metadata semantics, source registry, ingestion, or eval semantics unless explicitly in scope.
- Preserve `mvp003` protected deterministic reference.
- Keep `hybrid` as accepted comparison mode, not default.
- Keep `deterministic-test` reranker as plumbing-only.
- Do not add external services, paid APIs, cloud dependencies, vector DBs, secrets, or model binaries by default.
- Do not delete files.
- Do not commit.

Inspect and report:
1. current branch / HEAD / git status
2. existing relevant files
3. proposed smallest safe change
4. files to touch and files not to touch
5. verification commands
6. risks and blockers
7. recommendation to proceed or split smaller

Stop after the report.
```

## 2. Docs-Only Workflow Hardening

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
Implement a docs-only workflow hardening change.

Scope:
- Add or update documentation/templates only.
- Do not touch src/, scripts/, data/, eval fixtures, source registry, chunking, scoring, ingestion, reranking, or retrieval behavior.

Verification:
- Run git diff --stat.
- Run python -m pytest if available and cheap.
- Do not run full retrieval eval unless the repo policy requires it for this docs-only change.

Report:
1. objective
2. files changed
3. behavior changed? yes/no
4. tests/checks run
5. skipped checks and reason
6. risks / follow-ups
```

## 3. No-Behavior-Change Audit

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
Perform a no-behavior-change audit.

Hard constraints:
- Do not edit source code.
- Do not edit eval fixtures.
- Do not regenerate artifacts.
- Do not change default retrieval mode.
- Do not change scoring/chunking/reranking/eval semantics.

Audit:
1. inspect related issue/PR/files
2. inspect failed/recovered question IDs if applicable
3. run required checks
4. document close/update/keep-open decision
5. list risks and follow-up issues

Output:
- audit report only
- no source behavior change
```

## 4. Retrieval Behavior PR

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
Implement the explicitly scoped retrieval behavior change.

Required:
- Explain why this is a behavior-changing PR.
- Preserve or explicitly justify any deviation from `mvp003` protected reference.
- Keep `hybrid` non-default unless the issue explicitly authorizes default migration.
- Add/update tests.
- Run pytest, artifact verification, and full retrieval eval.
- Report before/after metrics and regressed question IDs.

Stop if:
- source-grounding metrics regress without explicit acceptance criteria
- eval fixture semantics need changing but were not in scope
- external services/secrets/model binaries are required
```

## 5. Review-Only Prompt

```text
Review only. Do not edit files.

Inspect the current diff and verify:
1. scope creep
2. retrieval behavior unchanged or explicitly authorized
3. `mvp003` protected reference not silently changed
4. `hybrid` not made default
5. `deterministic-test` remains plumbing-only
6. no eval semantics drift
7. no generated artifact rewrite
8. no secrets, external APIs, cloud dependencies, or model binaries
9. tests/evals match affected files
10. docs/templates are useful for a next developer

Return:
- blocking issues
- non-blocking issues
- merge readiness
- recommended next action
```
