# LANGSMITH Benchmark Notes

Priority: P6 External Benchmark
Use: evaluation lifecycle, observability, datasets, experiments, traces, regression testing.

## Source
- LangSmith Evaluation Concepts
- URL: https://docs.langchain.com/langsmith/evaluation-concepts

## Patterns to Absorb
- Define what good means before building evals.
- Use manually curated examples as early ground truth.
- Separate offline evals from online monitoring.
- Track examples, datasets, experiments, runs, traces, and evaluator scores.
- Use online production issues to update offline datasets.

## Asperitas V1 Application
- MVP-017: make eval artifacts comparable across runs.
- MVP-019: create a trace-like audit record for each query.
- V1: separate dev regression evals from future production monitoring.
