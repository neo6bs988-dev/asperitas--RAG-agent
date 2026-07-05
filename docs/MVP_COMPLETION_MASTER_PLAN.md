# MVP Completion Master Plan

Purpose: define the complete execution path from the current MVP-004/MVP-005 transition to a usable internal Asperitas RAG Agent, then to web-productized commercial-readiness gates.

This plan does not claim that future MVPs are already implemented. It defines the required sequence, acceptance criteria, quality gates, and non-regression rules so Codex can execute the remaining work safely.

## Source Baseline

The Top Source Triad is the active development baseline:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

These files define doctrine and development control-plane behavior. They are not evidence that production RAG, vector DB, KG, eval suite, legal review, wet-lab validation, regulatory approval, autonomous lab execution, or foundation-model capability is complete.

## Current Status

| Stage | Status | Meaning |
|---|---|---|
| MVP-001 Foundation | Completed / baseline | Repository and initial core structure exist. |
| MVP-002 Retrieval Structure | Completed / baseline | Initial retrieval pipeline structure exists. |
| MVP-002.5 Evaluation Baseline | Completed / baseline | Repeatable retrieval evaluation exists. |
| MVP-003 Metadata-Aware Retrieval | Completed / baseline | Metadata-aware deterministic retrieval exists. |
| MVP-004 Structure-Aware Chunking | Needs final quality-gate close | Section-aware metadata exists, but final gate output must be recorded before closure. |
| MVP-005 Embeddings + Vector DB | Planned / next technical frontier | Requires schema, provider boundary, local adapter, vector eval mode, then backend selection. |
| MVP-006 Hybrid Retrieval | Planned | Combine lexical, metadata-aware, section-aware, and vector retrieval. |
| MVP-007 Reranker | Planned | Reorder retrieved evidence before answer generation. |
| MVP-008 Source-Grounded Answer Generation | Planned | Generate cited answers only from retrieved evidence. |
| MVP-009 Compliance Guardrails | Planned | Add biosafety/compliance, uncertainty, and escalation behavior. |
| MVP-010 Internal UI/API | Planned | Provide internal interface/API for testing and operation. |
| MVP-011 Web Productization Foundation | Planned | Add production-shaped backend/API/provider/auth/observability/deployment contracts. |
| MVP-012 Web App MVP | Planned | Authenticated web UI for source-grounded answers, verifier status, and compliance review. |
| MVP-013 Production Readiness Gate | Planned | Commercialization blocker gate for security, privacy, license, compliance, latency, cost, and rollback evidence. |

## Master Execution Order

1. Close MVP-004 only after the full quality gate is run and recorded.
2. Implement MVP-005 Phase 1 embedding record schema.
3. Add offline embedding provider boundary.
4. Add local vector store adapter.
5. Add vector retrieval eval mode.
6. Review vector backend options and choose prototype backend only after eval mode exists.
7. Implement MVP-006 hybrid retrieval.
8. Implement MVP-007 reranker.
9. Implement MVP-008 source-grounded answer generation.
10. Implement MVP-009 compliance guardrails.
11. Implement MVP-010 internal UI/API.
12. Add internal release notes and final internal operating guide.
13. Implement MVP-011 web productization foundation.
14. Implement MVP-012 authenticated web app MVP.
15. Run MVP-013 production readiness and commercialization gate.

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

Execute Issue #1. Do not start MVP-005 implementation until MVP-004 gate output is known. Do not start MVP-011 implementation until MVP-010 internal UI/API evidence exists and a separate web-productization scope lock is approved.
