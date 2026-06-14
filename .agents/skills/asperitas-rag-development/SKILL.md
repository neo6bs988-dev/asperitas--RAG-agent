---
name: asperitas-rag-development
description: Use for Asperitas RAG architecture, chunking, retrieval, metadata, vector DB, reranking, and source-grounded answer generation work.
---

# Asperitas RAG Development

## When To Use

- RAG architecture changes.
- Chunking, metadata, indexing, retrieval, embeddings, vector DB, hybrid retrieval, reranking, or answer generation changes.
- Design review for MVP-004 through MVP-008.

## When Not To Use

- Pure documentation edits with no RAG behavior impact.
- General GitHub review with no retrieval or answer-generation impact.
- Compliance-only review with no RAG implementation decision.

## Required Inputs

- Objective and MVP stage.
- Relevant source files, tests, scripts, and docs.
- Current retrieval eval command and dataset, if present.
- Expected behavior and known failure modes.

## Workflow Steps

1. Inspect existing RAG files before editing.
2. Identify affected stage: chunking, metadata, retrieval, embeddings, vector DB, reranker, or answer generation.
3. Define the smallest safe change.
4. Update or add tests for changed behavior.
5. Run source code tests.
6. Run retrieval eval if retrieval quality can change.
7. Check source-grounding and compliance impact.
8. Report metrics, risks, and next MVP task.

## Quality Gates

- Source code tests pass or blocker is documented.
- Retrieval eval runs for retrieval-affecting changes.
- Citations and source IDs remain traceable.
- Compliance risks are surfaced.
- Docs are updated when behavior or commands change.

## Report Format

- Objective:
- Files changed:
- Tests:
- Retrieval eval:
- Source-grounding impact:
- Compliance impact:
- Risks:
- Next step:

## Failure Conditions

- Existing RAG files were not inspected.
- Retrieval behavior changed without tests or eval.
- Answer generation can use unsupported claims.
- Source IDs, metadata, or evidence labels are dropped.
- Biological or compliance risk is ignored.

## Next-Step Recommendation Format

Recommend one concrete MVP task with:

- MVP:
- Task:
- Why now:
- Quality gate:

