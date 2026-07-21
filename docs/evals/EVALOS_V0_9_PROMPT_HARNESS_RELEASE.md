# EvalOS v0.9 — Prompt-Harness Release Gate

## Decision

Prompt doctrine is frozen at S1-PCE v6.0. This subsystem does not add more
prompt principles. It operationalizes the existing standard as measurable
controls.

## Release object

A candidate is evaluated as a complete release:

```text
model + reasoning configuration
+ instructions
+ context manifest
+ tools and permissions
+ workflow and state
+ output contract
+ verification
+ rollback
```

## Controlling-failure rule

Prompt text may change only after authority, context, retrieval, freshness,
model, tools, workflow/state, verification, domain evidence, UX, and
operations are checked and the failure is reproduced at the prompt layer.

## Context quality

The gate rejects:

- duplicate content;
- included superseded or blocked sources;
- unisolated instructions from untrusted content;
- volatile facts without an `as_of` date;
- missing required context roles;
- context exceeding the frozen token budget.

## Candidate comparison

Incumbent and candidate are compared by slice using repeated paired trials.
Promotion requires:

- minimum trials per slice;
- no slice regression;
- 100% candidate pass on critical slices;
- positive aggregate quality delta;
- no private-oracle access;
- no post-result threshold change.

Cost and latency are reported but cannot compensate for critical failure.

## Truth boundary

A local synthetic pass produces only
`PROMPT_HARNESS_RELEASE_CANDIDATE`. Repository-wide regression, exact-head
CI, protected holdout, real traces, independent review, and action-specific
approval remain required before promotion.
