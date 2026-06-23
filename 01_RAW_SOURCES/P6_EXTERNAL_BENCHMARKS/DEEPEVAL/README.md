# DEEPEVAL Benchmark Notes

Priority: P6 External Benchmark
Use: local LLM/RAG eval tests, CI/CD evaluation pattern, component-level tracing.

## Source
- DeepEval Docs
- URL: https://deepeval.com/docs/getting-started

## Patterns to Absorb
- Evaluation test cases should be runnable locally.
- Evals should include input, actual output, expected output where useful, and metric thresholds.
- CI/CD can run eval tests to catch regressions.
- Agent tracing can evaluate retrievers, tools, and generation components separately.

## Asperitas V1 Application
- Use current custom evals first.
- Add DeepEval-style structure to future tests:
  - `tests/eval/`
  - `eval_results/`
  - JSON artifacts
  - regression thresholds
- Do not require external cloud service for basic V1 quality gates.
