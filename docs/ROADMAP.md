# Roadmap

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This file is a durable compatibility roadmap. It must not duplicate mutable phase names, commit SHAs, issue status, or the immediate next action. If an older status table or “next step” conflicts with the canonical roadmap, treat the older wording as historical while preserving its scoped technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

This roadmap is the execution map for the Asperitas RAG Agent and its path toward a web-productized commercial AI platform. It must stay aligned with `docs/MVP_COMPLETION_MASTER_PLAN.md`, `docs/PERFORMANCE_IMPROVEMENT_STRATEGY.md`, `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md`, `docs/WEB_PRODUCTIZATION_ROADMAP.md`, GitHub Issues, and the active quality gates.

## Current Rule

Do not mark an MVP as complete unless the relevant acceptance criteria, tests, evals, source-grounding review, compliance review, release decision, and merge evidence are recorded.

The Top Source Triad is the active operating baseline for future development. It is doctrine, not implementation proof.

```text
ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf
+ Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf
+ 딥리서치를 통해 GPT 채팅 학습용 자료.pdf
```

## Durable Development Sequence

Exact active status comes from the canonical current-state roadmap. The enduring sequence is:

```text
representative evaluation controls
-> retrieval and reranker hardening
-> real grounded answer path and diagnostic verifier
-> compliance/security adversarial gates
-> trace, latency, token, and cost control plane
-> internal dogfood
-> approved data flywheel
-> web productization and production-readiness gates
-> evidence-driven KG, DBTL, active learning, and foundation-model readiness
```

Do not reorder this sequence merely to add fashionable frameworks.

## V1 Internal Release Preparation — Historical Record

The post-PR77 V1 release-preparation record remains useful historical evidence, but it is not the live next-step queue.

| V1 step | Historical record |
|---|---|
| 1. Playbook v3 Absorption | Completed by `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| 2. Benchmark Absorption & Stage-Gate Calibration | Completed by `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| 3. MVP Performance Pack Backfill | Completed by `docs/V1_MVP_PERFORMANCE_PACK.md` |
| 4. V1 Performance Closure Matrix | Completed by `docs/V1_PERFORMANCE_CLOSURE_MATRIX.md` after closure checks pass |
| 5. P0/P1 Gap Fix Only | Recorded through `scripts/check_v1_p0_p1_gap_fix.py` and related PR evidence |
| 6. Final Pre-RC Regression | Recorded in `docs/V1_FINAL_PRE_RC_REGRESSION.md` for RC preparation only |
| 7. v1.0.0-rc1 | Historical prerelease baseline at `7f28f0a60fae2d7e0b674d1111287386d2d64fc6` |
| 8. Internal Dry-run | Status must be read from the canonical roadmap and live release evidence |
| 9. v1.0.0-internal | Status must be read from the canonical roadmap and live release evidence |

V1.1 handoff labels remain historical architectural context:

- V1.1A failure log collector
- V1.1B local/internal web dogfood UI
- V1.1C real RAG answer provider integration
- V1.1D retrieval/answer baseline

They must not override later merged roadmap decisions.

## V1.5 Gap Closure And Performance Hardening — Historical Contract

`docs/V1_5_PERFORMANCE_ROADMAP.md` preserves the V1.5 scoped harness-first, cost-aware, regression-safe contract. It is not the live phase authority.

Durable operating loop:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

V1.5A was governance and verification-policy work only. It did not implement production RAG, production KG, production vector DB, answer behavior changes, source ingestion, legal approval, regulatory approval, wet-lab validation, customer traction, public SaaS, or production readiness.

## MVP Status Table

Live status must be reconciled with the canonical current-state roadmap and current GitHub evidence.

| MVP | Name | Reconciled state | Boundary |
|---|---|---|---|
| MVP-001 | Foundation | Completed / baseline | Repository and core structure exist; not production deployment |
| MVP-002 | Retrieval Structure | Completed / baseline | Initial retrieval pipeline exists |
| MVP-002.5 | Evaluation Baseline | Completed / baseline | Repeatable retrieval evaluation exists; fixtures remain limited |
| MVP-003 | Metadata-Aware Retrieval | Completed / protected reference | Deterministic metadata-aware mode remains comparable |
| MVP-004 | Structure-Aware Chunking | Closed by recorded quality-gate evidence | Historical tables marking it pending are stale |
| MVP-005 | Embeddings + Vector DB | Offline vector comparison mode implemented | Not a selected production vector backend |
| MVP-006 | Hybrid Retrieval | Comparison mode implemented and accepted for comparison | Not default; fixture-specific section expectations limit claims |
| MVP-007 | Reranker | Interface and deterministic test reranker implemented | Existing test reranker regressed source@3; no quality-improvement claim |
| MVP-008 | Source-Grounded Answer Generation | Contracts/scaffolds exist | Real RAG answer provider is not the default production path |
| MVP-009 | Compliance Guardrails | Repository controls/scaffolds exist | Not production approval or external deployment |
| MVP-010 | Internal UI/API | Planned or partially scaffolded by component | Not authenticated commercial SaaS |
| MVP-011 | Web Productization Foundation | Planned | Requires backend/API/provider/auth/observability/deployment evidence |
| MVP-012 | Web App MVP | Planned | Requires authenticated web UI and operator-review evidence |
| MVP-013 | Production Readiness Gate | Planned | Requires security, privacy, license, compliance, cost, latency, rollback, and release evidence |

## MVP-001 Foundation

Establish the initial repository, development workflow, and baseline project structure for the Asperitas RAG Agent.

Status: completed baseline. Do not reopen unless repository structure breaks downstream work.

## MVP-002 Retrieval Structure

Define the first retrieval pipeline structure, including document loading, indexing boundaries, and query-time retrieval flow.

Status: completed baseline. Future retrieval work must remain backward-compatible unless a deliberate migration is approved.

## MVP-002.5 Evaluation Baseline

Create baseline retrieval evaluation so future changes can be measured against repeatable metrics.

Status: completed baseline. This is the foundation for performance claims, but current fixtures do not prove holdout generalization.

## MVP-003 Metadata-Aware Retrieval

Use document and chunk metadata to improve filtering, attribution, retrieval quality, and source traceability.

Status: completed protected reference. Existing `mvp003` eval mode must remain comparable.

## MVP-004 Structure-Aware Chunking

Improve chunking so document structure, biological context, headings, tables, methods, and source boundaries are preserved more effectively.

Status: closed by recorded quality-gate evidence. Historical references to Issue #1 as the active task are stale.

Exit criteria retained for regression review:

- full quality gate run;
- chunk section audit recorded;
- baseline and MVP-003 retrieval eval recorded;
- no unexplained regression against `docs/MVP004_BASELINE_METRICS.md`.

## MVP-005 Embeddings + Vector DB

Add embedding generation and vector database boundaries for scalable semantic retrieval.

Historical implementation sequence:

1. embedding record schema and metadata-preservation tests;
2. offline embedding provider boundary;
3. local vector store adapter;
4. vector retrieval eval mode;
5. backend selection after adapter and eval exist.

Current boundary: an offline vector comparison mode exists, but no production vector backend is selected.

Exit criteria:

- vector retrieval is implemented as a separate measurable mode;
- old retrieval modes still work;
- source-grounding metadata is preserved;
- vector backend choice is recorded or explicitly deferred.

## MVP-006 Hybrid Retrieval

Combine semantic vector retrieval with lexical, metadata-aware, and section-aware retrieval.

Current boundary: hybrid comparison exists and remains non-default. Promotion requires fresh, leakage-resistant evidence.

Exit criteria:

- hybrid mode is separately selectable;
- eval compares baseline, mvp003, vector, and hybrid;
- no source/evidence traceability regression;
- query-derived intent replaces fixture-answer or expected-section shortcuts before promotion.

## MVP-007 Reranker

Add a reranking stage to improve evidence ordering before answer generation.

Current boundary: interface/plumbing and a deterministic test reranker exist. The existing test reranker lowered source@3 and is not promoted.

Exit criteria:

- reranker preserves metadata;
- reranker can be measured before/after;
- ordering improves or deferral is justified by evidence;
- latency/token and source-priority effects are recorded.

## MVP-008 Source-Grounded Answer Generation

Generate answers only from retrieved source evidence, with citations and clear insufficient-evidence behavior.

Historical implementation sequence:

1. define answer contract and citation format;
2. implement source-grounded answer generator.

Exit criteria:

- material claims trace to evidence;
- citation format preserves source ID, source priority, and evidence label;
- insufficient evidence produces uncertainty/refusal, not fabrication;
- real provider behavior is evaluated separately from synthetic/offline diagnostics.

## MVP-009 Compliance Guardrails

Add guardrails for biological intelligence use cases, including source constraints, uncertainty handling, and compliance-aware refusal or escalation behavior.

Historical implementation sequence:

1. define compliance risk taxonomy and guardrail contract;
2. implement compliance guardrail tests and escalation behavior.

Exit criteria:

- high-risk domains are classified;
- guardrail tests exist;
- high-risk outputs block or escalate;
- public/investor claims require evidence;
- evaluator output grants no legal, compliance, biosafety, IP, wet-lab, public, investor, release, or production approval.

## MVP-010 Internal UI/API

Provide an internal interface and API for testing, reviewing, and operating the RAG agent.

Historical implementation sequence:

1. define internal API contract;
2. implement minimal internal API/UI with evidence and compliance debug view;
3. close first agent release with release notes and operating guide.

Exit criteria:

- internal API/UI runs the pipeline;
- evidence, citations, retrieval scores, and compliance warnings are visible;
- final release note and operating guide exist;
- CI passes.

## MVP-011 Web Productization Foundation

Convert the internal AI system into a production-shaped web architecture without claiming commercial readiness.

Required scope:

- backend API contract;
- LLM provider adapter interface;
- authentication and role boundary;
- secrets and environment policy;
- observability, audit, cost, and latency schema;
- deployment target and rollback plan;
- public/private source boundary.

Exit criteria:

- backend/API contract is documented and testable;
- provider adapter is replaceable and does not hard-code one LLM as the product moat;
- auth model distinguishes admin/operator/reviewer/user roles;
- secrets and environment variables are not committed;
- tracing/logging preserves source IDs, request IDs, verifier status, and compliance warnings;
- deployment plan includes rollback and human approval gate.

## MVP-012 Web App MVP

Build a minimal authenticated web application for operating Asperitas AI workflows.

Required scope:

- login-protected web UI;
- query workflow;
- retrieved evidence and citation panel;
- answer contract display;
- verifier status display;
- compliance warning/escalation display;
- operator review path;
- basic cost/latency visibility.

Exit criteria:

- web app runs against the internal API;
- citations and evidence spans are visible to operators;
- unsupported or high-risk outputs are blocked, labeled, or escalated;
- no confidential source text leaks into public/non-authorized UI paths;
- smoke tests or equivalent validation exist.

## MVP-013 Production Readiness Gate

Block public commercialization claims until production readiness evidence exists.

Exit criteria:

- security review recorded;
- privacy and PII handling reviewed;
- source license and confidentiality boundary reviewed;
- CITES/Nagoya/LMO/biosafety/IP/legal gates reviewed where relevant;
- cost and latency budget recorded;
- rollback and incident response plan exists;
- public/investor claims have source support and human approval;
- release note states exactly what is implemented and what remains unverified.

## Supporting Engineering References

Historical issue numbers and earlier future-work labels remain useful for provenance, but they are not live execution commands. New work must be scoped from the canonical current-state roadmap and current GitHub evidence.

## Default Next Command

Read the canonical current-state roadmap's `Immediate Next Action` and verify it against live GitHub evidence. Do not start work from historical issue numbers, stale phase labels, or old commit references in this compatibility roadmap.
