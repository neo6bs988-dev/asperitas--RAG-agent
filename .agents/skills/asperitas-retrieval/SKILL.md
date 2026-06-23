---
name: asperitas-retrieval
description: Use when modifying or evaluating Asperitas retrieval, metadata-aware search, source ranking, citation grounding, or RAG answer context selection.
---

# Asperitas Retrieval Skill

## Purpose
Improve retrieval without breaking source provenance, metadata filters, citations, or eval compatibility.

## Required Inputs
- User task / MVP number
- Target files or modules if known
- Current eval metrics if available
- Source hierarchy and metadata schema

## Workflow
1. Read `AGENTS.md` and relevant source/retrieval modules.
2. Identify retrieval layer boundaries: ingestion, chunking, indexing, search, reranking, answer synthesis.
3. Preserve backward compatibility with existing chunk/source schemas.
4. Prefer small changes that can be tested.
5. Ensure every returned context keeps source_id, path, title, priority, disclosure, and verification status.
6. Add or update tests for metadata filters, citation retention, and edge cases.
7. Run retrieval eval or document why it could not be run.

## Output Requirements
Report:
1. Objective
2. Files changed
3. Retrieval behavior before/after
4. Tests run
5. Eval metrics before/after
6. Risks
7. Remaining gaps
8. Next recommended MVP action

## Stop Rules
- Do not remove provenance fields.
- Do not claim production vector DB/KG/eval deployment without logs.
- Do not ingest external full text without license/terms review.
