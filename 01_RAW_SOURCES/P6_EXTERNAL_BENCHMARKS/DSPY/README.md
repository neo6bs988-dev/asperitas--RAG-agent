# DSPY Benchmark Notes

Priority: P6 External Benchmark
Use: metric-driven prompt and module optimization for V1+.

## Source
- DSPy official docs
- URL: https://dspy.ai/

## Patterns to Absorb
- Treat prompts and pipelines as tunable programs.
- Use metrics to improve modules instead of manual prompt tweaking only.
- Tune query rewriting, retrieval prompts, and answer synthesis against eval targets.

## Asperitas V1 Application
- Not MVP-016 scope.
- Use after stable eval metrics exist.
- Candidate V1+ use cases:
  - query rewrite tuning
  - answer synthesis tuning
  - citation completeness tuning
  - compliance-classification tuning
