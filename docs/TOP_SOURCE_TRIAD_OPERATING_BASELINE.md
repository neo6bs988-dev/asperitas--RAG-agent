# Top Source Triad + V11.1 + P0+ AI Lead Operating Baseline

## Current Execution Authority (2026-07-11)

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) as the authoritative current-status and forward-performance control plane.

Latest confirmed baseline before this documentation sync:

- `main`: `1e437c4515cc664f6acdb6e5bb197aaf576d34af`;
- PR #166 guard hardening: merged after CI #250 and Quality Gates #381 succeeded;
- V1.10B diagnostic answer-sample reporting: merged;
- V1.10C preflight: merged;
- V1.10C six-file implementation: preserved locally and pending publication; not on `main`.

If an older status table or “next step” conflicts with the current-state roadmap, treat the older status wording as historical. Preserve its technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

Current mandatory sequence:

```text
V1.10C publication
-> V1.10 closure
-> representative biology/compliance eval reset
-> retrieval and reranker hardening
-> real grounded answer path and diagnostic verifier
-> compliance/security adversarial gates
-> trace, latency, token, and cost control plane
-> internal dogfood
-> approved data flywheel
-> web productization and production-readiness gates
```


## Executive Bottom Line

This repository must treat the Top Source Triad as the active development baseline for Asperitas AI-agent/RAG work, with the V11.1 Supergap Agent Build Leader layer and the P0+ AI Lead Operating Layer as the latest performance, governance, and organizational-learning hardening layers.

Top Source Triad:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

V11.1 add-on sources:

4. `슈퍼갭 GPT 채팅 모델용 고임팩트 PDF 트레이닝 패키지 설계 보고서.pdf`
5. `초고성능 독자 AI 에이전트 구축과 최종 업그레이드 트레이닝 PDF 설계 보고서.pdf`

P0+ AI Lead Operating Layer sources:

6. `글로벌 AI 리더·기업·엔지니어 종합 보고서.pdf`
7. `프로젝트 내 AI 리드 내재화 실행계획 보고서.pdf`

The triad, v11.1 layer, and P0+ AI Lead layer define how development should proceed. They do not prove implementation status.

## P0+ AI Lead Operating Layer

The P0+ layer upgrades the repository's operating model from prompt improvement alone to system improvement in this order:

```text
Prompt
-> Workflow
-> Evaluation
-> Governance
-> Organizational Learning
```

Codex and other development agents should act as an AI Lead / CTO-level workflow architect, evaluation owner, governance owner, adoption coach, and Digital Devil's Advocate. The practical output of this layer is not longer prose. It is reusable organizational machinery:

- playbooks
- SOPs
- checklists
- PR templates
- workflow contracts
- evaluation datasets
- failure taxonomies
- governance assets
- training packages
- decision logs
- adoption rituals

For significant work, use this compact operating contract when useful:

```text
Goal:
Scope:
Evidence:
Constraints:
Output:
Verification:
Stop Rules:
```

## Truth Boundary

Do not convert doctrine into implementation claims.

| Doctrine artifact | Must not be claimed as |
|---|---|
| Top Source Triad attached | Production RAG complete |
| V11.1 Supergap doctrine added | Proprietary agent stack implemented |
| P0+ AI Lead reports attached | AI Lead organization, eval system, governance OS, or adoption system implemented |
| Source map or source registry plan | Licensed production database |
| Roadmap or architecture ladder | Deployed AI product |
| Eval plan | Passing eval suite |
| Tracing/observability plan | Production trace coverage |
| Compliance gate design | Legal/regulatory approval |
| DBTL workflow plan | Wet-lab validation |
| Agent runtime roadmap | Autonomous agent safely deployed |
| Foundation-model direction | Foundation model capability |

Only claim production status when there is merged code, configuration, logs, eval output, release note, and human approval evidence.

## How Codex Should Use The Baseline

Before any major PR, Codex or another coding agent should classify the task using this sequence:

```text
Scope Lock
-> Source & Risk Preflight
-> Contract Design
-> Minimal Implementation
-> Eval Harness
-> Dry Run & Regression
-> Human Gate
-> Merge & Evidence Log
-> Learn Back
```

The P0+ layer adds an explicit learn-back step: whenever a repeated failure, ambiguity, review bottleneck, or verification gap is found, convert it into a durable repo asset rather than a one-off chat correction.

## Architecture Ladder

Use the smallest sufficient design:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

Do not introduce LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, ADK, MCP, or autonomous execution unless a simpler layer fails and there is a documented quality gain, cost/latency/security analysis, rollback path, and eval requirement.

## V11.1 Agent-Stack Doctrine

The near-term strategic target is not from-scratch frontier pretraining. The realistic and fundable target is a proprietary agent stack over frontier models:

```text
proprietary source registry and biological data
-> retrieval/reranking/citation control
-> structured answer contracts
-> tool and workflow interfaces
-> offline/online evals
-> red-team and regression gates
-> tracing and observability
-> compliance/security/human approval layer
-> DBTL learning records
-> proprietary dataset flywheel
```

This layer becomes a moat only when GitHub evidence proves measurable improvements in retrieval quality, citation fidelity, unsupported-claim blocking, biology/compliance routing, latency/cost, traceability, and DBTL learning-record quality.

## Development Priority Stack

| Priority | Workstream | Definition of done |
|---|---|---|
| P0 | Source Registry / approved-only ingestion | Unapproved sources cannot enter index |
| P0 | Retrieval eval + citation fidelity | Expected source hit and citation regression report exist |
| P0 | Grounded answer contract | Unsupported claims are blocked or labeled |
| P0 | Compliance/security guardrails | CITES/Nagoya/LMO/biosafety/IP/privacy triggers tested |
| P0+ | AI Lead operating layer | Playbooks, SOPs, eval ownership, governance gates, and learn-back assets are represented in repo artifacts |
| P1 | Deep Research -> Registry pipeline | Candidate/review/approved/ingested/blocked states separated |
| P1 | Literature / Benchmark Agent | Evidence-backed action item generated |
| P1 | Trace/eval control plane | Workflow spans, eval artifacts, and regression history recorded |
| P2 | Hypothesis / Experiment Design Agent | Falsifiable hypothesis + approval gate |
| P2 | Biosafety / Compliance Router | Risk route, refusal, escalation verified |
| P3 | DBTL Planner + Failure Analysis | Failure taxonomy and next-cycle recommendation |
| P4 | Active Learning + Proprietary Dataset | Information-value ranking and dataset versioning |

## Commercial End State

The end state is not an internal chatbot. The intended commercial path is:

```text
biodiversity access
-> proprietary biological data
-> source-grounded RAG/KG/eval control plane
-> AI-bio decision workflows
-> DBTL validation records
-> IP/compliance trust layer
-> web-productized internal/external platform
-> products/licensing
-> global biological infrastructure
```

## Required Report Block For Future PRs

Every relevant PR should report:

```text
Top Source Triad + V11.1 + P0+ AI Lead alignment:
Codex reasoning level: 매우높음 / 높음 / 중간 / 낮음
MVP / phase affected:
Changed files:
Complexity level used:
Why simpler pattern is enough or insufficient:
Verification:
Retrieval/citation impact:
Eval/trace impact:
Compliance/source-grounding review:
Governance/organizational-learning impact:
Web-productization impact:
Production-status boundary:
Skipped checks and rationale:
Residual risks:
Next action:
```
