# MVP-018C Workflow Inspector Decision Log

Date: 2026-06-24

## Decision

Add read-only inspection and reporting for MVP-018B workflow-run artifacts.

## Rationale

MVP-018A created advisory workflow plans. MVP-018B wrapped those plans into explicit run artifacts. MVP-018C gives humans a deterministic inspection report over those artifacts before any execution-sensitive workflow layer exists.

## Scope

Added:

- workflow inspection finding and report dataclasses
- read-only artifact inspection
- JSON-safe report serialization and restoration
- explicit inspection report writer with overwrite and directory-creation gates
- local inspection CLI
- focused tests
- MVP documentation

## Boundaries

The inspector is read-only. It does not execute:

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

## Inspection Behavior

- Ready run: ok inspection when no blocking findings exist
- Blocked run: blocker findings
- Human approval run: approval findings
- Malformed run: blocked schema report
- `executes_plan=true`: blocked safety finding
- Missing plan: blocked schema finding
- Missing audit/evidence/source gates: gate findings
- Failed eval gate: blocked eval finding

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

MVP-018D should add a deterministic workflow artifact acceptance/regression gate over committed local artifacts without executing workflow plans.
