# MVP-019A Audit Trace Layer Decision Log

Date: 2026-06-25

## Decision

Add deterministic audit/trace logging contracts for V1 workflow and control decisions.

## Rationale

MVP-018 closed the workflow control layer. MVP-019A starts the audit layer by defining JSON-safe, redacted, JSONL-compatible audit events before chat/QA wiring or execution-sensitive behavior exists.

## Scope

Added:

- audit event, record, and policy dataclasses
- deterministic payload redaction
- JSON-safe event and record serialization
- JSONL write and load helpers
- strict and non-strict malformed JSONL behavior
- local CLI
- focused tests
- MVP documentation

## Boundaries

The audit trace layer is local and control-plane only. It does not execute:

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

Sensitive key fragments are redacted by default:

- `secret`
- `token`
- `api_key`
- `password`
- `private_key`
- `credential`

Long `raw_text` payloads are redacted unless explicitly allowed by policy.

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

MVP-019B should connect accepted workflow artifacts to audit events while preserving explicit local inputs and no automatic execution.
