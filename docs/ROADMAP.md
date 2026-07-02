# Roadmap

This roadmap is the execution map for the first Asperitas RAG Agent. It must stay aligned with `docs/MVP_COMPLETION_MASTER_PLAN.md`, `docs/PERFORMANCE_IMPROVEMENT_STRATEGY.md`, GitHub Issues, and the active quality gates.

## Current Rule

Do not mark an MVP as complete unless the relevant acceptance criteria, tests, evals, source-grounding review, compliance review, and release decision are recorded.

## V1 Internal Release Preparation

The post-PR77 V1 roadmap remains active and must not be collapsed into a single closeout claim. The current completed subtask is limited to Playbook v3 Absorption plus Benchmark Absorption & Stage-Gate Calibration; it is a docs/process/check-only step and does not implement performance features or alter runtime retrieval behavior.

| V1 step | Status |
|---|---|
| 1. Playbook v3 Absorption | Completed by `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| 2. Benchmark Absorption & Stage-Gate Calibration | Completed by `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` |
| 3. MVP Performance Pack Backfill | Completed by `docs/V1_MVP_PERFORMANCE_PACK.md` |
| 4. V1 Performance Closure Matrix | Completed by `docs/V1_PERFORMANCE_CLOSURE_MATRIX.md` after closure checks pass |
| 5. P0/P1 Gap Fix Only | Completed by `scripts/check_v1_p0_p1_gap_fix.py` after PR #86 main verification |
| 6. Final Pre-RC Regression | Completed by `docs/V1_FINAL_PRE_RC_REGRESSION.md` for RC preparation only |
| 7. v1.0.0-rc1 | V1.0.0-rc1 baseline complete as prerelease at `7f28f0a60fae2d7e0b674d1111287386d2d64fc6` |
| 8. Internal Dry-run | Pending reproducible dry-run evidence from `scripts/run_v1_internal_dry_run.py` |
| 9. v1.0.0-internal | Pending; v1.0.0-internal pending until internal dry-run evidence passes |

V1.1 handoff items:

- V1.1A failure log collector
- V1.1B local/internal web dogfood UI
- V1.1C real RAG answer provider integration
- V1.1D retrieval/answer baseline

Allowed status after the V1 Performance Closure Matrix passes its checks: ready to evaluate whether P0/P1 Gap Fix Only is needed. This is not final RC readiness, internal dry-run readiness, or internal release readiness.

## V1.5 Gap Closure And Performance Hardening

V1.5 begins with V1.5A harness-first, cost-aware, regression-safe documentation and gate sync. The active policy file is `docs/V1_5_PERFORMANCE_ROADMAP.md`.

Required V1.5A operating loop:

```text
Preflight -> Plan -> Implement -> Cheap QA -> Targeted Verification -> GitHub PR -> Log -> Improve
```

V1.5A is governance and verification-policy work only. It does not implement V2 vector DB/KG, V3 modular agents, V4 ML/DL, production RAG, production KG, production vector DB, answer behavior changes, retrieval scoring changes, source ingestion, generated indexes, legal approval, regulatory approval, wet-lab validation, customer traction, or production readiness.

## MVP Status Table

| MVP | Name | Status | Primary Issue(s) | Exit Condition |
|---|---|---|---|---|
| MVP-001 | Foundation | Completed / baseline | historical | repo and core structure exist |
| MVP-002 | Retrieval Structure | Completed / baseline | historical | initial retrieval pipeline exists |
| MVP-002.5 | Evaluation Baseline | Completed / baseline | historical | repeatable retrieval eval exists |
| MVP-003 | Metadata-Aware Retrieval | Completed / baseline | historical | metadata-aware retrieval exists |
| MVP-004 | Structure-Aware Chunking | Needs final close gate | #1 | quality gate output recorded with no unexplained regression |
| MVP-005 | Embeddings + Vector DB | Planned / next | #2, #3, #4, #5, #6 | vector retrieval exists as comparable mode with metadata preserved |
| MVP-006 | Hybrid Retrieval | Planned | #10, #11 | hybrid mode improves or preserves retrieval/source-grounding metrics |
| MVP-007 | Reranker | Planned | #12, #13 | reranker improves ordering or is rejected with evidence |
| MVP-008 | Source-Grounded Answer Generation | Planned | #14, #15 | generated answers cite retrieved evidence and handle insufficient evidence safely |
| MVP-009 | Compliance Guardrails | Planned | #16, #17 | high-risk biological/compliance outputs block or escalate |
| MVP-010 | Internal UI/API | Planned | #18, #19, #20 | internal interface/API operates the agent with evidence and compliance visibility |

## MVP-001 Foundation

Establish the initial repository, development workflow, and baseline project structure for the Asperitas RAG Agent.

Status: completed baseline. Do not reopen unless repository structure breaks downstream work.

## MVP-002 Retrieval Structure

Define the first retrieval pipeline structure, including document loading, indexing boundaries, and query-time retrieval flow.

Status: completed baseline. Future retrieval work must remain backward-compatible unless a deliberate migration is approved.

## MVP-002.5 Evaluation Baseline

Create baseline retrieval evaluation so future changes can be measured against repeatable metrics.

Status: completed baseline. This is the foundation for all performance claims.

## MVP-003 Metadata-Aware Retrieval

Use document and chunk metadata to improve filtering, attribution, retrieval quality, and source traceability.

Status: completed baseline. Existing `mvp003` eval mode must remain comparable.

## MVP-004 Structure-Aware Chunking

Improve chunking so document structure, biological context, headings, tables, methods, and source boundaries are preserved more effectively.

Active task: Issue #1.

Exit criteria:

- full quality gate run;
- chunk section audit recorded;
- baseline and MVP-003 retrieval eval recorded;
- no unexplained regression against `docs/MVP004_BASELINE_METRICS.md`.

## MVP-005 Embeddings + Vector DB

Add embedding generation and vector database boundaries for scalable semantic retrieval.

Active sequence:

1. Issue #2: embedding record schema and metadata-preservation tests.
2. Issue #3: offline embedding provider boundary.
3. Issue #4: local vector store adapter.
4. Issue #5: vector retrieval eval mode.
5. Issue #6: select vector backend after adapter and eval exist.

Exit criteria:

- vector retrieval is implemented as a separate measurable mode;
- old retrieval modes still work;
- source-grounding metadata is preserved;
- vector backend choice is recorded or explicitly deferred.

## MVP-006 Hybrid Retrieval

Combine semantic vector retrieval with lexical, metadata-aware, and section-aware retrieval.

Active sequence:

1. Issue #10: design hybrid scoring contract.
2. Issue #11: implement hybrid mode and eval comparison.

Exit criteria:

- hybrid mode is separately selectable;
- eval compares baseline, mvp003, vector, and hybrid;
- no source/evidence traceability regression.

## MVP-007 Reranker

Add a reranking stage to improve evidence ordering before answer generation.

Active sequence:

1. Issue #12: reranker interface and deterministic test reranker.
2. Issue #13: reranker eval and top-k ordering comparison.

Exit criteria:

- reranker preserves metadata;
- reranker can be measured before/after;
- ordering improves or deferral is justified by evidence.

## MVP-008 Source-Grounded Answer Generation

Generate answers only from retrieved source evidence, with citations and clear insufficient-evidence behavior.

Active sequence:

1. Issue #14: define answer contract and citation format.
2. Issue #15: implement source-grounded answer generator.

Exit criteria:

- material claims trace to evidence;
- citation format preserves source ID, source priority, and evidence label;
- insufficient evidence produces uncertainty/refusal, not fabrication.

## MVP-009 Compliance Guardrails

Add guardrails for biological intelligence use cases, including source constraints, uncertainty handling, and compliance-aware refusal or escalation behavior.

Active sequence:

1. Issue #16: define compliance risk taxonomy and guardrail contract.
2. Issue #17: implement compliance guardrail tests and escalation behavior.

Exit criteria:

- high-risk domains are classified;
- guardrail tests exist;
- high-risk outputs block or escalate;
- public/investor claims require evidence.

## MVP-010 Internal UI/API

Provide an internal interface and API for testing, reviewing, and operating the RAG agent.

Active sequence:

1. Issue #18: define internal API contract.
2. Issue #19: implement minimal internal API/UI with evidence and compliance debug view.
3. Issue #20: close first agent release with release notes and operating guide.

Exit criteria:

- internal API/UI runs the pipeline;
- evidence, citations, retrieval scores, and compliance warnings are visible;
- final release note and operating guide exist;
- CI passes.

## Supporting Engineering Issues

- Issue #7: dependency/security review before external libraries.
- Issue #8: later RAGAS/DSPy-style answer evaluation.
- Issue #9: later LangGraph-style orchestration.

## Default Next Command

Start with Issue #1. Do not start MVP-005 implementation until MVP-004 quality gate output is known.
