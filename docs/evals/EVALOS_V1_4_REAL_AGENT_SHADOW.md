# EvalOS v1.4 — Real Agent Adapter and No-Effect Shadow

## Status

`IMPLEMENTED_CANDIDATE` on the branch containing this document.

This subsystem is evaluation infrastructure. It does not establish deployment,
production monitoring, protected-holdout generalization, legal or scientific
clearance, or production readiness.

## Goal

Connect the incumbent deterministic `ask_agent()` runtime to a repeated,
privacy-safe, no-effect shadow harness without changing runtime behavior.

## Execution path

```text
actual ask_agent()
-> synthetic in-memory SourceRecord and Chunk inputs
-> AgentResponse normalization
-> immutable-input fingerprint
-> privacy-safe trace
-> semantic trajectory signature
-> repeated incumbent/candidate trials
-> no-effect and regression gates
-> non-promoting decision
```

## Frozen hard gates

A trial fails when any of the following is nonzero or false:

- external-effect count;
- network-egress count;
- provider-export count;
- source or chunk mutation;
- citation-integrity failure;
- trace-validation failure;
- privacy-validation failure.

Aggregate quality or latency cannot compensate for a failed hard gate.

## Measurement-noise controls

Trial-specific identifiers are excluded from semantic trajectory comparison.
The signature compares span type, parent operation, guardrail result,
verification result, and environment outcome.

Latency uses a ratio gate only when the incumbent mean is at least the frozen
latency floor. Smaller timings use an absolute-delta gate to avoid treating
clock and scheduler noise as a material regression.

## Repository boundary

The integration test imports and executes:

- `asperitas_agent.agent_runner.ask_agent`;
- `asperitas_agent.schemas.SourceRecord`;
- `asperitas_agent.schemas.Chunk`.

Only synthetic in-memory records and chunks are passed. No repository data file,
private holdout, external API, provider telemetry, network route, or external
write is required.

## Result states

- `INVALID`
- `NO_EFFECT_SHADOW_SPEC_CANDIDATE`
- `NO_EFFECT_SHADOW_READY_FOR_CONTROLLED_RUN`

Even the controlled-run state has `promotion_allowed=false`. Storage approval,
representative-case approval, exact-head checks, and a separate human release
decision remain required.

## Verification

```text
python -m pytest -q tests/test_evalos_v14_shadow_unit.py
python -m pytest -q tests/test_evalos_v14_repository_integration.py
python scripts/run_evalos_v14_shadow.py --expected-head <EXACT_SHA>
python -m pytest -q
```

## Rollback

Revert the additive commit or close the Draft PR. No data migration or incumbent
runtime modification is introduced.
