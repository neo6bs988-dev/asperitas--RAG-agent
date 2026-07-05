# V11.1 Supergap Agent Build Leader Doctrine

## Executive Bottom Line

V11.1 upgrades the repo doctrine from `Top Source Triad` to `Top Source Triad + Supergap Agent Build Leader`.

The target is not a bigger prompt and not a claim that a proprietary foundation model already exists. The target is a more execution-ready operating layer for building Asperitas's proprietary agent stack on top of frontier models:

```text
frontier models
-> proprietary source registry and biological data flywheel
-> RAG / memory / tool / structured-output control plane
-> eval, red-team, tracing, and guardrail flywheel
-> compliance / biosafety / IP approval gates
-> DBTL and productization workflows
-> future foundation-model-readiness dataset strategy
```

This document is governance and development doctrine only. It does not implement production RAG, vector DB, KG, eval suite, legal approval, wet-lab validation, autonomous lab execution, hosted web product, commercial readiness, or biological foundation-model capability.

## Source Status

| Source | Repo treatment | Status boundary |
|---|---|---|
| `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf` | Project-level control-plane baseline | Operating doctrine, not implementation proof |
| `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf` | AI Lead / CTO behavior, architecture ladder, RAG/KG/eval/control-plane design | Operating doctrine, not implementation proof |
| `딥리서치를 통해 GPT 채팅 학습용 자료.pdf` | Deep Research, ML/DL/LLM, benchmark, agent-development source layer | Operating doctrine, not implementation proof |
| `슈퍼갭 GPT 채팅 모델용 고임팩트 PDF 트레이닝 패키지 설계 보고서.pdf` | High-impact training-package doctrine: source-grounded RAG, biosafety gates, role-specialized reasoning, DBTL support, GitHub verification | Operating doctrine, not implementation proof |
| `초고성능 독자 AI 에이전트 구축과 최종 업그레이드 트레이닝 PDF 설계 보고서.pdf` | Proprietary agent-stack doctrine: data flywheel, agent runtime, eval system, tool interfaces, safety/security/governance | Operating doctrine, not implementation proof |

## V11.1 Non-Negotiables

1. Build a proprietary agent stack before claiming a proprietary base model.
2. Treat source governance, licensing, confidentiality, and approval state as hard infrastructure.
3. Use frontier models through a controlled architecture: routing, retrieval, tools, structured outputs, evals, traces, memory, and guardrails.
4. Keep biology outputs source-grounded and compliance-routed. Wet-lab, genetic engineering, CITES/Nagoya/LMO, IP, public/IR, legal, and investor-sensitive outputs require human approval.
5. Convert Deep Research and external benchmark material into `candidate -> needs_review -> approved -> ingested -> blocked` registry states before use in retrieval or training.
6. No agent swarm before the shared RAG Core, Registry, Eval, Compliance, and Trace systems are stable.
7. Every new framework or autonomous pattern requires complexity justification, rollback path, and eval evidence.

## Architecture Policy

Use the smallest sufficient pattern:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

A new framework or agent layer is allowed only when the PR states:

```text
Why simpler pattern fails:
Expected quality metric improvement:
Added latency/cost/security/debug burden:
Human approval and side-effect boundary:
Rollback path:
Eval/tracing evidence required:
```

## Ideal Control Plane

| Layer | Purpose | Required evidence before production claim |
|---|---|---|
| Source Registry | Approved-only source governance | Registry entries, license/confidentiality status, owner/date |
| Retrieval OS | Hybrid retrieval, rerank, citation packaging | Retrieval evals, source-hit report, citation regression |
| Answer Contract | Grounded, structured, uncertainty-aware outputs | Claim/evidence/span/confidence/compliance fields |
| Compliance Router | CITES/Nagoya/LMO/biosafety/IP/privacy escalation | Refusal/escalation tests and human approval records |
| Eval OS | Offline/online tests, golden tasks, red-team sets | Eval artifacts, thresholds, regression history |
| Trace OS | Workflow/model/tool/guardrail/span observability | Trace IDs, span coverage, cost/latency metadata |
| Agent Runtime | Specialist contracts, tools, handoffs, state | Tool contracts, state schema, approval graph, failure taxonomy |
| Data Flywheel | DBTL learning records and proprietary dataset versioning | Dataset versions, validation labels, experiment learning records |

## Priority Stack

| Priority | Workstream | Definition of Done |
|---|---|---|
| P0 | Source Registry / approved-only ingestion | Unapproved source cannot enter index |
| P0 | Retrieval eval + citation fidelity | Expected-source hit and citation-regression report exist |
| P0 | Grounded answer contract | Unsupported claims blocked or labeled |
| P0 | Compliance/security guardrails | CITES/Nagoya/LMO/biosafety/IP/privacy triggers tested |
| P1 | Deep Research -> Registry pipeline | Candidate/review/approved/ingested/blocked states separated |
| P1 | Literature / Benchmark Agent | Evidence-backed action item and limitation extracted |
| P1 | Trace/eval control plane | Workflow spans, eval artifacts, and regression history recorded |
| P2 | Hypothesis / Experiment Design Agent | Falsifiable hypothesis, safe abstract plan, approval gate |
| P2 | Biosafety / Compliance Router | Risk route, refusal, escalation verified |
| P3 | DBTL Planner + Failure Analysis | Failure taxonomy and next-cycle recommendation |
| P4 | Active Learning + Proprietary Dataset | Information-value ranking and dataset versioning |

## V11.1 PR Report Addendum

Every relevant future PR should include:

```text
V11.1 alignment:
Codex reasoning level: 매우높음 / 높음 / 중간 / 낮음
Changed surface:
Complexity level used:
Why simpler pattern is enough or insufficient:
Source registry impact:
Retrieval/citation impact:
Eval/trace impact:
Compliance/biosafety/IP/privacy review:
Production-status boundary:
Skipped checks and rationale:
Residual risks:
Next action:
```

## Stop Rules

Stop and escalate instead of implementing when:

- a source lacks license/confidentiality/approval status but would enter retrieval, training, or public output;
- the task would imply legal/regulatory approval without review;
- the task would automate wet-lab execution or risky genetic-engineering steps;
- the task adds an agent/framework only because it sounds impressive;
- the task claims production readiness without merged code, logs, eval artifacts, and approval evidence;
- the task expands beyond the PR scope or erases workflow boundaries.
