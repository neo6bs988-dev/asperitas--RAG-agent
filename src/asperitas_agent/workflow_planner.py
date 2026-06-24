from __future__ import annotations

from typing import Any

from asperitas_agent.workflow_state import (
    AgentWorkflowPlan,
    AgentWorkflowRequest,
    AgentWorkflowStep,
    WorkflowPlannerDecision,
    WorkflowPlannerPolicy,
)


def _string_tuple(values: tuple[str, ...] | list[str] | set[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value).strip() for value in values if str(value).strip())


def _status_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "passed" if value else "failed"
    return str(value).strip().lower()


def build_workflow_request(
    user_request: str,
    required_skill_id: str | None = None,
    request_id: str = "local_workflow_request",
) -> AgentWorkflowRequest:
    return AgentWorkflowRequest(
        user_request=user_request,
        required_skill_id=required_skill_id,
        request_id=request_id,
    )


def _step(
    step_kind: str,
    status: str,
    reason: str,
    risk_level: str = "low",
    approval_required: bool = False,
    blocks_execution: bool = False,
    metadata: dict[str, Any] | None = None,
) -> AgentWorkflowStep:
    return AgentWorkflowStep(
        step_kind=step_kind,
        status=status,
        reason=reason,
        risk_level=risk_level,
        approval_required=approval_required,
        blocks_execution=blocks_execution,
        metadata=metadata or {},
    )


def _decide_step(
    step_kind: str,
    request: AgentWorkflowRequest,
    policy: WorkflowPlannerPolicy,
    available_skills: tuple[str, ...],
    eval_gate: str | None,
    source_status: str | None,
    risk_flags: tuple[str, ...],
) -> AgentWorkflowStep:
    if request.validate():
        return _step(step_kind, "blocked", "invalid or missing workflow request", "blocked", blocks_execution=True)

    if "blocked" in risk_flags:
        return _step(step_kind, "blocked", "blocked risk flag present", "blocked", blocks_execution=True)

    if step_kind == "risk_preflight":
        if "high" in risk_flags:
            return _step(
                step_kind,
                "requires_human_approval",
                "high risk flag requires human approval",
                "high",
                approval_required=True,
                metadata={"risk_flags": list(risk_flags)},
            )
        risk_level = "medium" if "medium" in risk_flags else "low"
        return _step(step_kind, "allowed", "risk preflight passed", risk_level, metadata={"risk_flags": list(risk_flags)})

    if "high" in risk_flags:
        return _step(
            step_kind,
            "requires_human_approval",
            "high risk flag requires human approval before execution",
            "high",
            approval_required=True,
        )

    if step_kind == "source_check":
        if policy.require_source_status and source_status is None:
            return _step(
                step_kind,
                "requires_human_approval",
                "source status missing",
                "medium",
                approval_required=True,
            )
        if source_status in {"blocked", "failed"}:
            return _step(step_kind, "blocked", f"source status is {source_status}", "blocked", blocks_execution=True)
        return _step(step_kind, "allowed", "source status present", metadata={"source_status": source_status})

    if step_kind == "skill_selection":
        if policy.require_skill_check and request.required_skill_id:
            if request.required_skill_id not in available_skills:
                return _step(
                    step_kind,
                    "requires_human_approval",
                    "required skill is unavailable",
                    "medium",
                    approval_required=True,
                    metadata={"required_skill_id": request.required_skill_id, "available_skills": list(available_skills)},
                )
            return _step(
                step_kind,
                "allowed",
                "required skill is available",
                metadata={"required_skill_id": request.required_skill_id},
            )
        return _step(step_kind, "allowed", "no required skill declared")

    if step_kind == "eval_gate_check":
        if policy.require_eval_gate and eval_gate is None:
            return _step(
                step_kind,
                "requires_human_approval",
                "eval gate status missing",
                "medium",
                approval_required=True,
            )
        if eval_gate in {"failed", "blocked", "fail"}:
            return _step(step_kind, "blocked", "eval gate failed", "blocked", blocks_execution=True)
        return _step(step_kind, "allowed", "eval gate passed or not required", metadata={"eval_gate": eval_gate})

    return _step(step_kind, "allowed", f"{step_kind} gate allowed")


def build_workflow_plan(
    request: AgentWorkflowRequest,
    policy: WorkflowPlannerPolicy | None = None,
    available_skills: tuple[str, ...] | list[str] | set[str] | None = None,
    eval_gate: str | bool | None = None,
    source_status: str | bool | None = None,
    risk_flags: tuple[str, ...] | list[str] | set[str] | None = None,
) -> AgentWorkflowPlan:
    active_policy = policy or WorkflowPlannerPolicy()
    skill_ids = _string_tuple(available_skills)
    normalized_eval_gate = _status_value(eval_gate)
    normalized_source_status = _status_value(source_status)
    normalized_risk_flags = _string_tuple(risk_flags)

    steps = tuple(
        _decide_step(
            step_kind,
            request,
            active_policy,
            skill_ids,
            normalized_eval_gate,
            normalized_source_status,
            normalized_risk_flags,
        )
        for step_kind in active_policy.required_step_kinds
    )
    blocked = tuple(step for step in steps if step.status == "blocked")
    approvals = tuple(step for step in steps if step.status == "requires_human_approval")
    if blocked:
        decision = WorkflowPlannerDecision(
            ok=False,
            decision="blocked",
            reasons=tuple(dict.fromkeys(step.reason for step in blocked)),
        )
    elif approvals:
        decision = WorkflowPlannerDecision(
            ok=False,
            decision="requires_human_approval",
            reasons=tuple(dict.fromkeys(step.reason for step in approvals)),
        )
    else:
        decision = WorkflowPlannerDecision(ok=True, decision="allowed", reasons=("all workflow gates allowed",))

    return AgentWorkflowPlan(
        request=request,
        policy=active_policy,
        steps=steps,
        planner_decision=decision,
        ready_for_execution=decision.ok and all(step.status == "allowed" for step in steps),
    )


def summarize_workflow_plan(plan: AgentWorkflowPlan) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for step in plan.steps:
        status_counts[step.status] = status_counts.get(step.status, 0) + 1
    return {
        "plan_id": plan.plan_id,
        "version": plan.version,
        "decision": plan.planner_decision.decision,
        "ok": plan.planner_decision.ok,
        "ready_for_execution": plan.ready_for_execution,
        "executes_plan": plan.executes_plan,
        "status_counts": status_counts,
        "blocked_steps": [step.step_kind for step in plan.steps if step.status == "blocked"],
        "approval_steps": [step.step_kind for step in plan.steps if step.status == "requires_human_approval"],
    }


def workflow_plan_to_dict(plan: AgentWorkflowPlan) -> dict[str, Any]:
    return plan.to_dict()


def workflow_plan_from_dict(data: dict[str, Any]) -> AgentWorkflowPlan:
    request_data = data["request"]
    policy_data = data["policy"]
    decision_data = data["planner_decision"]
    return AgentWorkflowPlan(
        plan_id=data.get("plan_id", "local_agent_workflow_plan"),
        version=data.get("version", "MVP-018A"),
        executes_plan=bool(data.get("executes_plan", False)),
        ready_for_execution=bool(data["ready_for_execution"]),
        request=AgentWorkflowRequest(**request_data),
        policy=WorkflowPlannerPolicy(
            required_step_kinds=tuple(policy_data.get("required_step_kinds", ())),
            fail_closed=bool(policy_data.get("fail_closed", True)),
            require_source_status=bool(policy_data.get("require_source_status", True)),
            require_eval_gate=bool(policy_data.get("require_eval_gate", True)),
            require_skill_check=bool(policy_data.get("require_skill_check", True)),
            policy_id=policy_data.get("policy_id", "asperitas_workflow_planner_policy"),
            version=policy_data.get("version", "MVP-018A"),
        ),
        steps=tuple(
            AgentWorkflowStep(
                step_kind=step["step_kind"],
                status=step["status"],
                reason=step["reason"],
                risk_level=step.get("risk_level", "low"),
                approval_required=bool(step.get("approval_required", False)),
                blocks_execution=bool(step.get("blocks_execution", False)),
                metadata=dict(step.get("metadata") or {}),
            )
            for step in data["steps"]
        ),
        planner_decision=WorkflowPlannerDecision(
            ok=bool(decision_data["ok"]),
            decision=decision_data["decision"],
            reasons=tuple(decision_data.get("reasons", ())),
            warnings=tuple(decision_data.get("warnings", ())),
            version=decision_data.get("version", "MVP-018A"),
        ),
    )
