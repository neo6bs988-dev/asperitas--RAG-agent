---
name: retrieval-regression-closeout
description: Use to close, defer, or reclassify known retrieval regressions after fresh evals and failure taxonomy review.
---

# Retrieval Regression Closeout

## When To Use

- A known failed retrieval question, regression, or issue needs closeout.
- A task compares baseline, mvp003, vector, hybrid, or reranked retrieval modes.
- A previous failure may have been fixed by scoring, metadata, fixture semantics, or path-context handling.

## When Not To Use

- Pure docs work with no retrieval decision.
- New retrieval feature implementation before an eval contract exists.
- Answer generation review without retrieval evidence selection changes.

## Required Inputs

- Question IDs or regression IDs.
- Expected source, source priority, evidence label, section, and path-context expectations.
- Retriever modes and commands.
- Current baseline or historical metric report.
- Stop rule for code, fixture, or docs changes.

## Workflow Steps

1. Inspect the issue, PR handoff, and relevant eval fixture rows.
2. Run only the required fresh eval commands unless the task is read-only.
3. Label metrics as `Fresh Run`, `Historical`, or `Not Run`.
4. Compare top-k results against source, priority, evidence label, section, and path-context gates.
5. Classify each failure: fixed, fixed only in hybrid, fixed by fixture/eval semantics, still open, or deferred.
6. Do not relax source-grounding gates to close a failure.
7. Recommend close, update, defer, or implementation follow-up.

## Quality Gates

- `mvp003` remains protected and deterministic.
- `hybrid` remains explicit/manual and is not made default by closeout language.
- Source priority, evidence label, section, path-context, and metadata gates are preserved.
- Metrics are not mixed across fresh and historical runs.
- Regression closeout fails closed when required source-grounding gates cannot be verified.

## Report Format

- Objective:
- Commands run:
- Metrics:
- Question status:
- Failure taxonomy:
- Regression check:
- Decision:
- Risks:
- Next action:

## Failure Conditions

- A retrieval issue is closed while any required gate still fails without explanation.
- A fixture issue is treated as a retrieval improvement without evidence.
- Reranker test-double results are claimed as quality improvement.
- Historical metrics are reported as fresh runs.

## Next-Step Recommendation Format

- Next issue:
- Target failure:
- Required eval:
- Expected decision:
