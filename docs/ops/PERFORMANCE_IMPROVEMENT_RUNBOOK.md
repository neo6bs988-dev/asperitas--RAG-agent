# Performance Improvement Runbook

Status: docs-only operating runbook

Related issue: #96

## Objective

Define a repeatable loop for improving future AI-agent performance without changing product runtime behavior unless a separate implementation task explicitly authorizes it.

Performance means:

- better scoping;
- fewer unsafe or unrelated edits;
- better source-grounding discipline;
- better test/eval selection;
- clearer PR evidence;
- faster review and rollback;
- reduced overclaim and compliance risk.

This document does not claim improved RAG retrieval metrics or model performance. It defines a development-operations loop only.

## Baseline Before Improvement

Before using gstack-style workflow claims, capture:

- issue number and branch;
- task type;
- files changed;
- commands run;
- checks skipped and why;
- reviewer findings;
- time-to-PR if measured;
- defects caught before merge;
- defects caught after merge if known.

Do not invent productivity metrics. If metrics are not measured, label them as unmeasured.

## Standard Performance Loop

Use the operating loop:

1. ChatGPT scope.
2. `/office-hours`.
3. `/autoplan`.
4. `/plan-eng-review`.
5. Codex implementation.
6. `/review`.
7. `/cso`.
8. `/qa`.
9. `/ship`.
10. `/document-release`.
11. `/retro`.
12. GitHub evidence.

## Measurement Dimensions

Track performance by evidence, not vibes.

| Dimension | Evidence |
|---|---|
| Scope control | Diff matches issue, no unrelated files |
| Runtime safety | No runtime files changed for docs-only work |
| Source-grounding | Claims mapped to source priority or labeled inference |
| Gate selection | Commands match `docs/QUALITY_GATES.md` |
| Review quality | Findings caught before PR merge |
| Compliance awareness | CITES/Nagoya/LMO/biosafety/confidentiality risks surfaced |
| Release discipline | Release scripts and smoke tests run only when required |
| Documentation quality | Runbooks match implemented state and avoid false claims |
| GitHub evidence | PR body includes commands, results, risk, rollback, next action |

## Asperitas Gate Map

### Always Consider

```bash
python -m pytest
python scripts/verify_artifacts.py
```

For docs-only work, `python -m pytest` may be skipped if no code changed and the skip is explicit.

### Release Readiness

```bash
python scripts/check_v1_release_readiness.py --json
```

Use when a task affects release readiness, release docs, release gates, or internal RC claims.

### Smoke Tests

```bash
python scripts/run_v1_rc_smoke.py --json
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
```

Use for release readiness or behavior-impacting changes, not for docs-only operating-stack additions unless requested.

### Source And Truth Boundary Check

For every performance loop, confirm:

- no unsupported claim was presented as fact;
- P6 external doctrine, including gstack, was not treated as Asperitas company truth;
- internal source hierarchy remains authoritative for company facts;
- speculative future adoption is labeled as future, optional, or approval-gated;
- no production RAG/KG/eval/compliance/wet-lab completion is claimed without evidence.

### Release Evidence Docs

Update release evidence docs only when behavior, release state, or release gate results change. Do not mutate release artifacts for docs-only operating-stack work.

## Retro Template

Use this after meaningful PRs:

```markdown
## Retro

Issue:
Branch:
Task type:

What improved:
What slowed review:
What risk was caught:
What risk remains:
Checks run:
Checks skipped and why:
Custom skill that would have helped:
Next workflow improvement:
```

## GO/NO-GO Criteria

GO for docs-only operating-stack adoption when:

- only docs changed;
- `git diff --check` passes;
- artifact verification passes or documented blocker exists;
- no runtime, retrieval, chunk, source registry, release artifact, or test files changed;
- PR body references issue #96 and reports skipped checks.

NO-GO when:

- runtime behavior changes without approval;
- retrieval or answer-generation behavior changes without evals;
- release claims are made without release-readiness evidence;
- gstack source is vendored into this repo;
- team-required mode is proposed before stable internal release approval.

## Rollback

Docs-only rollback:

```bash
git revert <merge_commit>
```

or revert the `docs/ops/` files before merge.

No product runtime rollback should be necessary for this phase.
