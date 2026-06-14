---
name: embeddings-vector-db-mvp005
description: Use when implementing MVP-005 embeddings, vector database indexing, hybrid retrieval preparation, embedding cache design, or vector retrieval evaluation.
---

# Embeddings Vector DB MVP-005

## When To Use

- Adding embeddings.
- Selecting or integrating a vector DB.
- Designing embedding cache, index schema, vector metadata, or retrieval adapters.
- Moving from deterministic TF-IDF retrieval toward vector or hybrid retrieval.
- Evaluating whether embeddings improve retrieval quality without breaking source-grounding.

## When Not To Use

- Pure MVP-004 chunk metadata work with no embedding/index impact.
- Answer-generation-only changes that do not touch retrieval.
- Compliance-only review with no vector storage or data-governance implication.

## Required Inputs

- Current chunk schema and metadata fields.
- Current eval command and baseline metrics.
- Target embedding model or placeholder adapter.
- Vector DB choice or decision matrix.
- Storage location and persistence policy.
- Metadata fields required for source-grounding and compliance.

## Workflow Steps

1. Inspect current chunking, schema, registry, and retrieval modules.
2. Confirm MVP-004 baseline and non-regression rules.
3. Define embedding record schema before writing vector code.
4. Preserve source IDs, source file, priority, evidence label, section metadata, and confidence-related fields.
5. Add a deterministic fallback path so TF-IDF remains usable.
6. Add tests for embedding record generation, metadata preservation, and retrieval adapter behavior.
7. Run unit tests and artifact verification.
8. Run baseline and metadata-aware retrieval evals.
9. If vector retrieval is implemented, add a separate eval mode instead of replacing existing modes silently.
10. Report metric deltas and cost/storage implications.

## Quality Gates

- Existing TF-IDF and MVP-003 retrieval paths still work.
- Vector metadata preserves source-grounding fields.
- Eval can compare old and new retrievers.
- No API key or secret is committed.
- Index generation is reproducible or cache invalidation is documented.
- Compliance risk from storing biological/biodiversity metadata is reviewed.

## Report Format

- MVP:
- Objective:
- Vector DB / embedding approach:
- Files changed:
- Metadata preserved:
- Tests:
- Artifact verification:
- Retrieval eval before/after:
- Cost/storage impact:
- Compliance impact:
- Risks:
- Next step:

## Failure Conditions

- Vector retrieval replaces deterministic retrieval without fallback.
- Source IDs or evidence labels are lost in vector metadata.
- Evaluation cannot compare retrievers.
- Secrets, credentials, or private endpoints are committed.
- Biological/compliance storage risks are ignored.
- The implementation depends on external paid APIs without explicit configuration boundaries.

## Next-Step Recommendation Format

Recommend one concrete MVP-005 task with:

- Task:
- Why now:
- Required files:
- Required eval mode:
- Blocking decision:
