# MVP-017 Eval Layer Closeout

Status: MVP-017 closed

## Objective

MVP-017 adds the local, dependency-free eval reporting layer for Asperitas V1 without adopting RAGAS as a package or enabling automatic scoring.

## Completed Scope

- MVP-017A: local RAGAS-style eval metric schema.
- MVP-017B: local report generation from explicit metric results.
- MVP-017C: explicit eval report artifact writer and loader.
- MVP-017D: explicit artifact manifest and deterministic regression gate.

## Preserved Boundaries

MVP-017 does not:

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
- create default write paths for artifacts or manifests
- make production-performance claims

## Eval Layer Capability

The repository can now:

- define metric contracts
- load explicit metric results
- build JSON-safe eval reports
- write and load explicit report artifacts
- build explicit artifact manifests
- compare baseline and candidate artifacts through a deterministic regression gate

All capabilities operate on explicit local inputs and preserve fail-closed behavior for malformed inputs.

## Verification

MVP-017D closeout requires:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py
python scripts/build_eval_manifest.py --help
python scripts/run_eval_regression_gate.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_manifest.py src/asperitas_agent/eval_regression_gate.py scripts/build_eval_manifest.py scripts/run_eval_regression_gate.py
```

Retrieval eval remains not applicable because MVP-017 does not change retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior.

## Next MVP

MVP-018 should add an explicit eval-run workflow or CI-safe gate wrapper that consumes committed test artifacts only when explicitly provided. It should preserve no automatic scoring and no retrieval default changes unless separately scoped and eval-approved.
