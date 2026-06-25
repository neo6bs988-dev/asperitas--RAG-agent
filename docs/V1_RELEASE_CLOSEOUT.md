# V1 Release Closeout

Status: pre-RC readiness posture only; final RC, internal dry-run, and internal release remain pending

## Pre-RC Roadmap Guard

Playbook v3 Absorption and Benchmark Absorption & Stage-Gate Calibration are completed as a separated docs/process/check-only subtask in `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md`.

The later V1 steps remain pending: MVP Performance Pack Backfill, V1 Performance Closure Matrix, P0/P1 Gap Fix Only, Final Pre-RC Regression, `v1.0.0-rc1`, Internal Dry-run, and `v1.0.0-internal`.

This status means ready for next V1 step only after the subtask checks pass. It does not mean the final RC gate is ready, tag readiness, internal dry-run completion, internal release completion, production deployment, autonomous ingestion, source expansion completion, or full V1 closure.

## Release Decision

V1 may be evaluated for internal-RC posture when the release-readiness checker, full test suite, artifact verifier, security guard smoke, and chat dry-run smoke all pass on `main`. Any later release-note, RC tag, dry-run, GO, or internal-release claim requires fresh command output from that later implementing context.

This is an internal engineering milestone. It is not a public launch, customer deployment, production system, regulatory claim, clinical claim, commercial performance claim, or biological model validation claim.

## Completed V1 Layers

- MVP-016: skills layer
- MVP-017: eval layer
- MVP-018: workflow layer
- MVP-019A: audit trace layer
- MVP-019B: workflow audit bridge
- MVP-019C: security guard
- MVP-019D: chat/QA workflow wiring
- MVP-019E: release readiness and internal deploy guide

## Release Criteria

- deterministic local tests pass
- artifact verifier passes
- security guard smoke passes
- chat workflow dry-run smoke passes
- release-readiness report returns `ready_for_internal_rc`
- no retrieval/chunk/source-registry/eval-fixture/embedding/vector/reranker/answer/default runtime mutation
- known limitations are documented
- V1.1 handoff plan is documented

## Internal Use Boundary

Use V1 for internal workflow/control validation, smoke testing, failure collection, and handoff planning. Keep real user-facing answers, external claims, partner outputs, investor outputs, and wet-lab-sensitive outputs behind human review and separate approval.

## Release Artifacts

Recommended internal closeout packet evidence to capture in a later, human-approved release step:

- latest commit SHA on `main`
- full pytest result
- `verify_artifacts.py` result
- security guard smoke result
- chat dry-run smoke result
- release-readiness JSON result
- known limitation notes
- V1.1 tickets created from observed failures

## Next Step

After merge, verify `main`, run the closeout packet commands, and open V1.1 tickets only from observed failures or clearly scoped performance work.
