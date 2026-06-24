from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.workflow_run import WorkflowRunArtifact, workflow_run_from_dict, workflow_run_to_dict


WORKFLOW_INSPECTION_SEVERITIES = ("info", "warning", "error", "blocked")
WORKFLOW_INSPECTION_CATEGORIES = (
    "readiness",
    "approval",
    "source",
    "skill",
    "eval",
    "evidence",
    "audit",
    "safety",
    "schema",
)
DEFAULT_INSPECTION_VERSION = "MVP-018C"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
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


@dataclass(frozen=True)
class WorkflowInspectionFinding:
    finding_id: str
    severity: str
    category: str
    message: str
    step_kind: str | None = None
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.finding_id.strip():
            errors.append("finding_id is required")
        if self.severity not in WORKFLOW_INSPECTION_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")
        if self.category not in WORKFLOW_INSPECTION_CATEGORIES:
            errors.append(f"invalid category: {self.category}")
        if not self.message.strip():
            errors.append("message is required")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "step_kind": self.step_kind,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class WorkflowInspectionReport:
    report_id: str
    schema_version: str
    created_at_utc: str
    ok: bool
    run_id: str
    run_status: str
    ready_for_execution: bool
    executes_plan: bool
    findings: tuple[WorkflowInspectionFinding, ...]
    summary: dict[str, Any]
    run: WorkflowRunArtifact | None = None
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.report_id.strip():
            errors.append("report_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.executes_plan:
            errors.append("inspection report must preserve executes_plan=false")
        for finding in self.findings:
            errors.extend(f"{finding.finding_id}: {error}" for error in finding.validate())
        if self.ok and any(finding.severity in {"error", "blocked"} for finding in self.findings):
            errors.append("ok=true cannot include error or blocked findings")
        if self.ok and self.run_status != "ready":
            errors.append("ok=true requires run_status=ready")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "ok": self.ok,
            "run_id": self.run_id,
            "run_status": self.run_status,
            "ready_for_execution": self.ready_for_execution,
            "executes_plan": self.executes_plan,
            "findings": [finding.to_dict() for finding in self.findings],
            "summary": dict(self.summary),
            "run": workflow_run_to_dict(self.run) if self.run is not None else None,
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def _finding(
    finding_id: str,
    severity: str,
    category: str,
    message: str,
    step_kind: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> WorkflowInspectionFinding:
    return WorkflowInspectionFinding(
        finding_id=finding_id,
        severity=severity,
        category=category,
        message=message,
        step_kind=step_kind,
        metadata=metadata or {},
    )


def _blocked_report(run_id: str, message: str, warnings: tuple[str, ...] = ()) -> WorkflowInspectionReport:
    findings = (_finding("malformed_run_artifact", "blocked", "schema", message),)
    return WorkflowInspectionReport(
        report_id=f"{run_id}_inspection",
        schema_version=DEFAULT_INSPECTION_VERSION,
        created_at_utc=DEFAULT_CREATED_AT_UTC,
        ok=False,
        run_id=run_id,
        run_status="invalid",
        ready_for_execution=False,
        executes_plan=False,
        findings=findings,
        summary=_summary_from_findings(findings),
        warnings=warnings,
        errors=(message,),
    )


def _step_by_kind(run: WorkflowRunArtifact) -> dict[str, dict[str, Any]]:
    if run.plan is None:
        return {}
    return {step.step_kind: step.to_dict() for step in run.plan.steps}


def _summary_from_findings(findings: tuple[WorkflowInspectionFinding, ...]) -> dict[str, Any]:
    severity_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for finding in findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
    return {
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "category_counts": category_counts,
        "blocker_count": severity_counts.get("blocked", 0),
        "error_count": severity_counts.get("error", 0),
        "approval_count": category_counts.get("approval", 0),
    }


def inspect_workflow_run(run: WorkflowRunArtifact) -> WorkflowInspectionReport:
    findings: list[WorkflowInspectionFinding] = []
    validation_errors = run.validate()
    for index, error in enumerate(validation_errors, start=1):
        findings.append(_finding(f"run_validation_error_{index}", "blocked", "schema", error))
    if run.executes_plan:
        findings.append(_finding("executes_plan_true", "blocked", "safety", "workflow run artifact executes_plan=true"))
    if run.plan is None:
        findings.append(_finding("missing_plan", "blocked", "schema", "workflow run artifact is missing plan"))
    elif run.plan.executes_plan:
        findings.append(_finding("plan_executes_plan_true", "blocked", "safety", "workflow plan executes_plan=true"))

    steps = _step_by_kind(run)
    for required_step, category in (
        ("source_check", "source"),
        ("evidence_check", "evidence"),
        ("audit_ready", "audit"),
    ):
        if run.plan is not None and required_step not in steps:
            findings.append(
                _finding(
                    f"missing_{required_step}",
                    "error" if required_step != "audit_ready" else "warning",
                    category,
                    f"workflow plan is missing {required_step} step",
                    required_step,
                )
            )

    for step_kind, step in steps.items():
        status = step.get("status")
        if status == "blocked":
            category = {
                "source_check": "source",
                "skill_selection": "skill",
                "eval_gate_check": "eval",
                "evidence_check": "evidence",
                "audit_ready": "audit",
            }.get(step_kind, "readiness")
            findings.append(
                _finding(
                    f"{step_kind}_blocked",
                    "blocked",
                    category,
                    step.get("reason", f"{step_kind} blocked"),
                    step_kind,
                )
            )
        if status == "requires_human_approval":
            findings.append(
                _finding(
                    f"{step_kind}_requires_human_approval",
                    "warning",
                    "approval",
                    step.get("reason", f"{step_kind} requires human approval"),
                    step_kind,
                )
            )
    if steps.get("eval_gate_check", {}).get("status") == "blocked":
        findings.append(_finding("failed_eval_gate", "blocked", "eval", "eval gate step failed", "eval_gate_check"))

    if run.status == "ready" and run.ok and not findings:
        findings.append(_finding("workflow_ready", "info", "readiness", "workflow run is ready for human review"))
    elif run.status == "blocked":
        findings.append(_finding("run_blocked", "blocked", "readiness", "workflow run status is blocked"))
    elif run.status == "requires_human_approval":
        findings.append(_finding("run_requires_human_approval", "warning", "approval", "workflow run requires human approval"))
    elif run.status == "invalid":
        findings.append(_finding("run_invalid", "blocked", "schema", "workflow run status is invalid"))

    warnings = tuple(run.warnings)
    errors = tuple(run.errors)
    ok = run.status == "ready" and run.ok and not any(finding.severity in {"error", "blocked"} for finding in findings)
    findings_tuple = tuple(findings)
    return WorkflowInspectionReport(
        report_id=f"{run.run_id}_inspection",
        schema_version=DEFAULT_INSPECTION_VERSION,
        created_at_utc=DEFAULT_CREATED_AT_UTC,
        ok=ok,
        run_id=run.run_id,
        run_status=run.status,
        ready_for_execution=run.ready_for_execution,
        executes_plan=run.executes_plan,
        findings=findings_tuple,
        summary=_summary_from_findings(findings_tuple),
        run=run,
        metadata={"inspection_scope": "read_only_workflow_run_artifact"},
        warnings=warnings,
        errors=errors,
    )


def inspect_workflow_run_dict(data: dict[str, Any]) -> WorkflowInspectionReport:
    if not isinstance(data, dict):
        return _blocked_report("invalid_workflow_run", "workflow run artifact must be an object")
    warnings = tuple(f"unknown run artifact field: {key}" for key in sorted(set(data) - set(KNOWN_RUN_FIELDS)))
    try:
        run = workflow_run_from_dict(data)
    except Exception as exc:
        return _blocked_report(str(data.get("run_id", "invalid_workflow_run")), f"malformed run artifact: {exc}", warnings)
    report = inspect_workflow_run(run)
    if warnings:
        unknown_findings = tuple(
            _finding(f"unknown_field_{index}", "warning", "schema", warning)
            for index, warning in enumerate(warnings, start=1)
        )
        findings = (*report.findings, *unknown_findings)
        return WorkflowInspectionReport(
            report_id=report.report_id,
            schema_version=report.schema_version,
            created_at_utc=report.created_at_utc,
            ok=report.ok,
            run_id=report.run_id,
            run_status=report.run_status,
            ready_for_execution=report.ready_for_execution,
            executes_plan=report.executes_plan,
            findings=findings,
            summary=_summary_from_findings(findings),
            run=report.run,
            metadata=report.metadata,
            warnings=(*report.warnings, *warnings),
            errors=report.errors,
        )
    return report


def workflow_inspection_to_dict(report: WorkflowInspectionReport) -> dict[str, Any]:
    return report.to_dict()


def workflow_inspection_from_dict(data: dict[str, Any]) -> WorkflowInspectionReport:
    return WorkflowInspectionReport(
        report_id=data["report_id"],
        schema_version=data["schema_version"],
        created_at_utc=data["created_at_utc"],
        ok=bool(data["ok"]),
        run_id=data["run_id"],
        run_status=data["run_status"],
        ready_for_execution=bool(data["ready_for_execution"]),
        executes_plan=bool(data["executes_plan"]),
        findings=tuple(
            WorkflowInspectionFinding(
                finding_id=finding["finding_id"],
                severity=finding["severity"],
                category=finding["category"],
                message=finding["message"],
                step_kind=finding.get("step_kind"),
                metadata=dict(finding.get("metadata") or {}),
            )
            for finding in data.get("findings", ())
        ),
        summary=dict(data.get("summary") or {}),
        run=workflow_run_from_dict(data["run"]) if data.get("run") is not None else None,
        metadata=dict(data.get("metadata") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
    )


def write_workflow_inspection_report(
    report: WorkflowInspectionReport,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"workflow inspection report already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"workflow inspection report parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(workflow_inspection_to_dict(report), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def summarize_workflow_inspection(report: WorkflowInspectionReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "ok": report.ok,
        "run_id": report.run_id,
        "run_status": report.run_status,
        "ready_for_execution": report.ready_for_execution,
        "executes_plan": report.executes_plan,
        "summary": dict(report.summary),
    }
