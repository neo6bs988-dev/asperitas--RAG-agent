# Top Source Triad Operating Baseline

## Executive Bottom Line

This repository must now treat the Top Source Triad as the active development baseline for Asperitas AI-agent/RAG work:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

The triad defines how development should proceed. It does not prove implementation status.

## Truth Boundary

Do not convert doctrine into implementation claims.

| Doctrine artifact | Must not be claimed as |
|---|---|
| Top Source Triad attached | Production RAG complete |
| Source map or source registry plan | Licensed production database |
| Roadmap or architecture ladder | Deployed AI product |
| Eval plan | Passing eval suite |
| Compliance gate design | Legal/regulatory approval |
| DBTL workflow plan | Wet-lab validation |
| Foundation-model direction | Foundation model capability |

Only claim production status when there is merged code, configuration, logs, eval output, release note, and human approval evidence.

## How Codex Should Use The Triad

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

## Development Priority Stack

| Priority | Workstream | Definition of done |
|---|---|---|
| P0 | Source Registry / approved-only ingestion | unapproved sources cannot enter index |
| P0 | Retrieval eval + citation fidelity | expected source hit and citation regression report exist |
| P0 | Grounded answer contract | unsupported claims are blocked or labeled |
| P1 | Deep Research -> Registry pipeline | candidate/review/approved/ingested/blocked states separated |
| P1 | Literature / Benchmark Agent | evidence-backed action item generated |
| P2 | Hypothesis / Experiment Design Agent | falsifiable hypothesis + approval gate |
| P2 | Biosafety / Compliance Router | risk route, refusal, escalation verified |
| P3 | DBTL Planner + Failure Analysis | failure taxonomy and next-cycle recommendation |
| P4 | Active Learning + Proprietary Dataset | information-value ranking and dataset versioning |

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
Top Source Triad alignment:
MVP / phase affected:
Changed files:
Verification:
Retrieval/citation impact:
Compliance/source-grounding review:
Web-productization impact:
Skipped checks and rationale:
Residual risks:
Next action:
```
