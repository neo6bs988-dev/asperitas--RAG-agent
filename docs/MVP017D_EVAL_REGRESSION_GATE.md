# MVP-017D Eval Regression Gate

Status: MVP-017D manifest and deterministic regression gate

## Objective

MVP-017D closes the MVP-017 eval layer by adding explicit eval artifact manifests and a deterministic regression gate over explicit baseline and candidate artifacts.

This is manifest and gate logic only. It does not perform automatic scoring, retrieval, source ingestion, chunking, indexing, LLM judging, eval fixture mutation, or production-performance reporting.

## Manifest Contracts

- `EvalManifestEntry`
- `EvalManifest`
- `build_eval_manifest(artifact_paths, metadata=None) -> EvalManifest`
- `write_eval_manifest(manifest, path, overwrite=False, create_dirs=False) -> Path`
- `load_eval_manifest(path) -> EvalManifest`

Manifests are built only from explicit artifact paths. There is no repo-wide discovery and no default write path.

## Regression Gate Contracts

- `EvalRegressionPolicy`
- `EvalRegressionDecision`
- `compare_eval_artifacts(baseline, candidate, policy=None) -> EvalRegressionDecision`

The gate accepts explicit `EvalReportArtifact` objects or explicit artifact paths.

## Default Policy

```text
min_required_strict_metrics = [
  "faithfulness",
  "answer_relevance",
  "context_precision",
  "context_recall",
  "unsupported_claim_rate"
]
max_strict_metric_drop = 0.02
max_unsupported_claim_rate_increase = 0.0
allow_unknown_metrics = true
```

## Gate Behavior

- Candidate malformed -> fail.
- Baseline malformed -> fail.
- Candidate `ok=false` -> fail.
- Missing required strict metric from candidate -> fail.
- New strict failure -> fail.
- `unsupported_claim_rate` increase above tolerance -> fail.
- Strict metric drop beyond tolerance -> fail.
- Report-only metrics never fail the gate.
- Unknown metrics warn by default.

## CLI

```bash
python scripts/build_eval_manifest.py --artifact artifact.json --artifact artifact2.json --output manifest.json
python scripts/run_eval_regression_gate.py --baseline baseline_artifact.json --candidate candidate_artifact.json --json
```

## Verification

Required checks:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python scripts/build_eval_manifest.py --help
python scripts/run_eval_regression_gate.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_manifest.py src/asperitas_agent/eval_regression_gate.py scripts/build_eval_manifest.py scripts/run_eval_regression_gate.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.
