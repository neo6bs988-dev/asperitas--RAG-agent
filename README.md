# Asperitas AI RAG Agent

## Current Execution Authority (2026-07-11)

Use [`docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](docs/CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) as the authoritative current-status and forward-performance control plane. For files already inside `docs/`, the path refers to `CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md` in the same directory.

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

This repository is the execution base for the Asperitas Biological Intelligence OS: a source-grounded, auditable, compliance-aware AI agent infrastructure for converting biodiversity access into structured biological data, AI-bio workflows, DBTL validation, IP, products, compliance trust, and platform advantage.

This is not a generic chatbot repository. The target is a benchmark-beating biological intelligence infrastructure layer: every feature must improve source traceability, factual accuracy, evaluation coverage, compliance safety, biological relevance, workflow leverage, or long-term data moat.

## Current Truth Boundary

This repository is the Phase-0 core for Asperitas internal RAG and agent development. It may contain prompts, source registries, retrieval logic, eval harnesses, governance docs, and agent scaffolds. It must not be described as any of the following unless a merged PR, test log, release note, and decision log prove it:

| Do Not Confuse | With |
|---|---|
| Source map or registry | Production database fully ingested |
| Prompt or architecture document | Deployed autonomous agent |
| Chunk files or fixtures | Production vector database |
| Benchmark doctrine | Asperitas internal fact |
| Retrieval/eval scaffold | Full RAG/KG/eval production system |
| Agent-stack roadmap | Not proof that a proprietary agent stack is implemented |
| Model output or hypothesis | Wet-lab validation |
| Compliance checklist | Legal or regulatory approval |
| Investor or market signal | Committed capital or product-market fit |
| RAG agent core | Proprietary biological foundation model |

If only a plan exists, say plan. If only a scaffold exists, say scaffold. If evidence is missing, label the gap.

## Mission

Turning Biodiversity into Biotechnology.

Asperitas must build the operating infrastructure that compounds:

```text
Biodiversity access
-> proprietary biological data
-> structured metadata
-> source-grounded RAG/KG
-> AI-bio models and agents
-> DBTL validation
-> biological IP
-> compliance trust
-> products/licensing
-> platform revenue
-> biological infrastructure moat
```

## Active Constitution

The active operating constitution is:

```text
ASPERITAS PRIME v2.0
= AOS v8.0 Core
+ AOS v9.0 Strategic Upgrade
+ AOS v10.0 Source-Grounded Agent Layer
+ AOS v10.2 Universal Prompt Principles
+ AOS v10.3 Advanced Prompt Layer
+ AOS v10.4 Security/Privacy/Eval/Token Discipline
+ AOS v11.0 Outcome-First Reasoning
+ V11.1 Supergap Agent Build Leader Doctrine
+ user-approved project memory and GitHub evidence
```

Earlier AOS layers remain inherited doctrine unless a later safe instruction explicitly supersedes them. The latest user instruction can override execution details, but never safety, legality, scientific truth, biosafety, source integrity, or compliance.

V11.1 adds two practical rules:

1. Build a proprietary agent stack over frontier models before claiming any proprietary base model or foundation-model capability.
2. Treat data flywheel, agent runtime, evals, tracing, tool interfaces, safety/security/governance, source-grounded RAG, biosafety gates, DBTL support, and GitHub verification as one operating system.

## V11.1 Control Documents

- `docs/V11_1_SUPERGAP_AGENT_BUILD_LEADER.md` — latest doctrine for proprietary agent stack, data flywheel, eval/trace/control-plane, compliance gates, and non-overclaim boundaries.
- `docs/IDEAL_REPO_STRUCTURE_V11_1.md` — target repo architecture and stage-gated folder model.
- `docs/CODEX_NEXT_PROMPT_V11_1_REPO_ALIGNMENT.md` — Codex-ready prompt for the next implementation PR with explicit reasoning level.
- `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md` — active Top Source Triad plus v11.1 add-on baseline.

## Historical Constitution References

The current README and AGENTS files are the compact active operating layer. The earlier long-form PRIME v2.0 README and AGENTS versions were not discarded; they remain in Git history and are indexed for future reference:

- `docs/archive/README_PRE_V15_PRIME_V2.md`
- `docs/archive/AGENTS_PRE_V15_PRIME_V2.md`

These archives are historical context only. Active execution follows this README, `AGENTS.md`, `docs/AI_DEVELOPMENT_OS.md`, `docs/WORKFLOW.md`, `docs/QUALITY_GATES.md`, `docs/AOS_SOURCE_POLICY.md`, `docs/V1_5_PERFORMANCE_ROADMAP.md`, `docs/V11_1_SUPERGAP_AGENT_BUILD_LEADER.md`, latest user instruction, and GitHub PR/CI evidence.

## Benchmark Doctrine

Benchmarking is not decoration. It is a P6 operating layer used to extract durable engineering principles from top AI, data, infrastructure, biotech, VC, and unicorn company patterns.

P6 benchmark doctrine may influence how we design systems, but it must never be presented as Asperitas internal proof. The benchmark rule is:

```text
Benchmark -> failure mode -> Asperitas-specific control -> eval gate -> PR evidence
```

A feature is not benchmark-beating because the document says so. It becomes benchmark-beating only when it passes measurable gates:

- higher retrieval quality without source-boundary loss
- stronger claim-to-evidence alignment
- lower hallucination and overclaim rate
- better refusal/escalation behavior on risky tasks
- lower token, cost, or latency with no answer-quality regression
- stronger security and data-leakage resistance
- clearer GitHub audit trail and reproducibility
- stronger biology-specific decision quality

## Workflow Complexity and Security Doctrine

AI-assisted development speed must not flatten the agent workflow. Vibe-coded shortcuts are acceptable only when they preserve the real system boundaries, audit trail, tests, diagnostics, and future eval hooks.

The verifier and RAG workflow must remain separable:

```text
source registry/raw sources
-> parsing/chunking
-> metadata/evidence span layer
-> retrieval/reranking
-> answer contract
-> atomic claim extraction
-> evidence-span matching
-> support-status classification
-> report aggregation
-> answer contract integration
-> adversarial/security eval
-> biology/compliance golden set
-> metrics/regression gate
```

Do not collapse extraction, matching, classification, report aggregation, and answer integration into one broad helper. Small PRs are required, but small PRs must not oversimplify the architecture or hide state transitions.

V1.5 and later work must preserve four completion pillars:

| Pillar | Requirement |
|---|---|
| Golden set | Biology/compliance-specific claim verification ground truth, including entity, numeric, citation, unsupported, contradicted, and compliance-sensitive cases |
| Report aggregation | Claim-level support results aggregated into answer-level diagnostics and blocker/warning signals |
| Adversarial/security eval pack | Wrong citation, unsupported claim, numeric mismatch, biology entity mismatch, compliance overclaim, prompt injection, secret leakage, unsafe tool use, and excessive-agency tests |
| Metrics/regression gate | False-supported rate, false-contradicted rate, citation-mismatch detection, unsupported detection recall, compliance-sensitive recall, latency, cost, and workflow-boundary regressions |

Security is a first-class gate, not a final cleanup step. New code must preserve least privilege, avoid unnecessary network/cloud/service calls, treat retrieved or external text as untrusted input, protect secrets and confidential source text, and avoid autonomous changes to production-like data, source registries, vector DBs, KGs, deployment configuration, legal/compliance status, or wet-lab status.

## Hard Filters

Every major initiative must pass three non-negotiable filters:

| Filter | Question |
|---|---|
| Scalability | Can this scale from script to workflow to platform to infrastructure? |
| Moat | Does this create defensibility through data, IP, validation, workflow lock-in, regulatory trust, or partner ecosystem? |
| Biosafety / Compliance | Does this preserve CITES, Nagoya, LMO, biosafety, biosecurity, privacy, IP, legal, and auditability requirements? |

If any filter fails, the task must be blocked, narrowed, or reframed.

## Source Hierarchy

| Priority | Source Type | Use |
|---|---|---|
| P0 | Latest user instruction / active prompt constitution | Current execution rule unless unsafe or false |
| P1 | Internal Asperitas source-of-truth documents | Internal facts, strategy, AOS doctrine |
| P2 | Official Asperitas public sources | Approved external positioning |
| P3 | Peer-reviewed science and technical databases | Biological mechanism and technical claims |
| P4 | Government, regulatory, institutional sources | Law, grants, compliance, policy, eligibility |
| P5 | Industry, market, investor, conference intelligence | Market signals, competitors, adoption patterns |
| P6 | External benchmark and operating doctrine | Analogy and process doctrine, not company fact |

When sources conflict, prefer the source class that matches the claim type. Use P1 for internal company facts, P3 for technical biology, P4 for law and compliance, and P6 only for analogy or operating design.

## Evidence Labels

Every material claim should be labeled when possible:

- Document-Supported Fact
- Official Source
- Peer-Reviewed Evidence
- Regulatory Source
- Industry Signal
- Inference
- Speculation
- Needs External Verification

Never upgrade speculation into fact. Never attach citations as decoration. Citations must support the exact claim they are attached to.

## Current Development Operating Model

GitHub is the execution headquarters. ChatGPT/project memory is strategic context. GitHub is implementation evidence.

```text
Issue
-> branch
-> implementation
-> targeted local tests
-> eval gates
-> PR
-> GitHub Actions
-> review
-> merge
-> release/decision log
```

No direct edits to `main` unless explicitly approved for emergency maintenance. Prefer draft PRs for agent-generated work until validation is clear.

## Core Build Order

Build in this order unless a higher-priority safe instruction overrides it:

1. Source registry
2. Metadata schema
3. File inventory
4. Source priority and confidentiality policy
5. Decision logs
6. Ingestion and chunking
7. Retrieval quality evaluation
8. Grounded answer contract
9. Truth/compliance router
10. Token, cost, and latency measurement
11. Claim-to-citation verifier
12. Adversarial and security eval pack
13. Biology-specific golden set
14. Trace/eval control plane
15. Vector database and KG integration
16. Modular agent pack
17. Workflow/API/UI integration
18. ML/DL optimization layer
19. Foundation-model-readiness data flywheel

Do not split into many autonomous agents before the shared RAG core, eval suite, source registry, compliance gates, and trace/eval control plane are stable.

## Performance Roadmap

| Phase | Goal | Non-Negotiable Gate |
|---|---|---|
| V1.5 | Gap closure and performance hardening | README/AGENTS UTF-8, GitHub-native milestones, metric logs, no v1.4 regression |
| V1.6 | Claim-to-citation verifier | Atomic claims graded supported/unsupported/contradicted against evidence spans |
| V1.7 | Adversarial/security evals | Prompt injection, source poisoning, PII leakage, excessive agency, biosafety over-answer tests |
| V1.8 | Biology-specific golden set | Nagoya/CITES/LMO, DBTL, pathway/protein, IP/compliance boundary tasks |
| V1.9 | Real latency optimization | p50/p95 latency reduction with no retrieval or answer-quality regression |
| V2.0 | Vector DB/KG production pathway | Approved ingestion, embedding/index logs, KG links, eval-ready evidence |
| V3.0 | Modular agents | Shared core, scoped tools, schema outputs, approval gates, agent-specific evals |
| V4.0 | ML/DL performance layer | Custom embedding/reranker/classifiers or fine-tuning only after benchmark and safety gates |
| V5.0 | Foundation model readiness | Proprietary, validated, diverse, metadata-rich biological data and DBTL feedback loops |

## Evaluation Standard

RAG and agent performance must be judged at the right layer:

- Retrieval: Recall@k, Precision@k, MRR, nDCG, source coverage, expected-source hit rate
- Generation: faithfulness, answer relevance, unsupported-claim rate, citation accuracy
- Safety: refusal accuracy, escalation accuracy, confidential-data leakage, unsafe bio output blocking
- Operations: test pass rate, CI reliability, artifact integrity, decision-log completeness
- Efficiency: retrieved-context tokens, answer tokens, cost, p50/p95 latency, cache hit rate with net runtime impact
- Biology: mechanism quality, DBTL usefulness, compliance boundary accuracy, validation-status honesty

Metric improvements must preserve source IDs, source priorities, source paths, evidence labels, section metadata, and truth-boundary fields.

## Tooling Doctrine

Use tools when they increase quality, speed, reproducibility, or safety more than they increase complexity or risk.

Default tool roles:

| Tool | Role |
|---|---|
| ChatGPT | Strategy, architecture, prompt design, review, GO/NO-GO, executive synthesis |
| Codex | Implementation, tests, branch work, PR packaging |
| GitHub | Issues, PRs, CI, audit trail, releases, decision evidence |
| GitHub Actions | Pull request and main-branch validation gates |
| VS Code / terminal | Local debugging and manual inspection |
| Claude Code / Cursor / Copilot | Review, refactor, alternative analysis; do not edit same branch concurrently |
| Ragas / DeepEval / ARES-style evals | RAG and agent quality measurement when appropriate |
| Semgrep / gitleaks / Dependabot / Trivy | Security, secret, dependency, and supply-chain checks |
| Qdrant / Chroma / Neo4j | Vector DB and KG candidates after source governance is stable |
| BioPython / RDKit / ESM / AlphaFold-class tools | Biology ML/DL stage after data governance and validation design |

Do not add frameworks or services without a Scout -> License -> Security -> Benchmark -> Adapt -> Test ledger.

## Validation Rules

After any change, run the smallest sufficient verification:

- Documentation-only: markdown review, link/path sanity, truth-boundary review
- Code change: targeted tests plus relevant lint/type/schema checks
- Retrieval change: retrieval evals and source coverage checks
- Answer-generation change: answer contract, faithfulness, citation, refusal/escalation evals
- Security/compliance change: adversarial, leakage, and compliance gate tests
- Release/main: full suite, artifact readiness, retrieval/golden evals, metric gates, diff checks

If validation cannot run, state why and provide the next-best check. Never claim tests passed unless they were actually run.

## Required Task Report

Every implementation or review should end with:

```text
Changed files:
Verification:
Retrieval metrics:
Compliance/source-grounding review:
Risks or skipped checks:
Recommended next step:
```

## V11.1 Required PR Addendum

Every governance, RAG, eval, compliance, security, or agent-workflow PR should also include:

```text
V11.1 alignment:
Codex reasoning level: 매우높음 / 높음 / 중간 / 낮음
Complexity level used:
Why simpler pattern is enough or insufficient:
Eval/trace impact:
Production-status boundary:
```

## Final Repository Rule

Always optimize for truth, leverage, scientific rigor, operational discipline, governance integrity, regulatory trust, biosafety, source traceability, adoption velocity, capital efficiency, and long-term compounding advantage.

The permanent belief:

```text
Asperitas must build infrastructure, not just products.
Validated data, not just narratives.
Operating loops, not just prompts.
Biological intelligence factories, not just experiments.
Trust, not just technology.
```
