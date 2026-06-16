# Workflow Hardening CI Gates

Date: 2026-06-17

Related issue: #30

## Objective

Prevent unverified Codex changes from silently entering `main` and define which gates run locally, in CI, or at release time.

This is a workflow and merge-safety hardening task. It does not change retrieval behavior, reranker behavior, model behavior, scoring semantics, eval fixtures, source registry artifacts, or generated indexes.

## Files Inspected

- `.github/workflows/quality-gates.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/` status: not present
- `README.md`
- `AGENTS.md`
- `docs/QUALITY_GATES.md`
- `docs/WORKFLOW.md`
- `docs/PIPELINE_AUTOMATION.md`
- `docs/EVALS.md`
- `scripts/verify_artifacts.py`
- `scripts/run_retrieval_eval.py`
- `tests/test_retrieval_eval.py`
- `tests/test_reranking.py`
- `tests/test_static_integrity.py`
- `pyproject.toml`
- GitHub Issue #30 comments: none at audit time

## Current Workflow And CI Coverage

The executable CI workflow is `.github/workflows/quality-gates.yml`.

It runs on:

- push to `main`;
- pull request to `main`;
- manual workflow dispatch.

Current required CI commands:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Current coverage:

| Area | Covered by CI? | Evidence |
|---|---|---|
| Unit and integration tests | Yes | `python -m pytest` |
| Artifact verification | Yes | `python scripts/verify_artifacts.py` |
| Source registry and chunk artifact verification | Yes | artifact verification plus chunk audit |
| Chunk section metadata audit | Yes | `python scripts/audit_chunk_sections.py --json` |
| Baseline retrieval eval | Yes | `--retriever baseline --limit 5` |
| MVP-003 retrieval eval | Yes | `--retriever mvp003 --limit 5` |
| Vector eval | Not required in CI | Conditional local or release gate |
| Hybrid eval | Not required in CI | Conditional local or release gate |
| Reranker eval | Not required in CI | Conditional local or release gate |
| Reranker unit tests | Yes | included in `pytest`, especially `tests/test_reranking.py` and `tests/test_retrieval_eval.py` |
| Metadata preservation tests | Yes | included in `pytest` |
| Path-context eval tests | Yes | included in `pytest` |

## Gaps Found

1. The PR template listed only older baseline and `mvp003` retrieval gates.
2. The central quality-gate docs did not clearly separate always-local, required CI, conditional retrieval/reranker, optional expensive, and release-only gates.
3. Vector, hybrid, and deterministic reranker eval commands were not clearly assigned to local/release gates.
4. CI token permissions were implicit instead of read-only.
5. CI did not cancel stale superseded runs on the same ref.
6. Branch protection cannot be enforced from repo files and remains a repository-admin setting.

## Gate Policy

### Always Local Before PR

Run before PR unless the change is docs/governance-only and skipped checks are explained:

```bash
python -m pytest
python scripts/verify_artifacts.py
```

### Required CI

Run on every PR to `main`, push to `main`, and manual dispatch:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

### Conditional Local Retrieval Gates

Run when retrieval, chunking, metadata, embeddings, vector search, hybrid retrieval, eval fixtures, or answer-generation behavior changes:

```bash
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

### Conditional Local Reranker Gates

Run when reranking code, reranker eval plumbing, or reranker policy changes:

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5
```

`deterministic-test` remains a plumbing-only reranker and must not be claimed as a quality-improving reranker.

### Optional Expensive Gates

Keep out of required CI until runtime, thresholds, and failure modes are stable:

- full vector eval;
- full hybrid eval;
- full reranker comparison;
- machine-readable retrieval report artifacts;
- threshold checker for hard retrieval regressions.

### Release-Only Gates

Run during milestone closeout when relevant:

- full retrieval eval across baseline, `mvp003`, vector, hybrid, and reranker variants;
- answer faithfulness eval after MVP-008;
- compliance guardrail eval after MVP-009;
- release notes and operating guide after MVP-010.

## Implementation Decision

Implemented the smallest safe hardening change:

- keep existing CI coverage focused on stable gates;
- add read-only CI token permissions;
- add CI concurrency cancellation for stale superseded runs;
- set unbuffered Python output for clearer CI logs;
- update PR template with local, conditional, CI, and merge-safety checks;
- update quality-gate and automation docs with the current gate policy.

Did not add vector, hybrid, or reranker full eval to required CI because those gates are slower and should first get stable thresholds and machine-readable reporting. This avoids making CI flaky or too slow while still requiring those commands locally when the changed surface needs them.

## CI Risk

Low.

No dependencies were added. No external service, API, secret, endpoint, model binary, generated index, cloud resource, or network-dependent eval logic was added.

The CI YAML changes are operational only:

- `permissions: contents: read`;
- per-ref concurrency cancellation;
- `PYTHONUNBUFFERED=1`.

## Regression Check

- No retrieval behavior changed.
- No reranker behavior changed.
- No model behavior changed.
- No eval scoring semantics changed.
- No retrieval modes were removed or replaced.
- `mvp003` remains protected.
- `hybrid` remains accepted comparison mode, not default.

## Verification Run

Required local gates:

| Command | Result |
|---|---|
| `python -m pytest` | Passed: 178 tests |
| `python scripts/verify_artifacts.py` | Passed: 48 registry records, 2821 chunks, 0 warnings, 0 errors |

Current CI command set:

| Command | Result |
|---|---|
| `python scripts/audit_chunk_sections.py --json` | Passed: 2821 chunks, 2097 with section metadata, 724 missing section metadata |
| `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` | Completed: 34.4% overall, 43.8% source @5 |
| `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` | Completed: 93.8% overall, 100.0% source @5 |

Additional policy-relevant eval checks:

| Command or check | Result |
|---|---|
| `python scripts/run_retrieval_eval.py --retriever hybrid --limit 5` | Completed with stdout/stderr capture: 100.0% overall, 100.0% source @5 |
| `mvp003 + deterministic-test` via `scripts/run_retrieval_eval.py` module driver | Completed: 93.8% overall, 93.8% source @3, 100.0% source @5 |
| `python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5` | Direct shell path returned no output locally; module-driver fallback completed |
| `python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5` | Direct and captured shell paths returned no output locally; not required for this non-behavioral change |

The no-output reranker shell behavior is a local execution issue already observed in earlier reranker eval work. It is not treated as a retrieval regression because this task did not change retrieval or reranker behavior, and the required local gates plus current CI commands passed.

## Remaining Manual Checks

- Repository admin should require the `Quality Gates` workflow in GitHub branch protection for `main`.
- Future automation should add machine-readable eval output artifacts before threshold-based CI failures.
- Full vector, hybrid, and reranker evals should remain local or release-only until they have stable runtime and regression thresholds.

## Next Task

Configure GitHub branch protection for `main` so the `Quality Gates` workflow is required before merge, then add machine-readable retrieval eval artifacts as a future CI enhancement.
