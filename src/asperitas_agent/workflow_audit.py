from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.audit_trace import (
    AuditTraceEvent,
    AuditTracePolicy,
    AuditTraceRecord,
    build_audit_event,
    build_audit_record,
    write_audit_jsonl,
)
from asperitas_agent.workflow_acceptance import WorkflowAcceptanceDecision, workflow_acceptance_from_dict
from asperitas_agent.workflow_inspector import WorkflowInspectionReport, workflow_inspection_from_dict
from asperitas_agent.workflow_run import WorkflowRunArtifact, workflow_run_from_dict


WORKFLOW_AUDIT_STATUSES = ("recorded", "rejected", "requires_human_approval", "invalid")
DEFAULT_WORKFLOW_AUDIT_VERSION = "MVP-019B"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
KNOWN_AUDIT_INPUT_FIELDS = ("trace_id", "run", "inspection", "acceptance", "metadata")


@dataclass(frozen=True)
class WorkflowAuditPolicy:
    audit_policy: AuditTracePolicy = AuditTracePolicy()
    fail_closed: bool = True
    policy_id: str = "asperitas_workflow_audit_policy"
    schema_version: str = DEFAULT_WORKFLOW_AUDIT_VERSION
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
            errors.append("workflow audit policy must fail closed")
        errors.extend(f"audit_policy: {error}" for error in self.audit_policy.validate())
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["audit_policy"] = self.audit_policy.to_dict()
        return data


@dataclass(frozen=True)
class WorkflowAuditInput:
    trace_id: str
    run: dict[str, Any]
    inspection: dict[str, Any]
    acceptance: dict[str, Any]
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        for field_name in ("run", "inspection", "acceptance"):
            if not isinstance(getattr(self, field_name), dict):
                errors.append(f"{field_name} must be an object")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "run": dict(self.run),
            "inspection": dict(self.inspection),
            "acceptance": dict(self.acceptance),
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class WorkflowAuditResult:
    trace_id: str
    status: str
    ok: bool
    record: AuditTraceRecord | None
    events: tuple[AuditTraceEvent, ...]
    run_id: str | None = None
    decision_id: str | None = None
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    schema_version: str = DEFAULT_WORKFLOW_AUDIT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        if self.status not in WORKFLOW_AUDIT_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.ok and self.status != "recorded":
            errors.append("ok=true requires status=recorded")
        for event in self.events:
            errors.extend(f"{event.event_id}: {error}" for error in event.validate())
            if event.trace_id != self.trace_id:
                errors.append(f"{event.event_id}: event trace_id does not match result trace_id")
        if self.record is not None:
            errors.extend(f"record: {error}" for error in self.record.validate())
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "schema_version": self.schema_version,
            "status": self.status,
            "ok": self.ok,
            "run_id": self.run_id,
            "decision_id": self.decision_id,
            "events": [event.to_dict() for event in self.events],
            "record": self.record.to_dict() if self.record is not None else None,
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def build_workflow_audit_input(
    trace_id: str,
    run: dict[str, Any],
    inspection: dict[str, Any],
    acceptance: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> WorkflowAuditInput:
    return WorkflowAuditInput(trace_id=trace_id, run=run, inspection=inspection, acceptance=acceptance, metadata=metadata or {})


def _status_from_acceptance(acceptance_decision: WorkflowAcceptanceDecision) -> tuple[str, str, str]:
    if acceptance_decision.status == "accepted":
        return "recorded", "workflow_accepted", "info"
    if acceptance_decision.status == "requires_human_approval":
        return "requires_human_approval", "human_approval_required", "warning"
    return "rejected", "workflow_rejected", "blocked"


def _step_status(run_artifact: WorkflowRunArtifact, step_kind: str) -> str | None:
    if run_artifact.plan is None:
        return None
    for step in run_artifact.plan.steps:
        if step.step_kind == step_kind:
            return step.status
    return None


def build_workflow_audit_events(
    run_artifact: WorkflowRunArtifact,
    inspection_report: WorkflowInspectionReport,
    acceptance_decision: WorkflowAcceptanceDecision,
    policy: WorkflowAuditPolicy | None = None,
) -> list[AuditTraceEvent]:
    active_policy = policy or WorkflowAuditPolicy()
    status, event_type, severity = _status_from_acceptance(acceptance_decision)
    trace_id = str((acceptance_decision.metadata or {}).get("trace_id") or run_artifact.run_id or "local_workflow_trace")
    artifact_refs = (
        f"run:{run_artifact.run_id}",
        f"inspection:{inspection_report.report_id}",
        f"acceptance:{acceptance_decision.decision_id}",
    )
    events = [
        build_audit_event(
            trace_id=trace_id,
            event_type=event_type,
            event_id=f"{trace_id}_{event_type}",
            severity=severity,
            actor="system",
            run_id=run_artifact.run_id,
            request_id=run_artifact.inputs.run_id if run_artifact.inputs is not None else None,
            decision_id=acceptance_decision.decision_id,
            artifact_refs=artifact_refs,
            payload={
                "audit_status": status,
                "run_status": run_artifact.status,
                "inspection_ok": inspection_report.ok,
                "acceptance_status": acceptance_decision.status,
                "secret_note": (acceptance_decision.metadata or {}).get("secret_note"),
            },
            created_at_utc=active_policy.created_at_utc,
            policy=active_policy.audit_policy,
        )
    ]
    eval_status = _step_status(run_artifact, "eval_gate_check")
    if eval_status is not None:
        events.append(
            build_audit_event(
                trace_id=trace_id,
                event_type="eval_gate_checked",
                event_id=f"{trace_id}_eval_gate_checked",
                severity="info" if eval_status == "allowed" else "blocked",
                actor="system",
                run_id=run_artifact.run_id,
                decision_id=acceptance_decision.decision_id,
                artifact_refs=artifact_refs,
                payload={"step_kind": "eval_gate_check", "status": eval_status},
                created_at_utc=active_policy.created_at_utc,
                policy=active_policy.audit_policy,
            )
        )
    source_status = _step_status(run_artifact, "source_check")
    if source_status is not None:
        events.append(
            build_audit_event(
                trace_id=trace_id,
                event_type="source_gate_checked",
                event_id=f"{trace_id}_source_gate_checked",
                severity="info" if source_status == "allowed" else "blocked",
                actor="system",
                run_id=run_artifact.run_id,
                decision_id=acceptance_decision.decision_id,
                artifact_refs=artifact_refs,
                payload={"step_kind": "source_check", "status": source_status},
                created_at_utc=active_policy.created_at_utc,
                policy=active_policy.audit_policy,
            )
        )
    if run_artifact.executes_plan or inspection_report.executes_plan or acceptance_decision.executes_plan:
        events.append(
            build_audit_event(
                trace_id=trace_id,
                event_type="security_guard_triggered",
                event_id=f"{trace_id}_security_guard_triggered",
                severity="blocked",
                actor="system",
                run_id=run_artifact.run_id,
                decision_id=acceptance_decision.decision_id,
                artifact_refs=artifact_refs,
                payload={"reason": "executes_plan=true"},
                created_at_utc=active_policy.created_at_utc,
                policy=active_policy.audit_policy,
            )
        )
    return events


def build_workflow_audit_record(
    run_artifact: WorkflowRunArtifact,
    inspection_report: WorkflowInspectionReport,
    acceptance_decision: WorkflowAcceptanceDecision,
    metadata: dict[str, Any] | None = None,
    policy: WorkflowAuditPolicy | None = None,
) -> AuditTraceRecord:
    active_policy = policy or WorkflowAuditPolicy()
    events = build_workflow_audit_events(run_artifact, inspection_report, acceptance_decision, active_policy)
    trace_id = events[0].trace_id if events else str((metadata or {}).get("trace_id", "local_workflow_trace"))
    return build_audit_record(tuple(events), metadata={**(metadata or {}), "trace_id": trace_id}, policy=active_policy.audit_policy)


def _invalid_result(trace_id: str, message: str, policy: WorkflowAuditPolicy | None = None) -> WorkflowAuditResult:
    active_policy = policy or WorkflowAuditPolicy()
    event = build_audit_event(
        trace_id=trace_id or "invalid_workflow_trace",
        event_type="security_guard_triggered",
        event_id=f"{trace_id or 'invalid_workflow_trace'}_malformed_artifact",
        severity="error",
        actor="system",
        payload={"error": message},
        created_at_utc=active_policy.created_at_utc,
        policy=active_policy.audit_policy,
    )
    return WorkflowAuditResult(
        trace_id=event.trace_id,
        status="invalid",
        ok=False,
        record=build_audit_record((event,), metadata={"trace_id": event.trace_id}, policy=active_policy.audit_policy),
        events=(event,),
        errors=(message,),
    )


def audit_workflow_artifact_dicts(
    run_data: dict[str, Any],
    inspection_data: dict[str, Any],
    acceptance_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    policy: WorkflowAuditPolicy | None = None,
) -> WorkflowAuditResult:
    active_policy = policy or WorkflowAuditPolicy()
    trace_id = str((metadata or {}).get("trace_id") or run_data.get("run_id", "local_workflow_trace"))
    try:
        run_artifact = workflow_run_from_dict(run_data)
    except Exception as exc:
        return _invalid_result(trace_id, f"malformed run artifact: {exc}", active_policy)
    try:
        inspection_report = workflow_inspection_from_dict(inspection_data)
    except Exception as exc:
        return _invalid_result(trace_id, f"malformed inspection report: {exc}", active_policy)
    try:
        acceptance_decision = workflow_acceptance_from_dict(acceptance_data)
    except Exception as exc:
        return _invalid_result(trace_id, f"malformed acceptance decision: {exc}", active_policy)

    warnings: list[str] = []
    if run_artifact.run_id != inspection_report.run_id or run_artifact.run_id != acceptance_decision.run_id:
        acceptance_status = "rejected"
        warnings.append("run_id mismatch across workflow artifacts")
    else:
        acceptance_status = acceptance_decision.status
    decision_metadata = dict(acceptance_decision.metadata or {})
    decision_metadata.setdefault("trace_id", trace_id)
    acceptance_decision = WorkflowAcceptanceDecision(
        decision_id=acceptance_decision.decision_id,
        schema_version=acceptance_decision.schema_version,
        created_at_utc=acceptance_decision.created_at_utc,
        status=acceptance_status,
        ok=acceptance_status == "accepted",
        run_id=acceptance_decision.run_id,
        inspection_report_id=acceptance_decision.inspection_report_id,
        ready_for_execution=acceptance_decision.ready_for_execution,
        executes_plan=acceptance_decision.executes_plan,
        policy=acceptance_decision.policy,
        reasons=acceptance_decision.reasons,
        warnings=acceptance_decision.warnings,
        metadata=decision_metadata,
    )
    record = build_workflow_audit_record(run_artifact, inspection_report, acceptance_decision, metadata=metadata, policy=active_policy)
    status, _, _ = _status_from_acceptance(acceptance_decision)
    if run_artifact.executes_plan or inspection_report.executes_plan or acceptance_decision.executes_plan:
        status = "rejected"
        warnings.append("executes_plan=true security guard triggered")
    return WorkflowAuditResult(
        trace_id=record.trace_id,
        status=status,
        ok=status == "recorded",
        record=record,
        events=record.events,
        run_id=run_artifact.run_id,
        decision_id=acceptance_decision.decision_id,
        metadata=metadata or {},
        warnings=tuple(dict.fromkeys((*warnings, *record.warnings))),
        errors=record.errors,
    )


def workflow_audit_result_to_dict(result: WorkflowAuditResult) -> dict[str, Any]:
    return result.to_dict()


def workflow_audit_result_from_dict(data: dict[str, Any]) -> WorkflowAuditResult:
    from asperitas_agent.audit_trace import audit_event_from_dict, audit_record_from_dict

    return WorkflowAuditResult(
        trace_id=data["trace_id"],
        status=data["status"],
        ok=bool(data["ok"]),
        record=audit_record_from_dict(data["record"]) if data.get("record") is not None else None,
        events=tuple(audit_event_from_dict(event) for event in data.get("events", ())),
        run_id=data.get("run_id"),
        decision_id=data.get("decision_id"),
        metadata=dict(data.get("metadata") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
        schema_version=data.get("schema_version", DEFAULT_WORKFLOW_AUDIT_VERSION),
    )


def write_workflow_audit_jsonl(
    result: WorkflowAuditResult,
    path: str | Path,
    append: bool = False,
    create_dirs: bool = False,
) -> Path:
    return write_audit_jsonl(result.events, path, append=append, create_dirs=create_dirs)


def summarize_workflow_audit(result: WorkflowAuditResult) -> dict[str, Any]:
    event_type_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    for event in result.events:
        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
        severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
    return {
        "trace_id": result.trace_id,
        "status": result.status,
        "ok": result.ok,
        "run_id": result.run_id,
        "decision_id": result.decision_id,
        "event_count": len(result.events),
        "event_type_counts": event_type_counts,
        "severity_counts": severity_counts,
        "warning_count": len(result.warnings),
        "error_count": len(result.errors),
    }
