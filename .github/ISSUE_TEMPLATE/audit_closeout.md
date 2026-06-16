---
name: Closeout Audit
description: Audit whether an issue can be closed without hiding regression or scope drift
title: "[Audit] "
labels: ["audit", "closeout"]
body:
  - type: textarea
    id: objective
    attributes:
      label: Closeout Objective
      description: What exact condition must be true to close this issue?
    validations:
      required: true
  - type: dropdown
    id: audit_type
    attributes:
      label: Audit Type
      options:
        - no-behavior-change audit
        - behavior verification
        - regression closeout
        - failed-question recovery audit
        - release readiness audit
    validations:
      required: true
  - type: textarea
    id: non_goals
    attributes:
      label: Non-Goals
      value: |
        - Do not change retrieval behavior.
        - Do not change scoring, chunking, reranking, metadata semantics, source registry, ingestion, or eval semantics.
        - Do not make `hybrid` the default.
        - Do not treat `deterministic-test` reranker as quality-improving.
    validations:
      required: true
  - type: textarea
    id: evidence
    attributes:
      label: Evidence to Inspect
      value: |
        - Related issue:
        - Related PRs:
        - Eval fixture:
        - Historical failed question IDs:
        - Decision logs / eval reports:
    validations:
      required: true
  - type: textarea
    id: gates
    attributes:
      label: Verification Gates
      value: |
        - [ ] `python -m pytest`
        - [ ] `python scripts/verify_artifacts.py`
        - [ ] Retrieval eval, level: smoke / target-only / full
        - [ ] `git diff --stat`
        - [ ] no-behavior-change checklist
    validations:
      required: true
  - type: textarea
    id: decision
    attributes:
      label: Closeout Decision
      value: |
        - [ ] Close issue
        - [ ] Update issue and keep open
        - [ ] Split follow-up issue
        - [ ] Blocked

        Rationale:
    validations:
      required: true
