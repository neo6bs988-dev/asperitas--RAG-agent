from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.workflow_planner import (
    build_workflow_plan,
    build_workflow_request,
    summarize_workflow_plan,
    workflow_plan_from_dict,
    workflow_plan_to_dict,
)
from asperitas_agent.workflow_state import AgentWorkflowPlan, WorkflowPlannerPolicy


WORKFLOW_RUN_STATUSES = ("ready", "blocked", "requires_human_approval", "invalid")
DEFAULT_WORKFLOW_RUN_VERSION = "MVP-018B"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
KNOWN_INPUT_FIELDS = (
    "run_id",
    "request",
    "available_skills",
    "source_status",
    "eval_gate",
    "risk_flags",
    "metadata",
)


@dataclass(frozen=True)
class WorkflowRunPolicy:
    fail_closed: bool = True
    allow_output_overwrite: bool = False
    allow_create_dirs: bool = False
    policy_id: str = "asperitas_workflow_run_policy"
    schema_version: str = DEFAULT_WORKFLOW_RUN_VERSION
    created_at_utc: str = DEFAULT_CREATED_AT_UTC

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if not self.fail_closed:
            errors.append("workflow run policy must fail closed")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkflowRunInput:
    run_id: str
    user_request: str
    required_skills: tuple[str, ...] = ()
    available_skills: tuple[str, ...] = ()
    source_status: dict[str, Any] | None = None
    eval_gate: dict[str, Any] | None = None
    risk_flags: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None
    raw_input: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.run_id.strip():
            errors.append("run_id is required")
        if not self.user_request.strip():
            errors.append("user_request is required")
        for field_name in ("required_skills", "available_skills", "risk_flags"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                errors.append(f"{field_name} must be a tuple")
            elif any(not str(item).strip() for item in value):
                errors.append(f"{field_name} must contain non-empty strings")
        if self.source_status is not None and not isinstance(self.source_status, dict):
            errors.append("source_status must be an object when provided")
        if self.eval_gate is not None and not isinstance(self.eval_gate, dict):
            errors.append("eval_gate must be an object when provided")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "request": {
                "user_request": self.user_request,
                "required_skills": list(self.required_skills),
                "metadata": dict((self.metadata or {}).get("request_metadata", {})),
            },
            "available_skills": list(self.available_skills),
            "source_status": self.source_status,
            "eval_gate": self.eval_gate,
            "risk_flags": list(self.risk_flags),
            "metadata": dict(self.metadata or {}),
            "provenance": dict(self.provenance or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class WorkflowRunArtifact:
    run_id: str
    schema_version: str
    created_at_utc: str
    status: str
    ok: bool
    executes_plan: bool
    ready_for_execution: bool
    plan: AgentWorkflowPlan | None
    summary: dict[str, Any]
    inputs: WorkflowRunInput | None
    metadata: dict[str, Any]
    provenance: dict[str, Any]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.run_id.strip():
            errors.append("run_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.status not in WORKFLOW_RUN_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.executes_plan:
            errors.append("workflow run artifact must not execute")
        if self.ok and self.status != "ready":
            errors.append("ok=true requires status=ready")
        if self.status == "ready" and not self.ok:
            errors.append("status=ready requires ok=true")
        if self.plan is not None:
            errors.extend(f"plan: {error}" for error in self.plan.validate())
            if self.executes_plan or self.plan.executes_plan:
                errors.append("workflow run must preserve executes_plan=false")
        if self.ready_for_execution and self.status != "ready":
            errors.append("ready_for_execution requires status=ready")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "status": self.status,
            "ok": self.ok,
            "executes_plan": self.executes_plan,
            "ready_for_execution": self.ready_for_execution,
            "plan": workflow_plan_to_dict(self.plan) if self.plan is not None else None,
            "summary": dict(self.summary),
            "inputs": self.inputs.to_dict() if self.inputs is not None else None,
            "metadata": dict(self.metadata),
            "provenance": dict(self.provenance),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def _string_tuple(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if not isinstance(values, (list, tuple, set)):
        return ()
    return tuple(str(value).strip() for value in values if str(value).strip())


def _input_from_dict(data: Any, provenance: dict[str, Any] | None = None) -> WorkflowRunInput:
    if not isinstance(data, dict):
        return WorkflowRunInput(
            run_id="invalid_workflow_run",
            user_request="",
            provenance=provenance or {},
            errors=("input JSON must be an object",),
        )
    warnings = tuple(f"unknown input field: {key}" for key in sorted(set(data) - set(KNOWN_INPUT_FIELDS)))
    request = data.get("request", {})
    if not isinstance(request, dict):
        return WorkflowRunInput(
            run_id=str(data.get("run_id", "invalid_workflow_run")),
            user_request="",
            raw_input=data,
            provenance=provenance or {},
            warnings=warnings,
            errors=("request must be an object",),
        )
    request_metadata = request.get("metadata", {})
    metadata = dict(data.get("metadata") or {}) if isinstance(data.get("metadata", {}), dict) else {}
    if isinstance(request_metadata, dict):
        metadata["request_metadata"] = dict(request_metadata)
    return WorkflowRunInput(
        run_id=str(data.get("run_id", "local_workflow_run")),
        user_request=str(request.get("user_request", "")),
        required_skills=_string_tuple(request.get("required_skills")),
        available_skills=_string_tuple(data.get("available_skills")),
        source_status=data.get("source_status") if isinstance(data.get("source_status"), dict) else data.get("source_status"),
        eval_gate=data.get("eval_gate") if isinstance(data.get("eval_gate"), dict) else data.get("eval_gate"),
        risk_flags=_string_tuple(data.get("risk_flags")),
        metadata=metadata,
        raw_input=data,
        provenance=provenance or {},
        warnings=warnings,
    )


def load_workflow_run_input(path: str | Path) -> WorkflowRunInput:
    input_path = Path(path)
    provenance = {"input_path": str(input_path)}
    try:
        data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # fail closed into an invalid artifact path
        return WorkflowRunInput(
            run_id="invalid_workflow_run",
            user_request="",
            provenance=provenance,
            errors=(f"failed to load input JSON: {exc}",),
        )
    return _input_from_dict(data, provenance=provenance)


def _source_status_value(source_status: dict[str, Any] | None) -> str | None:
    if source_status is None:
        return None
    if source_status.get("available") is True:
        return "available"
    if source_status.get("ok") is True:
        return "available"
    if source_status.get("blocked") is True:
        return "blocked"
    if source_status.get("available") is False:
        return None
    return str(source_status.get("status", "available")).strip().lower() or None


def _eval_gate_value(eval_gate: dict[str, Any] | None) -> str | None:
    if eval_gate is None:
        return None
    if eval_gate.get("ok") is True:
        return "passed"
    if eval_gate.get("ok") is False:
        return "failed"
    return str(eval_gate.get("status", "passed")).strip().lower() or None


def _required_skill_for_planner(input_data: WorkflowRunInput) -> str | None:
    missing = tuple(skill for skill in input_data.required_skills if skill not in input_data.available_skills)
    if missing:
        return missing[0]
    if input_data.required_skills:
        return input_data.required_skills[0]
    return None


def _invalid_artifact(input_data: WorkflowRunInput, policy: WorkflowRunPolicy, errors: tuple[str, ...]) -> WorkflowRunArtifact:
    return WorkflowRunArtifact(
        run_id=input_data.run_id or "invalid_workflow_run",
        schema_version=policy.schema_version,
        created_at_utc=policy.created_at_utc,
        status="invalid",
        ok=False,
        executes_plan=False,
        ready_for_execution=False,
        plan=None,
        summary={"status": "invalid", "error_count": len(errors)},
        inputs=input_data,
        metadata=dict(input_data.metadata or {}),
        provenance=dict(input_data.provenance or {}),
        warnings=input_data.warnings,
        errors=errors,
    )


def build_workflow_run(input_data: WorkflowRunInput, policy: WorkflowRunPolicy | None = None) -> WorkflowRunArtifact:
    active_policy = policy or WorkflowRunPolicy()
    errors = tuple((*active_policy.validate(), *input_data.validate()))
    if errors:
        return _invalid_artifact(input_data, active_policy, errors)

    request = build_workflow_request(
        input_data.user_request,
        required_skill_id=_required_skill_for_planner(input_data),
        request_id=input_data.run_id,
    )
    plan = build_workflow_plan(
        request,
        policy=WorkflowPlannerPolicy(),
        available_skills=input_data.available_skills,
        eval_gate=_eval_gate_value(input_data.eval_gate),
        source_status=_source_status_value(input_data.source_status),
        risk_flags=input_data.risk_flags,
    )
    decision = plan.planner_decision.decision
    status = {
        "allowed": "ready",
        "blocked": "blocked",
        "requires_human_approval": "requires_human_approval",
    }[decision]
    return WorkflowRunArtifact(
        run_id=input_data.run_id,
        schema_version=active_policy.schema_version,
        created_at_utc=active_policy.created_at_utc,
        status=status,
        ok=status == "ready",
        executes_plan=False,
        ready_for_execution=plan.ready_for_execution,
        plan=plan,
        summary=summarize_workflow_plan(plan),
        inputs=input_data,
        metadata=dict(input_data.metadata or {}),
        provenance=dict(input_data.provenance or {}),
        warnings=input_data.warnings,
        errors=(),
    )


def workflow_run_to_dict(run: WorkflowRunArtifact) -> dict[str, Any]:
    return run.to_dict()


def workflow_run_from_dict(data: dict[str, Any]) -> WorkflowRunArtifact:
    input_payload = data.get("inputs")
    input_data = None
    if input_payload is not None:
        request_payload = input_payload.get("request", {}) if isinstance(input_payload, dict) else {}
        input_data = WorkflowRunInput(
            run_id=input_payload.get("run_id", "local_workflow_run"),
            user_request=request_payload.get("user_request", ""),
            required_skills=tuple(request_payload.get("required_skills") or ()),
            available_skills=tuple(input_payload.get("available_skills") or ()),
            source_status=input_payload.get("source_status"),
            eval_gate=input_payload.get("eval_gate"),
            risk_flags=tuple(input_payload.get("risk_flags") or ()),
            metadata=dict(input_payload.get("metadata") or {}),
            provenance=dict(input_payload.get("provenance") or {}),
            warnings=tuple(input_payload.get("warnings") or ()),
            errors=tuple(input_payload.get("errors") or ()),
        )
    return WorkflowRunArtifact(
        run_id=data["run_id"],
        schema_version=data["schema_version"],
        created_at_utc=data["created_at_utc"],
        status=data["status"],
        ok=bool(data["ok"]),
        executes_plan=bool(data["executes_plan"]),
        ready_for_execution=bool(data["ready_for_execution"]),
        plan=workflow_plan_from_dict(data["plan"]) if data.get("plan") is not None else None,
        summary=dict(data.get("summary") or {}),
        inputs=input_data,
        metadata=dict(data.get("metadata") or {}),
        provenance=dict(data.get("provenance") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
    )


def write_workflow_run_artifact(
    run: WorkflowRunArtifact,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"workflow run artifact already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"workflow run artifact parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(workflow_run_to_dict(run), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path
