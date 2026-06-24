# MVP-018D Workflow Acceptance Gate Decision Log

Date: 2026-06-25

## Decision

Add a deterministic workflow acceptance gate over explicit workflow-run and workflow-inspection artifacts.

## Rationale

MVP-018A through MVP-018C established advisory planning, run artifacts, and inspection reports. MVP-018D closes the workflow layer by adding an explicit acceptance decision before future chat/QA wiring.

## Scope

Added:

- workflow acceptance policy, reason, and decision dataclasses
- deterministic acceptance over run and inspection artifacts
- JSON-safe serialization and restoration
- explicit acceptance decision writer with overwrite and directory-creation gates
- local CLI
- focused tests
- MVP-018D documentation
- MVP-018 closeout documentation

## Boundaries

The acceptance gate is advisory only. It does not execute:

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

## Gate Behavior

- Ready run plus ok inspection plus all required steps: accepted
- Malformed artifact: invalid
- Run ID mismatch: rejected
- `executes_plan=true`: rejected
- Blocked run or blocked/error inspection finding: rejected
- Human-approval run: requires human approval
- Missing required gates: rejected

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

MVP-019 should add read-only chat/QA workflow wiring that consumes accepted workflow artifacts without enabling automatic workflow execution.
