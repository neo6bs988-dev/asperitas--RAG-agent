# AI Development OS

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This document defines the durable operating model. It must not duplicate mutable phase names, commit SHAs, or next-step claims. Any older embedded phase wording is historical and cannot override the canonical roadmap.

The Asperitas AI Development OS is the operating model for building a source-grounded, eval-driven, compliance-native, biology-specific AI agent infrastructure with Codex, GitHub, tests, evals, reusable skills, and executable quality gates.

This document is an operating layer. Do not use it as proof that any database, retrieval system, graph system, evaluation system, tracing system, approval process, lab result, autonomous execution, commercial deployment, or biological foundation capability exists.

## Current Operating State

The live phase, completed milestones, and immediate next action are controlled by the canonical current-state roadmap and merged GitHub evidence.

Durable repository state:

- the repository is Phase-0 internal RAG/agent infrastructure, not a production deployment;
- deterministic source registry, metadata, retrieval, answer-contract, evaluator, governance, and audit scaffolds exist in varying maturity;
- public-safe synthetic evaluation infrastructure does not prove protected-holdout generalization or production answer quality;
- production vector DB/KG, legal approval, wet-lab validation, autonomous execution, and foundation-model capability remain evidence-gated claims.

## Top Source Triad Baseline

Future development uses the Top Source Triad as operating doctrine:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

The triad is not implementation evidence. It defines how work should proceed: outcome-first, source-grounded, MVP-gated, audit-ready, compliance-aware, token-efficient, and Digital Devil's Advocate reviewed.

## Command Tower and Repository Engine

ChatGPT / Asperitas Project Chat is the command tower for synthesizing Deep Research, PDFs, AOS/PRIME doctrine, benchmark doctrine, user memory, and strategy into task-specific Codex prompts and strategic GO/NO-GO review.

Codex is the repository-aware implementation engine. It uses the distilled prompt plus `AGENTS.md`, `README.md`, repository docs, tests, evals, GitHub history, and CI evidence to implement, validate, package, and report changes. Codex should not request broad PDF uploads by default; request exact missing source text only when source ingestion, source registry status, citation-level evidence, or PDF-derived content is directly required.

PDF and Deep Research sources remain upstream operating doctrine. They guide work but do not certify implementation, deployment, approval, validation, readiness, or biological foundation capability.

## System Layers

| Layer | Purpose | Source of Truth |
|---|---|---|
| Strategy layer | Mission, benchmark doctrine, roadmap, operating philosophy | Project chat, AOS/PRIME docs, `README.md` |
| Current-state layer | Active status, completion claims, next phase | Canonical current-state roadmap + live GitHub evidence |
| Source-triad layer | Operating baseline and development doctrine | `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md` |
| Agent instruction layer | Codex/agent behavior and stop rules | `AGENTS.md`, `.agents/skills/*` |
| Governance layer | Source priority, confidentiality, truth boundary, compliance | `docs/AOS_SOURCE_POLICY.md`, registry docs |
| Workflow layer | Human + Codex execution loop | `docs/WORKFLOW.md`, PR template |
| Quality layer | Tests, evals, CI, metrics, merge gates | `docs/QUALITY_GATES.md`, GitHub Actions |
| Productization layer | Backend/API, auth, web UI, observability, deployment, commercial gates | `docs/WEB_PRODUCTIZATION_ROADMAP.md` |
| Evidence layer | Implemented behavior, PRs, logs, releases | GitHub issues, PRs, CI, decision logs |

Project memory guides intent. GitHub evidence proves implementation.

## Architecture Ladder

Use the smallest sufficient layer:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

Escalation requires evidence that the simpler layer fails, expected quality gain, added latency/cost/security burden, approval boundaries, rollback, and an evaluation plan.

## Development Loop

```text
Scope Lock
-> Source and Risk Preflight
-> Contract Design
-> Minimal Implementation
-> Eval Harness
-> Dry Run and Regression
-> Human Gate
-> Merge and Evidence Log
-> Learn Back
```

## Non-Overclaim Rule

Always separate:

- confirmed implementation;
- reasonable inference;
- unverified or unimplemented state;
- evidence required to upgrade the claim.

No roadmap, doctrine, source registry, synthetic fixture, benchmark report, or generated output is sufficient evidence for production readiness, compliance approval, wet-lab validation, autonomous execution, proprietary data moat, or foundation-model capability.
