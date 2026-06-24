# MVP-018 Workflow Layer Closeout

Status: MVP-018 closed after MVP-018D

## Objective

MVP-018 adds the local, dependency-free workflow control layer for Asperitas V1.

The layer is deterministic, JSON-safe, and advisory. It does not execute retrieval, tools, connectors, LLM judges, answer generation, source ingestion, chunking, embeddings, vector DB writes, reranking, wet-lab actions, or production actions.

## Completed Scope

- MVP-018A: workflow/planner core.
- MVP-018B: workflow-run wrapper.
- MVP-018C: workflow artifact inspection/reporting.
- MVP-018D: workflow acceptance gate.

## Capability

The repository can now:

- build a deterministic advisory workflow plan;
- wrap explicit local inputs into workflow-run artifacts;
- inspect workflow-run artifacts for readiness, blockers, approval needs, and audit-readiness;
- run a deterministic acceptance gate over explicit run and inspection artifacts.

## Preserved Boundaries

MVP-018 does not:

- execute workflow plans
- execute retrieval
- execute answer generation
- execute LLM judges
- execute MCP or external connectors
- ingest, chunk, index, or embed sources
- mutate source artifacts
- mutate eval fixtures
- change reranking behavior
- change default runtime behavior
- create default write paths
- make production, autonomous, wet-lab, regulatory, or performance claims

## Verification

MVP-018D closeout requires:

```bash
python -m pytest -q tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py
python scripts/run_workflow_acceptance_gate.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_acceptance.py scripts/run_workflow_acceptance_gate.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval remains not applicable because MVP-018 does not change retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior.

## Next MVP

MVP-019 should add read-only chat/QA workflow wiring that consumes accepted workflow artifacts and still preserves explicit human approval gates before any execution-sensitive behavior.
