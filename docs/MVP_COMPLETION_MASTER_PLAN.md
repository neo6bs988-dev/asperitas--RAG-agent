# MVP Completion Master Plan

## Current Execution Authority

Use [`CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md`](CURRENT_STATE_AND_PERFORMANCE_ROADMAP_2026_07_11.md) together with the latest merged GitHub PR, commit, CI, Quality Gates, test, eval, release, and human-review evidence for live status.

This document is a durable execution blueprint, not a second live status table. Older phase names, issue numbers, commit SHAs, and next-step wording are historical unless the canonical roadmap confirms them.

Purpose: define the staged path from the internal Asperitas RAG/agent core to a credible internal operating system, web-productization pathway, and evidence-gated production readiness.

This plan does not claim that future MVPs are implemented. It defines sequencing, acceptance criteria, quality gates, and non-regression rules so development can proceed safely.

## Source Baseline

The Top Source Triad is the active development baseline:

1. `ASPERITAS_PROJECT_SOURCE_CONSTITUTION_v11_0_KR.pdf`
2. `Asperitas_AI_Lead_Expert_GPT_Training_Source_v1_0_KR.pdf`
3. `딥리서치를 통해 GPT 채팅 학습용 자료.pdf`

These files define doctrine and development control-plane behavior. They are not evidence that production RAG, vector DB, KG, eval suite, legal review, wet-lab validation, regulatory approval, autonomous lab execution, or foundation-model capability is complete.

## Capability Snapshot Routing

Live capability status is maintained only in the canonical current-state roadmap. This master plan preserves target capabilities and exit conditions.

Durable confirmed baseline:

- MVP-001 Foundation: repository and core structure exist.
- MVP-002 Retrieval Structure: initial retrieval pipeline exists.
- MVP-002.5 Evaluation Baseline: repeatable retrieval evaluation exists.
- MVP-003 Metadata-Aware Retrieval: deterministic metadata-aware reference mode exists.
- MVP-004 Structure-Aware Chunking: closure evidence is recorded in repository history; older tables marking it pending are stale.
- Vector and hybrid retrieval: implemented as measurable comparison modes, not selected production defaults.
- Reranker: interface/plumbing exists; quality improvement is not established by the existing deterministic test reranker.
- Source-grounded answer generation, compliance guardrails, internal UI/API, production vector DB/KG, and web productization remain evidence-gated by the canonical roadmap.

## Master Execution Order

Exact active phase names and status come from the canonical roadmap. The durable order is:

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

## MVP Exit Conditions

### Foundation and Retrieval Core

- repository structure, source boundaries, and deterministic test harness exist;
- retrieval modes remain selectable and comparable;
- source IDs, priorities, evidence labels, paths, and metadata are preserved;
- no performance mode is promoted without reproducible metrics and rollback.

### Retrieval and Reranker Hardening

- baseline, after, and delta are recorded;
- Source@k, MRR, nDCG, source priority, evidence label, section, and path-context impact are measured where supported;
- answer-key or fixture-only fields are not used as runtime ranking features;
- p50/p95 latency and context-token impact are recorded;
- regressions cause rejection or rollback.

### Source-Grounded Answer Generation

- material claims trace to evidence spans;
- citations preserve source ID, source priority, evidence label, and uncertainty;
- insufficient evidence produces uncertainty, refusal, or escalation rather than fabrication;
- real generated-answer metrics are distinguished from synthetic/offline diagnostics.

### Compliance Guardrails

- high-risk domains and escalation routes are explicit;
- CITES, Nagoya/ABS, LMO/GMO, biosafety, biosecurity, privacy, IP, license, public, and investor boundaries are tested;
- evaluator output cannot grant legal, compliance, biosafety, IP, wet-lab, public, investor, or release approval;
- human review remains mandatory where risk requires it.

### Internal UI/API and Dogfood

- retrieved evidence, citations, verifier status, uncertainty, retrieval scores, compliance warnings, latency, and cost are visible;
- operator review and failure logging exist;
- authentication and role boundaries are explicit before broader access;
- internal dogfood evidence precedes public productization claims.

### Web Productization Foundation

- backend/API contract is testable;
- provider adapter is replaceable;
- authentication and role-based authorization are defined;
- secrets and environment variables are not committed;
- tracing/logging preserves source IDs, request IDs, verifier status, and compliance warnings;
- deployment plan includes rollback and incident response.

### Production Readiness Gate

- security, privacy, PII, source license, confidentiality, compliance, latency, cost, rollback, and incident response evidence exists;
- public/investor claims have source support and human approval;
- release notes state exactly what is implemented and what remains unverified;
- production vector DB/KG, wet-lab validation, autonomous execution, commercial readiness, and foundation-model capability are never inferred from planning artifacts.

## Architecture and Dependency Gate

Use the smallest sufficient layer:

```text
deterministic helper
-> single LLM/RAG/tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent/graph
```

New dependencies, services, frameworks, model providers, vector backends, or graph systems require license/allowed-use review, security/privacy review, benchmark evidence, adapter boundaries, targeted tests/evals, rollback, and human approval.

## Default Next Action

Read the canonical current-state roadmap's `Immediate Next Action` and verify it against live GitHub evidence. Do not use old issue numbers or historical phase labels in this document as an execution command.
