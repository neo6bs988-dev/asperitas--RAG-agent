# Decision Log: MVP-017B Eval Report Generator

Date: 2026-06-24

## Decision

Add local eval report generation from explicit MVP-017A metric results.

## Rationale

MVP-017A established dependency-free eval metric contracts. MVP-017B adds the next local reporting layer so explicit metric results can be loaded, summarized, and emitted as stable JSON before any future scoring or judge implementation exists.

## Scope

Added:

- `load_metric_results(path)`
- `build_eval_report(results, metric_specs=None, metadata=None)`
- `summarize_eval_report(report)`
- `scripts/generate_eval_report.py`
- focused tests for loading, validation, summary behavior, CLI JSON output, and artifact non-mutation
- MVP documentation

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
- make production-performance claims

Unknown metric IDs warn but are carried as report-only placeholders. Malformed result inputs fail closed. Report-only results do not fail gates.

## Verification Plan

Run:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py
python scripts/generate_eval_report.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_report.py scripts/generate_eval_report.py
```

Retrieval eval is not applicable because retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, and default runtime behavior are unchanged.

## Next

MVP-017C should add fixture-compatible explicit result capture or a local report artifact writer while preserving no automatic scoring and no retrieval default changes.
