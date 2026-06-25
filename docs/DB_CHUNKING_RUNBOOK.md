# DB Chunking and Ingestion Runbook

Status: active runbook
Repository: `asperitas--RAG-agent`

## Executive Bottom Line

Database work must proceed as a verified pipeline, not as a claim that documents are already fully learned. The safe sequence is:

source inventory -> source registry -> metadata validation -> text extraction -> chunking -> artifact verification -> retrieval eval -> decision log -> PR review.

## Required Boundary

Do not claim a production database exists until ingestion artifacts, registry counts, chunk counts, retrieval metrics, and approval records are actually present in the repository or attached release artifacts.

## Pipeline Order

1. Inspect existing repo structure and current artifact state.
2. Register new playbook and related source files in the source registry.
3. Assign priority, source type, confidentiality level, license/review status, and verification status.
4. Extract text into parser-friendly markdown or text artifacts.
5. Chunk extracted text using the existing chunking policy.
6. Preserve source ID, document ID, page/section reference, priority, and citation target on every chunk.
7. Run artifact verification.
8. Run retrieval eval if chunking, scoring, metadata, embeddings, or answer generation changed.
9. Write a decision log with counts, commands, skipped checks, and risks.
10. Open PR for review.

## Minimum Chunk Metadata

Each chunk should preserve:

- source_id
- document_id
- title
- source_priority
- source_type
- confidentiality_level
- license_or_review_status
- extraction_method
- chunk_id
- chunk_index
- section_or_page
- citation_target
- verification_status
- created_at

## Default Chunking Policy

Use the repository's existing chunking policy if one exists. If no explicit policy exists, implement the smallest compatible policy:

- stable deterministic IDs
- section-aware splitting where possible
- overlap only when needed for continuity
- no mutation of source meaning
- no loss of provenance
- test coverage for deterministic chunk IDs and required metadata

## Required Verification Commands

Use the actual repository commands after inspection. Expected candidates:

```bash
python -m pytest -q
python scripts/verify_artifacts.py
python scripts/evaluate_agent.py
python scripts/run_golden_agent_eval.py
```

Run retrieval evals when retrieval-related behavior changes.

## Codex Execution Prompt

```text
Use AGENTS.md and relevant .agents/skills instructions.

Task:
Absorb the new agent development playbook into the repository knowledge base and advance DB chunking/ingestion work safely.

Context:
- Current repo: asperitas--RAG-agent
- Current MVP stage: MVP-018
- New source: docs/PLAYBOOK_AGENT_DEVELOPMENT_WORKFLOW.md
- Target: source registry, metadata, extraction/chunking artifacts, verification, retrieval eval if affected, decision log

Constraints:
- Inspect existing files first.
- Do not delete files.
- Make the smallest safe change.
- Do not duplicate existing ingestion or chunking logic.
- Preserve source IDs, metadata, citation targets, and evidence labels.
- If existing ingestion/chunking scripts exist, reuse them.
- If raw source ingestion is not possible, create a preflight report and do not claim ingestion completed.
- Add/update tests for source-code changes.
- Run pytest if source code changes.
- Run artifact verification.
- Run retrieval eval if retrieval/chunking/scoring/metadata/embedding/answer generation changes.
- Update docs and decision logs.

Report:
1. objective
2. files inspected
3. files changed
4. registry delta
5. chunk count before/after
6. verification commands and results
7. retrieval metrics before/after
8. skipped checks and reason
9. risks
10. next action
```
