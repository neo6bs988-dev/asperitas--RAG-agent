# MVP-018B Workflow Run Wrapper Decision Log

Date: 2026-06-24

## Decision

Add a deterministic local workflow-run wrapper that consumes explicit JSON inputs, calls the MVP-018A planner, and emits a workflow-run artifact.

## Rationale

MVP-018A established advisory planner control artifacts. MVP-018B creates the next workflow layer: an explicit run artifact that records inputs, planner output, status, provenance, warnings, and errors without executing the plan.

## Scope

Added:

- workflow-run input and artifact dataclasses
- JSON input loader
- deterministic artifact builder
- JSON-safe serialization and restoration
- explicit artifact writer with overwrite and directory-creation gates
- local CLI
- focused tests
- MVP documentation

## Boundaries

The wrapper is advisory only. It does not execute:

- retrieval
- source ingestion
- chunking
- embeddings
- vector DB behavior
- reranking
- answer generation
- LLM judging
- MCP or external connector calls
- wet-lab, production, or autonomous actions

## Gate Behavior

- Malformed input: invalid
- Missing request: invalid
- Planner blocked: blocked
- Planner requires approval: requires human approval
- Planner ready: ready
- Existing output path: blocked unless overwrite is explicit
- Missing output parent directory: blocked unless directory creation is explicit

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

MVP-018C should add read-only workflow artifact inspection/reporting while preserving no automatic execution-sensitive behavior.
