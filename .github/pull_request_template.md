# Pull Request Review

## 0. Executive Summary

- Objective:
- Related issue:
- MVP / OPS stage:
- Branch:
- Change classification: docs-only / no-behavior-change audit / feature / bugfix / eval-only / CI-only

## 1. Scope Lock

- [ ] The objective is stated clearly.
- [ ] The change matches the requested scope.
- [ ] Unrelated files are excluded.
- [ ] Non-goals are explicitly listed.
- [ ] This PR is small enough to review safely.

### Non-goals / out-of-scope

-

## 2. Change Type

- [ ] Docs/governance only
- [ ] GitHub workflow / template only
- [ ] CI quality gate only
- [ ] No-behavior-change audit
- [ ] Source code
- [ ] Tests
- [ ] Retrieval/chunking/scoring
- [ ] Metadata/source registry/ingestion
- [ ] Eval fixture or eval semantics
- [ ] Embedding/vector/hybrid retrieval
- [ ] Reranking
- [ ] Answer generation/citation
- [ ] Compliance/biosafety/regulatory
- [ ] MVP release

## 3. Behavior Boundary

- [ ] Retrieval behavior unchanged.
- [ ] Default retriever unchanged.
- [ ] `mvp003` remains the protected deterministic reference.
- [ ] `hybrid` remains accepted comparison mode, not default.
- [ ] `deterministic-test` reranker remains plumbing-only.
- [ ] No scoring/chunking/reranking/metadata/source registry/ingestion/eval semantic changes.
- [ ] No generated artifacts, indexes, model binaries, APIs, secrets, cloud resources, or vector DBs added.
- [ ] Not applicable because this is an intentional behavior-changing PR; justification:

## 4. Dangerous Change Checklist

Mark any touched area:

- [ ] `src/asperitas_agent/retrieval_mvp003.py`
- [ ] `src/asperitas_agent/chunking.py`
- [ ] `src/asperitas_agent/hybrid_scoring.py`
- [ ] `src/asperitas_agent/reranking.py`
- [ ] `scripts/run_retrieval_eval.py`
- [ ] `scripts/verify_artifacts.py`
- [ ] `eval/retrieval_questions.jsonl`
- [ ] `eval/expected_sources.jsonl`
- [ ] `data/chunks.jsonl`
- [ ] source registry / metadata CSV/XLSX
- [ ] `.github/workflows/*`

If any are checked, explain why the change is safe and what eval was run:

## 5. Required Checks

### Always report

- [ ] `git diff --stat`
- [ ] Scope / behavior boundary reviewed

### Source code or tests changed

- [ ] `python -m pytest`

### Artifacts, registry, metadata, source files, chunks, or schemas changed

- [ ] `python scripts/verify_artifacts.py`
- [ ] `python scripts/audit_chunk_sections.py --json`

### Retrieval/chunking/scoring/embedding/vector/hybrid/reranking/eval semantics changed

- [ ] Full retrieval eval command(s):

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

### Docs/template/no-behavior-change PR

- [ ] Full retrieval eval not required; reason:

## 6. Eval Level Used

- [ ] Smoke test: repo integrity only; not retrieval quality proof.
- [ ] Target-only eval: issue closeout or narrow investigation only; not global regression proof.
- [ ] Full eval: required for behavior-changing retrieval/eval PRs.
- [ ] No eval: docs/template-only; reason:

## 7. Retrieval Metrics

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Source file match @3 | | | |
| Source file match @5 | | | |
| Source priority match | | | |
| Evidence label match | | | |
| Section match | | | |
| Path context match | | | |
| Overall pass rate | | | |

## 8. Failed / Recovered / Regressed Questions

| Question ID | Before | After | Status | Notes |
|---|---|---|---|---|
| | | | | |

## 9. Source-Grounding / Citation Impact

- [ ] Source IDs are preserved.
- [ ] Source priority is preserved.
- [ ] Evidence labels are preserved.
- [ ] Citation targets are preserved.
- [ ] Unsupported claims are removed or labeled.
- [ ] Not applicable.

## 10. Compliance / Biosafety Impact

- [ ] CITES/Nagoya/LMO/K-BDS risk reviewed if relevant.
- [ ] Privacy/security/IP/legal risk reviewed if relevant.
- [ ] No confidential, secret, or personal data added.
- [ ] Public/investor-facing claims are source-supported.
- [ ] Human approval needed for high-risk external output.
- [ ] Not applicable.

## 11. Risk Summary

Known risks:

Deferred work:

Human approval needed:

Rollback plan:

## 12. Merge Decision

- [ ] Ready
- [ ] Conditional
- [ ] Blocked

Reason:
