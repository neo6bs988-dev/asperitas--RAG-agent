# OPS-001 Workflow & Pipeline Hardening

## Executive Bottom Line

OPS-001 hardens the Asperitas RAG Agent development workflow without changing retrieval behavior. The purpose is to make future Codex work repeatable, reviewable, and regression-resistant through small PRs, issue/PR templates, decision logs, eval reports, CI gates, and explicit protected-reference rules.

This is not MVP-007 Phase 3, MVP-008, MVP-009, or retrieval performance work.

## Non-Negotiable Boundaries

- Do not change retrieval behavior for workflow/governance tasks.
- Do not change scoring, chunking, reranking, metadata semantics, source registry, ingestion, or eval semantics unless a dedicated issue explicitly authorizes it.
- Preserve `mvp003` as the protected deterministic reference retriever.
- Keep `hybrid` as an accepted comparison mode, not the default.
- Keep `deterministic-test` reranker as plumbing-only.
- Do not add external services, paid APIs, cloud dependencies, vector DBs, secrets, or model binaries by default.
- Prefer small, additive PRs. Do not delete files unless explicitly authorized.

## Standard Development Loop

1. **Issue scope lock**: objective, context, in-scope files, non-goals, verification level.
2. **Codex preflight**: inspect repo, report plan, do not edit until scope is confirmed.
3. **Branch**: one branch per small PR.
4. **Implementation**: smallest safe change only.
5. **Verification**: run the correct gate for the affected area.
6. **Report**: files changed, commands, metrics, skipped checks, risks.
7. **PR review**: behavior boundary and dangerous-change checklist.
8. **Decision log / eval report**: update when policy, behavior, or eval evidence changes.
9. **Merge**: only when scope, verification, and risk are explicit.

## PR Size Rules

| PR type | Expected size | Required review focus |
|---|---:|---|
| Docs/template | 1-8 files | Accuracy, clarity, no behavior change |
| CI-only | 1-2 files | Reproducibility, no external services/secrets |
| Eval report | 1 report file | Commands, metrics, interpretation, scope |
| Source code | Smallest module-level patch | Tests, behavior boundary, regression |
| Retrieval behavior | Dedicated PR only | Full eval, before/after metrics, protected reference |

## Branch Naming

Use lowercase kebab-case:

- `ops001-workflow-pipeline-hardening`
- `ops001-pr-templates`
- `mvp007-phase3-reranker-acceptance`
- `audit-issue21-closeout`
- `fix-eval-path-context-reporting`

## Commit Message Rules

Use concise imperative commits:

- `ops001: add workflow hardening runbook`
- `ops001: harden pull request template`
- `audit: document issue 21 closeout`
- `eval: report hybrid comparison metrics`
- `retrieval: preserve mvp003 source grounding`

Avoid vague messages:

- `fix stuff`
- `update`
- `final`
- `codex changes`

## PR Naming Rules

Recommended formats:

- `OPS-001: Harden RAG workflow and quality gates`
- `OPS-001: Add issue and closeout templates`
- `Audit: Document Issue #21 closeout`
- `MVP-007 Phase 3: Define reranker acceptance policy`

## MVP Definition of Done

Every MVP PR must report:

- Objective satisfied.
- Files changed.
- Tests run.
- Artifact verification result if data/schema/artifacts are touched.
- Retrieval eval result if retrieval/chunking/scoring/reranking/eval semantics are touched.
- Metrics before/after when quality claims are made.
- Regression risks.
- Follow-up issue or next action.

## No-Behavior-Change Audit Rules

A no-behavior-change audit may inspect code and eval artifacts, but should not modify source code, generated artifacts, fixtures, scoring, chunking, or retrieval settings. Acceptable outputs are:

- audit report
- closeout report
- issue comment / PR description
- decision log entry
- follow-up issue recommendation

If an audit discovers that behavior must change, stop and open a dedicated feature/bugfix issue.

## Dangerous Change Detection

Treat these as high-risk paths:

- `src/asperitas_agent/retrieval_mvp003.py`
- `src/asperitas_agent/chunking.py`
- `src/asperitas_agent/hybrid_scoring.py`
- `src/asperitas_agent/reranking.py`
- `scripts/run_retrieval_eval.py`
- `scripts/verify_artifacts.py`
- `eval/retrieval_questions.jsonl`
- `eval/expected_sources.jsonl`
- `data/chunks.jsonl`
- source registry / metadata files
- generated indexes or embeddings

Touching these files requires explicit issue scope and the correct verification gate.

## Next-Developer Rule

A new developer should be able to read the issue, branch, PR template, eval report, and decision log and reconstruct:

- what changed
- why it changed
- what did not change
- how it was verified
- what remains risky
- what to do next
