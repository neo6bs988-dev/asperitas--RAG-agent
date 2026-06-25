# MVP-019D Chat QA Workflow Decision Log

Date: 2026-06-25

## Decision

Add a local/internal chat/QA workflow wrapper that gates a question through security, workflow acceptance, and audit events before any answer provider can run.

## Rationale

MVP-019A through MVP-019C established audit trace, workflow audit, and security guard layers. MVP-019D wires those control layers into a first chat/QA wrapper while keeping the CLI dry-run by default because no real answer provider needs to be changed or invoked for this MVP.

## Scope

Added:

- chat question, answer evidence, answer artifact, policy, provider, and result contracts
- deterministic security -> workflow -> audit gate flow
- provider injection contract for tests and future opt-in integration
- dry-run CLI
- explicit result and audit output writers
- focused tests
- MVP documentation

## Boundaries

The wrapper is local and internal. It does not execute:

- detected source or user instructions
- shell commands
- external connectors
- workflow plans
- retrieval internals
- answer generation internals
- source ingestion
- chunking
- embeddings
- vector DB behavior
- reranking
- wet-lab, production, or autonomous actions

## Answer Provider Status

No real RAG answer provider is wired in this MVP. Programmatic tests use a stub provider. The CLI returns `dry_run_ready` after gates pass and does not fake an answer.

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

Open MVP-019D as a draft PR for review. Do not start MVP-019E until MVP-019D is merged and verified on main.
