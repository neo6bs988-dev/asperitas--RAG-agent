# MVP-015 Benchmark Workflow Schema Closeout

Date: 2026-06-23

## Objective

Close MVP-015 after PR #49 merged the Ginkgo/OpenAI-inspired benchmark workflow schema into `main`.

MVP-015 adapts the Ginkgo/OpenAI autonomous-lab paper as a software-process benchmark for Asperitas RAG Agent governance. The purpose is to capture schema-first validation, explicit workflow boundaries, benchmark metrics, source metadata, and human approval gates without reproducing autonomous wet-lab execution.

## Scope Completed

MVP-015 added a local Python contract layer for benchmark workflow specifications. The implementation is deterministic, fail-closed, and non-executing.

Completed scope:

- local benchmark workflow schema and validation contracts;
- source path, source priority, evidence label, allowed use, and prohibited use fields;
- compliance and wet-lab risk flags;
- human approval gates for wet-lab-sensitive, legal/IP, investor-facing, biosafety, and confidential-source cases;
- explicit workflow translation boundary that is descriptive only and not executable;
- benchmark metric guardrails so source metrics cannot be represented as Asperitas performance;
- retriever, hybrid, and reranker policy fields that preserve existing boundaries;
- tests for validation, prohibited execution claims, approval gates, metric overclaim prevention, and retrieval-policy preservation.

## Files Added

| File | Purpose |
|---|---|
| `src/asperitas_agent/benchmark_workflow.py` | Local schema/contract layer for Ginkgo-inspired benchmark workflows |
| `tests/test_benchmark_workflow.py` | Unit tests for fail-closed validation, non-execution boundaries, approval gates, metric boundaries, and retriever policy preservation |

## Source Status

The Ginkgo/OpenAI source PDF exists as a raw P5 source:

`01_RAW_SOURCES/P5_INDUSTRY_INTELLIGENCE/Gingko bio 오픈ai 활용한 software 개발process.pdf`

Current status:

- raw source: yes
- processed markdown: no
- chunked: no
- embedded: no
- source-registry/eval coverage added by MVP-015: no
- retrieval/eval fixture mutation: no

The source remains raw-only. MVP-015 did not ingest, chunk, embed, index, or eval-cover the PDF.

## Verification Results

| Gate | Result |
|---|---|
| `python -m pytest -q tests/test_benchmark_workflow.py` | `13 passed` |
| `python -m pytest -q tests/test_role_registry.py` | `15 passed` |
| `python -m pytest -q` | `232 passed` |
| `python scripts/verify_artifacts.py` | `ok: true`, `registry_records: 48`, `chunk_count: 2821`, no errors/warnings |
| `git diff --check main...HEAD` | passed after formatting fix |

## Retrieval Eval Rationale

Retrieval eval was not run because MVP-015 did not change:

- retrieval logic;
- chunking;
- scoring;
- eval fixtures;
- embeddings;
- vector DB behavior;
- reranking;
- answer generation.

No retrieval metrics are claimed for MVP-015.

## Compliance / Source-Grounding Review

MVP-015 uses the Ginkgo/OpenAI paper only as a raw P5 industry benchmark source and software-process analogy. It does not claim Ginkgo-reported metrics as Asperitas performance.

Compliance and grounding boundaries:

- source metadata is required for valid benchmark workflow specs;
- evidence labels are required and validated;
- benchmark metrics are source-context only;
- wet-lab, biosafety, legal/IP, investor-facing, and confidential-source cases require human approval gates;
- external execution targets are prohibited;
- workflow translation boundaries are descriptive only;
- wet-lab validation, autonomous wet-lab capability, production hybrid retrieval, and default reranker claims are blocked.

This is a contract layer only. It is not legal, regulatory, biosafety, investor, public-communication, or wet-lab approval.

## Non-Goals

MVP-015 did not implement:

- autonomous wet-lab capability or claims;
- wet-lab execution;
- protocol automation;
- cloud-lab, LIMS, ELN, robotics, or external execution integration;
- source ingestion;
- source registry mutation;
- chunk mutation;
- eval fixture mutation;
- retrieval ranking changes;
- embedding or vector DB changes;
- answer-generation changes;
- production hybrid retrieval claims;
- default reranker behavior.

## Remaining Risks

- The contract layer is local and not yet integrated into runtime workflows.
- The Ginkgo/OpenAI PDF remains raw-only.
- There is no chunk, embedding, retrieval, or eval coverage for the Ginkgo source yet.
- Future runtime integration could accidentally treat benchmark workflow contracts as execution permission unless the non-execution boundary remains enforced.
- Future public, investor, or partner-facing references must keep benchmark metrics separate from Asperitas performance claims.

## Recommended Next MVP

MVP-016 should integrate the benchmark workflow contract into a read-only planning/validation interface without changing retrieval defaults or executing workflows.

Recommended MVP-016 boundaries:

- no retrieval default changes;
- no production hybrid claim;
- no default reranker;
- no wet-lab execution;
- no protocol automation;
- no cloud-lab, LIMS, ELN, robotics, or external execution system;
- preserve `mvp003` as the protected deterministic reference retriever;
- require tests and approval gates before any runtime use.

