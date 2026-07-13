# Document Hygiene Audit — 2026-07-13

## Executive Bottom Line

This audit removes stale live-status duplication from active guidance documents while preserving historical contracts and evidence. It does not change source code, tests, workflows, retrieval, generation, source registry data, dependencies, vector DB/KG state, or runtime behavior.

## Audit Trigger

The repository contains many documents created across rapidly changing V1.x phases. Documents older than three weeks, and newer documents that still contain old baselines or obsolete active-phase wording, were treated as review candidates.

Age alone is not a deletion criterion. A document is deleted only when it is both operationally unnecessary and unreferenced, and when deletion would not remove audit evidence or break links.

## Confirmed Stale Active-State Patterns

The audit found active guidance documents duplicating mutable state such as:

- old `main` commit SHAs;
- V1.10C publication as a future step after it had merged;
- V1.5 or MVP-004 as the active focus after later phases had advanced;
- historical issue numbers presented as current execution commands;
- duplicated mandatory sequences that could drift from the authoritative roadmap.

The following six documents are updated in this branch:

1. `docs/ROADMAP.md`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/MVP_COMPLETION_MASTER_PLAN.md`
4. `docs/AI_DEVELOPMENT_OS.md`
5. `docs/WORKFLOW.md`
6. `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md`

## Repair Strategy

- Route live phase status, completion claims, bottlenecks, and the immediate next action to `docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` plus live GitHub evidence.
- Preserve scoped technical contracts, exit criteria, architecture doctrine, safety rules, and historical release evidence.
- Reclassify old issue sequences and phase labels as historical references rather than current commands.
- Reconcile stale MVP-004/vector/hybrid/reranker status with the authoritative roadmap without claiming production readiness or performance improvement.
- Keep truth boundaries explicit for protected holdout, human gold labels, runtime quality, legal/compliance/biosafety approval, production vector DB/KG, wet-lab validation, autonomous execution, and foundation-model capability.

## Deletion Decision

No document is deleted in this PR.

Reason:

- the reviewed documents remain referenced by README, AGENTS, other roadmaps, workflow guidance, or productization documents;
- several contain durable acceptance criteria and historical contracts that remain useful for regression review;
- deleting them would create broken links or remove audit context;
- Git history alone is not a sufficient replacement for actively referenced governance contracts.

Historical phase-specific closure and preflight documents are intentionally retained as immutable evidence. They must not be rewritten merely because their embedded status is old.

## Deferred Active Banners

`README.md` and `AGENTS.md` still contain stale active-authority banners on current `main`. They are tracked by Issue #173 and should be synchronized only after PR #172 provides the final V1.11C merge/main SHA and post-merge evidence.

The authoritative current-state roadmap is being repaired in PR #172. This audit branch does not modify that file to avoid overlapping changes.

## Validation Contract

Required before merge:

- exact seven-file scope;
- Markdown fence balance;
- relative path/link existence;
- stale SHA and obsolete active-command scan across the six repaired docs;
- UTF-8 and trailing-whitespace review;
- `git diff --check`;
- docs-only CI/Quality Gates;
- no code, test, workflow, dependency, source registry, retrieval, generation, vector DB, KG, secret, or protected-data change.

Local full pytest and retrieval evaluation are not required because this branch changes documentation only. GitHub Actions remains the clean-environment final gate.

## Truth Boundary

This audit improves documentation routing and reduces operational ambiguity. It does not improve retrieval, reranking, answer generation, biological decision quality, compliance accuracy, latency, token use, security posture, production readiness, or proprietary data moat unless separate measured evidence proves those claims.

## Rollback

Revert the final documentation-hygiene PR. No migration, generated artifact, runtime state, external service, or data-store compensation is required.
