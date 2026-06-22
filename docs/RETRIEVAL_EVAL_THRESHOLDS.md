# Retrieval Eval Thresholds

This policy defines the first executable retrieval eval threshold gate.

Run threshold enforcement explicitly:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever vector --limit 5 --enforce-thresholds
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5 --enforce-thresholds
```

Default eval commands remain unchanged. Thresholds are enforced only when `--enforce-thresholds` is present.

## Metric Set

The gate uses the existing retrieval eval vocabulary:

- `source_file_match_at_5`
- `source_priority_match`
- `evidence_label_match`
- `section_match`
- `path_context_match`
- `overall_pass_rate`

`source_file_match_at_3` remains report-only for now. It should be used for reranker analysis and future stricter top-k policy, but it is not yet a hard fail threshold.

## Threshold Profiles

| Retriever | Required minimums |
|---|---|
| `baseline` | source @5 >= 30%, source priority >= 30%, evidence label >= 30%, overall >= 30% |
| `mvp003` | source @5 = 100%, source priority = 100%, evidence label = 100%, section >= 90%, path context = 100%, overall >= 90% |
| `vector` | source @5 >= 50%, source priority >= 50%, evidence label >= 50%, path context = 100%, overall >= 50% |
| `hybrid` | source @5 = 100%, source priority = 100%, evidence label = 100%, section = 100%, path context = 100%, overall >= 95% |

## Pass / Fail Behavior

- Passing threshold enforcement exits with code `0`.
- Failing threshold enforcement exits with code `1`.
- Eval setup errors, missing files, invalid fixtures, or unsupported threshold profiles exit with code `2`.
- JSON output includes a `thresholds` object when enforcement is enabled.
- Plain-text output prints a `Threshold gate` section when enforcement is enabled.
- Threshold metrics that are not applicable to the selected eval set, such as `path_context_match` when no question has path-context expectations, are reported as `n/a` and do not fail the gate.

## Runtime Diagnostics

The eval script emits flushed progress diagnostics to `stderr` while loading inputs, running each retriever question, aggregating metrics, and enforcing thresholds. This keeps long `mvp003` and `hybrid` runs observable without changing `stdout` summaries or JSON output.

If a local OS or native-runtime hard exit occurs, use the last `[retrieval-eval]` line on `stderr` to identify the failed stage and question. Do not treat a hard exit as a threshold pass.

## Guardrails

- `mvp003` remains the protected deterministic reference retriever.
- `hybrid` remains an explicit comparison mode, not the default.
- Thresholds must not relax source priority, evidence label, section, path-context, or metadata preservation gates.
- Historical metrics must not be treated as fresh threshold evidence.
- Reranker test-double results must not be claimed as quality improvement unless fresh thresholded evals support that claim.

## Future P3 Tightening

Consider adding hard `source_file_match_at_3` thresholds after reranker strategy is candidate-preserving and measured without source @3 regression.
