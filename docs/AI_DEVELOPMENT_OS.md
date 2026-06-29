# AI Development OS

The Asperitas AI Development OS is the operating model for building a source-grounded, eval-driven, compliance-native, biology-specific AI agent infrastructure with Codex, GitHub, tests, evals, reusable skills, and executable quality gates.

This document is an operating layer, not evidence that production RAG, vector DB, KG, legal review, wet-lab validation, autonomous lab operation, or a biological foundation model is complete.

## Current Operating State

- V1.3 strengthened retrieval diagnostics, source coverage, answer contract, and truth/compliance routing.
- V1.4 strengthened token/context efficiency and closed optimization readiness.
- V1.5 is the next operating focus: gap closure, documentation sync, GitHub-native gates, performance hardening, and modular-agent readiness.

The repository should be treated as Phase-0 core infrastructure: source registry, metadata, retrieval, answer contract, truth/compliance router, eval harnesses, decision logs, and agent scaffolds.

## System Layers

| Layer | Purpose | Source of Truth |
|---|---|---|
| Strategy layer | Mission, benchmark doctrine, roadmap, operating philosophy | Project chat, AOS/PRIME docs, `README.md` |
| Agent instruction layer | Codex/agent behavior and stop rules | `AGENTS.md`, `.agents/skills/*` |
| Governance layer | Source priority, confidentiality, truth boundary, compliance | `docs/AOS_SOURCE_POLICY.md`, registry docs |
| Workflow layer | Human + Codex execution loop | `docs/WORKFLOW.md`, PR template |
| Quality layer | Tests, evals, CI, metrics, merge gates | `docs/QUALITY_GATES.md`, GitHub Actions |
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
- `docs/WORKFLOW.md` defines the standard human + Codex loop.
- `docs/QUALITY_GATES.md` defines checks that must pass before work is called done.
- `docs/AOS_SOURCE_POLICY.md` defines source priority, disclosure, evidence labels, and do-not-confuse boundaries.
- `docs/V1_5_PERFORMANCE_ROADMAP.md` defines the current performance-hardening path.
- `.github/pull_request_template.md` makes scope, tests, metrics, source grounding, and compliance explicit.
- GitHub Actions run executable CI gates when configured.
- Tests and evals prove behavior.
- Decision logs preserve why choices were made.

## Default Operating Loop

1. Define the outcome and success criteria.
2. Read `AGENTS.md`, relevant docs, and relevant skills.
3. Inspect existing files before editing.
4. Choose the smallest safe change.
5. Run the smallest sufficient checks.
6. Report changed files, verification, metrics, risks, skipped checks, and next step.
7. Open a PR with truth boundary and validation notes.
8. Use GitHub Actions and review to decide merge readiness.
9. Merge only when scope and pass/fail evidence are clear.
10. Update the next Codex prompt based on gaps found.

## Performance Doctrine

Token minimization must never reduce reasoning quality. Reduce useless context, not critical evidence.

Performance claims require evidence:

- token reduction requires before/after token or context metrics;
- latency improvement requires net runtime improvement, not only cache hits;
- retrieval improvement requires before/after retrieval metrics;
- answer improvement requires faithfulness/citation/unsupported-claim evidence;
- compliance improvement requires refusal/escalation/adversarial evidence.

## Tooling Doctrine

Use additional tools when they materially improve quality, speed, reproducibility, or safety more than they increase complexity or risk.

Default roles:

| Tool | Role |
|---|---|
| ChatGPT | Strategy, architecture, prompt design, review, GO/NO-GO |
| Codex | Implementation, tests, branch work, PR packaging |
| GitHub | Issues, PRs, CI, audit trail, release evidence |
| GitHub Actions | PR/main validation gates |
| VS Code / terminal | Local debugging and manual inspection |
| Claude Code / Cursor / Copilot | Review/refactor/alternative analysis; avoid concurrent same-branch edits |
| Ragas / DeepEval / ARES-style evals | RAG/agent quality measurement when appropriate |
| Semgrep / gitleaks / Dependabot / Trivy | Security, secret, dependency, and supply-chain checks |
| Qdrant / Chroma / Neo4j | Vector DB and KG candidates after governance stabilizes |
| BioPython / RDKit / ESM / AlphaFold-class tools | Biology ML/DL stage after source/compliance controls |

Do not add frameworks or services without a Scout -> License -> Security -> Benchmark -> Adapt -> Test ledger.

## Reuse For Future Asperitas Agents

To reuse this system:

1. Copy `README.md`, `AGENTS.md`, `docs/AI_DEVELOPMENT_OS.md`, `docs/WORKFLOW.md`, `docs/QUALITY_GATES.md`, `docs/AOS_SOURCE_POLICY.md`, and relevant `.agents/skills`.
2. Replace project mission, source hierarchy, compliance domains, and roadmap.
3. Keep the gate pattern: inspect, plan, implement, test/eval, review, report.
4. Add agent-specific skills only when repeated work needs a dedicated checklist.
5. Keep every skill tied to inputs, commands, quality gates, and failure conditions.
6. Add CI only after commands are stable enough to run repeatedly.

Do not treat this OS as static. Update it when repeated mistakes, new risks, new pipelines, or new stages appear.
