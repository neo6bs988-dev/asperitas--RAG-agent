# Codex Next Prompt - Coding Performance Max

```text
Codex Reasoning Level: 매우높음

Goal:
Convert the Codex Coding Performance Max Layer into one machine-checkable improvement without adding unreviewed dependencies or weakening CI/security/compliance gates.

Scope:
- Read AGENTS.md, docs/P0_PLUS_AI_LEAD_OPERATING_LAYER.md, docs/CODEX_CODING_PERFORMANCE_MAX_LAYER.md, .github/workflows/ci.yml, and .github/workflows/quality-gates.yml.
- Choose exactly one narrow next step:
  1. add a test that validates required PR-template sections,
  2. add a JSON/CSV candidate registry for coding-performance tools,
  3. add a docs-only CI fixture that proves uppercase .github/PULL_REQUEST_TEMPLATE.md is fast-pathed,
  4. add a benchmark script that compares targeted pytest command timing without changing CI defaults.
- Do not install Ruff, uv, pre-commit, pytest-xdist, mypy, or any new dependency unless a separate approval ledger is included.

Evidence:
- Treat Ruff, uv, pre-commit, pytest-xdist, and mypy as external open-source candidates only.
- Use official docs as source candidates, not as proof of repo adoption.

Constraints:
- Preserve the architecture ladder: deterministic helper before workflow before agent.
- Preserve source registry, truth-boundary, compliance, and non-overclaim gates.
- No runtime RAG/retrieval/generation/vector DB/KG changes.
- No broad reformatting.
- No dependency lockfile churn unless explicitly scoped.

Output:
- One branch and one PR.
- PR body must include:
  - Codex reasoning level
  - changed files
  - open-source candidate status
  - expected speed/quality metric
  - verification command and result
  - skipped checks and rationale
  - rollback path
  - production-status boundary

Verification:
- For docs/template checks: targeted pytest or deterministic script if added, plus GitHub Actions.
- For workflow changes: let CI and Quality Gates pass before merge.
- For benchmark scripts: run the benchmark on a bounded command and report raw timing.

Stop Rules:
- Stop if the change requires unreviewed dependencies, mass formatting, external service calls, autonomous execution, or relaxing a gate.
- Stop if faster CI would skip tests for source, retrieval, compliance, eval, security, schema, or release-scope changes.
```
