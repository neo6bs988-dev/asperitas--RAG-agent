# MVP-016A Benchmark Workflow Preflight Decision Layer

Date: 2026-06-23

## Objective

MVP-016A adds a local read-only preflight decision layer for MVP-015 benchmark workflow specifications.

The layer accepts a `BenchmarkWorkflowSpec`, runs the existing MVP-015 validation contract, and returns one of:

- `allowed`
- `blocked`
- `requires_human_approval`

It does not execute workflows, ingest sources, alter retrieval, or change default runtime behavior.

## Scope

Implemented scope:

- preserve MVP-015 validation as the fail-closed contract;
- return structured decision payloads with reasons, validation errors, risk flags, human approval requirements, source metadata, policy metadata, and metrics metadata;
- always report `executed: false` and `ingested: false`;
- block invalid specs, execution intent, external execution targets, metric overclaims, retrieval policy changes, wet-lab validation claims, and autonomous wet-lab claims through MVP-015 validation;
- require human approval for valid specs with active approval-triggering risk flags;
- extend preflight approval classification for CITES, Nagoya, LMO, and privacy risk flags without changing the MVP-015 schema.

## Non-Goals

MVP-016A does not:

- create a CLI;
- execute any benchmark workflow;
- ingest, chunk, embed, index, or eval-cover the Ginkgo/OpenAI PDF;
- change source registry, chunks, eval fixtures, retrieval, embeddings, vector DB, reranker, answer generation, or default runtime behavior;
- change `mvp003`;
- make hybrid or reranker default;
- claim Asperitas performance from benchmark metrics;
- claim autonomous wet-lab capability, wet-lab validation, protocol automation, external execution, cloud-lab/LIMS/ELN/robotics integration, legal/regulatory/biosafety approval, or production readiness.

## Decision Semantics

`blocked`:

- `spec.validate()` returns one or more errors.

`requires_human_approval`:

- `spec.validate()` passes; and
- at least one active risk flag is in the MVP-015 approval-required domains or the MVP-016A added domains: CITES, Nagoya, LMO, or privacy.

`allowed`:

- `spec.validate()` passes;
- the spec remains non-executing and non-ingesting;
- no active approval-triggering risk flags are present.

## Source-Grounding Boundary

The Ginkgo/OpenAI PDF remains raw-only P5 industry intelligence. MVP-016A preserves source path, source priority, and evidence label in the decision payload but does not treat the PDF as ingested, chunked, embedded, indexed, eval-covered, or evidence of Asperitas performance.

## Security and Open-Source Review

No third-party code, snippets, dependencies, external connectors, or copied workflows were added. The implementation is local Python code and uses only existing MVP-015 contracts.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py
python scripts/verify_artifacts.py
git diff --check
python -m pytest -q
```

Retrieval eval is not applicable because MVP-016A does not change retrieval, chunking, metadata handling, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.
