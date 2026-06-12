# MVP-001 Failure Modes

## Source Metadata Loss

Risk: chunks become anonymous or lose priority/disclosure data.  
Mitigation: tests assert `source_id`, priority, disclosure, and verification status survive chunking.

## Confidential Data Leakage

Risk: confidential P0/P1 material is used in external-facing outputs.  
Mitigation: disclosure metadata is preserved; external-use filtering should be strengthened in MVP-002.

## Unsupported File Parse Failure

Risk: PDFs, HWPX, ZIP, or Office files fail parsing.  
Mitigation: register parse status as failed, partial, or unsupported; log every file-level reason and continue where safe.

## Unsafe ZIP Payload

Risk: a ZIP archive contains path traversal, executable payloads, suspicious binaries, or unsupported inner files.  
Mitigation: inspect ZIP members in memory, reject unsafe entries, never extract to disk, and record rejected entries in the ingestion log.

## Partial Archive Ingestion

Risk: users confuse partial ZIP ingestion with full source learning.  
Mitigation: outer ZIP sources can be marked `partial`, inner unsupported/failed files are logged, and no production ingestion claim is made.

## HWPX Fallback Ambiguity

Risk: HWPX files fail extraction silently or appear learned when no text was extracted.  
Mitigation: MVP-002 returns explicit parsed, unsupported, or failed status with a reason.

## Hallucinated Source

Risk: answer cites nonexistent or unsupported sources.  
Mitigation: answer schema uses retrieved chunk metadata only.

## False Compliance Negative

Risk: risky CITES, Nagoya, LMO, wet-lab, legal, investor, or external-communication request is not flagged.  
Mitigation: rule coverage tests; expand terms in MVP-002.

## Overblocking Harmless Queries

Risk: normal strategy questions are blocked.  
Mitigation: tests assert ordinary source hierarchy queries do not require human approval.

## Production-Readiness Overclaim

Risk: MVP is described as production RAG, KG, legal review, regulatory approval, or wet-lab validation.  
Mitigation: docs and answer limitations explicitly reject those claims.

## Path and Import Fragility

Risk: Windows paths or src-layout imports fail.  
Mitigation: use `pathlib`, relative paths, and local `sitecustomize.py` for direct CLI use.

## No API Key Failure

Risk: ask command fails without LLM access.  
Mitigation: ask returns retrieved evidence, compliance analysis, limitations, and next action.

## Large-File Ingestion Failure

Risk: large PDFs, decks, or ZIP files slow or fail extraction.  
Mitigation: loader failures are non-fatal; ZIP members are size-limited; future MVPs should add richer parsing and performance controls.
