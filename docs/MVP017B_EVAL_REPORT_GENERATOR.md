# MVP-017B Eval Report Generator

Status: MVP-017B local report generation

## Objective

MVP-017B adds local, dependency-free eval report generation from explicit metric results. It consumes the MVP-017A `EvalMetricResult` contract and returns a JSON-safe summary with pass/fail counts, warnings, errors, and metadata.

This is report generation only. It does not perform automatic scoring, retrieval, source ingestion, chunking, indexing, LLM judging, eval fixture mutation, or production-performance reporting.

## Public Functions

- `load_metric_results(path) -> list[EvalMetricResult]`
- `build_eval_report(results, metric_specs=None, metadata=None) -> EvalMetricReport`
- `summarize_eval_report(report) -> dict`

## CLI

```bash
python scripts/generate_eval_report.py --input metric_results.json --json
```

Input shape:

```json
{
  "report_id": "local_eval_report",
  "metadata": {},
  "results": [
    {
      "metric_id": "context_precision",
      "value": 0.9,
      "passed": true,
      "mode": "strict",
      "notes": []
    }
  ]
}
```

Output fields:

- `ok`
- `report_id`
- `summary`
- `results`
- `passed_count`
- `failed_count`
- `report_only_count`
- `strict_count`
- `warnings`
- `errors`
- `metadata`

## Behavior

- Unknown metric IDs warn and are carried as report-only placeholder specs.
- Malformed JSON or malformed result objects fail closed.
- Empty result lists fail closed.
- Strict failed metrics make `ok=false`.
- Report-only metrics never fail the gate.
- `unsupported_claim_rate` remains lower-is-better through the MVP-017A metric spec metadata.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_eval_metrics.py tests/test_eval_report.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py
python scripts/generate_eval_report.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_report.py scripts/generate_eval_report.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.
