# AI Development OS

The Asperitas AI Development OS is the operating model for building a source-grounded, eval-driven, compliance-native, biology-specific AI agent infrastructure with Codex, GitHub, tests, evals, reusable skills, and executable quality gates.

This document is an operating layer. Do not use it as proof that any database, retrieval system, graph system, evaluation system, tracing system, approval process, lab result, autonomous execution, commercial deployment, or biological foundation capability exists.

## Current Operating State

- V1.3 strengthened retrieval diagnostics, source coverage, answer contract, and truth/compliance routing.
- V1.4 strengthened token/context efficiency and closed optimization readiness.
- V1.5 is the current operating focus: gap closure, documentation sync, GitHub-native gates, performance hardening, and modular-agent readiness.
- V1.6 and later work should harden claim-to-citation verification, adversarial/security evals, biology/compliance golden sets, and measurable latency/cost/token performance.
- MVP-011 through MVP-013 define the web-productization and commercialization-readiness pathway after the internal RAG/API/UI foundation is credible.

The repository should be treated as Phase-0 core infrastructure: source registry, metadata, retrieval, answer contract, truth/compliance router, eval harnesses, decision logs, and agent scaffolds.

## Top Source Triad Baseline

Future development uses the Top Source Triad as operating doctrine:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

The triad is not implementation evidence. It defines how work should proceed: outcome-first, source-grounded, MVP-gated, audit-ready, compliance-aware, token-efficient, and Digital Devil's Advocate reviewed.

## Command Tower And Repo Engine

ChatGPT / Asperitas Project Chat is the command tower for synthesizing Deep Research, PDFs, AOS/PRIME doctrine, benchmark doctrine, user memory, and strategy into task-specific Codex prompts and strategic GO/NO-GO review.

Codex is the repo-aware implementation engine. It uses the distilled prompt plus `AGENTS.md`, `README.md`, repo docs, tests, evals, GitHub history, and CI evidence to implement, validate, package, and report changes. Codex should not request broad PDF uploads by default; request exact missing source text only when source ingestion, source registry status, citation-level evidence, or PDF-derived content is directly required.

PDF and Deep Research sources remain upstream operating doctrine. They guide work but do not certify implementation, deployment, approval, validation, readiness, or biological foundation capability.

## System Layers

| Layer | Purpose | Source of Truth |
|---|---|---|
| Strategy layer | Mission, benchmark doctrine, roadmap, operating philosophy | Project chat, AOS/PRIME docs, `README.md` |
| Source-triad layer | Latest operating baseline and development doctrine | `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md` |
| Agent instruction layer | Codex/agent behavior and stop rules | `AGENTS.md`, `.agents/skills/*` |
| Governance layer | Source priority, confidentiality, truth boundary, compliance | `docs/AOS_SOURCE_POLICY.md`, registry docs |
| Workflow layer | Human + Codex execution loop | `docs/WORKFLOW.md`, PR template |
| Quality layer | Tests, evals, CI, metrics, merge gates | `docs/QUALITY_GATES.md`, GitHub Actions |
| Productization layer | Backend/API, auth, web UI, observability, deployment, commercial gates | `docs/WEB_PRODUCTIZATION_ROADMAP.md` |
| Evidence layer | Implemented behavior, PRs, logs, releases | GitHub issues, PRs, CI, decision logs |

Project memory guides intent. GitHub evidence proves implementation.

## Workflow, Pipeline, Skill

- Workflow: the human + Codex loop from objective to verification, PR, review, merge, and next task.
- Pipeline: executable behavior such as ingestion, chunking, retrieval, embeddings, vector indexing, reranking, answer generation, eval, or compliance routing.
- Skill: reusable Codex instruction that defines when to act, what context to gather, which gates apply, how to fail safely, and how to report.

Use workflows to coordinate people, pipelines to run systems, and skills to make Codex repeat the right judgment.

## Benchmark Conversion Rule

Benchmark sources are P6 doctrine. They are useful only when converted into controls and evals:

```text
Benchmark pattern
-> failure mode
-> Asperitas-specific operating control
-> measurable gate
-> GitHub PR evidence
```

Do not claim a benchmark capability is implemented until code, docs, tests, evals, and PR evidence prove it.

## How The Pieces Work Together

- `README.md` states the repository mission, truth boundary, benchmark doctrine, roadmap, and tool doctrine.
- `AGENTS.md` defines repo-wide agent behavior, safety rules, testing expectations, report format, and stop rules.
- `docs/AI_DEVELOPMENT_OS.md` explains this full operating system.
- `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md` defines the active source triad and how future development must use it.
- `docs/WEB_PRODUCTIZATION_ROADMAP.md` defines the path from internal RAG/API/UI to web app and commercialization gates.
- `docs/CODEX_NEXT_PROMPT_WEB_PRODUCTIZATION.md` provides the next Codex-ready prompt for this workstream.
- `docs/WORKFLOW.md` defines the standard human + Codex loop.
