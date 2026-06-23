# Decision Log: MVP-016A Benchmark Workflow Preflight

## Date

2026-06-23

## Decision

Implement MVP-016A as a local read-only preflight decision layer for MVP-015 benchmark workflow specifications.

## Rationale

MVP-015 provides deterministic, fail-closed benchmark workflow validation, but it returns validation errors rather than a planning-interface decision. MVP-016A adds the smallest safe bridge from validation contract to planning decision without executing workflows or changing runtime retrieval behavior.

## Accepted Scope

- Add `src/asperitas_agent/benchmark_workflow_preflight.py`.
- Add `tests/test_benchmark_workflow_preflight.py`.
- Add documentation for the decision semantics.
- Return `allowed`, `blocked`, or `requires_human_approval`.
- Preserve source path, source priority, evidence label, risk flags, metrics metadata, and retriever policy metadata.
- Always report `executed: false` and `ingested: false`.
- Treat CITES, Nagoya, LMO, and privacy as approval-triggering domains when active.

## Rejected Scope

- Workflow execution.
- Source ingestion, chunking, embedding, indexing, or eval coverage.
- Source registry, chunk, eval fixture, retrieval, embedding, vector DB, reranker, answer-generation, or default-runtime changes.
- CLI integration.
- New dependencies.
- Copied third-party code.
- Any autonomous wet-lab, wet-lab validation, protocol automation, cloud-lab/LIMS/ELN/robotics, legal/regulatory/biosafety approval, production-readiness, or Asperitas performance claim.

## Source Status

The Ginkgo/OpenAI PDF remains raw-only P5 industry intelligence. MVP-016A does not ingest, chunk, embed, index, or eval-cover it.

## Retrieval Eval Applicability

Retrieval eval is not applicable. MVP-016A does not change retrieval, chunking, metadata handling, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.

## Verification Plan

- `python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py`
- `python scripts/verify_artifacts.py`
- `git diff --check`
- `python -m pytest -q`

## Residual Risks

- Public communication and security risk domains are not first-class MVP-015 `BenchmarkRiskFlag` values. Unknown risk domains still fail closed through MVP-015 validation.
- This is a planning decision layer only; it must not be interpreted as legal, regulatory, biosafety, wet-lab, investor, public-communication, or production approval.
