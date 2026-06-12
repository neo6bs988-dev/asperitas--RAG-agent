# MVP-002 Recovery Checkpoint

Date: 2026-06-12 KST

## Current MVP Status

MVP-002 is stable and locally verified.

- MVP-001 behavior is preserved: deterministic TF-IDF retrieval, source provenance, registry validation, artifact verification, and CITES/high-risk compliance blocking.
- MVP-002 source ingestion upgrade is implemented: PPTX extraction, safe ZIP inspection, explicit HWPX fallback, and deterministic ingestion logging.
- This checkpoint does not claim production RAG, vector DB indexing, embeddings, legal approval, regulatory approval, KG completion, UI readiness, or wet-lab validation.

## Stable Architecture

Current data flow:

1. `inventory.py` discovers root constitution files and `01_RAW_SOURCES/`.
2. `registry.py` validates and writes `data/source_registry.csv`.
3. `loaders.py` parses supported source types and safely inspects ZIP archives.
4. `chunking.py` creates provenance-preserving chunks.
5. `retrieval_tfidf.py` performs deterministic local lexical retrieval.
6. `compliance.py` flags CITES, Nagoya, LMO/GMO, biosafety, biosecurity, wet-lab, legal, financial, and external-communication risks.
7. `rag.py` returns source-grounded structured answers with limitations and next actions.
8. `ingestion_log.py` writes deterministic ingestion logs to `09_LOGS/run_logs/source_ingestion_log.md`.
9. `verification.py` verifies registry/chunk artifact integrity.
10. `cli.py` exposes validation, inventory, ingest, search, ask, and artifact verification commands.

## Current Modules

- `src/asperitas_agent/schemas.py`
- `src/asperitas_agent/inventory.py`
- `src/asperitas_agent/registry.py`
- `src/asperitas_agent/loaders.py`
- `src/asperitas_agent/ingestion_log.py`
- `src/asperitas_agent/chunking.py`
- `src/asperitas_agent/retrieval_tfidf.py`
- `src/asperitas_agent/compliance.py`
- `src/asperitas_agent/rag.py`
- `src/asperitas_agent/verification.py`
- `src/asperitas_agent/decision_log.py`
- `src/asperitas_agent/cli.py`

## Supported File Types

Supported directly:

- `.md`
- `.txt`
- `.pdf`
- `.docx`
- `.pptx`
- `.hwpx` through explicit ZIP/XML fallback
- `.zip` through safe in-memory inspection of supported inner files

Supported inside ZIP archives:

- `.md`
- `.txt`
- `.pdf`
- `.docx`
- `.pptx`
- `.hwpx`

## Unsupported or Partial File Types

- ZIP inner files with unsupported extensions are logged as unsupported.
- ZIP path traversal members are rejected.
- Suspicious executable or binary inner files are rejected.
- macOS ZIP metadata/resource fork files such as `__MACOSX/` and `._*` are logged as unsupported metadata.
- HWPX files that do not expose extractable ZIP/XML text are explicitly marked unsupported or failed.
- Nested ZIP/archive recursion is not implemented.

Current artifact state:

- Registry records: 48
- Parse status: 47 parsed, 1 partial
- Chunk count: 2821
- Ingestion log entries: 81
- Ingestion log status: 64 success, 17 unsupported

## Test Status

Last stabilization result:

```powershell
python -m pytest -q
```

Expected result:

```text
36 passed
```

Local one-command smoke test:

```powershell
.\scripts\verify_mvp001.cmd
```

Expected final line:

```text
MVP-001 verification passed.
```

Note: despite the script name, it now also verifies stabilized MVP-002 artifacts.

## Compliance Boundaries

- CITES/high-risk biological, regulatory, wet-lab, legal, financial, or external-facing requests require human approval.
- The system can flag risk and provide source-grounded context, but it does not grant legal, regulatory, biosafety, or external-communication approval.
- The system must not generate operational wet-lab instructions that bypass qualified supervision.
- The system must not claim production vector DB, embeddings, KG, legal approval, regulatory approval, or wet-lab validation.

## Known Limitations

- Retrieval remains deterministic local TF-IDF, not embeddings or vector search.
- PPTX parsing extracts slide/notes XML text only; layout, images, charts, and visual semantics are not interpreted.
- HWPX parsing is best-effort ZIP/XML fallback, not full HWP semantic parsing.
- ZIP archives are inspected in memory, but nested archive recursion is not implemented.
- No UI, reranker, LLM answer generation, external connector, or production deployment is included.

## Critical Rollback Files

Code:

- `pyproject.toml`
- `sitecustomize.py`
- `asperitas_agent/__init__.py`
- `src/asperitas_agent/*.py`
- `scripts/verify_mvp001.ps1`
- `scripts/verify_mvp001.cmd`

Tests:

- `tests/test_chunking.py`
- `tests/test_compliance.py`
- `tests/test_ingestion_mvp002.py`
- `tests/test_inventory.py`
- `tests/test_loaders.py`
- `tests/test_rag_schema.py`
- `tests/test_registry.py`
- `tests/test_retrieval.py`
- `tests/test_verification.py`

Artifacts:

- `data/source_registry.csv`
- `data/chunks.jsonl`
- `09_LOGS/run_logs/source_ingestion_log.md`
- `09_LOGS/decision_logs/mvp001_decision_log.md`

Docs:

- `docs/AGENT_ARCHITECTURE.md`
- `docs/AOS_SOURCE_POLICY.md`
- `docs/EVALS.md`
- `docs/FAILURE_MODES.md`
- `CHECKPOINT_MVP_002.md`

## Recommended Commit Message

```text
Stabilize MVP-002 source ingestion upgrade
```

## Next Planned Milestone

MVP-002.5 Retrieval Evaluation Set
