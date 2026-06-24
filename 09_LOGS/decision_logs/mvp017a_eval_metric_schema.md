# Decision Log: MVP-017A Eval Metric Schema

Date: 2026-06-24

## Decision

Add local, dependency-free RAGAS-style evaluation metric contracts for Asperitas eval reporting.

## Rationale

MVP-016 closed the local skills layer and identified MVP-017 as the next eval-layer step. MVP-017A defines metric schemas before introducing scoring behavior so future eval work can report retrieval quality, grounding, citation quality, answer quality, abstention, compliance, and tool or skill use through explicit contracts.

## Scope

Added:

- `EvalMetricSpec`
- `EvalMetricResult`
- `EvalMetricReport`
- `EvalGatePolicy`
- default metric specifications
- focused validation tests
- schema documentation

## Safety Boundary

This change does not:

- adopt the RAGAS package
- add dependencies
- copy third-party code
- call OpenAI, Anthropic, LangGraph, LlamaIndex, MCP, Google ADK, or external services
- change retrieval behavior
- change chunking behavior
- mutate source registry data
- mutate eval fixtures
- change embeddings or vector DB behavior
- change reranking behavior
- change answer generation
- change production defaults
- claim production performance

LLM-judge-dependent metrics are report-only by default. Compliance metrics require source grounding and audit fields.

## Verification Plan

Run:

```bash
python -m pytest -q tests/test_eval_metrics.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/eval_metrics.py
```

Retrieval eval is not applicable because retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, and default runtime behavior are unchanged.

## Next

MVP-017B should add local eval report generation or fixture-compatible metric result capture without changing retrieval defaults or adopting external scoring dependencies.
