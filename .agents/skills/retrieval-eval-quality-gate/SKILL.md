---
name: retrieval-eval-quality-gate
description: Use whenever retrieval, chunking, scoring, eval datasets, or ranking behavior changes.
---

# Retrieval Eval Quality Gate

## When To Use

- Chunk boundaries, document parsing, metadata filters, scoring, embeddings, vector DB, hybrid search, reranking, eval datasets, or ranking behavior changes.
- A PR claims retrieval quality improvement.
- An MVP milestone depends on retrieval performance.

## When Not To Use

- Docs-only changes unrelated to retrieval behavior.
- UI-only changes that do not alter retrieval inputs or outputs.
- Compliance-only review with no ranking or evidence retrieval change.

## Required Inputs

- Changed files and expected retrieval impact.
- Eval dataset name and location.
- Eval command and settings.
- Baseline metrics or previous run summary.
- Known golden queries.

## Workflow Steps

1. Identify which retrieval stage changed.
2. Confirm eval data is appropriate for the change.
3. Run targeted unit tests.
4. Run retrieval eval.
5. Compare metrics with baseline.
6. Inspect regressions and surprising wins.
7. Decide pass, conditional pass, or fail.

## Quality Gates

- Eval command is reported.
- Dataset and top-k settings are reported.
- Pass/fail count is reported.
- Regressions are explained.
- No metric is invented.

## Report Format

- Changed retrieval stage:
- Eval dataset:
- Command:
- Metrics:
- Regressions:
- Decision:
- Follow-up:

## Failure Conditions

- No baseline or eval data is available and the gap is not reported.
- Eval fails but task is reported as complete.
- Ranking changes are merged without regression analysis.
- Metrics are summarized without command or dataset.

## Next-Step Recommendation Format

- Next eval task:
- Target metric:
- Dataset needed:
- Owner decision needed:

