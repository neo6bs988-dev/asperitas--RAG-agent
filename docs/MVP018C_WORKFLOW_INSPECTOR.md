# MVP-018C Workflow Inspector

Status: MVP-018C workflow artifact inspection/reporting

## Objective

MVP-018C adds read-only inspection and reporting for MVP-018B workflow-run artifacts.

The inspector helps a human understand readiness, blockers, approval needs, missing gates, and audit-readiness. It never executes the workflow.

## Contracts

- `WorkflowInspectionFinding`
- `WorkflowInspectionReport`
- `WorkflowInspectionSeverity`: `info | warning | error | blocked`
- `WorkflowInspectionCategory`: `readiness | approval | source | skill | eval | evidence | audit | safety | schema`

## Functions

- `inspect_workflow_run(run) -> WorkflowInspectionReport`
- `inspect_workflow_run_dict(data) -> WorkflowInspectionReport`
- `workflow_inspection_to_dict(report) -> dict`
- `workflow_inspection_from_dict(data) -> WorkflowInspectionReport`
- `write_workflow_inspection_report(report, path, overwrite=False, create_dirs=False) -> Path`
- `summarize_workflow_inspection(report) -> dict`

## Behavior

- Malformed run artifact returns a blocked schema report.
- `status=ready` and `ok=true` returns `inspection.ok=true` when no blocking findings exist.
- `status=blocked` returns `inspection.ok=false` with blocker findings.
- `status=requires_human_approval` returns `inspection.ok=false` with approval findings.
- `executes_plan=true` creates a blocked safety finding.
- Missing plan creates a blocked schema finding.
- Missing `audit_ready` creates an audit finding.
- Missing evidence/source steps create evidence/source findings.
- Failed eval gate creates blocked eval findings.
- Unknown extra fields create warnings and do not block by themselves.
- Reports preserve `run_id`, run status, `ready_for_execution`, and `executes_plan`.

## CLI

```bash
python scripts/inspect_workflow_run.py --input workflow_run_artifact.json --json
python scripts/inspect_workflow_run.py --input workflow_run_artifact.json --output workflow_inspection.json --json
```

The CLI reads only an explicit input path. It writes only when `--output` is provided.

## Boundaries Preserved

MVP-018C does not:

- add dependencies
- execute workflow plans
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
python -m pytest -q tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py
python scripts/inspect_workflow_run.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_inspector.py scripts/inspect_workflow_run.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-018D should add a workflow artifact regression or acceptance gate over committed workflow-run and inspection artifacts, while preserving explicit local inputs and no workflow execution.
