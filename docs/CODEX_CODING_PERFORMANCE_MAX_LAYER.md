# Codex Coding Performance Max Layer

## Executive Bottom Line

This layer turns external open-source coding-performance practices into a controlled Codex development operating system. It does not install tools by default. It creates a candidate registry and adoption gate so Codex can improve speed, quality, and reproducibility without weakening source grounding, CI discipline, security, or compliance.

## Operating Goal

Maximize Codex coding performance by improving this loop:

```text
Scope Lock
-> Fast Context Retrieval
-> Minimal Implementation
-> Targeted Static Checks
-> Targeted Tests
-> CI Surface Detection
-> Review Evidence
-> Learn Back
```

The target metric is not "more tools." The target is faster correct merges with fewer regressions, lower CI waste, clearer evidence, and lower human review burden.

## Open-Source Candidate Registry

| Candidate | Current Status | Primary Use | Why It Matters | Adoption Gate |
|---|---|---|---|---|
| Ruff | candidate | Python lint + format | Fast linter/formatter; official docs describe Ruff as an extremely fast Python linter and formatter and a drop-in replacement for multiple tools | Add config in one PR, run check-only first, no mass reformat without approval |
| uv | candidate | Python dependency/project/tool execution | Official docs describe uv as a fast Python package and project manager with lockfile, cache, and pip-compatible workflows | Benchmark install/sync time against current CI before migration |
| pre-commit | candidate | Local and CI hook orchestration | Official project describes it as a framework for managing multi-language pre-commit hooks | Start with non-mutating hooks; allow manual run path; do not block urgent work without bypass policy |
| pytest-xdist | candidate | Parallel test execution | Official docs describe xdist as distributing pytest tests across CPUs with `pytest -n auto` | Only use after tests are proven parallel-safe; isolate flaky/global-state tests |
| mypy | candidate | Static type checking | Official docs define mypy as a static type checker that checks annotated Python without running code | Start with targeted modules or non-strict mode; no repo-wide strict gate until baseline is clean |

## Source Notes

- Ruff official docs: https://docs.astral.sh/ruff/
- Ruff formatter docs: https://docs.astral.sh/ruff/formatter/
- uv official docs: https://docs.astral.sh/uv/
- pre-commit official docs: https://pre-commit.com/
- pytest-xdist docs: https://pytest-xdist.readthedocs.io/en/stable/
- mypy official docs: https://mypy.readthedocs.io/en/stable/getting_started.html

These sources are external operating inputs. They are not Asperitas implementation evidence.

## Adoption Gate

No open-source tool or workflow change should be adopted without this ledger:

```text
Tool / pattern:
Source URL:
License status:
Security review:
Current bottleneck:
Expected metric improvement:
Baseline command and result:
Pilot scope:
Rollback path:
CI impact:
Developer friction:
Compliance/source-grounding impact:
Decision: candidate / needs_review / approved / rejected
Owner/date:
```

## Coding Performance Principles

1. Prefer deterministic checks before LLM judgment.
2. Prefer changed-surface tests before full suites.
3. Prefer check-only adoption before auto-fix adoption.
4. Prefer tool consolidation when it reduces CI time and config complexity.
5. Do not add a dependency unless it improves speed, safety, or correctness enough to justify maintenance cost.
6. Keep docs-only, schema-only, source-code, retrieval, eval, and release paths separate.
7. Store repeated failures as fixtures, checklist items, or workflow gates.
8. Never weaken truth-boundary, source registry, compliance, or non-overclaim gates for speed.

## Immediate Repo-Level Optimizations

The first optimization is already represented in CI workflow policy:

```text
docs/template-only PR
-> source registry contract validation
-> markdown/path/truth-boundary checks
-> skip full pytest/retrieval eval
```

For code/retrieval/eval/security changes, keep full relevant checks. For docs-only work, avoid burning full CI minutes unless the docs modify release, compliance, registry, or workflow behavior in a high-risk way.

## Recommended Next PRs

1. Add a machine-checkable PR-template required-section test.
2. Add a coding-performance candidate registry JSON or CSV.
3. Add Ruff as check-only in CI if license/security review passes.
4. Benchmark `pytest -q` vs selected targeted tests vs `pytest-xdist` on the current suite.
5. Add a failure taxonomy entry whenever Codex causes avoidable CI waste.

## Non-Overclaim Boundary

This layer does not claim that Ruff, uv, pre-commit, pytest-xdist, or mypy are installed, approved, or active in CI. It only creates a controlled evaluation path for future adoption.
