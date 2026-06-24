# MVP-001/MVP-002 Eval Plan

## Retrieval Quality Evals

- Query returns relevant chunks.
- Empty index returns an empty result rather than crashing.
- Result objects include source ID, title, score, priority, disclosure level, evidence label, and verification status.

## Retrieval Oracle Policy

Retrieval evals report strict and relaxed oracle metrics separately.

- Strict metrics preserve the original exact `expected_source_file` behavior and remain the regression/threshold source of truth.
- Relaxed metrics are additive and pass source matching when a retrieved source matches the strict expected source, an `accepted_sources` path, an `accepted_source_ids` value, or a conservative `accepted_aliases` match.
- Relaxed metrics are for oracle-quality diagnosis only. They must not silently replace strict metrics, threshold gates, or historical baseline comparisons.
- `multi_valid_source` marks questions where duplicate copies, version aliases, or closely overlapping governance/source documents can make exact single-source labels too narrow.
- Accepted source sets should be added only when justified by the source registry, duplicate filenames, folder path context, or documented audit findings.
- Adding relaxed oracle metadata does not optimize retrieval, change ranking, make hybrid default, or imply production vector/RAG readiness.

Eval expansion to 60-100 questions remains blocked until strict and relaxed oracle behavior is reviewed on the current 32-question set.

## Citation and Source Coverage Evals

- Every chunk preserves `source_id`.
- Every answer lists retrieved sources.
- Unsupported claims are represented as limitations instead of invented evidence.

## Compliance and Refusal Evals

- CITES, Nagoya, LMO/GMO, biosafety, biosecurity, wet-lab, legal, financial, investor, and external communication triggers are detected.
- Wet-lab or operational biological requests require human approval.
- Harmless strategy questions should not be overblocked.

## Hallucination Evals

- No answer should claim legal approval, regulatory approval, wet-lab validation, production deployment, vector DB indexing, or KG completion unless an implemented system proves it.
- No answer should fabricate source IDs or unsupported citations.

## Schema Validity Evals

- Registry columns match the required schema.
- RAG answer contains evidence labels, limitations, next action, risk tags, confidence, and verification status.

## Regression Evals

- Unsupported file types do not crash ingestion.
- Mislabeled or binary files are registered safely.
- No API key is required for ask/search.

## MVP-002 Ingestion Evals

- PPTX slide XML text is extracted.
- Safe ZIP archives parse supported inner files without writing archive contents to disk.
- ZIP path traversal members are rejected and logged.
- Suspicious executable or binary ZIP members are rejected and logged.
- Unsupported ZIP inner files are explicitly logged.
- HWPX fallback returns parsed text or a clear unsupported/failed reason.
- Mixed ingestion keeps the registry valid and all chunks preserve provenance metadata.

## Windows PowerShell Verification

Run the repo-local verification script before moving from MVP-001 to the next milestone:

```powershell
.\scripts\verify_mvp001.cmd
```

If local PowerShell script execution is allowed, the script can also be run directly:

```powershell
.\scripts\verify_mvp001.ps1
```

If `python` is not available on `PATH`, pass an explicit interpreter:

```powershell
.\scripts\verify_mvp001.ps1 -Python "C:\path\to\python.exe"
```

The script runs pytest, validates the registry, checks artifact integrity, checks search provenance, and confirms that a CITES document-generation request requires human approval.

For lower-level artifact inspection, run:

```powershell
python -m asperitas_agent.cli verify-artifacts
```

After source changes, regenerate ingestion artifacts with:

```powershell
python -m asperitas_agent.cli ingest
python -m asperitas_agent.cli verify-artifacts
```
