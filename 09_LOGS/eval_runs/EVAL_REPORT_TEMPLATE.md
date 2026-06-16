# Retrieval / Eval Report Template

## 0. Metadata

- Report ID:
- Date:
- Author:
- Branch:
- Commit:
- PR:
- Issue:
- Eval scope: smoke / target-only / full
- Dataset:
- Top-k / limit:
- Retriever mode(s):
- Reranker mode:

## 1. Objective

What is being evaluated and why?

## 2. Scope Classification

- Behavior change? yes/no
- Retrieval/chunking/scoring affected? yes/no
- Metadata/source registry/ingestion affected? yes/no
- Eval fixture/semantics affected? yes/no
- Default mode affected? yes/no
- Protected reference affected? yes/no

## 3. Commands Run

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Skipped commands and reason:

## 4. Artifact Status

- Source registry records:
- Chunk count:
- Eval question count:
- Changed artifacts:
- Regenerated artifacts? yes/no

## 5. Metrics Before / After

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline before | | | | | | | | |
| baseline after | | | | | | | | |
| mvp003 before | | | | | | | | |
| mvp003 after | | | | | | | | |
| vector before | | | | | | | | |
| vector after | | | | | | | | |
| hybrid before | | | | | | | | |
| hybrid after | | | | | | | | |

## 6. Failed / Recovered / Regressed Questions

| Question ID | Before | After | Status | Interpretation |
|---|---|---|---|---|
| | | | | |

## 7. Protected Reference Review

- `mvp003` behavior changed? yes/no
- `hybrid` made default? yes/no
- `deterministic-test` treated as quality-improving? yes/no
- Any source-grounding metric regressed? yes/no

## 8. Conclusion

- [ ] Accept
- [ ] Reject
- [ ] Keep issue open
- [ ] Close issue
- [ ] Split follow-up

Rationale:

## 9. Risks / Follow-ups

-
