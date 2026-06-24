# MVP-017C Eval Artifact Writer

Status: MVP-017C explicit eval artifact persistence

## Objective

MVP-017C adds a dependency-free writer and loader for explicit eval report artifacts. It builds on MVP-017A metric contracts and MVP-017B local report generation.

This is artifact persistence only. It does not perform automatic scoring, retrieval, source ingestion, chunking, indexing, LLM judging, eval fixture mutation, or production-performance reporting.

## Contracts

- `EvalReportArtifact`
- `build_eval_report_artifact(report, metadata=None) -> EvalReportArtifact`
- `write_eval_report_artifact(artifact, path, overwrite=False) -> Path`
- `load_eval_report_artifact(path) -> EvalReportArtifact`

`write_eval_report_artifact` also accepts `create_dirs=False` so callers can opt in to parent directory creation. Without that opt-in, missing parent directories fail closed.

## Artifact JSON Fields

- `artifact_id`
- `schema_version`
- `created_at_utc`
- `report_id`
- `ok`
- `summary`
- `report`
- `metadata`
- `provenance`
- `warnings`
- `errors`

## CLI

```bash
python scripts/generate_eval_report.py --input metric_results.json --json
python scripts/generate_eval_report.py --input metric_results.json --output report_artifact.json --json
```

No artifact is written unless `--output` is explicitly provided.

## Validation

- Explicit output path is required for writes.
- Parent directory must exist unless `create_dirs=True`.
- Existing files are not overwritten unless `overwrite=True`.
- Malformed artifact files fail closed.
- Artifact payloads must be JSON-safe.
- Load/write roundtrips preserve stable JSON content.
- Strict/report-only counts and failed strict metrics are preserved from the report summary.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py
python scripts/generate_eval_report.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_artifacts.py scripts/generate_eval_report.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.
