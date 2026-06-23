---
name: mvp-implementation
description: Use when implementing a scoped Asperitas MVP after preflight approval. Applies to code, tests, docs, decision logs, and PR preparation. Do not use for preflight-only tasks.
---

# MVP Implementation Skill

## Purpose

Implement the smallest safe change that advances the current Asperitas Agent MVP while preserving source-grounding, auditability, compliance gates, and existing retrieval defaults.

## Trigger

Use this skill when the user or task explicitly says implementation is approved after preflight, or asks to implement a specific MVP scope.

Do not use for broad research, source ingestion, production deployment, autonomous wet-lab execution, or unspecified performance tuning.

## Required Operating Rules

1. Read `AGENTS.md`, `README.md`, and relevant MVP docs before editing.
2. Confirm branch, HEAD, and worktree status before edits.
3. Use a clean feature branch.
4. Make additive, backward-compatible changes.
5. Do not delete files unless explicitly approved.
6. Do not change retrieval defaults unless the task explicitly scopes retrieval and requires eval.
7. Preserve `mvp003` as the protected deterministic default retriever.
8. Keep hybrid, reranker, embeddings, vector DB, and answer generation behavior opt-in unless eval-proven and explicitly approved.
9. Do not ingest, chunk, embed, index, or mutate source registries unless explicitly scoped.
10. Do not claim production readiness, wet-lab validation, regulatory approval, or autonomous-lab capability without verified evidence.

## Implementation Loop

```text
scope lock
-> inspect existing files
-> identify minimal file set
-> implement smallest safe change
-> add/update focused tests
-> update docs when architecture changes
-> add decision log when MVP state changes
-> run verification
-> report risks and next MVP
```

## Required Verification

For source-code changes:

```bash
python -m pytest -q
python scripts/verify_artifacts.py
git diff --check
```

For retrieval, chunking, scoring, metadata filtering, embeddings, vector DB, reranking, or answer-generation changes:

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 --json
```

For docs-only changes:

```bash
git status --short --branch
git diff --check
```

## Report Format

Return:

1. Objective
2. Architecture Impact
3. Files Modified
4. Tests Executed
5. Metrics Before
6. Metrics After
7. Risks
8. Remaining Gaps
9. Recommended Next MVP
