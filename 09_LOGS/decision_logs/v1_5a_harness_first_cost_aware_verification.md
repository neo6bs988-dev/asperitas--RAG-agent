# V1.5A Harness-First Cost-Aware Verification Decision

## Date

2026-07-02

## Task

Record V1.5A harness-first, cost-aware, regression-safe verification policy across agent instructions, workflow docs, quality gates, roadmap, GitHub templates, and decision logging.

## Issue/PR

- Issue: not yet opened.
- PR: not yet opened.
- Branch: `codex/v1-5-gap-closure-harness-clean`
- Baseline: `origin/main` at `1697c29c5466e77ec20f9ed7333339a3d637862d`

## Files Changed Or Inspected

Changed:

- `AGENTS.md`
- `docs/AI_DEVELOPMENT_OS.md`
- `docs/WORKFLOW.md`
- `docs/QUALITY_GATES.md`
- `docs/ROADMAP.md`
- `docs/V1_5_PERFORMANCE_ROADMAP.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/v1_5_task.yml`
- `09_LOGS/decision_logs/v1_5a_harness_first_cost_aware_verification.md`

Inspected:

- `README.md`
- `AGENTS.md`
- `docs/AI_DEVELOPMENT_OS.md`
- `docs/WORKFLOW.md`
- `docs/QUALITY_GATES.md`
- `docs/ROADMAP.md`
- `docs/V1_5_PERFORMANCE_ROADMAP.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/`
- `09_LOGS/decision_logs/`

## Commands And Metrics

- Branch baseline: Fresh Run, `origin/main` at `1697c29c5466e77ec20f9ed7333339a3d637862d`.
- Risk level: Fresh Run, low.
- Changed surface: Fresh Run, docs/templates/decision-log governance only.
- Retrieval metrics: Not Run, because no retrieval, chunking, scoring, metadata filtering, embeddings, vector DB, reranking, answer generation, or eval behavior changed.
- Test metrics: Not Run, because no source code or executable behavior changed.
- GitHub Actions minutes: Not Run, because no PR has been opened yet.

## Verification Evidence

- `git diff --check`: Fresh Run, passed with only LF-to-CRLF working-copy warnings.
- README/AGENTS encoding check: Fresh Run, passed; both files are UTF-8 no BOM with no NUL bytes.
- Markdown/template sanity: Fresh Run, passed; changed Markdown code fences are balanced and required V1.5A fields are present.
- Issue-template sanity: Fresh Run, passed by text schema check; PyYAML was unavailable locally.
- Changed-surface sanity: Fresh Run, passed; changed files are docs/templates/decision-log governance only.
- Truth-boundary sanity: Fresh Run, passed; no production DB, production KG, production vector DB, wet-lab, legal, regulatory, or foundation-model claim was added.

## Decision

Accept V1.5A as a harness-first, cost-aware, regression-safe governance backfill. V1.5+ work must follow:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

Targeted checks are the default. Full suites, broad retrieval evals, expanded GitHub Actions coverage, or release gates are required only when risk level or changed surface justifies them.

## V1.4 No-Regression Boundary

This decision does not authorize answer behavior changes, retrieval scoring changes, source ingestion, chunk regeneration, embedding/vector DB behavior changes, reranking behavior changes, generated indexes, model binaries, dependencies, services, secrets, cloud resources, or claims of production DB, production KG, production vector DB, wet-lab, legal, regulatory, or foundation-model status.

## Risks And Residual Issues

- GitHub Actions status cannot be reported until a PR exists.
- The policy is governance only; future enforcement depends on issue/PR use, review, and CI evidence.

## Next Action

Open a small PR from `codex/v1-5-gap-closure-harness-clean`. Reviewer focus should be policy consistency, clean textual diff, no V1.4 regression, and whether skipped tests/evals are justified for docs/templates-only work.
