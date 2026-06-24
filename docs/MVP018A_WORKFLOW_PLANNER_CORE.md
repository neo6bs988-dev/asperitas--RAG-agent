# MVP-018A Workflow Planner Core

Status: MVP-018A workflow/planner core

## Objective

MVP-018A adds a deterministic local workflow planner for Asperitas V1 agent steps.

The planner creates advisory control artifacts only. It does not execute retrieval, tools, connectors, LLM judges, answer generation, source ingestion, chunking, embeddings, vector DB writes, reranking, or production actions.

## Contracts

- `WorkflowRiskLevel`: `low | medium | high | blocked`
- `WorkflowStepStatus`: `pending | allowed | blocked | requires_human_approval | completed`
- `WorkflowStepKind`: `source_check | skill_selection | risk_preflight | eval_gate_check | evidence_check | answer_plan | audit_ready`
- `AgentWorkflowRequest`
- `AgentWorkflowStep`
- `AgentWorkflowPlan`
- `WorkflowPlannerPolicy`
- `WorkflowPlannerDecision`

## Functions

- `build_workflow_request(...)`
- `build_workflow_plan(request, policy=None, available_skills=None, eval_gate=None, source_status=None, risk_flags=None)`
- `summarize_workflow_plan(plan)`
- `workflow_plan_to_dict(plan)`
- `workflow_plan_from_dict(data)`

## Planner Behavior

- Missing user request fails closed.
- Missing source status requires human approval.
- `blocked` risk flag blocks the plan.
- `high` risk flag requires human approval.
- Failed eval gate blocks the plan.
- Missing required skill requires human approval.
- Available required skill allows the skill step.
- All required gates allowed sets `ready_for_execution=true`.
- `executes_plan` remains `false`.

## CLI

```bash
python scripts/plan_agent_workflow.py --request "Summarize source-grounded evidence for X" --json
python scripts/plan_agent_workflow.py --input workflow_request.json --json
```

The CLI emits a workflow plan JSON object. The default CLI inputs provide `source_status=available` and `eval_gate=passed` so a simple low-risk smoke command returns an allowed plan.

## Boundaries Preserved

MVP-018A does not:

- add dependencies
- adopt LangGraph
- execute MCP or external connectors
- execute retrieval
- execute answer generation
- mutate source registries
- mutate chunk files
- mutate eval fixtures
- change embedding, vector DB, reranking, or default runtime behavior
- make autonomous or production-readiness claims

## Verification

Required checks:

```bash
python -m pytest -q tests/test_workflow_state.py tests/test_workflow_planner.py
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py tests/test_eval_metrics.py tests/test_eval_report.py tests/test_eval_artifacts.py tests/test_eval_manifest.py tests/test_eval_regression_gate.py tests/test_workflow_state.py tests/test_workflow_planner.py
python scripts/plan_agent_workflow.py --help
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/workflow_state.py src/asperitas_agent/workflow_planner.py scripts/plan_agent_workflow.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-018B should connect this advisory plan contract to an explicit workflow-run wrapper that consumes committed local inputs only and still requires human approval before execution-sensitive steps.
