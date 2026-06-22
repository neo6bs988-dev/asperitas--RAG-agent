# Decision Log: MVP-015 Benchmark Workflow Schema

## Date

2026-06-23

## Decision

Close MVP-015 after PR #49 merged the Ginkgo/OpenAI-inspired benchmark workflow schema into `main`.

## Evidence

- PR: #49, `Add MVP-015 benchmark workflow schema`
- Merge commit: `46f54e9839db87d8bcbe2d7af765c0bb14e83a0b`
- Added files:
  - `src/asperitas_agent/benchmark_workflow.py`
  - `tests/test_benchmark_workflow.py`
- Raw P5 benchmark source:
  - `01_RAW_SOURCES/P5_INDUSTRY_INTELLIGENCE/Gingko bio 오픈ai 활용한 software 개발process.pdf`

## Verification

- `python -m pytest -q tests/test_benchmark_workflow.py`: `13 passed`
- `python -m pytest -q tests/test_role_registry.py`: `15 passed`
- `python -m pytest -q`: `232 passed`
- `python scripts/verify_artifacts.py`: `ok: true`, `registry_records: 48`, `chunk_count: 2821`, no errors/warnings
- `git diff --check main...HEAD`: passed after formatting fix

Retrieval eval was not run because retrieval, chunking, scoring, eval fixtures, embeddings, vector DB behavior, reranking, and answer generation were not changed.

## Accepted Scope

- Local deterministic schema/contract layer only.
- Fail-closed validation.
- Source metadata, evidence label, allowed use, prohibited use, and risk-flag fields.
- Human approval gates for wet-lab-sensitive, biosafety, legal/IP, investor-facing, and confidential-source cases.
- Benchmark metric boundary preventing Ginkgo/OpenAI metrics from being represented as Asperitas performance.
- Explicit preservation of `mvp003`, manual/experimental hybrid policy, and non-default deterministic-test reranker policy.

## Rejected Scope

- Autonomous wet-lab claim.
- Wet-lab execution.
- Protocol automation.
- Cloud-lab, LIMS, ELN, robotics, or external execution integration.
- Source ingestion, chunking, embedding, indexing, or eval coverage.
- Source registry, chunk, eval fixture, retrieval, reranker, answer-generation, or runtime pipeline changes.
- Production hybrid retrieval claim.
- Default reranker behavior.

## Source Status

The Ginkgo/OpenAI PDF remains raw-only.

It is not:

- processed into markdown;
- chunked;
- embedded;
- indexed;
- source-registry/eval-covered by MVP-015;
- used to change retrieval behavior.

## Compliance / Source-Grounding Boundary

MVP-015 treats the Ginkgo/OpenAI paper as P5 industry benchmark context only. It is useful as a schema-first, validation-first software-process analogy, not as Asperitas performance evidence and not as authority to operate autonomous wet-lab workflows.

Human approval remains required for wet-lab-sensitive, biosafety, legal/IP, investor-facing, confidential-source, or public-communication use.

## Remaining Risks

- Contract layer is not yet integrated into a runtime planning or validation interface.
- Ginkgo PDF remains raw-only with no chunk/eval coverage.
- Future runtime integration must preserve non-execution and approval-gate boundaries.

## Handoff

Proceed to MVP-016 only after this closeout is reviewed and merged.

Recommended MVP-016: integrate the benchmark workflow contract into a read-only planning/validation interface without changing retrieval defaults or executing workflows.

