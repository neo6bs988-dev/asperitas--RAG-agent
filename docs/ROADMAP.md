# Roadmap

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This file is a durable compatibility roadmap. It must not duplicate mutable phase names, commit SHAs, issue status, or the immediate next action. Historical milestone descriptions remain useful technical context, but any status conflict is resolved by the canonical current-state roadmap and live GitHub evidence.

## Current Rule

Do not mark an MVP or phase complete unless its acceptance criteria, tests, evals, source-grounding review, security/compliance review, release decision, and merge evidence are recorded.

The Top Source Triad is operating doctrine, not implementation proof:

```text
ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf
+ Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf
+ 딥리서치를 통해 GPT 채팅 학습용 자료.pdf
```

## Durable Development Sequence

The canonical roadmap controls exact active status. The enduring sequence is:

```text
representative evaluation controls
-> retrieval and reranker hardening
-> real grounded answer path
-> claim-to-citation verification
-> compliance/security adversarial gates
-> trace, latency, token, and cost control plane
-> internal dogfood
-> approved data flywheel
-> authenticated web productization
-> production-readiness gate
-> evidence-driven KG, DBTL, active learning, and foundation-model readiness
```

Do not reorder this sequence merely to add fashionable frameworks.

## Historical V1 Internal Release Preparation

The following entries are historical release-preparation evidence. They are not the live next-step queue.

| V1 step | Historical record |
|---|---|
| Playbook v3 Absorption | Recorded in `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| Benchmark Absorption & Stage-Gate Calibration | Recorded in `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| MVP Performance Pack Backfill | Recorded in `docs/V1_MVP_PERFORMANCE_PACK.md` |
| V1 Performance Closure Matrix | Recorded in `docs/V1_PERFORMANCE_CLOSURE_MATRIX.md` |
| P0/P1 Gap Fix | Recorded through `scripts/check_v1_p0_p1_gap_fix.py` and related PR evidence |
| Final Pre-RC Regression | Recorded in `docs/V1_FINAL_PRE_RC_REGRESSION.md` |
| v1.0.0-rc1 | Historical prerelease baseline at `7f28f0a60fae2d7e0b674d1111287386d2d64fc6` |
| Internal dry-run / internal release | Status must be read from the canonical roadmap and live release evidence |

Historical handoff labels such as V1.1A–V1.1D remain architectural context only. They must not override later merged roadmap decisions.

## Capability Map

Live capability status belongs in the canonical current-state roadmap. The table below preserves durable meaning and exit conditions.

| Capability | Durable meaning | Exit condition |
|---|---|---|
| Foundation | Repository and deterministic core structure | Core paths, tests, governance, and rollback exist |
| Retrieval structure | Initial retrieval pipeline and metadata-aware reference mode | Retrieval remains repeatable and source metadata is preserved |
| Evaluation baseline | Repeatable retrieval/evaluator harnesses | Dataset/version and metric provenance are explicit |
| Structure-aware chunking | Section-aware metadata and quality-gate evidence | No unexplained chunk/retrieval regression |
| Vector retrieval | Separate measurable comparison mode | Metadata preserved; backend choice evidence-backed |
| Hybrid retrieval | Lexical/metadata/vector combination | Safe metric improvement or explicit rejection |
| Reranker | Reordering interface before answer generation | Ordering improves without source-boundary, latency, or safety regression |
| Source-grounded answer generation | Answers restricted to retrieved evidence | Material claims trace to evidence; insufficient evidence is explicit |
| Compliance guardrails | Risk classification, refusal, escalation, human review | High-risk outputs block or escalate; evaluator grants no approval |
| Internal UI/API | Operator-facing internal workflow | Evidence, scores, warnings, traces, latency, and cost are visible |
| Web productization | Authenticated product-shaped architecture | API/provider/auth/secrets/observability/deployment contracts pass |
| Production readiness | Commercialization blocker gate | Security, privacy, license, compliance, cost, latency, rollback, and incident evidence pass |

## Retrieval and Reranker Gate

Any performance-changing retrieval PR must report:

- dataset and version;
- metric provenance: `Fresh Run`, `Historical`, or `Not Run`;
- baseline, after, and delta;
- Source@k, MRR, nDCG, priority/evidence/section/path impact where supported;
- answer-key leakage review;
- latency and context-token impact;
- regression status;
- rollback.

Do not promote a reranker or hybrid mode that does not improve ordering safely.

## Grounded Answer and Compliance Gate

Material claims must preserve source ID, evidence span, confidence, uncertainty, and compliance tags. Missing evidence must produce uncertainty, refusal, or escalation rather than fabrication.

High-risk biological, CITES, Nagoya/ABS, LMO/GMO, biosafety, biosecurity, privacy, IP, license, public, and investor outputs remain human-gated. Evaluator output cannot grant legal, compliance, biosafety, IP, wet-lab, public, investor, release, or production approval.

## Productization Gate

A web interface is not production readiness. Before public or commercial promotion, require:

- authenticated role boundaries;
- secrets/environment policy;
- public/private source separation;
- durable trace and audit storage;
- security/privacy/license/compliance review;
- latency and cost budgets;
- rollback and incident response;
- evidence-backed release claims.

## Architecture Gate

Use the smallest sufficient layer:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

New frameworks, services, vector backends, KG systems, model providers, or agent runtimes require license/allowed-use review, security/privacy review, benchmark evidence, an adapter boundary, targeted tests/evals, rollback, and human approval.

## Default Next Action

Read the canonical current-state roadmap's `Immediate Next Action` and verify it against current GitHub evidence. Do not execute historical issue numbers, old phase labels, or stale commit references from this compatibility document.
