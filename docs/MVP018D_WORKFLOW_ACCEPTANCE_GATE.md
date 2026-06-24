# MVP-018D Workflow Acceptance Gate

Status: MVP-018D workflow acceptance gate

## Objective

MVP-018D adds a deterministic acceptance gate over explicit workflow-run and workflow-inspection artifacts.

The gate validates readiness for later chat/QA wiring. It never executes the workflow.

## Contracts

- `WorkflowAcceptancePolicy`
- `WorkflowAcceptanceDecision`
- `WorkflowAcceptanceStatus`: `accepted | rejected | requires_human_approval | invalid`
- `WorkflowAcceptanceReason`

## Functions

- `accept_workflow_artifacts(run_artifact, inspection_report, policy=None) -> WorkflowAcceptanceDecision`
- `accept_workflow_artifact_dicts(run_data, inspection_data, policy=None) -> WorkflowAcceptanceDecision`
- `workflow_acceptance_to_dict(decision) -> dict`
- `workflow_acceptance_from_dict(data) -> WorkflowAcceptanceDecision`
- `write_workflow_acceptance_decision(decision, path, overwrite=False, create_dirs=False) -> Path`
- `summarize_workflow_acceptance(decision) -> dict`

## Required Steps

```text
source_check
skill_selection
risk_preflight
eval_gate_check
evidence_check
answer_plan
audit_ready
```

## Behavior

- Malformed run artifact returns `invalid`.
- Malformed inspection report returns `invalid`.
- Run ID mismatch returns `rejected`.
- `executes_plan=true` returns `rejected`.
- Blocked run returns `rejected`.
- Human-approval run returns `requires_human_approval`.
- `run.ok=false` returns `rejected` unless the run requires human approval.
- `inspection.ok=false` returns `rejected` unless the run requires human approval.
- Inspection blocked/error findings return `rejected`.
- Missing required workflow step returns `rejected`.
- Missing `audit_ready` returns `rejected`.
- Failed `eval_gate_check`, `evidence_check`, or `source_check` returns `rejected`.
- Ready run plus ok inspection plus all required steps returns `accepted`.
- Unknown extra fields warn and do not block by themselves.

## CLI

```bash
python scripts/run_workflow_acceptance_gate.py --run workflow_run_artifact.json --inspection workflow_inspection.json --json
python scripts/run_workflow_acceptance_gate.py --run workflow_run_artifact.json --inspection workflow_inspection.json --output workflow_acceptance.json --json
```

The CLI reads only explicit input paths. It writes only when `--output` is provided.

## Boundaries Preserved

MVP-018D does not:

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
python -m pytest -q tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py
python scripts/run_workflow_acceptance_gate.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_acceptance.py scripts/run_workflow_acceptance_gate.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-019 should wire the accepted workflow artifacts into a read-only chat/QA planning surface without enabling automatic retrieval or execution.
