# MVP-018B Workflow Run Wrapper

Status: MVP-018B workflow-run wrapper

## Objective

MVP-018B adds a deterministic wrapper that consumes explicit local JSON inputs, calls the MVP-018A planner, and emits a workflow-run artifact.

The wrapper never executes the plan. It creates a control artifact only.

## Contracts

- `WorkflowRunInput`
- `WorkflowRunArtifact`
- `WorkflowRunStatus`: `ready | blocked | requires_human_approval | invalid`
- `WorkflowRunPolicy`

## Functions

- `load_workflow_run_input(path) -> WorkflowRunInput`
- `build_workflow_run(input_data, policy=None) -> WorkflowRunArtifact`
- `workflow_run_to_dict(run) -> dict`
- `workflow_run_from_dict(data) -> WorkflowRunArtifact`
- `write_workflow_run_artifact(run, path, overwrite=False, create_dirs=False) -> Path`

## Input Shape

```json
{
  "run_id": "local_workflow_run",
  "request": {
    "user_request": "Summarize source-grounded evidence for X",
    "required_skills": ["source-grounding-check"],
    "metadata": {}
  },
  "available_skills": ["source-grounding-check"],
  "source_status": {"available": true, "source_count": 1},
  "eval_gate": {"ok": true},
  "risk_flags": [],
  "metadata": {}
}
```

## Output Shape

The artifact emits:

```text
run_id, schema_version, created_at_utc, status, ok,
executes_plan, ready_for_execution, plan, summary,
inputs, metadata, provenance, warnings, errors
```

## Behavior

- Malformed input returns `status=invalid`.
- Missing `user_request` returns `status=invalid`.
- Planner blocked returns `status=blocked`.
- Planner requires approval returns `status=requires_human_approval`.
- Planner ready returns `status=ready`.
- `executes_plan` is always `false`.
- `ready_for_execution` mirrors planner readiness only as advisory readiness.
- Unknown extra input fields warn and do not block.
- No output path means print JSON only and no file write.
- Existing output path blocks unless `overwrite=True`.
- Missing parent directory blocks unless `create_dirs=True`.

## CLI

```bash
python scripts/run_agent_workflow.py --input workflow_run_input.json --json
python scripts/run_agent_workflow.py --input workflow_run_input.json --output workflow_run_artifact.json --json
```

## Boundaries Preserved

MVP-018B does not:

- add dependencies
- adopt LangGraph
- execute retrieval
- execute answer generation
- execute LLM judges
- execute MCP or external connectors
- mutate source registries
- mutate chunk files
- mutate eval fixtures
- change embedding, vector DB, reranking, or default runtime behavior
- make autonomous, wet-lab, production, or regulatory-readiness claims

## Verification

Required checks:

```bash
python -m pytest -q tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py
python scripts/run_agent_workflow.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_run.py scripts/run_agent_workflow.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-018C should add a read-only workflow inspection/report command over workflow-run artifacts, still without executing retrieval, connectors, or production actions.
