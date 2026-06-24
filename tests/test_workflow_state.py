from __future__ import annotations

import json

from asperitas_agent.workflow_planner import (
    build_workflow_plan,
    build_workflow_request,
    workflow_plan_from_dict,
    workflow_plan_to_dict,
)
from asperitas_agent.workflow_state import (
    WORKFLOW_STEP_KINDS,
    AgentWorkflowPlan,
    AgentWorkflowRequest,
    AgentWorkflowStep,
    WorkflowPlannerDecision,
    WorkflowPlannerPolicy,
)


def test_workflow_contracts_validate():
    request = build_workflow_request("Summarize source-grounded evidence for X", required_skill_id="asperitas_workflow")
    policy = WorkflowPlannerPolicy()
    steps = tuple(
        AgentWorkflowStep(step_kind=step_kind, status="allowed", reason=f"{step_kind} allowed")
        for step_kind in WORKFLOW_STEP_KINDS
    )
    plan = AgentWorkflowPlan(
        request=request,
        policy=policy,
        steps=steps,
        planner_decision=WorkflowPlannerDecision(True, "allowed", ("all workflow gates allowed",)),
        ready_for_execution=True,
    )

    assert request.validate() == ()
    assert policy.validate() == ()
    assert plan.validate() == ()
    assert plan.executes_plan is False


def test_missing_request_fails_closed_validation():
    request = AgentWorkflowRequest(user_request="")
    plan = build_workflow_plan(request, eval_gate="passed", source_status="available")

    assert "user_request is required" in request.validate()
    assert plan.planner_decision.decision == "blocked"
    assert plan.ready_for_execution is False
    assert all(step.status == "blocked" for step in plan.steps)


def test_json_roundtrip_stable():
    plan = build_workflow_plan(
        build_workflow_request("Summarize source-grounded evidence for X", required_skill_id="asperitas_workflow"),
        available_skills=("asperitas_workflow",),
        eval_gate="passed",
        source_status="available",
    )
    first = json.dumps(workflow_plan_to_dict(plan), sort_keys=True, separators=(",", ":"))
    restored = workflow_plan_from_dict(json.loads(first))
    second = json.dumps(workflow_plan_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second
