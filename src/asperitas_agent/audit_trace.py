from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


AUDIT_EVENT_TYPES = (
    "workflow_plan_created",
    "workflow_run_created",
    "workflow_inspected",
    "workflow_accepted",
    "workflow_rejected",
    "human_approval_required",
    "chat_request_received",
    "chat_response_blocked",
    "chat_response_ready",
    "security_guard_triggered",
    "eval_gate_checked",
    "source_gate_checked",
)
AUDIT_SEVERITIES = ("info", "warning", "error", "blocked")
AUDIT_ACTORS = ("system", "user", "human_reviewer", "tool")
DEFAULT_AUDIT_VERSION = "MVP-019A"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
SENSITIVE_KEY_FRAGMENTS = ("secret", "token", "api_key", "password", "private_key", "credential")


@dataclass(frozen=True)
class AuditTracePolicy:
    allow_raw_text: bool = False
    raw_text_max_chars: int = 240
    redaction_text: str = "[REDACTED]"
    fail_closed: bool = True
    policy_id: str = "asperitas_audit_trace_policy"
    schema_version: str = DEFAULT_AUDIT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if self.raw_text_max_chars < 0:
            errors.append("raw_text_max_chars must be non-negative")
        if not self.redaction_text:
            errors.append("redaction_text is required")
        if not self.fail_closed:
            errors.append("audit trace policy must fail closed")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditTraceEvent:
    trace_id: str
    event_id: str
    event_type: str
    created_at_utc: str
    severity: str
    actor: str
    run_id: str | None = None
    request_id: str | None = None
    decision_id: str | None = None
    artifact_refs: tuple[str, ...] = ()
    payload: dict[str, Any] | None = None
    redactions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    schema_version: str = DEFAULT_AUDIT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        if not self.event_id.strip():
            errors.append("event_id is required")
        if self.event_type not in AUDIT_EVENT_TYPES:
            errors.append(f"invalid event_type: {self.event_type}")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.severity not in AUDIT_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")
        if self.actor not in AUDIT_ACTORS:
            errors.append(f"invalid actor: {self.actor}")
        if not isinstance(self.artifact_refs, tuple):
            errors.append("artifact_refs must be a tuple")
        if self.payload is not None and not isinstance(self.payload, dict):
            errors.append("payload must be an object when provided")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "created_at_utc": self.created_at_utc,
            "severity": self.severity,
            "actor": self.actor,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "decision_id": self.decision_id,
            "artifact_refs": list(self.artifact_refs),
            "payload": dict(self.payload or {}),
            "redactions": list(self.redactions),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class AuditTraceRecord:
    trace_id: str
    events: tuple[AuditTraceEvent, ...]
    metadata: dict[str, Any] | None = None
    policy: AuditTracePolicy = AuditTracePolicy()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    schema_version: str = DEFAULT_AUDIT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.trace_id.strip():
            errors.append("trace_id is required")
        errors.extend(f"policy: {error}" for error in self.policy.validate())
        if not isinstance(self.events, tuple):
            errors.append("events must be a tuple")
        for event in self.events:
            errors.extend(f"{event.event_id}: {error}" for error in event.validate())
            if event.trace_id != self.trace_id:
                errors.append(f"{event.event_id}: event trace_id does not match record trace_id")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "schema_version": self.schema_version,
            "events": [event.to_dict() for event in self.events],
            "metadata": dict(self.metadata or {}),
            "policy": self.policy.to_dict(),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def _redact(value: Any, policy: AuditTracePolicy, path: str, redactions: list[str]) -> Any:
    key = path.rsplit(".", 1)[-1]
    if _is_sensitive_key(key):
        redactions.append(path)
        return policy.redaction_text
    if isinstance(value, dict):
        return {str(k): _redact(v, policy, f"{path}.{k}" if path else str(k), redactions) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item, policy, f"{path}[{index}]", redactions) for index, item in enumerate(value)]
    if key == "raw_text" and isinstance(value, str) and not policy.allow_raw_text and len(value) > policy.raw_text_max_chars:
        redactions.append(path)
        return policy.redaction_text
    return value


def redact_audit_payload(payload: dict[str, Any], policy: AuditTracePolicy | None = None) -> dict[str, Any]:
    active_policy = policy or AuditTracePolicy()
    redactions: list[str] = []
    redacted = _redact(dict(payload or {}), active_policy, "", redactions)
    return {"payload": redacted, "redactions": redactions}


def build_audit_event(
    trace_id: str,
    event_type: str,
    event_id: str | None = None,
    severity: str = "info",
    actor: str = "system",
    run_id: str | None = None,
    request_id: str | None = None,
    decision_id: str | None = None,
    artifact_refs: tuple[str, ...] | list[str] | None = None,
    payload: dict[str, Any] | None = None,
    created_at_utc: str = DEFAULT_CREATED_AT_UTC,
    policy: AuditTracePolicy | None = None,
) -> AuditTraceEvent:
    active_policy = policy or AuditTracePolicy()
    policy_errors = active_policy.validate()
    warnings: list[str] = []
    redacted = redact_audit_payload(payload or {}, active_policy)
    event = AuditTraceEvent(
        trace_id=trace_id,
        event_id=event_id or f"{trace_id}_{event_type}",
        event_type=event_type,
        created_at_utc=created_at_utc,
        severity=severity,
        actor=actor,
        run_id=run_id,
        request_id=request_id,
        decision_id=decision_id,
        artifact_refs=tuple(str(ref) for ref in (artifact_refs or ()) if str(ref).strip()),
        payload=redacted["payload"],
        redactions=tuple(redacted["redactions"]),
        warnings=tuple(warnings),
        errors=tuple(policy_errors),
        schema_version=active_policy.schema_version,
    )
    validation_errors = event.validate()
    if validation_errors:
        return AuditTraceEvent(
            trace_id=trace_id,
            event_id=event.event_id or "invalid_audit_event",
            event_type=event_type,
            created_at_utc=created_at_utc,
            severity=severity if severity in AUDIT_SEVERITIES else "blocked",
            actor=actor if actor in AUDIT_ACTORS else "system",
            run_id=run_id,
            request_id=request_id,
            decision_id=decision_id,
            artifact_refs=event.artifact_refs,
            payload=event.payload,
            redactions=event.redactions,
            warnings=event.warnings,
            errors=validation_errors,
            schema_version=event.schema_version,
        )
    return event


def build_audit_record(
    events: tuple[AuditTraceEvent, ...] | list[AuditTraceEvent],
    metadata: dict[str, Any] | None = None,
    policy: AuditTracePolicy | None = None,
) -> AuditTraceRecord:
    active_policy = policy or AuditTracePolicy()
    event_tuple = tuple(events)
    trace_id = event_tuple[0].trace_id if event_tuple else str((metadata or {}).get("trace_id", "local_audit_trace"))
    return AuditTraceRecord(trace_id=trace_id, events=event_tuple, metadata=metadata or {}, policy=active_policy)


def audit_event_to_dict(event: AuditTraceEvent) -> dict[str, Any]:
    return event.to_dict()


def audit_event_from_dict(data: dict[str, Any]) -> AuditTraceEvent:
    warnings = tuple(f"unknown audit event field: {key}" for key in sorted(set(data) - set(AuditTraceEvent.__dataclass_fields__)))
    return AuditTraceEvent(
        trace_id=str(data.get("trace_id", "")),
        event_id=str(data.get("event_id", "")),
        event_type=str(data.get("event_type", "")),
        created_at_utc=str(data.get("created_at_utc", "")),
        severity=str(data.get("severity", "blocked")),
        actor=str(data.get("actor", "system")),
        run_id=data.get("run_id"),
        request_id=data.get("request_id"),
        decision_id=data.get("decision_id"),
        artifact_refs=tuple(data.get("artifact_refs") or ()),
        payload=dict(data.get("payload") or {}),
        redactions=tuple(data.get("redactions") or ()),
        warnings=tuple(data.get("warnings") or ()) + warnings,
        errors=tuple(data.get("errors") or ()),
        schema_version=str(data.get("schema_version", DEFAULT_AUDIT_VERSION)),
    )


def audit_record_to_dict(record: AuditTraceRecord) -> dict[str, Any]:
    return record.to_dict()


def audit_record_from_dict(data: dict[str, Any]) -> AuditTraceRecord:
    policy_data = data.get("policy") or {}
    return AuditTraceRecord(
        trace_id=str(data.get("trace_id", "")),
        events=tuple(audit_event_from_dict(event) for event in data.get("events", ())),
        metadata=dict(data.get("metadata") or {}),
        policy=AuditTracePolicy(
            allow_raw_text=bool(policy_data.get("allow_raw_text", False)),
            raw_text_max_chars=int(policy_data.get("raw_text_max_chars", 240)),
            redaction_text=str(policy_data.get("redaction_text", "[REDACTED]")),
            fail_closed=bool(policy_data.get("fail_closed", True)),
            policy_id=str(policy_data.get("policy_id", "asperitas_audit_trace_policy")),
            schema_version=str(policy_data.get("schema_version", DEFAULT_AUDIT_VERSION)),
        ),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
        schema_version=str(data.get("schema_version", DEFAULT_AUDIT_VERSION)),
    )


def write_audit_jsonl(
    events: tuple[AuditTraceEvent, ...] | list[AuditTraceEvent],
    path: str | Path,
    append: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not append:
        raise FileExistsError(f"audit JSONL already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"audit JSONL parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with output_path.open(mode, encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(audit_event_to_dict(event), ensure_ascii=False, sort_keys=True) + "\n")
    return output_path


def load_audit_jsonl(path: str | Path, strict: bool = True) -> list[AuditTraceEvent]:
    events: list[AuditTraceEvent] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = audit_event_from_dict(json.loads(line))
            errors = event.validate()
            if errors and strict:
                raise ValueError("; ".join(errors))
            if errors and not strict:
                event = AuditTraceEvent(
                    **{**event.to_dict(), "errors": tuple(event.errors) + tuple(errors), "warnings": tuple(event.warnings) + (f"malformed JSONL line {line_number}",)}
                )
            events.append(event)
        except Exception as exc:
            if strict:
                raise ValueError(f"malformed audit JSONL line {line_number}: {exc}") from exc
            events.append(
                AuditTraceEvent(
                    trace_id="invalid_audit_trace",
                    event_id=f"invalid_line_{line_number}",
                    event_type="security_guard_triggered",
                    created_at_utc=DEFAULT_CREATED_AT_UTC,
                    severity="blocked",
                    actor="system",
                    payload={},
                    warnings=(f"malformed JSONL line {line_number}",),
                    errors=(str(exc),),
                )
            )
    return events


def summarize_audit_record(record: AuditTraceRecord) -> dict[str, Any]:
    event_type_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    for event in record.events:
        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
        severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
    return {
        "trace_id": record.trace_id,
        "event_count": len(record.events),
        "event_type_counts": event_type_counts,
        "severity_counts": severity_counts,
        "warning_count": len(record.warnings) + sum(len(event.warnings) for event in record.events),
        "error_count": len(record.errors) + sum(len(event.errors) for event in record.events),
    }
