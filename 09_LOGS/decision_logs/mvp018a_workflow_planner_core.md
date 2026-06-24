# MVP-018A Workflow Planner Core Decision Log

Date: 2026-06-24

## Decision

Add a deterministic local workflow/planner core for Asperitas V1 agent steps.

## Rationale

MVP-017 completed the local eval layer. MVP-018A starts the workflow layer by defining explicit plan state, step gates, and fail-closed decisions before any execution wrapper exists.

## Scope

Added:

- workflow state dataclasses
- deterministic planner decisions
- JSON-safe serialization and restoration
- local planning CLI
- focused tests
- MVP documentation

## Boundaries

The planner is advisory only. It does not execute:

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

- Missing request: blocked
- Missing source status: requires human approval
- Blocked risk flag: blocked
- High risk flag: requires human approval
- Failed eval gate: blocked
- Missing required skill: requires human approval
- Available required skill: allowed
- All required gates allowed: ready for execution, but execution is not performed

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

MVP-018B should add an explicit workflow-run wrapper around committed local inputs while preserving human approval gates and no automatic execution-sensitive behavior.
