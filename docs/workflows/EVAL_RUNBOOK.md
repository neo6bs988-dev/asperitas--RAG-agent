# Eval Runbook

## Purpose

This runbook defines when to run smoke tests, target-only eval, and full retrieval eval for the Asperitas RAG Agent.

The core rule: do not use a narrow eval to justify a broad behavior change.

## Eval Levels

| Level | Use when | Required for | Not sufficient for |
|---|---|---|---|
| Smoke | docs/template/CI-only changes, repo integrity checks | quick sanity | retrieval quality claims |
| Target-only | failed-question closeout or narrow bug investigation | specific issue evidence | global regression proof |
| Full | retrieval/chunking/scoring/metadata/source registry/ingestion/eval semantics/reranking/default-mode changes | behavior-changing PRs | proof of production readiness |

## Default Commands

### Unit tests

```bash
python -m pytest
```

### Artifact verification

```bash
python scripts/verify_artifacts.py
```

### Chunk section audit

```bash
python scripts/audit_chunk_sections.py --json
```

### Smoke retrieval eval

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

### Full comparison eval

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

### Reranker plumbing eval

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --reranker deterministic-test --limit 5
```

## Decision Table

| Changed area | pytest | verify artifacts | chunk audit | retrieval eval |
|---|---|---|---|---|
| docs only | optional | no | no | no |
| `.github` templates only | optional | no | no | no |
| CI workflow only | yes if possible | yes if available | no | smoke if cheap |
| tests only | yes | no | no | no unless retrieval assertions changed |
| source code, non-retrieval | yes | maybe | no | no unless output behavior affects RAG |
| source registry / metadata | yes | yes | maybe | full |
| ingestion / chunking | yes | yes | yes | full |
| retrieval scoring / filtering | yes | yes | maybe | full |
| embedding / vector / hybrid | yes | yes | maybe | full |
| reranking | yes | yes | maybe | full + reranker comparison |
| eval fixture / semantics | yes | yes | maybe | full, with before/after explanation |

## Reporting Rules

Every eval report must include:

- branch and commit
- command(s) run
- dataset and top-k/limit
- retriever mode(s)
- reranker mode if used
- before/after metrics when a behavior claim is made
- failed, recovered, and regressed question IDs
- skipped checks with reason
- interpretation and risks

## Protected Reference Reminders

- `mvp003` is the protected deterministic reference.
- `hybrid` is an accepted comparison mode, not default.
- `deterministic-test` is plumbing-only and must not be claimed as quality-improving.
- Target-only success must not be presented as global quality improvement.
