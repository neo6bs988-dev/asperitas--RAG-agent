# Asperitas MVP-001/MVP-002 Agent Architecture

## Executive Bottom Line

MVP-001 implements a local, source-grounded, compliance-aware RAG core. MVP-002 upgrades ingestion for real company sources by adding PPTX parsing, safe ZIP inspection, explicit HWPX fallback handling, and deterministic ingestion logs. This is not a production vector database, autonomous agent network, legal review system, regulatory approval system, or wet-lab validation system.

## MVP Architecture

Data flow:

1. `01_RAW_SOURCES/` and root constitution files are discovered.
2. `inventory.py` creates portable relative paths and checksums.
3. `registry.py` writes and validates `data/source_registry.csv`.
4. `loaders.py` extracts text from supported files without modifying originals.
5. `chunking.py` creates metadata-preserving chunks.
6. `retrieval_tfidf.py` performs local lexical retrieval.
7. `compliance.py` scans query and evidence for risk triggers.
8. `rag.py` returns a structured answer object.
9. `cli.py` exposes inventory, ingest, search, ask, and validation commands.
10. `ingestion_log.py` writes a deterministic file-by-file ingestion report to `09_LOGS/run_logs/source_ingestion_log.md`.

## Module Responsibilities

- `schemas.py`: source, chunk, retrieval, compliance, and answer contracts.
- `inventory.py`: source discovery, priority classification, checksums.
- `registry.py`: registry writing and schema validation.
- `loaders.py`: text, PDF, DOCX, PPTX, HWPX fallback, and safe ZIP parsing.
- `chunking.py`: chunk creation with provenance and risk tags.
- `retrieval_tfidf.py`: local TF-IDF-style retrieval.
- `compliance.py`: rule-based compliance gate.
- `rag.py`: answer schema and source-grounded evidence summary.
- `decision_log.py`: append-only decision logging with fallback if the admin log is not plain text.
- `ingestion_log.py`: per-file ingestion status, reason, chunk count, disclosure, priority, and compliance flags.
- `cli.py`: Windows PowerShell-friendly interface.

## MVP-002 Ingestion Behavior

- PPTX files are parsed from slide and notes XML text. Layout, images, charts, and visual semantics are not interpreted.
- ZIP files are inspected in memory only. Archive members are never extracted to disk.
- ZIP path traversal entries and suspicious executable/binary payloads are rejected and logged.
- Supported ZIP inner files are parsed individually while preserving the outer registered `source_id`.
- HWPX files use a ZIP/XML fallback. If no text can be extracted, they are explicitly marked unsupported or failed with a reason.

## Compliance Gate Location

Compliance checks run after retrieval in `rag.py` and independently in `compliance.py`. High-risk biological, legal, regulatory, investor, external communication, or wet-lab requests require human approval.

## Why TF-IDF First

TF-IDF avoids cloud services, API keys, Docker, vector database setup, and embedding drift. This makes MVP-001 testable, deterministic, and easier to audit before moving to embeddings.

## Future Agent Roadmap

MVP-003 can add stronger retrieval, citation evaluation, governance review UI, and optional embeddings. Future agents should reuse this registry, chunk metadata, compliance gate, ingestion log, and answer schema.
