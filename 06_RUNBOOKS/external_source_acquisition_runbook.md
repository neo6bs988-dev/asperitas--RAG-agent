# External Source Acquisition Runbook

## Objective
Convert registered-only external benchmark sources into legally reviewable raw sources and then into processed KB artifacts without confusing source mapping with production ingestion.

## Current state
- Registry exists: `00_ADMIN/source_registries/external_benchmark_source_registry.csv`
- All entries start as `registered_only`.
- No raw files, processed markdown, chunks, embeddings, vector DB records, or eval results are created by this scaffold.

## Acquisition sequence
1. Select one source row from the registry.
2. Verify URL, organization, source type, and source priority.
3. Review license, terms of service, IP constraints, confidentiality, privacy, and compliance risk.
4. If approved, record approval evidence in a decision log.
5. Acquire raw source only through official/public/legal channels.
6. Store raw source in the correct P-folder with provenance metadata.
7. Update `ingestion_status` from `registered_only` to `raw_acquired`.
8. Extract to markdown only after raw acquisition is approved.
9. Preserve source ID, title, URL, retrieval date, disclosure, license status, and checksum.
10. Run metadata validation tests.
11. Chunk and embed only after markdown extraction and metadata validation pass.
12. Run retrieval/eval cases before using the source in answers.

## Stop rules
- Stop before raw acquisition if terms/license status is unclear.
- Stop before processing if the source contains personal data, secrets, private company data, or restricted material.
- Stop before indexing if metadata is incomplete.
- Stop before production claims unless raw acquisition, extraction, chunking, embedding, retrieval, and eval logs exist.

## Status transitions
- `registered_only`: metadata only; no raw content.
- `raw_acquired`: raw source legally acquired and stored with provenance.
- `processed_markdown`: extracted markdown exists and retains metadata.
- `chunked`: chunk artifacts exist and pass schema checks.
- `embedded`: embeddings/vector records exist and are reproducible.
- `evaluated`: eval cases pass and regression status is logged.
- `rejected`: source cannot be used due to license, terms, quality, or compliance risk.

## Required evidence before processing
- Source URL and retrieval date.
- License/terms review outcome.
- Disclosure level.
- Intended use case.
- Evidence weight.
- Decision log entry.
- Checksum if raw file is stored.

## Next recommended command for Codex
Run registry validation, then create a source-by-source license review table before acquiring raw sources. Do not crawl or ingest full web pages until each source is approved.
