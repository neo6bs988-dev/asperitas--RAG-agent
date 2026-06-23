# PHOENIX Benchmark Notes

Priority: P6 External Benchmark
Use: LLM tracing, RAG observability, debug workflows.

## Source
- Arize Phoenix LLM Tracing Docs
- URL: https://arize.com/docs/phoenix/tracing/llm-traces

## Patterns to Absorb
- Trace the full RAG/agent execution path.
- Capture retrieval spans, generation spans, tool calls, latency, and outputs.
- Use traces to debug hallucination, bad retrieval, and validation failures.

## Asperitas V1 Application
- MVP-019 should implement lightweight local audit traces:
  - query
  - planner output
  - retrieved chunks
  - reranker output
  - validation result
  - final answer
  - citations
  - warnings/gates
