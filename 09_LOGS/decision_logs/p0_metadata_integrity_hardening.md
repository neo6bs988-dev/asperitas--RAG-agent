# P0 Metadata Integrity Hardening Decision Log

Date: 2026-06-25
Status: implemented as deterministic reporting hardening

## Decision

Add a metadata integrity audit module and CLI report that classify missing section metadata without mutating chunk artifacts, source registry records, retrieval behavior, embeddings, vector DB state, reranking, or answer generation.

## Evidence

Baseline section audit:

- total chunks: 2,821
- chunks with section metadata: 2,097
- chunks missing section metadata: 724
- missing-section rate: 25.6647%

Metadata integrity audit:

- derivable: 41
- parser limitation: 211
- source-format limitation: 472
- unresolved missing chunks: 683
- path context present for missing chunks: 724
- duplicate source IDs: 0

## Rationale

Only first chunks can safely report source-title-derived section candidates from existing registry metadata. Non-first chunks missing section data do not contain enough reliable local structure in existing chunk fields to infer section metadata without guessing.

## Boundaries Preserved

- No new sources.
- No external scraping or ingestion.
- No source registry mutation.
- No chunk artifact mutation.
- No retrieval ranking, scoring, embedding, vector DB, reranking, hybrid default, or answer-generation changes.
- `mvp003` remains the protected deterministic reference retriever.
- Relaxed metrics remain report-only.

## Next Step

Plan a separate parser/chunking upgrade for approved source artifacts if the team wants to turn safe candidates or recovered headings into stored metadata. That future PR should regenerate artifacts deterministically and include before/after retrieval metrics.
