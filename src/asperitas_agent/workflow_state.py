from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


WORKFLOW_RISK_LEVELS = ("low", "medium", "high", "blocked")
WORKFLOW_STEP_STATUSES = ("pending", "allowed", "blocked", "requires_human_approval", "completed")
WORKFLOW_STEP_KINDS = (
    "source_check",
    "skill_selection",
    "risk_preflight",
    "eval_gate_check",
    "evidence_check",
    "answer_plan",
    "audit_ready",
)
DEFAULT_WORKFLOW_VERSION = "MVP-018A"


@dataclass(frozen=True)
class WorkflowPlannerPolicy:
    required_step_kinds: tuple[str, ...] = WORKFLOW_STEP_KINDS
    fail_closed: bool = True
    require_source_status: bool = True
    require_eval_gate: bool = True
    require_skill_check: bool = True
    policy_id: str = "asperitas_workflow_planner_policy"
    version: str = DEFAULT_WORKFLOW_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if not self.fail_closed:
            errors.append("workflow planner policy must fail closed")
        if not isinstance(self.required_step_kinds, tuple) or not self.required_step_kinds:
            errors.append("required_step_kinds must be a non-empty tuple")
        else:
            for step_kind in self.required_step_kinds:
                if step_kind not in WORKFLOW_STEP_KINDS:
                    errors.append(f"invalid required step kind: {step_kind}")
            if len(self.required_step_kinds) != len(set(self.required_step_kinds)):
                errors.append("required_step_kinds must be unique")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class AgentWorkflowRequest:
    user_request: str
    required_skill_id: str | None = None
    source_requirement: str = "source_status_required"
    evidence_requirement: str = "evidence_check_required"
    audit_requirement: str = "audit_ready_required"
    request_id: str = "local_workflow_request"
    version: str = DEFAULT_WORKFLOW_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.request_id.strip():
            errors.append("request_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if not self.user_request.strip():
            errors.append("user_request is required")
        for field_name in ("source_requirement", "evidence_requirement", "audit_requirement"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        if self.required_skill_id is not None and not self.required_skill_id.strip():
            errors.append("required_skill_id must be non-empty when provided")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentWorkflowStep:
    step_kind: str
    status: str
    reason: str
    risk_level: str = "low"
    approval_required: bool = False
    blocks_execution: bool = False
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.step_kind not in WORKFLOW_STEP_KINDS:
            errors.append(f"invalid step_kind: {self.step_kind}")
        if self.status not in WORKFLOW_STEP_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.risk_level not in WORKFLOW_RISK_LEVELS:
            errors.append(f"invalid risk_level: {self.risk_level}")
        if not self.reason.strip():
            errors.append("reason is required")
        if self.status == "blocked" and not self.blocks_execution:
            errors.append("blocked step must set blocks_execution=true")
        if self.status == "requires_human_approval" and not self.approval_required:
            errors.append("approval step must set approval_required=true")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_kind": self.step_kind,
            "status": self.status,
            "reason": self.reason,
            "risk_level": self.risk_level,
            "approval_required": self.approval_required,
            "blocks_execution": self.blocks_execution,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class WorkflowPlannerDecision:
    ok: bool
    decision: str
    reasons: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    version: str = DEFAULT_WORKFLOW_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.decision not in ("allowed", "blocked", "requires_human_approval"):
            errors.append(f"invalid decision: {self.decision}")
        if self.ok and self.decision != "allowed":
            errors.append("ok=true requires decision=allowed")
        if not self.ok and self.decision == "allowed":
            errors.append("ok=false cannot use decision=allowed")
        if not isinstance(self.reasons, tuple) or not self.reasons:
            errors.append("reasons must be a non-empty tuple")
        elif any(not str(reason).strip() for reason in self.reasons):
            errors.append("reasons must contain non-empty strings")
        if any(not str(warning).strip() for warning in self.warnings):
            errors.append("warnings must contain non-empty strings")
        if not self.version.strip():
            errors.append("version is required")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "decision": self.decision,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "version": self.version,
        }


@dataclass(frozen=True)
class AgentWorkflowPlan:
    request: AgentWorkflowRequest
    policy: WorkflowPlannerPolicy
    steps: tuple[AgentWorkflowStep, ...]
    planner_decision: WorkflowPlannerDecision
    ready_for_execution: bool
    executes_plan: bool = False
    plan_id: str = "local_agent_workflow_plan"
    version: str = DEFAULT_WORKFLOW_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.plan_id.strip():
            errors.append("plan_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if self.executes_plan:
            errors.append("workflow plan must not execute")
        errors.extend(f"request: {error}" for error in self.request.validate())
        errors.extend(f"policy: {error}" for error in self.policy.validate())
        errors.extend(f"planner_decision: {error}" for error in self.planner_decision.validate())
        if tuple(step.step_kind for step in self.steps) != self.policy.required_step_kinds:
            errors.append("steps must match policy.required_step_kinds")
        for step in self.steps:
            errors.extend(f"{step.step_kind}: {error}" for error in step.validate())
        if self.ready_for_execution and self.planner_decision.decision != "allowed":
            errors.append("ready_for_execution requires allowed planner decision")
        if self.ready_for_execution and any(step.status != "allowed" for step in self.steps):
            errors.append("ready_for_execution requires all steps allowed")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "version": self.version,
            "executes_plan": self.executes_plan,
            "ready_for_execution": self.ready_for_execution,
            "request": self.request.to_dict(),
            "policy": self.policy.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "planner_decision": self.planner_decision.to_dict(),
        }
