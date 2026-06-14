---
name: dependency-security-quality-gate
description: Use when adding, updating, or evaluating dependencies, CI checks, security scanners, linters, type checkers, or package-management policy.
---

# Dependency Security Quality Gate

## When To Use

- Adding a dependency to `pyproject.toml` or other package manifests.
- Introducing a vector DB, embedding library, parser, web framework, eval framework, or agent framework.
- Adding CI security, lint, formatting, type, or dependency checks.
- Reviewing dependency risk before adopting open-source libraries.

## When Not To Use

- Internal source-code changes with no dependency or tooling impact.
- Docs-only changes that do not claim new security or dependency policy.
- Temporary local experiments that are not committed.

## Required Inputs

- Dependency name and version range.
- Purpose of dependency.
- License status.
- Security/vulnerability status if known.
- Whether tests require external services.
- Rollback plan.
- Files affected.

## Workflow Steps

1. Identify the dependency or tool and why it is needed now.
2. Check whether the need can be satisfied by an internal interface first.
3. Verify license compatibility before committing.
4. Confirm no API key, credential, or secret is required for tests.
5. Add the smallest dependency scope possible.
6. Add tests or CI checks that prove the tool works.
7. Keep existing quality gates fast enough for normal PRs.
8. Report new failure modes and rollback path.

## Quality Gates

- Dependency purpose is explicit.
- License status is not ignored.
- No secrets are committed.
- Tests remain offline unless explicitly approved.
- CI remains understandable and debuggable.
- Failure behavior is documented.
- Rollback path is clear.

## Report Format

- Dependency/tool:
- Reason:
- Why now:
- License status:
- Security risk:
- Files changed:
- Tests/CI checks:
- Runtime impact:
- Rollback path:
- Decision:

## Failure Conditions

- Dependency is added for prestige instead of a current bottleneck.
- Tests require paid API access or network access without approval.
- License is unknown.
- CI becomes too slow or flaky without justification.
- Secrets or credentials are committed.
- Existing retrieval/source-grounding behavior is broken.

## Next-Step Recommendation Format

- Next dependency/tooling task:
- Required evidence:
- Blocking risk:
- Quality gate:
