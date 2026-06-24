# MVP-019C Security Guard Decision Log

Date: 2026-06-25

## Decision

Add a deterministic local security guard for chat/QA readiness before enabling any answer-generation path.

## Rationale

The repository now has workflow and audit-control layers. MVP-019C adds a narrow guard that inspects explicit request, source, and control-artifact text for prompt-injection, secret exposure, policy bypass, execution-sensitive requests, external-connector requests, and unsafe operational biological requests.

## Scope

Added:

- security guard input, finding, policy, and report contracts
- deterministic text-pattern inspection
- fail-closed schema handling
- source-instruction classification
- secret-like and policy-bypass blocking
- tool and external connector request blocking
- unsafe operational approval gate
- security-to-audit event mapping
- explicit-input CLI
- focused tests
- MVP documentation

## Boundaries

The guard is local and advisory. It does not execute:

- detected instructions
- workflow plans
- retrieval
- source ingestion
- chunking
- embeddings
- vector DB behavior
- reranking
- answer generation
- LLM judging
- shell commands
- MCP or external connector calls
- wet-lab, production, or autonomous actions

## Compliance Gate

Unsafe operational bio/lab/protocol automation requests require human approval by default. The guard does not claim regulatory approval, legal approval, production readiness, or wet-lab validation.

## Retrieval Eval Applicability

Not applicable. This change does not modify retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Next Step

Open MVP-019C as a draft PR for review. Do not start MVP-019D until MVP-019C is merged and verified on main.
