from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from asperitas_agent.audit_trace import AuditTraceEvent, AuditTracePolicy, audit_event_from_dict, build_audit_event, write_audit_jsonl
from asperitas_agent.security_guard import (
    SecurityGuardReport,
    build_security_audit_events,
    inspect_security_dict,
    security_guard_report_from_dict,
    security_guard_report_to_dict,
)
from asperitas_agent.workflow_acceptance import (
    WorkflowAcceptanceDecision,
    accept_workflow_artifacts,
    workflow_acceptance_from_dict,
    workflow_acceptance_to_dict,
)
from asperitas_agent.workflow_audit import build_workflow_audit_events
from asperitas_agent.workflow_inspector import (
    WorkflowInspectionReport,
    inspect_workflow_run,
    workflow_inspection_from_dict,
    workflow_inspection_to_dict,
)
from asperitas_agent.workflow_run import WorkflowRunArtifact, WorkflowRunInput, build_workflow_run, workflow_run_from_dict, workflow_run_to_dict


ChatWorkflowStatus = str

CHAT_WORKFLOW_STATUSES = ("answered", "blocked", "requires_human_approval", "dry_run_ready", "invalid")
DEFAULT_CHAT_WORKFLOW_VERSION = "MVP-019D"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
KNOWN_CHAT_INPUT_FIELDS = (
    "request_id",
    "trace_id",
    "question",
    "required_skills",
    "available_skills",
    "source_status",
    "eval_gate",
    "source_texts",
    "metadata",
)


@dataclass(frozen=True)
class ChatQuestionInput:
    request_id: str
    trace_id: str
    question: str
    required_skills: tuple[str, ...] = ()
    available_skills: tuple[str, ...] = ()
    source_status: dict[str, Any] | None = None
    eval_gate: dict[str, Any] | None = None
    source_texts: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.request_id.strip():
            errors.append("request_id is required")
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        if not self.question.strip():
            errors.append("question is required")
        for field_name in ("required_skills", "available_skills"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                errors.append(f"{field_name} must be a tuple")
        if self.source_status is not None and not isinstance(self.source_status, dict):
            errors.append("source_status must be an object")
        if self.eval_gate is not None and not isinstance(self.eval_gate, dict):
            errors.append("eval_gate must be an object")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "question": self.question,
            "required_skills": list(self.required_skills),
            "available_skills": list(self.available_skills),
            "source_status": dict(self.source_status or {}),
            "eval_gate": dict(self.eval_gate or {}),
            "source_texts": [dict(source) for source in self.source_texts],
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class ChatAnswerEvidence:
    source_id: str
    citation: str
    evidence_label: str
    confidence: str
    text: str = ""
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.source_id.strip():
            errors.append("source_id is required")
        if not self.citation.strip():
            errors.append("citation is required")
        if not self.evidence_label.strip():
            errors.append("evidence_label is required")
        if self.confidence not in {"low", "medium", "high"}:
            errors.append(f"invalid confidence: {self.confidence}")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "citation": self.citation,
            "evidence_label": self.evidence_label,
            "confidence": self.confidence,
            "text": self.text,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class ChatAnswerArtifact:
    answer: str
    citations: tuple[str, ...]
    evidence: tuple[ChatAnswerEvidence, ...]
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.answer.strip():
            errors.append("answer is required")
        if not isinstance(self.citations, tuple) or not self.citations:
            errors.append("citations are required")
        if not isinstance(self.evidence, tuple) or not self.evidence:
            errors.append("answer evidence is required")
        for item in self.evidence:
            errors.extend(f"{item.source_id}: {error}" for error in item.validate())
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": list(self.citations),
            "evidence": [item.to_dict() for item in self.evidence],
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class ChatWorkflowPolicy:
    require_security_ok: bool = True
    require_workflow_acceptance: bool = True
    require_source_status: bool = True
    require_citations: bool = True
    require_answer_evidence: bool = True
    dry_run_default: bool = True
    allow_answer_provider: bool = False
    audit_policy: AuditTracePolicy = AuditTracePolicy()
    policy_id: str = "asperitas_chat_workflow_policy"
    schema_version: str = DEFAULT_CHAT_WORKFLOW_VERSION
    created_at_utc: str = DEFAULT_CREATED_AT_UTC

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        errors.extend(f"audit_policy: {error}" for error in self.audit_policy.validate())
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["audit_policy"] = self.audit_policy.to_dict()
        return data


class ChatAnswerProvider(Protocol):
    def answer(self, input_data: ChatQuestionInput) -> ChatAnswerArtifact | dict[str, Any]:
        ...


@dataclass(frozen=True)
class ChatWorkflowResult:
    request_id: str
    trace_id: str
    schema_version: str
    created_at_utc: str
    status: ChatWorkflowStatus
    ok: bool
    blocked: bool
    requires_human_approval: bool
    dry_run: bool
    question: str
    answer: str | None
    citations: tuple[str, ...]
    evidence: tuple[ChatAnswerEvidence, ...]
    security_report: SecurityGuardReport | None
    workflow_run: WorkflowRunArtifact | None
    workflow_inspection: WorkflowInspectionReport | None
    workflow_acceptance: WorkflowAcceptanceDecision | None
    audit_events: tuple[AuditTraceEvent, ...]
    summary: dict[str, Any]
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.request_id.strip():
            errors.append("request_id is required")
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        if self.status not in CHAT_WORKFLOW_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.ok and self.status not in {"answered", "dry_run_ready"}:
            errors.append("ok=true requires answered or dry_run_ready")
        if self.status == "answered":
            if not self.answer:
                errors.append("answered status requires answer")
            if not self.citations:
                errors.append("answered status requires citations")
            if not self.evidence:
                errors.append("answered status requires evidence")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "status": self.status,
            "ok": self.ok,
            "blocked": self.blocked,
            "requires_human_approval": self.requires_human_approval,
            "dry_run": self.dry_run,
            "question": self.question,
            "answer": self.answer,
            "citations": list(self.citations),
            "evidence": [item.to_dict() for item in self.evidence],
            "security_report": security_guard_report_to_dict(self.security_report) if self.security_report else None,
            "workflow_run": workflow_run_to_dict(self.workflow_run) if self.workflow_run else None,
            "workflow_inspection": workflow_inspection_to_dict(self.workflow_inspection) if self.workflow_inspection else None,
            "workflow_acceptance": workflow_acceptance_to_dict(self.workflow_acceptance) if self.workflow_acceptance else None,
            "audit_events": [event.to_dict() for event in self.audit_events],
            "summary": dict(self.summary),
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def build_chat_question_input(
    request_id: str,
    trace_id: str,
    question: str,
    required_skills: list[str] | tuple[str, ...] | None = None,
    available_skills: list[str] | tuple[str, ...] | None = None,
    source_status: dict[str, Any] | None = None,
    eval_gate: dict[str, Any] | None = None,
    source_texts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ChatQuestionInput:
    return ChatQuestionInput(
        request_id=str(request_id),
        trace_id=str(trace_id),
        question=str(question),
        required_skills=tuple(str(skill) for skill in (required_skills or ())),
        available_skills=tuple(str(skill) for skill in (available_skills or ())),
        source_status=dict(source_status or {}),
        eval_gate=dict(eval_gate or {}),
        source_texts=tuple(dict(source) for source in (source_texts or ())),
        metadata=dict(metadata or {}),
    )


def _input_from_dict(data: dict[str, Any]) -> ChatQuestionInput:
    warnings = tuple(f"unknown chat input field: {key}" for key in sorted(set(data) - set(KNOWN_CHAT_INPUT_FIELDS)))
    return ChatQuestionInput(
        request_id=str(data.get("request_id", "")),
        trace_id=str(data.get("trace_id", data.get("request_id", "local_trace"))),
        question=str(data.get("question", "")),
        required_skills=tuple(str(skill) for skill in (data.get("required_skills") or ())),
        available_skills=tuple(str(skill) for skill in (data.get("available_skills") or ())),
        source_status=dict(data.get("source_status") or {}),
        eval_gate=dict(data.get("eval_gate") or {}),
        source_texts=tuple(dict(source) for source in (data.get("source_texts") or ())),
        metadata=dict(data.get("metadata") or {}),
        warnings=warnings,
    )


def _workflow_input(input_data: ChatQuestionInput) -> WorkflowRunInput:
    return WorkflowRunInput(
        run_id=input_data.request_id,
        user_request=input_data.question,
        required_skills=input_data.required_skills,
        available_skills=input_data.available_skills,
        source_status=input_data.source_status,
        eval_gate=input_data.eval_gate,
        risk_flags=(),
        metadata={"trace_id": input_data.trace_id, **dict(input_data.metadata or {})},
    )


def _answer_from_provider(provider_result: ChatAnswerArtifact | dict[str, Any]) -> ChatAnswerArtifact:
    if isinstance(provider_result, ChatAnswerArtifact):
        return provider_result
    evidence = tuple(
        ChatAnswerEvidence(
            source_id=str(item.get("source_id", "")),
            citation=str(item.get("citation", "")),
            evidence_label=str(item.get("evidence_label", "")),
            confidence=str(item.get("confidence", "low")),
            text=str(item.get("text", "")),
            metadata=dict(item.get("metadata") or {}),
        )
        for item in provider_result.get("evidence", ())
    )
    return ChatAnswerArtifact(
        answer=str(provider_result.get("answer", "")),
        citations=tuple(str(citation) for citation in (provider_result.get("citations") or ())),
        evidence=evidence,
        metadata=dict(provider_result.get("metadata") or {}),
        warnings=tuple(provider_result.get("warnings") or ()),
        errors=tuple(provider_result.get("errors") or ()),
    )


def _status_summary(status: str, security: SecurityGuardReport | None, acceptance: WorkflowAcceptanceDecision | None, audit_events: tuple[AuditTraceEvent, ...]) -> dict[str, Any]:
    return {
        "status": status,
        "security_risk_level": security.risk_level if security else None,
        "workflow_acceptance_status": acceptance.status if acceptance else None,
        "audit_event_count": len(audit_events),
    }


def _acceptance_with_trace(decision: WorkflowAcceptanceDecision, trace_id: str) -> WorkflowAcceptanceDecision:
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
        reasons=decision.reasons,
        warnings=decision.warnings,
        metadata={**dict(decision.metadata or {}), "trace_id": trace_id},
    )


def _events(
    input_data: ChatQuestionInput,
    status: str,
    security_report: SecurityGuardReport | None,
    run: WorkflowRunArtifact | None,
    inspection: WorkflowInspectionReport | None,
    acceptance: WorkflowAcceptanceDecision | None,
    policy: ChatWorkflowPolicy,
) -> tuple[AuditTraceEvent, ...]:
    events: list[AuditTraceEvent] = [
        build_audit_event(
            trace_id=input_data.trace_id,
            event_type="chat_request_received",
            event_id=f"{input_data.trace_id}_chat_request_received",
            severity="info",
            actor="user",
            request_id=input_data.request_id,
            payload={"request_id": input_data.request_id, "question": input_data.question},
            created_at_utc=policy.created_at_utc,
            policy=policy.audit_policy,
        )
    ]
    if security_report is not None:
        events.extend(build_security_audit_events(security_report, input_data.trace_id))
    if run is not None and inspection is not None and acceptance is not None:
        events.extend(build_workflow_audit_events(run, inspection, acceptance))
    response_type = "chat_response_ready" if status in {"answered", "dry_run_ready"} else "chat_response_blocked"
    events.append(
        build_audit_event(
            trace_id=input_data.trace_id,
            event_type=response_type,
            event_id=f"{input_data.trace_id}_{response_type}",
            severity="info" if response_type == "chat_response_ready" else "blocked",
            actor="system",
            request_id=input_data.request_id,
            payload={"status": status},
            created_at_utc=policy.created_at_utc,
            policy=policy.audit_policy,
        )
    )
    return tuple(events)


def _result(
    input_data: ChatQuestionInput,
    status: str,
    policy: ChatWorkflowPolicy,
    security_report: SecurityGuardReport | None = None,
    workflow_run: WorkflowRunArtifact | None = None,
    workflow_inspection: WorkflowInspectionReport | None = None,
    workflow_acceptance: WorkflowAcceptanceDecision | None = None,
    answer_artifact: ChatAnswerArtifact | None = None,
    warnings: tuple[str, ...] = (),
    errors: tuple[str, ...] = (),
) -> ChatWorkflowResult:
    audit_events = _events(input_data, status, security_report, workflow_run, workflow_inspection, workflow_acceptance, policy)
    return ChatWorkflowResult(
        request_id=input_data.request_id or "invalid_chat_request",
        trace_id=input_data.trace_id or "invalid_chat_trace",
        schema_version=policy.schema_version,
        created_at_utc=policy.created_at_utc,
        status=status,
        ok=status in {"answered", "dry_run_ready"},
        blocked=status in {"blocked", "invalid"},
        requires_human_approval=status == "requires_human_approval",
        dry_run=status == "dry_run_ready",
        question=input_data.question,
        answer=answer_artifact.answer if answer_artifact else None,
        citations=answer_artifact.citations if answer_artifact else (),
        evidence=answer_artifact.evidence if answer_artifact else (),
        security_report=security_report,
        workflow_run=workflow_run,
        workflow_inspection=workflow_inspection,
        workflow_acceptance=workflow_acceptance,
        audit_events=audit_events,
        summary=_status_summary(status, security_report, workflow_acceptance, audit_events),
        metadata=dict(input_data.metadata or {}),
        warnings=tuple(dict.fromkeys((*input_data.warnings, *warnings, *((answer_artifact.warnings if answer_artifact else ()))))),
        errors=tuple(dict.fromkeys((*input_data.errors, *errors, *((answer_artifact.errors if answer_artifact else ()))))),
    )


def run_chat_workflow(
    input_data: ChatQuestionInput | dict[str, Any],
    answer_provider: ChatAnswerProvider | None = None,
    policy: ChatWorkflowPolicy | None = None,
) -> ChatWorkflowResult:
    active_policy = policy or ChatWorkflowPolicy()
    chat_input = _input_from_dict(input_data) if isinstance(input_data, dict) else input_data
    input_errors = tuple((*active_policy.validate(), *chat_input.validate()))
    if input_errors:
        return _result(chat_input, "invalid", active_policy, errors=input_errors)

    security_report = inspect_security_dict(
        {
            "request_id": chat_input.request_id,
            "user_request": chat_input.question,
            "source_texts": [dict(source) for source in chat_input.source_texts],
            "control_artifacts": {"source_status": chat_input.source_status, "eval_gate": chat_input.eval_gate},
            "metadata": chat_input.metadata or {},
        }
    )
    if active_policy.require_security_ok and security_report.blocked:
        return _result(chat_input, "blocked", active_policy, security_report=security_report, errors=security_report.errors)
    if active_policy.require_security_ok and security_report.requires_human_approval:
        return _result(chat_input, "requires_human_approval", active_policy, security_report=security_report, warnings=security_report.warnings)

    workflow_run = build_workflow_run(_workflow_input(chat_input))
    workflow_inspection = inspect_workflow_run(workflow_run)
    workflow_acceptance = _acceptance_with_trace(accept_workflow_artifacts(workflow_run, workflow_inspection), chat_input.trace_id)
    if active_policy.require_workflow_acceptance and workflow_acceptance.status != "accepted":
        status = "requires_human_approval" if workflow_acceptance.status == "requires_human_approval" else "blocked"
        return _result(
            chat_input,
            status,
            active_policy,
            security_report=security_report,
            workflow_run=workflow_run,
            workflow_inspection=workflow_inspection,
            workflow_acceptance=workflow_acceptance,
            warnings=workflow_acceptance.warnings,
        )

    if answer_provider is None:
        return _result(
            chat_input,
            "dry_run_ready",
            active_policy,
            security_report=security_report,
            workflow_run=workflow_run,
            workflow_inspection=workflow_inspection,
            workflow_acceptance=workflow_acceptance,
            warnings=("no answer provider wired; dry-run only",),
        )

    try:
        provider_result = answer_provider.answer(chat_input)
        answer_artifact = _answer_from_provider(provider_result)
    except Exception as exc:
        return _result(
            chat_input,
            "blocked",
            active_policy,
            security_report=security_report,
            workflow_run=workflow_run,
            workflow_inspection=workflow_inspection,
            workflow_acceptance=workflow_acceptance,
            errors=(f"answer provider failed: {exc}",),
        )

    answer_errors = answer_artifact.validate()
    if answer_errors:
        return _result(
            chat_input,
            "invalid",
            active_policy,
            security_report=security_report,
            workflow_run=workflow_run,
            workflow_inspection=workflow_inspection,
            workflow_acceptance=workflow_acceptance,
            answer_artifact=answer_artifact,
            errors=answer_errors,
        )
    return _result(
        chat_input,
        "answered",
        active_policy,
        security_report=security_report,
        workflow_run=workflow_run,
        workflow_inspection=workflow_inspection,
        workflow_acceptance=workflow_acceptance,
        answer_artifact=answer_artifact,
    )


def chat_workflow_result_to_dict(result: ChatWorkflowResult) -> dict[str, Any]:
    return result.to_dict()


def chat_workflow_result_from_dict(data: dict[str, Any]) -> ChatWorkflowResult:
    return ChatWorkflowResult(
        request_id=str(data.get("request_id", "")),
        trace_id=str(data.get("trace_id", "")),
        schema_version=str(data.get("schema_version", DEFAULT_CHAT_WORKFLOW_VERSION)),
        created_at_utc=str(data.get("created_at_utc", DEFAULT_CREATED_AT_UTC)),
        status=str(data.get("status", "invalid")),
        ok=bool(data.get("ok", False)),
        blocked=bool(data.get("blocked", True)),
        requires_human_approval=bool(data.get("requires_human_approval", False)),
        dry_run=bool(data.get("dry_run", False)),
        question=str(data.get("question", "")),
        answer=data.get("answer"),
        citations=tuple(data.get("citations") or ()),
        evidence=tuple(
            ChatAnswerEvidence(
                source_id=str(item.get("source_id", "")),
                citation=str(item.get("citation", "")),
                evidence_label=str(item.get("evidence_label", "")),
                confidence=str(item.get("confidence", "low")),
                text=str(item.get("text", "")),
                metadata=dict(item.get("metadata") or {}),
            )
            for item in data.get("evidence", ())
        ),
        security_report=security_guard_report_from_dict(data["security_report"]) if data.get("security_report") else None,
        workflow_run=workflow_run_from_dict(data["workflow_run"]) if data.get("workflow_run") else None,
        workflow_inspection=workflow_inspection_from_dict(data["workflow_inspection"]) if data.get("workflow_inspection") else None,
        workflow_acceptance=workflow_acceptance_from_dict(data["workflow_acceptance"]) if data.get("workflow_acceptance") else None,
        audit_events=tuple(audit_event_from_dict(event) for event in data.get("audit_events", ())),
        summary=dict(data.get("summary") or {}),
        metadata=dict(data.get("metadata") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
    )


def write_chat_workflow_result(
    result: ChatWorkflowResult,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"chat workflow result already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"chat workflow result parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(chat_workflow_result_to_dict(result), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def build_chat_audit_events(result: ChatWorkflowResult, trace_id: str, metadata: dict[str, Any] | None = None) -> list[AuditTraceEvent]:
    if trace_id == result.trace_id and not metadata:
        return list(result.audit_events)
    return [
        build_audit_event(
            trace_id=trace_id,
            event_type=event.event_type,
            event_id=f"{trace_id}_{event.event_type}_{index}",
            severity=event.severity,
            actor=event.actor,
            run_id=event.run_id,
            request_id=event.request_id,
            decision_id=event.decision_id,
            artifact_refs=event.artifact_refs,
            payload={**dict(event.payload or {}), "metadata": dict(metadata or {})},
        )
        for index, event in enumerate(result.audit_events, start=1)
    ]


def write_chat_audit_jsonl(result: ChatWorkflowResult, path: str | Path, append: bool = False, create_dirs: bool = False) -> Path:
    return write_audit_jsonl(result.audit_events, path, append=append, create_dirs=create_dirs)


def summarize_chat_workflow(result: ChatWorkflowResult) -> dict[str, Any]:
    event_type_counts: dict[str, int] = {}
    for event in result.audit_events:
        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
    return {
        "request_id": result.request_id,
        "trace_id": result.trace_id,
        "status": result.status,
        "ok": result.ok,
        "blocked": result.blocked,
        "requires_human_approval": result.requires_human_approval,
        "dry_run": result.dry_run,
        "citation_count": len(result.citations),
        "evidence_count": len(result.evidence),
        "audit_event_count": len(result.audit_events),
        "audit_event_type_counts": event_type_counts,
        "warning_count": len(result.warnings),
        "error_count": len(result.errors),
    }
