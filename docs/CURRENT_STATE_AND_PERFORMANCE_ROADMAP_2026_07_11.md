# Current State and Performance Roadmap — 2026-07-11

## Authority

This document is the current execution-status and forward-performance control plane for `neo6bs988-dev/asperitas--RAG-agent`.

When an older planning document conflicts with this document about whether a phase is completed, active, pending, or production-ready, use this document together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence.

Older documents remain authoritative for their scoped technical contracts, acceptance criteria, risk analysis, and historical decisions. They are not deleted or silently rewritten.

## Source Doctrine

The active doctrine stack is:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`
4. `슈퍼갭 GPT 채팅 모델용 고임팩트 PDF 트레이닝 패키지 설계 보고서.pdf`
5. `초고성능 독자 AI 에이전트 구축과 최종 업그레이드 트레이닝 PDF 설계 보고서.pdf`
6. `AI_Top50_Development_Workflow_Benchmark_Asperitas_KR.pdf`
7. `글로벌 AI 리더·기업·엔지니어 종합 보고서.pdf`
8. `프로젝트 내 AI 리드 내재화 실행계획 보고서.pdf`
9. `Asperitas_Ultimate_Prompt_Command_v10_4_20260628.pdf`

These sources define operating doctrine and future direction. They do not prove implementation, deployment, biological validation, legal review, regulatory approval, production readiness, proprietary foundation-model capability, or autonomous wet-lab capability.

## Latest Confirmed GitHub Baseline

As of 2026-07-11:

- latest confirmed `main`: `1e437c4515cc664f6acdb6e5bb197aaf576d34af`;
- PR #166 was squash-merged after CI #250 and Quality Gates #381 succeeded;
- PR #166 changed exactly four protected-state guard test files;
- the merged guard hardening makes protected-state checks independent of Git index staging state;
- V1.10B answer-sample diagnostic reporting is merged;
- V1.10C docs-only preflight is merged;
- the V1.10C six-file implementation is reported as preserved in a separate local worktree but is not yet committed, pushed, reviewed, or merged;
- therefore V1.10C implementation is not on `main`.

PR #166 improves test integrity only. It does not improve runtime retrieval, generation, biological decision quality, compliance approval, or production readiness.

## Reconciled Capability State

| Capability | Confirmed state | Boundary |
|---|---|---|
| Repository foundation and deterministic test harness | Implemented and repeatedly exercised | Not production deployment |
| Source registry and processed artifacts | Repository artifacts and validators exist | Not proof of complete licensed production ingestion |
| MVP-004 structure-aware chunking closure | Closed by recorded quality-gate evidence | Historical status tables saying pending are stale |
| Deterministic `mvp003` retrieval | Implemented reference mode | Current fixtures are limited |
| Offline vector retrieval mode | Implemented comparison mode | Not a selected production vector backend |
| Hybrid retrieval mode | Implemented and accepted for comparison | Not default; current 32-question result includes fixture-specific section expectations |
| Reranker interface and deterministic test reranker | Plumbing implemented | Test reranker regressed source@3 and is not a quality-improvement claim |
| Source-grounded answer contracts and internal workflow scaffolds | Contracts/scaffolds exist | Real RAG answer provider is not the default production path |
| Security, audit, failure-log, readiness, and internal dry-run layers | Repository controls exist | Not external customer deployment or approval authority |
| Biology/compliance golden-set validator and offline evaluator | Deterministic diagnostic infrastructure exists | Synthetic/offline evidence only |
| V1.10B answer-sample report | Merged diagnostic report | No runtime capture, blocking, or approval |
| V1.10C stable evaluator sample IDs | Local implementation reported; publication pending | Not on `main` until separate PR passes and merges |
| Internal UI/API and web product | Planned/partially scaffolded depending on component | Not authenticated commercial SaaS |
| Production vector DB and KG | Not confirmed | Requires implementation, data, eval, security, and release evidence |
| Proprietary foundation model for biology | Strategic direction only | Requires proprietary validated data and DBTL feedback at scale |

## Current Bottleneck

The next performance gap is not lack of another agent framework.

The main bottlenecks are:

1. small and partially synthetic evaluation fixtures;
2. retrieval results that can saturate current fixtures without proving holdout generalization;
3. fixture-specific expected-section information in the accepted hybrid evaluation path;
4. a deterministic test reranker that validates plumbing but lowers source@3;
5. real answer-provider integration and claim-to-citation verification not yet proven as a production-shaped path;
6. insufficient online/internal-dogfood traces for latency, cost, failure, and operator-review learning;
7. the proprietary biological data and DBTL learning flywheel remains a future moat, not a completed asset.

After V1.10C closes, development must shift from evaluator/report scaffolding toward representative data, holdout evaluation, real grounded answers, measurable retrieval/reranking improvements, compliance routing, and internal dogfood.

## Mandatory Development Order

```text
test-integrity closure
-> V1.10C stable sample identity
-> V1.10 final closure
-> representative biology/compliance eval reset
-> retrieval and reranker hardening
-> real source-grounded answer path
-> claim-to-citation verifier in diagnostic/shadow mode
-> compliance/security adversarial gates
-> tracing, latency, token, and cost control plane
-> internal API/UI dogfood
-> approved Deep Research-to-Registry data flywheel
-> authenticated web productization
-> production-readiness gate
-> evidence-driven KG, DBTL, active learning, and foundation-model readiness
```

Do not reorder this sequence merely to add fashionable frameworks.

## Phase 0 — V1.10C Publication

Required sequence:

1. update the preserved local V1.10C worktree onto the merged guard-hardening `main`;
2. preserve exactly the approved six-file V1.10C implementation scope;
3. rerun V1.10C targeted evaluator/report checks;
4. verify 13/13 deterministic stable-ID joins with zero unmatched rows;
5. preserve the existing 13-case outcome distribution unless an independently scoped scoring change is approved;
6. run artifact verification and `git diff --check`;
7. run the full suite once under the hardened guards;
8. commit, push, and open a separate Draft PR;
9. require GitHub Actions and human review before merge.

V1.10C must remain deterministic, stdlib-only, diagnostic-only, and independent of runtime behavior.

## Phase 1 — Evaluation Reset

Build a versioned representative benchmark that separates development and holdout data.

Required task families:

- biodiversity and species provenance;
- CITES, Nagoya, LMO, biosafety, privacy, and licensing boundaries;
- protein, pathway, mechanism, and biological-activity claims;
- DBTL planning and validation-status honesty;
- IP, partner, investor, and public-claim boundaries;
- insufficient-evidence, contradiction, citation mismatch, refusal, and escalation;
- prompt injection, malicious retrieved text, source poisoning, secret leakage, and excessive agency.

Required controls:

- stable task and sample IDs;
- explicit source and evidence-span labels;
- development/holdout separation;
- multi-valid-source handling separated from strict match metrics;
- no expected-answer fields exposed to the runtime retrieval path;
- human-reviewed gold labels for high-risk tasks;
- dataset/version provenance and change log;
- failure taxonomy connected to regression tests.

## Phase 2 — Retrieval and Reranker Hardening

The protected deterministic reference remains available.

Hybrid or reranker promotion requires fresh holdout evidence:

- source@5, source priority, evidence label, section, and path-context non-regression;
- source@3, MRR, or nDCG improvement;
- query-derived section intent rather than answer-key or fixture-only fields;
- complete source metadata preservation;
- measured p50/p95 latency and context-token impact;
- repeatable results without network-only hidden dependencies;
- documented rollback.

Reject or defer any reranker that does not improve ordering safely.

## Phase 3 — Real Grounded Answer Path

Use the smallest sufficient architecture:

```text
retrieval
-> evidence packaging and compression
-> provider-neutral structured answer adapter
-> atomic claim extraction
-> evidence-span matching
-> support-status classification
-> compliance routing
-> human review
-> trace and eval record
```

Required answer metrics:

- faithfulness;
- claim-level citation precision and recall;
- unsupported-claim rate;
- contradiction detection;
- missing-evidence honesty;
- refusal and escalation accuracy;
- biology/compliance boundary accuracy;
- answer/context tokens, cost proxy, and p50/p95 latency.

The claim verifier begins in diagnostic or shadow mode. Runtime blocking requires separate calibration evidence and approval.

## Phase 4 — Security, Compliance, and Observability

Before internal product promotion, record and test:

- prompt injection and indirect prompt injection;
- malicious retrieved-document instructions;
- source poisoning;
- confidential and personal-data leakage;
- unsafe biological over-answer;
- excessive agency and unauthorized tool use;
- CITES/Nagoya/LMO/biosafety/IP/legal/public-claim escalation;
- request ID, trace ID, workflow step, tool call, guardrail, model/provider, latency, token, cost, and reviewer decision;
- incident, rollback, and failure learn-back path.

Evaluator output never grants compliance, biosafety, legal, IP, wet-lab, public, investor, or release approval.

## Phase 5 — Internal Dogfood and Data Flywheel

Internal dogfood must expose:

- retrieved evidence and source metadata;
- citations and evidence spans;
- verifier result and uncertainty;
- compliance warning and human-review route;
- retrieval mode and scores;
- latency and cost visibility;
- failure logging and operator feedback.

Deep Research and external evidence move through:

```text
candidate
-> needs_review
-> approved
-> ingested
or blocked
```

No source enters a production-shaped index before license, confidentiality, provenance, allowed-use, and compliance review.

## Phase 6 — Web Productization

Only after the internal dogfood loop is evidence-backed:

1. backend/API and provider-adapter contract;
2. authentication and role-based authorization;
3. secrets and environment policy;
4. public/private source boundaries;
5. durable observability and audit storage;
6. deployment target, rollback, and incident response;
7. authenticated web UI with evidence, verifier, compliance, and operator-review panels;
8. security, privacy, source-license, cost, latency, and commercialization gates.

A web interface is not production readiness by itself.

## Phase 7 — KG, DBTL, Active Learning, and Foundation-Model Readiness

Introduce a KG only when repeated multi-hop questions cannot be handled reliably by simpler metadata/retrieval structures and a measurable eval demonstrates the need.

Introduce stateful agents or multi-agent graphs only after fixed workflows fail against explicit quality targets.

DBTL planning remains human-approved and must not become autonomous wet-lab execution.

Foundation-model readiness requires:

- legally usable proprietary biological data;
- versioned metadata and provenance;
- diverse, high-quality biological modalities;
- reproducible validation labels;
- DBTL feedback and failure records;
- governance, security, and compliance controls;
- dataset scale and model-training evidence.

A roadmap or source registry is not foundation-model capability.

## Performance Scorecard

Every performance-changing PR must report:

```text
Dataset and version:
Metric provenance: Fresh Run / Historical / Not Run
Baseline:
After:
Delta:
Retrieval impact:
Citation and answer impact:
Compliance/security impact:
Latency/token/cost impact:
Trace/eval impact:
Regression status:
Skipped checks and rationale:
Residual risk:
Rollback:
Next experiment:
```

Do not claim “improved performance” without measurable before/after evidence.

## Architecture and Tool Gate

Use the smallest sufficient layer:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

New frameworks, services, vector backends, KG systems, model providers, and agent runtimes require:

```text
Scout
-> license and allowed-use review
-> security/privacy review
-> benchmark
-> adapter boundary
-> targeted tests and evals
-> rollback
-> human gate
```

## GitHub and Codex Operating Loop

```text
Scope Lock
-> Source and Risk Preflight
-> Contract Design
-> Minimal Implementation
-> Cheap QA
-> Targeted Tests/Evals
-> risk-based full suite
-> commit and push
-> Draft PR
-> GitHub Actions
-> human review
-> merge
-> evidence log
-> learn back
```

GitHub Actions are clean-environment final gates, not the primary debugging environment.

Codex reasoning levels:

- 매우높음: core RAG, retrieval/ranking, eval/schema, security/compliance, CI/release, production gates;
- 높음: normal multi-file behavior changes;
- 중간: bounded docs/tests/refactors;
- 낮음: read-only status checks and mechanical edits.

## Stop Rules

Stop and split scope if:

- protected source, registry, chunk, eval, vector, KG, or confidential data would change unexpectedly;
- a performance claim lacks a baseline and reproducible eval;
- a test fixture leaks expected-answer information into runtime behavior;
- a dependency, service, model, or framework is added without preflight;
- high-risk biological, legal, compliance, IP, public, or investor output would bypass human review;
- user changes or separate worktrees cannot be preserved;
- the requested claim exceeds merged code, tests, logs, evals, and approval evidence.

## Immediate Next Action

Do not begin a broad new performance feature.

First publish and close the preserved V1.10C six-file implementation on top of `1e437c4515cc664f6acdb6e5bb197aaf576d34af`. Then perform a separate V1.10 final closure and start the representative evaluation-reset preflight.

