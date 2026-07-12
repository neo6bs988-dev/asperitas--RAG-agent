# MVP Completion Master Plan

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This document preserves durable sequencing and exit criteria. It must not duplicate mutable phase names, commit SHAs, issue status, or the immediate next action. If an older status table or “next step” conflicts with the canonical roadmap, treat the older wording as historical while preserving its scoped technical contracts and acceptance criteria. Do not treat doctrine, plans, scaffolds, synthetic fixtures, or diagnostic reports as proof of runtime quality, production readiness, compliance approval, biological validation, vector DB/KG completion, or foundation-model capability.

Purpose: define the complete execution path from the internal retrieval/evaluation foundation to a usable internal Asperitas RAG Agent, then to web-productized commercial-readiness gates.

This plan does not claim that future MVPs are already implemented. It defines the required sequence, acceptance criteria, quality gates, and non-regression rules so Codex can execute the remaining work safely.

## Source Baseline

The Top Source Triad is the active development baseline:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

These files define doctrine and development control-plane behavior. They are not evidence that production RAG, vector DB, KG, eval suite, legal review, wet-lab validation, regulatory approval, autonomous lab execution, or foundation-model capability is complete.

## Current Status Routing

Live capability status belongs only in the canonical current-state roadmap. The table below records durable capability meaning, not a live queue.

| Stage | Durable meaning | Live status source |
|---|---|---|
| MVP-001 Foundation | Repository and initial core structure exist. | Canonical roadmap + GitHub evidence |
| MVP-002 Retrieval Structure | Initial retrieval pipeline structure exists. | Canonical roadmap + GitHub evidence |
| MVP-002.5 Evaluation Baseline | Repeatable retrieval evaluation exists. | Canonical roadmap + GitHub evidence |
| MVP-003 Metadata-Aware Retrieval | Metadata-aware deterministic retrieval exists. | Canonical roadmap + GitHub evidence |
| MVP-004 Structure-Aware Chunking | Section-aware metadata and closure criteria are defined. | Canonical roadmap + recorded gate evidence |
| MVP-005 Embeddings + Vector DB | Embedding/vector boundaries and comparison mode. | Canonical roadmap + current implementation evidence |
| MVP-006 Hybrid Retrieval | Lexical, metadata-aware, section-aware, and vector combination. | Canonical roadmap + current implementation evidence |
| MVP-007 Reranker | Evidence reordering before answer generation. | Canonical roadmap + current evaluation evidence |
| MVP-008 Source-Grounded Answer Generation | Cited answers from retrieved evidence. | Canonical roadmap + current implementation evidence |
| MVP-009 Compliance Guardrails | Biosafety/compliance, uncertainty, and escalation behavior. | Canonical roadmap + current implementation evidence |
| MVP-010 Internal UI/API | Internal interface/API for testing and operation. | Canonical roadmap + current implementation evidence |
| MVP-011 Web Productization Foundation | Backend/API/provider/auth/observability/deployment contracts. | Canonical roadmap + current implementation evidence |
| MVP-012 Web App MVP | Authenticated web UI for evidence-backed operation. | Canonical roadmap + current implementation evidence |
| MVP-013 Production Readiness Gate | Commercialization blocker gate. | Canonical roadmap + release evidence |

## Master Execution Order

Exact active phase names and completion status come from the canonical roadmap. The durable order is:

1. Maintain representative, leakage-resistant evaluation controls.
2. Harden retrieval and reranking with fresh before/after evidence.
3. Implement a real source-grounded answer path.
4. Add claim-to-citation verification in diagnostic/shadow mode before blocking.
5. Add compliance/security adversarial gates.
6. Add tracing, latency, token, cost, and failure observability.
7. Run internal API/UI dogfood with operator feedback.
8. Build an approved Deep Research-to-Registry data flywheel.
9. Add authenticated web productization.
10. Pass a production-readiness gate.
11. Introduce KG, DBTL learning, active learning, and foundation-model readiness only when evidence justifies them.

## Non-Negotiable Invariants

- Deterministic retrieval remains available.
- Existing retrieval eval modes remain comparable.
- Every retrieval result preserves source ID, source file, source priority, evidence label, and section metadata.
- Every answer-generation path maps material claims to retrieved evidence.
- Unsupported claims are removed, refused, or labeled uncertain.
- Compliance-sensitive outputs escalate rather than fabricate certainty.
- Tests remain offline unless explicitly approved.
- No API keys, credentials, secrets, local binary indexes, or confidential raw data are committed.
- LLM providers remain replaceable; the moat is the Asperitas control plane, data governance, verifier, eval, compliance, DBTL/IP workflow, and proprietary biological dataset path.
- Internal UI/API is not public SaaS or commercial readiness.

## MVP-004 Exit Criteria

MVP-004 can close only if:

- `python -m pytest` passes or blocker is documented;
- `python scripts/verify_artifacts.py` passes;
- `python scripts/audit_chunk_sections.py --json` runs;
- baseline and MVP-003 retrieval evals run;
- no unexplained regression against `docs/MVP004_BASELINE_METRICS.md` exists;
- decision log or task report records the final observed metrics.

Historical documents that mark MVP-004 pending are stale when later gate evidence and the canonical roadmap record closure.

## MVP-005 Exit Criteria

MVP-005 can close only if:

- embedding record schema exists;
- metadata preservation tests pass;
- offline deterministic embedding provider exists;
- local vector adapter exists;
- vector retrieval can be evaluated as a separate mode;
- existing `baseline` and `mvp003` modes still work;
- vector backend decision is recorded or explicitly deferred.

## MVP-006 Exit Criteria

MVP-006 can close only if:

- hybrid retrieval combines at least two retrieval signals without breaking old modes;
- weights or scoring logic are explicit and test-covered;
- retrieval eval compares baseline, metadata-aware, vector, and hybrid modes;
- hybrid retrieval improves or preserves source/evidence traceability.

## MVP-007 Exit Criteria

MVP-007 can close only if:

- reranker is isolated behind an interface;
- deterministic or fixture-based reranker exists for tests;
- reranker can be evaluated separately;
- no reranker can drop source metadata;
- reranking improves ordering or has a documented reason to defer.

## MVP-008 Exit Criteria

MVP-008 can close only if:

- generated answers cite retrieved source IDs;
- material claims map to retrieved evidence;
- unsupported claims are refused or labeled;
- insufficient evidence behavior is tested;
- output format preserves source priority, evidence label, and confidence/uncertainty.

## MVP-009 Exit Criteria

MVP-009 can close only if:

- compliance risk domains are classified;
- CITES, Nagoya, LMO, K-BDS, privacy, security, IP, legal, and public/investor-claim risks are represented in guardrail tests where relevant;
- high-risk outputs escalate to human review;
- biological/biosafety-sensitive operational instructions are blocked or constrained;
- public-facing claims require source support.

## MVP-010 Exit Criteria

MVP-010 can close only if:

- internal API or UI can run the RAG pipeline;
- outputs show retrieved evidence and citations;
- eval/debug view exposes retrieval mode and scores;
- compliance warnings are visible;
- system can be operated internally without editing code;
- CI passes.

## MVP-011 Exit Criteria

MVP-011 can close only if:

- backend/API contract is documented and testable;
- LLM provider adapter interface exists or is specified with replaceability requirements;
- auth and role model are defined;
- secrets and environment policy are defined;
- observability fields are defined: request ID, trace ID, retrieval IDs, citation/verifier status, compliance status, latency, token/cost metrics;
- deployment target and rollback path are documented;
- commercial readiness remains explicitly out of scope.

## MVP-012 Exit Criteria

MVP-012 can close only if:

- authenticated web UI exists;
- users can submit queries through the web interface;
- retrieved evidence, citations, verifier status, confidence/uncertainty, and compliance warnings are visible;
- high-risk or unsupported outputs are blocked, labeled, or escalated;
- operator review workflow exists;
- smoke tests or equivalent validation are recorded.

## MVP-013 Exit Criteria

MVP-013 can close only if:

- security review is recorded;
- privacy/PII handling is reviewed;
- source license/confidentiality boundary is reviewed;
- CITES/Nagoya/LMO/biosafety/IP/legal gates are reviewed where relevant;
- public/investor claims have evidence and approval;
- cost and latency budgets are recorded;
- rollback and incident response plan exists;
- release note distinguishes implemented capability, unverified gaps, and blocked claims.

## Final Agent Completion Definition

The first internal Asperitas RAG Agent is complete when it can ingest approved sources, preserve structure, retrieve evidence, compare retrieval modes, generate source-grounded answers, enforce compliance guardrails, and expose an internal API/UI with reproducible CI and eval outputs.

The first web-productized Asperitas AI platform is complete only when MVP-011 through MVP-013 have evidence-backed gates. Internal RAG completion is necessary but not sufficient for commercialization.

## Recommended Immediate Action

Read the canonical current-state roadmap's `Immediate Next Action` and verify it against live GitHub evidence. Do not execute historical issue numbers or old phase labels from this master plan as current instructions.
