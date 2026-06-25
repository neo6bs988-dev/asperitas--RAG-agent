# V1.1 Performance Handoff

Status: post-V1 handoff plan

## Objective

V1.1 should improve real internal performance only after V1 release-candidate gates are verified on `main` and actual failure logs exist.

## Handoff Inputs

- failure log collection
- failure taxonomy
- baseline artifact
- candidate artifact
- regression gate
- V1.1 retrieval and answer-quality optimization backlog
- V1.2 source acquisition and briefing pipeline candidates
- V2 research planning and DBTL assistant candidates

## Failure Taxonomy

Classify failures into:

- setup or dependency issue
- artifact verifier issue
- security guard false positive or false negative
- workflow gate issue
- audit trace issue
- dry-run CLI usability issue
- retrieval-quality issue
- answer-quality issue
- citation/evidence issue
- compliance or confidentiality risk

## V1.1 Work Principles

- Use observed failures, not speculative polish, to prioritize.
- Keep retrieval and answer changes behind before/after evals.
- Preserve the current deterministic default retriever unless a scoped, eval-backed change is approved.
- Keep answer-provider wiring explicit and opt-in until source-grounding and regression checks justify a broader default.
- Keep public, investor, partner, legal, regulatory, and wet-lab-sensitive outputs behind human approval.

## Candidate V1.1 Work

- failure log schema
- baseline and candidate result artifacts
- expanded security guard fixtures
- answer-provider adapter contract review
- retrieval and answer-quality eval expansion
- citation/evidence failure triage

## Later Work

V1.2 may focus on source acquisition and briefing pipeline improvements. V2 may explore research planning and DBTL assistant workflows after governance, safety, audit, and eval gates remain stable.
