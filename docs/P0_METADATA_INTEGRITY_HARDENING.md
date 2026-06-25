# P0 Metadata Integrity Hardening

Status: deterministic audit/reporting hardening
Branch: `p0-metadata-integrity-hardening`
Date: 2026-06-25

## Objective

Audit chunk/source metadata integrity after PR #51 and classify why section metadata remains missing, without changing retrieval ranking, scoring, embeddings, vector DB behavior, reranking, answer generation, source registry contents, or chunk artifacts.

## Root Cause Taxonomy

The current metadata gap is concentrated in parsed source formats where stable structural headings were not recoverable by the existing fixed-window section marker pass.

Baseline audit:

- total chunks: 2,821
- chunks with section metadata: 2,097
- chunks missing section metadata: 724
- missing-section rate: 25.6647%
- safe derivable candidates: 41
- unresolved missing chunks: 683

Risk classes from `python scripts/audit_metadata_integrity.py --json`:

- derivable: 41
- parser limitation: 211
- source-format limitation: 472

Missing by extension:

- pdf: 465
- zip: 223
- docx: 14
- pptx: 12
- hwpx: 10

Missing by source type:

- internal: 720
- prompt: 4

Missing by priority:

- P0: 4
- P1: 720

Missing by chunker:

- fixed_window_section_marker: 724

Missing by path context availability:

- present: 724

## Safe Repair Policy

No chunk artifacts are rewritten in this PR.

The new metadata integrity audit reports a safe derivation candidate only when all of the following are true:

- the chunk is missing section metadata;
- the chunk starts at character offset 0;
- the source registry has a stable title;
- the derived value is reported as a candidate, not silently promoted into stored metadata.

This prevents invented section metadata for non-first chunks, parser-limited PDFs, archive-derived chunks, and extracted office formats whose local heading context cannot be recovered from existing chunk fields.

## Deterministic Report

Run:

```bash
python scripts/audit_metadata_integrity.py --json
```

The report includes:

- total chunks;
- chunks with/missing section metadata;
- missing-section rate;
- missing count by source file;
- missing count by source ID;
- missing count by extension;
- missing count by type;
- missing count by priority;
- missing count by parser;
- missing count by chunker;
- missing count by path context availability;
- example missing chunks;
- safe derivation candidate status;
- risk classification counts.

## Retrieval Behavior

This PR does not change retrieval behavior. `mvp003` remains the protected deterministic reference retriever, hybrid remains explicit/manual/experimental, and relaxed metrics remain report-only.

## Remaining Missing Metadata

The unresolved 683 chunks should remain missing/unknown until a future scoped parser or ingestion upgrade can prove section context from approved existing source content. The highest-volume unresolved groups are PDF and archive-derived internal sources, especially Korean PDF extraction and ZIP-contained source material.

## Next Recommended Task

Scope a separate parser/ingestion improvement that reconstructs heading paths before fixed-window chunking, then regenerate artifacts only with before/after metadata counts, retrieval evals, and artifact verification.
