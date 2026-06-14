# MVP Completion Master Plan

Purpose: define the complete execution path from the current MVP-004/MVP-005 transition to a usable internal Asperitas RAG Agent.

This plan does not claim that future MVPs are already implemented. It defines the required sequence, acceptance criteria, quality gates, and non-regression rules so Codex can execute the remaining work safely.

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
12. Add release notes and final operating guide.

## Non-Negotiable Invariants

- Deterministic retrieval remains available.
- Existing retrieval eval modes remain comparable.
- Every retrieval result preserves source ID, source file, source priority, evidence label, and section metadata.
- Every answer-generation path maps material claims to retrieved evidence.
- Unsupported claims are removed, refused, or labeled uncertain.
- Compliance-sensitive outputs escalate rather than fabricate certainty.
- Tests remain offline unless explicitly approved.
- No API keys, credentials, secrets, local binary indexes, or confidential raw data are committed.

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

## Final Agent Completion Definition

The first Asperitas RAG Agent is complete when it can ingest sources, preserve structure, retrieve evidence, compare retrieval modes, generate source-grounded answers, enforce compliance guardrails, and expose an internal API/UI with reproducible CI and eval outputs.

## Recommended Immediate Action

Execute Issue #1. Do not start MVP-005 implementation until MVP-004 gate output is known.