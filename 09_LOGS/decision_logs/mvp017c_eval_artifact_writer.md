# Decision Log: MVP-017C Eval Artifact Writer

Date: 2026-06-24

## Decision

Add a local, dependency-free eval report artifact writer and loader for explicit eval reports.

## Rationale

MVP-017A defined local metric schemas. MVP-017B generated local report summaries from explicit metric results. MVP-017C adds explicit artifact persistence so reports can be saved and reloaded without introducing automatic scoring, retrieval execution, or eval fixture mutation.

## Scope

Added:

- `EvalReportArtifact`
- `build_eval_report_artifact(report, metadata=None)`
- `write_eval_report_artifact(artifact, path, overwrite=False, create_dirs=False)`
- `load_eval_report_artifact(path)`
- optional `--output <path>` support in `scripts/generate_eval_report.py`
- tests for artifact build/write/load/roundtrip, overwrite protection, create-dir behavior, malformed artifact failure, strict/report-only preservation, script output, and no default writes

## Safety Boundary

This change does not:

- adopt the RAGAS package
- add dependencies
- copy third-party code
- execute an LLM judge
- execute retrieval
- ingest, chunk, index, or embed sources
- mutate eval fixtures
- mutate source artifacts
- change reranking behavior
- change answer generation
- create a default artifact write path
- make production-performance claims

Artifacts are written only when an explicit output path is provided.

## Verification Plan

Run:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py
python scripts/generate_eval_report.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_artifacts.py scripts/generate_eval_report.py
```

Retrieval eval is not applicable because retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, and default runtime behavior are unchanged.

## Next

MVP-017D should add an explicit eval artifact index or manifest contract while preserving opt-in writes and no automatic scoring.
