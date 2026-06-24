# MVP-017A Eval Metric Schema

Status: MVP-017A schema/report contract

## Objective

MVP-017A adds dependency-free RAGAS-style evaluation metric contracts for local reporting. It defines schema objects, default metric specifications, report aggregation, validation rules, and JSON-safe serialization.

This is schema/report only. It does not score answers, call an LLM judge, mutate eval fixtures, or change retrieval, chunking, embeddings, vector DB, reranking, answer generation, or default runtime behavior.

## Contracts

- `EvalMetricSpec`: metric definition, category, mode, thresholds, risk flags, audit flags, and source-grounding requirements.
- `EvalMetricResult`: one reported metric value and pass state.
- `EvalMetricReport`: metric specs plus results, gate policy, validation, aggregate counts, and JSON-safe output.
- `EvalGatePolicy`: strict/report-only metric policy that fails closed.

## Categories

- `retrieval_quality`
- `grounding`
- `citation_quality`
- `answer_quality`
- `abstention`
- `compliance`
- `tool_or_skill_use`

## Default Metrics

- `context_precision`
- `context_recall`
- `faithfulness`
- `groundedness`
- `answer_relevancy`
- `citation_accuracy`
- `abstention_accuracy`
- `unsupported_claim_rate`
- `compliance_trigger_correctness`
- `skill_selection_accuracy`

## Validation Rules

- Duplicate `metric_id` fails.
- Invalid category or mode fails.
- `strict` metrics must define a pass or fail threshold.
- `report_only` metrics may omit thresholds.
- LLM-judge metrics must be `report_only` by default.
- `unsupported_claim_rate` is lower-is-better.
- Compliance metrics require source grounding and audit.
- Reports serialize through plain Python dictionaries suitable for stable JSON output.

## Boundary

No RAGAS package is adopted. The metric names follow common RAGAS-style evaluation concepts, but the implementation remains local dataclasses with no new dependency, copied third-party code, external connector, or runtime scoring behavior.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_eval_metrics.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_metrics.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.
