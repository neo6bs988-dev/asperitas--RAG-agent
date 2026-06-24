# Decision Log: MVP-017D Eval Regression Gate

Date: 2026-06-24

## Decision

Close MVP-017 by adding explicit eval artifact manifests and a deterministic regression gate for baseline-versus-candidate artifact comparison.

## Rationale

MVP-017A defined local metric contracts. MVP-017B generated local reports from explicit results. MVP-017C wrote and loaded explicit report artifacts. MVP-017D adds the minimal comparison and indexing layer needed to make those artifacts useful for regression review without introducing automatic scoring, retrieval, or external dependencies.

## Scope

Added:

- `EvalManifestEntry`
- `EvalManifest`
- `build_eval_manifest`
- `write_eval_manifest`
- `load_eval_manifest`
- `EvalRegressionPolicy`
- `EvalRegressionDecision`
- `compare_eval_artifacts`
- `scripts/build_eval_manifest.py`
- `scripts/run_eval_regression_gate.py`
- tests for manifest build/write/load, malformed paths, gate failures, unknown metric warnings, CLI JSON output, and no source/eval fixture mutation
- MVP-017D documentation
- MVP-017 closeout documentation

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
- create default write paths
- perform repo-wide artifact discovery
- make production-performance claims

Manifest construction requires explicit artifact paths. Regression comparison requires explicit baseline and candidate artifacts.

## Verification Plan

Run:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python scripts/build_eval_manifest.py --help
python scripts/run_eval_regression_gate.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_manifest.py src/asperitas_agent/eval_regression_gate.py scripts/build_eval_manifest.py scripts/run_eval_regression_gate.py
```

Retrieval eval is not applicable because retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, and default runtime behavior are unchanged.

## Next

Proceed to MVP-018: explicit eval-run workflow or CI-safe gate wrapper using provided artifacts only.
