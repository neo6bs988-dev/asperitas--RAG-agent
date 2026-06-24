# MVP-019B Workflow Audit Bridge Decision Log

Date: 2026-06-25

## Decision

Add a local workflow audit bridge that converts workflow run, inspection, and acceptance artifacts into redacted MVP-019A audit trace events.

## Rationale

MVP-019A defined deterministic audit records. MVP-019B gives the workflow-control layer a narrow bridge into that audit contract without enabling execution-sensitive behavior or changing retrieval/runtime paths.

## Scope

Added:

- workflow audit input, policy, and result contracts
- deterministic artifact-to-audit event mapping
- fail-closed handling for malformed artifacts
- run id mismatch and `executes_plan=true` guards
- explicit-output JSONL writer wrapper
- local CLI
- focused tests
- MVP documentation

## Boundaries

The bridge is local and control-plane only. It does not execute:

- workflow plans
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

## Redaction Policy

Sensitive payload keys remain governed by the MVP-019A audit trace policy. The workflow audit bridge does not introduce a new redaction policy or bypass the existing one.

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

Open MVP-019B as a draft PR for review. Do not start MVP-019C until MVP-019B is merged and verified on main.
