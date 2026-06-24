# MVP-019B Workflow Audit Bridge

Status: MVP-019B workflow audit bridge

## Objective

MVP-019B connects existing workflow-control artifacts to the MVP-019A audit trace layer.

The bridge reads explicit workflow run, inspection, and acceptance artifacts, then emits deterministic, redacted audit events. It remains local and control-plane only. It does not execute workflow plans, retrieval, answer generation, connectors, or production actions.

## Inputs

- workflow run artifact
- workflow inspection report
- workflow acceptance decision
- explicit trace metadata

The CLI accepts either a combined input JSON object or separate artifact JSON files.

## Outputs

- `workflow_accepted`, `workflow_rejected`, or `human_approval_required`
- `eval_gate_checked` when the run contains an eval gate step
- `source_gate_checked` when the run contains a source gate step
- `security_guard_triggered` when any artifact indicates `executes_plan=true`

Audit JSONL is written only when an explicit `--output` path is provided. Existing output files are blocked unless `--append` is explicit.

## Failure Behavior

- malformed run artifacts return `invalid`
- malformed inspection reports return `invalid`
- malformed acceptance decisions return `invalid`
- run id mismatches fail closed as `rejected`
- `executes_plan=true` fails closed as `rejected`
- sensitive payload keys are redacted by the MVP-019A audit policy

## CLI

```bash
python scripts/audit_workflow_artifacts.py --run workflow_run.json --inspection workflow_inspection.json --acceptance workflow_acceptance.json --trace-id local_trace --json
python scripts/audit_workflow_artifacts.py --input workflow_audit_input.json --output audit.jsonl --json
```

## Boundaries Preserved

MVP-019B does not:

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
python -m pytest -q tests/test_workflow_audit.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py tests/test_audit_trace.py tests/test_workflow_audit.py
python scripts/audit_workflow_artifacts.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_audit.py scripts/audit_workflow_artifacts.py
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-019C should continue the audit/chat path only after the workflow audit bridge is merged and verified on main.
