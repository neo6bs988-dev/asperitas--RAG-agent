# AI Development OS

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
- `docs/QUALITY_GATES.md` defines checks that must pass before work is called done.
- `docs/AOS_SOURCE_POLICY.md` defines source priority, disclosure, evidence labels, and do-not-confuse boundaries.
- `docs/V1_5_PERFORMANCE_ROADMAP.md` defines the current performance-hardening path.
- `.github/pull_request_template.md` makes scope, tests, metrics, source grounding, and compliance explicit.
- GitHub Actions run executable CI gates when configured.
- Tests and evals prove behavior.
- Decision logs preserve why choices were made.

## Default Operating Loop

1. Define the outcome and success criteria.
2. Read `AGENTS.md`, relevant docs, the Top Source Triad baseline, and relevant skills.
3. Inspect existing files before editing.
4. Choose the smallest safe change.
5. Run the smallest sufficient checks.
6. Report changed files, verification, metrics, risks, skipped checks, and next step.
7. Open a PR with truth boundary and validation notes.
8. Use GitHub Actions and review to decide merge readiness.
9. Merge only when scope and pass/fail evidence are clear.
10. Update the next Codex prompt based on gaps found.

## V1.5A Harness-First Discipline

V1.5A makes the default development loop harness-first, cost-aware, and regression-safe:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

Every task should name risk level, changed surface, verification scope, skipped checks, residual risk, and metric provenance before merge readiness is claimed.

Cheap QA means re-reading edited files, checking headings/paths/code fences, inspecting the diff, and running `git diff --check`. Targeted verification means running the smallest command set that protects the changed surface. Full suites, broad retrieval evals, release gates, or expanded GitHub Actions coverage are reserved for high-risk work, release/main work, CI/config changes, core RAG/eval/compliance/security changes, or behavior-changing source code.

Metrics must be labeled as `Fresh Run`, `Historical`, or `Not Run`. GitHub Actions disconnections, cancellations, and timeouts are validation-scope evidence, not product failures unless required gates remain unclear, fail, or cannot be rerun.

## Web Productization Discipline

Internal RAG/API/UI is not commercial readiness. Web productization must be gated:

```text
internal source-grounded RAG core
-> verifier/compliance/eval hardening
-> internal API/UI
-> backend/API/provider/auth/observability contract
-> authenticated web app MVP
-> production readiness gate
-> commercial product pathway
```

The web product must keep the LLM provider replaceable. Asperitas's proprietary layer is the source registry, biological metadata, retrieval/evidence pipeline, verifier, compliance gate, eval suite, DBTL/failure records, IP/product decision workflow, and proprietary biological dataset path.

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
| FastAPI / Next.js / Vercel / Render / AWS / GCP | Web productization candidates only after MVP-011 scope lock and security review |

Do not add frameworks or services without a Scout -> License -> Security -> Benchmark -> Adapt -> Test ledger.

## Reuse For Future Asperitas Agents

To reuse this system:

1. Copy `README.md`, `AGENTS.md`, `docs/AI_DEVELOPMENT_OS.md`, `docs/WORKFLOW.md`, `docs/QUALITY_GATES.md`, `docs/AOS_SOURCE_POLICY.md`, and relevant `.agents/skills`.
2. Replace project mission, source hierarchy, compliance domains, and roadmap.
3. Keep the gate pattern: inspect, plan, implement, test/eval, review, report.
4. Add agent-specific skills only when repeated work needs a dedicated checklist.
5. Keep every skill tied to inputs, commands, quality gates, and failure conditions.
6. Add CI only after commands are stable enough to run repeatedly.
7. Add web-productization layers only after internal source-grounded behavior is stable and testable.

Do not treat this OS as static. Update it when repeated mistakes, new risks, new pipelines, new stages, or web-productization gates appear.
