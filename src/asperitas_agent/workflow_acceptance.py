from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.workflow_inspector import WorkflowInspectionReport, workflow_inspection_from_dict
from asperitas_agent.workflow_run import WorkflowRunArtifact, workflow_run_from_dict


WORKFLOW_ACCEPTANCE_STATUSES = ("accepted", "rejected", "requires_human_approval", "invalid")
WORKFLOW_ACCEPTANCE_REASON_SEVERITIES = ("info", "warning", "error", "blocked")
DEFAULT_ACCEPTANCE_VERSION = "MVP-018D"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
DEFAULT_REQUIRED_STEPS = (
    "source_check",
    "skill_selection",
    "risk_preflight",
    "eval_gate_check",
    "evidence_check",
    "answer_plan",
    "audit_ready",
)
KNOWN_RUN_FIELDS = (
    "run_id",
    "schema_version",
    "created_at_utc",
    "status",
    "ok",
    "executes_plan",
    "ready_for_execution",
    "plan",
    "summary",
    "inputs",
    "metadata",
    "provenance",
    "warnings",
    "errors",
)
KNOWN_INSPECTION_FIELDS = (
    "report_id",
    "schema_version",
    "created_at_utc",
    "ok",
    "run_id",
    "run_status",
    "ready_for_execution",
    "executes_plan",
    "findings",
    "summary",
    "run",
    "metadata",
    "warnings",
    "errors",
)


@dataclass(frozen=True)
class WorkflowAcceptancePolicy:
    required_step_kinds: tuple[str, ...] = DEFAULT_REQUIRED_STEPS
    fail_closed: bool = True
    reject_error_findings: bool = True
    reject_blocked_findings: bool = True
    policy_id: str = "asperitas_workflow_acceptance_policy"
    schema_version: str = DEFAULT_ACCEPTANCE_VERSION
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
            errors.append("workflow acceptance policy must fail closed")
        if not isinstance(self.required_step_kinds, tuple) or not self.required_step_kinds:
            errors.append("required_step_kinds must be a non-empty tuple")
        elif any(not str(step).strip() for step in self.required_step_kinds):
            errors.append("required_step_kinds must contain non-empty strings")
        elif len(self.required_step_kinds) != len(set(self.required_step_kinds)):
            errors.append("required_step_kinds must be unique")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class WorkflowAcceptanceReason:
    reason_id: str
    severity: str
    message: str
    category: str = "acceptance"
    step_kind: str | None = None
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.reason_id.strip():
            errors.append("reason_id is required")
        if self.severity not in WORKFLOW_ACCEPTANCE_REASON_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")
        if not self.category.strip():
            errors.append("category is required")
        if not self.message.strip():
            errors.append("message is required")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason_id": self.reason_id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "step_kind": self.step_kind,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class WorkflowAcceptanceDecision:
    decision_id: str
    schema_version: str
    created_at_utc: str
    status: str
    ok: bool
    run_id: str
    inspection_report_id: str
    ready_for_execution: bool
    executes_plan: bool
    policy: WorkflowAcceptancePolicy
    reasons: tuple[WorkflowAcceptanceReason, ...]
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.decision_id.strip():
            errors.append("decision_id is required")
        if self.status not in WORKFLOW_ACCEPTANCE_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.ok and self.status != "accepted":
            errors.append("ok=true requires status=accepted")
        if self.status == "accepted" and not self.ok:
            errors.append("status=accepted requires ok=true")
        if self.executes_plan:
            errors.append("workflow acceptance decision must preserve executes_plan=false")
        errors.extend(f"policy: {error}" for error in self.policy.validate())
        for reason in self.reasons:
            errors.extend(f"{reason.reason_id}: {error}" for error in reason.validate())
        if self.ok and any(reason.severity in {"error", "blocked"} for reason in self.reasons):
            errors.append("ok=true cannot include error or blocked reasons")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "status": self.status,
            "ok": self.ok,
            "run_id": self.run_id,
            "inspection_report_id": self.inspection_report_id,
            "ready_for_execution": self.ready_for_execution,
            "executes_plan": self.executes_plan,
            "policy": self.policy.to_dict(),
            "reasons": [reason.to_dict() for reason in self.reasons],
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata or {}),
        }


def _reason(
    reason_id: str,
    severity: str,
    message: str,
    category: str = "acceptance",
    step_kind: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> WorkflowAcceptanceReason:
    return WorkflowAcceptanceReason(
        reason_id=reason_id,
        severity=severity,
        message=message,
        category=category,
        step_kind=step_kind,
        metadata=metadata or {},
    )


def _step_by_kind(run: WorkflowRunArtifact) -> dict[str, dict[str, Any]]:
    if run.plan is None:
        return {}
    return {step.step_kind: step.to_dict() for step in run.plan.steps}


def _status_from_reasons(
    run: WorkflowRunArtifact | None,
    inspection_report: WorkflowInspectionReport | None,
    reasons: tuple[WorkflowAcceptanceReason, ...],
) -> str:
    if any(
        reason.reason_id.startswith(("malformed_", "policy_validation_error"))
        and reason.severity in {"error", "blocked"}
        for reason in reasons
    ):
        return "invalid"
    if any(reason.severity in {"error", "blocked"} for reason in reasons):
        return "rejected"
    if run is not None and run.status == "requires_human_approval":
        return "requires_human_approval"
    if inspection_report is not None and inspection_report.run_status == "requires_human_approval":
        return "requires_human_approval"
    return "accepted"


def _unique_reasons(reasons: tuple[WorkflowAcceptanceReason, ...]) -> tuple[WorkflowAcceptanceReason, ...]:
    seen: set[tuple[str, str, str, str, str | None]] = set()
    unique: list[WorkflowAcceptanceReason] = []
    for reason in reasons:
        key = (reason.reason_id, reason.severity, reason.category, reason.message, reason.step_kind)
        if key not in seen:
            seen.add(key)
            unique.append(reason)
    return tuple(unique)


def _decision(
    run_id: str,
    inspection_report_id: str,
    ready_for_execution: bool,
    executes_plan: bool,
    policy: WorkflowAcceptancePolicy,
    reasons: tuple[WorkflowAcceptanceReason, ...],
    warnings: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
    run: WorkflowRunArtifact | None = None,
    inspection_report: WorkflowInspectionReport | None = None,
) -> WorkflowAcceptanceDecision:
    status = _status_from_reasons(run, inspection_report, reasons)
    if status == "accepted" and not reasons:
        reasons = (_reason("workflow_acceptance_passed", "info", "workflow artifacts accepted"),)
    return WorkflowAcceptanceDecision(
        decision_id=f"{run_id}_workflow_acceptance",
        schema_version=policy.schema_version,
        created_at_utc=policy.created_at_utc,
        status=status,
        ok=status == "accepted",
        run_id=run_id,
        inspection_report_id=inspection_report_id,
        ready_for_execution=ready_for_execution,
        executes_plan=executes_plan,
        policy=policy,
        reasons=_unique_reasons(reasons),
        warnings=warnings,
        metadata=metadata or {},
    )


def accept_workflow_artifacts(
    run_artifact: WorkflowRunArtifact,
    inspection_report: WorkflowInspectionReport,
    policy: WorkflowAcceptancePolicy | None = None,
) -> WorkflowAcceptanceDecision:
    active_policy = policy or WorkflowAcceptancePolicy()
    reasons: list[WorkflowAcceptanceReason] = []
    warnings: list[str] = []

    for index, error in enumerate(active_policy.validate(), start=1):
        reasons.append(_reason(f"policy_validation_error_{index}", "blocked", error, "schema"))

    if run_artifact.run_id != inspection_report.run_id:
        reasons.append(
            _reason(
                "run_id_mismatch",
                "error",
                "run artifact and inspection report run_id values differ",
                "schema",
                metadata={"run_id": run_artifact.run_id, "inspection_run_id": inspection_report.run_id},
            )
        )
    if run_artifact.executes_plan or inspection_report.executes_plan:
        reasons.append(_reason("executes_plan_true", "blocked", "workflow artifacts must preserve executes_plan=false", "safety"))
    if run_artifact.plan is not None and run_artifact.plan.executes_plan:
        reasons.append(_reason("plan_executes_plan_true", "blocked", "workflow plan must preserve executes_plan=false", "safety"))

    if run_artifact.status == "blocked":
        reasons.append(_reason("run_status_blocked", "blocked", "workflow run status is blocked", "readiness"))
    elif run_artifact.status == "requires_human_approval":
        reasons.append(_reason("run_requires_human_approval", "warning", "workflow run requires human approval", "approval"))
    elif run_artifact.status == "invalid":
        reasons.append(_reason("run_status_invalid", "blocked", "workflow run status is invalid", "schema"))
    elif run_artifact.status != "ready":
        reasons.append(_reason("run_status_unaccepted", "error", f"workflow run status is {run_artifact.status}", "readiness"))

    if not run_artifact.ok and run_artifact.status != "requires_human_approval":
        reasons.append(_reason("run_not_ok", "error", "workflow run ok=false", "readiness"))
    if not inspection_report.ok and run_artifact.status != "requires_human_approval":
        reasons.append(_reason("inspection_not_ok", "error", "workflow inspection ok=false", "readiness"))

    blocked_or_error_findings = tuple(
        finding
        for finding in inspection_report.findings
        if finding.severity in {"blocked", "error"}
    )
    for finding in blocked_or_error_findings:
        reasons.append(
            _reason(
                f"inspection_finding_{finding.finding_id}",
                finding.severity,
                finding.message,
                finding.category,
                finding.step_kind,
            )
        )

    steps = _step_by_kind(run_artifact)
    for step_kind in active_policy.required_step_kinds:
        if step_kind not in steps:
            reasons.append(_reason(f"missing_{step_kind}", "error", f"missing required workflow step: {step_kind}", "readiness", step_kind))
    for step_kind in ("audit_ready", "source_check", "evidence_check"):
        if step_kind not in steps:
            reasons.append(_reason(f"missing_required_gate_{step_kind}", "error", f"missing required gate: {step_kind}", "readiness", step_kind))

    for step_kind in ("eval_gate_check", "evidence_check", "source_check"):
        step = steps.get(step_kind)
        if step and step.get("status") == "blocked":
            reasons.append(_reason(f"failed_{step_kind}", "blocked", step.get("reason", f"{step_kind} failed"), "readiness", step_kind))

    if not run_artifact.ready_for_execution and run_artifact.status != "requires_human_approval":
        reasons.append(_reason("run_not_ready_for_execution", "error", "workflow run ready_for_execution=false", "readiness"))
    if not inspection_report.ready_for_execution and run_artifact.status != "requires_human_approval":
        reasons.append(_reason("inspection_not_ready_for_execution", "error", "inspection ready_for_execution=false", "readiness"))

    warnings.extend(run_artifact.warnings)
    warnings.extend(inspection_report.warnings)
    return _decision(
        run_artifact.run_id or "invalid_workflow_run",
        inspection_report.report_id or "invalid_workflow_inspection",
        run_artifact.ready_for_execution and inspection_report.ready_for_execution,
        run_artifact.executes_plan or inspection_report.executes_plan,
        active_policy,
        tuple(reasons),
        tuple(dict.fromkeys(warnings)),
        metadata={"acceptance_scope": "explicit_workflow_run_and_inspection_artifacts"},
        run=run_artifact,
        inspection_report=inspection_report,
    )


def accept_workflow_artifact_dicts(
    run_data: dict[str, Any],
    inspection_data: dict[str, Any],
    policy: WorkflowAcceptancePolicy | None = None,
) -> WorkflowAcceptanceDecision:
    active_policy = policy or WorkflowAcceptancePolicy()
    warnings: list[str] = []
    if not isinstance(run_data, dict):
        return _decision(
            "invalid_workflow_run",
            "invalid_workflow_inspection",
            False,
            False,
            active_policy,
            (_reason("malformed_run_artifact", "blocked", "run artifact must be an object", "schema"),),
        )
    if not isinstance(inspection_data, dict):
        return _decision(
            str(run_data.get("run_id", "invalid_workflow_run")),
            "invalid_workflow_inspection",
            False,
            False,
            active_policy,
            (_reason("malformed_inspection_report", "blocked", "inspection report must be an object", "schema"),),
        )
    warnings.extend(f"unknown run artifact field: {key}" for key in sorted(set(run_data) - set(KNOWN_RUN_FIELDS)))
    warnings.extend(
        f"unknown inspection report field: {key}" for key in sorted(set(inspection_data) - set(KNOWN_INSPECTION_FIELDS))
    )
    try:
        run_artifact = workflow_run_from_dict(run_data)
    except Exception as exc:
        return _decision(
            str(run_data.get("run_id", "invalid_workflow_run")),
            str(inspection_data.get("report_id", "invalid_workflow_inspection")),
            False,
            bool(run_data.get("executes_plan", False)),
            active_policy,
            (_reason("malformed_run_artifact", "blocked", f"malformed run artifact: {exc}", "schema"),),
            tuple(warnings),
        )
    try:
        inspection_report = workflow_inspection_from_dict(inspection_data)
    except Exception as exc:
        return _decision(
            run_artifact.run_id,
            str(inspection_data.get("report_id", "invalid_workflow_inspection")),
            False,
            run_artifact.executes_plan or bool(inspection_data.get("executes_plan", False)),
            active_policy,
            (_reason("malformed_inspection_report", "blocked", f"malformed inspection report: {exc}", "schema"),),
            tuple(warnings),
        )
    decision = accept_workflow_artifacts(run_artifact, inspection_report, active_policy)
    if warnings:
        return WorkflowAcceptanceDecision(
            decision_id=decision.decision_id,
            schema_version=decision.schema_version,
            created_at_utc=decision.created_at_utc,
            status=decision.status,
            ok=decision.ok,
            run_id=decision.run_id,
            inspection_report_id=decision.inspection_report_id,
            ready_for_execution=decision.ready_for_execution,
            executes_plan=decision.executes_plan,
            policy=decision.policy,
            reasons=(
                *decision.reasons,
                *(
                    _reason(f"unknown_field_{index}", "warning", warning, "schema")
                    for index, warning in enumerate(warnings, start=1)
                ),
            ),
            warnings=tuple(dict.fromkeys((*decision.warnings, *warnings))),
            metadata=decision.metadata,
        )
    return decision


def workflow_acceptance_to_dict(decision: WorkflowAcceptanceDecision) -> dict[str, Any]:
    return decision.to_dict()


def workflow_acceptance_from_dict(data: dict[str, Any]) -> WorkflowAcceptanceDecision:
    policy_data = data["policy"]
    return WorkflowAcceptanceDecision(
        decision_id=data["decision_id"],
        schema_version=data["schema_version"],
        created_at_utc=data["created_at_utc"],
        status=data["status"],
        ok=bool(data["ok"]),
        run_id=data["run_id"],
        inspection_report_id=data["inspection_report_id"],
        ready_for_execution=bool(data["ready_for_execution"]),
        executes_plan=bool(data["executes_plan"]),
        policy=WorkflowAcceptancePolicy(
            required_step_kinds=tuple(policy_data.get("required_step_kinds") or DEFAULT_REQUIRED_STEPS),
            fail_closed=bool(policy_data.get("fail_closed", True)),
            reject_error_findings=bool(policy_data.get("reject_error_findings", True)),
            reject_blocked_findings=bool(policy_data.get("reject_blocked_findings", True)),
            policy_id=policy_data.get("policy_id", "asperitas_workflow_acceptance_policy"),
            schema_version=policy_data.get("schema_version", DEFAULT_ACCEPTANCE_VERSION),
            created_at_utc=policy_data.get("created_at_utc", DEFAULT_CREATED_AT_UTC),
        ),
        reasons=tuple(
            WorkflowAcceptanceReason(
                reason_id=reason["reason_id"],
                severity=reason["severity"],
                message=reason["message"],
                category=reason.get("category", "acceptance"),
                step_kind=reason.get("step_kind"),
                metadata=dict(reason.get("metadata") or {}),
            )
            for reason in data.get("reasons", ())
        ),
        warnings=tuple(data.get("warnings") or ()),
        metadata=dict(data.get("metadata") or {}),
    )


def write_workflow_acceptance_decision(
    decision: WorkflowAcceptanceDecision,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"workflow acceptance decision already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"workflow acceptance decision parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(workflow_acceptance_to_dict(decision), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def summarize_workflow_acceptance(decision: WorkflowAcceptanceDecision) -> dict[str, Any]:
    severity_counts: dict[str, int] = {}
    for reason in decision.reasons:
        severity_counts[reason.severity] = severity_counts.get(reason.severity, 0) + 1
    return {
        "decision_id": decision.decision_id,
        "status": decision.status,
        "ok": decision.ok,
        "run_id": decision.run_id,
        "inspection_report_id": decision.inspection_report_id,
        "ready_for_execution": decision.ready_for_execution,
        "executes_plan": decision.executes_plan,
        "reason_count": len(decision.reasons),
        "severity_counts": severity_counts,
        "warning_count": len(decision.warnings),
    }
