from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FAILURE_LOG_SCHEMA_VERSION = "V1.1A-failure-log-v1"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
DEFAULT_SESSION_ID = "local_failure_session"

FAILURE_CATEGORIES = (
    "retrieval_miss",
    "source_gap",
    "citation_issue",
    "unsupported_claim",
    "security_overblock",
    "workflow_overblock",
    "dry_run_provider_needed",
    "format_issue",
    "internal_dogfood_feedback",
    "user_need_unknown",
    "other",
)
FAILURE_SEVERITIES = ("low", "medium", "high", "critical")
FAILURE_STATUSES = ("open", "triaged", "in_progress", "resolved", "wont_fix")
SENSITIVE_KEY_FRAGMENTS = ("secret", "token", "api_key", "password", "private_key", "credential")


@dataclass(frozen=True)
class FailureLogRecord:
    schema_version: str
    failure_id: str
    created_at_utc: str
    session_id: str
    query: str
    expected_behavior: str
    actual_behavior: str
    category: str
    severity: str
    status: str
    source_context: dict[str, Any]
    security_result: dict[str, Any]
    workflow_result: dict[str, Any]
    dry_run_result: dict[str, Any]
    reproduction_steps: tuple[str, ...]
    proposed_fix: str
    redaction_notes: str
    metadata: dict[str, Any]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.failure_id.strip():
            errors.append("failure_id is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if not self.session_id.strip():
            errors.append("session_id is required")
        if not self.query.strip():
            errors.append("query is required")
        if not self.expected_behavior.strip():
            errors.append("expected_behavior is required")
        if not self.actual_behavior.strip():
            errors.append("actual_behavior is required")
        if self.category not in FAILURE_CATEGORIES:
            errors.append(f"invalid category: {self.category}")
        if self.severity not in FAILURE_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")
        if self.status not in FAILURE_STATUSES:
            errors.append(f"invalid status: {self.status}")
        for field_name in ("source_context", "security_result", "workflow_result", "dry_run_result", "metadata"):
            if not isinstance(getattr(self, field_name), dict):
                errors.append(f"{field_name} must be an object")
        if not isinstance(self.reproduction_steps, tuple):
            errors.append("reproduction_steps must be a tuple")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "failure_id": self.failure_id,
            "created_at_utc": self.created_at_utc,
            "session_id": self.session_id,
            "query": self.query,
            "expected_behavior": self.expected_behavior,
            "actual_behavior": self.actual_behavior,
            "category": self.category,
            "severity": self.severity,
            "status": self.status,
            "source_context": dict(self.source_context),
            "security_result": dict(self.security_result),
            "workflow_result": dict(self.workflow_result),
            "dry_run_result": dict(self.dry_run_result),
            "reproduction_steps": list(self.reproduction_steps),
            "proposed_fix": self.proposed_fix,
            "redaction_notes": self.redaction_notes,
            "metadata": dict(self.metadata),
        }


def deterministic_failure_id(query: str, category: str, created_at_utc: str, session_id: str) -> str:
    payload = {
        "category": category,
        "created_at_utc": created_at_utc,
        "query": query,
        "session_id": session_id,
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"fail_{digest[:16]}"


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def redact_failure_payload(value: Any, redaction_text: str = "[REDACTED]", path: str = "") -> tuple[Any, tuple[str, ...]]:
    redactions: list[str] = []

    def _redact(item: Any, current_path: str) -> Any:
        key = current_path.rsplit(".", 1)[-1].split("[", 1)[0]
        if key and _is_sensitive_key(key):
            redactions.append(current_path)
            return redaction_text
        if isinstance(item, dict):
            return {str(k): _redact(v, f"{current_path}.{k}" if current_path else str(k)) for k, v in item.items()}
        if isinstance(item, list):
            return [_redact(v, f"{current_path}[{index}]") for index, v in enumerate(item)]
        return item

    return _redact(_json_safe(value), path), tuple(redactions)


def build_failure_record(
    query: str,
    expected_behavior: str,
    actual_behavior: str,
    category: str,
    severity: str,
    status: str = "open",
    created_at_utc: str = DEFAULT_CREATED_AT_UTC,
    session_id: str = DEFAULT_SESSION_ID,
    failure_id: str | None = None,
    source_context: dict[str, Any] | None = None,
    security_result: dict[str, Any] | None = None,
    workflow_result: dict[str, Any] | None = None,
    dry_run_result: dict[str, Any] | None = None,
    reproduction_steps: tuple[str, ...] | list[str] | None = None,
    proposed_fix: str = "",
    redaction_notes: str = "",
    metadata: dict[str, Any] | None = None,
    schema_version: str = FAILURE_LOG_SCHEMA_VERSION,
) -> FailureLogRecord:
    record = FailureLogRecord(
        schema_version=schema_version,
        failure_id=failure_id or deterministic_failure_id(query, category, created_at_utc, session_id),
        created_at_utc=created_at_utc,
        session_id=session_id,
        query=query,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        category=category,
        severity=severity,
        status=status,
        source_context=dict(_json_safe(source_context or {})),
        security_result=dict(_json_safe(security_result or {})),
        workflow_result=dict(_json_safe(workflow_result or {})),
        dry_run_result=dict(_json_safe(dry_run_result or {})),
        reproduction_steps=tuple(str(step) for step in (reproduction_steps or ())),
        proposed_fix=proposed_fix,
        redaction_notes=redaction_notes,
        metadata=dict(_json_safe(metadata or {})),
    )
    errors = record.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return record


def failure_record_to_dict(record: FailureLogRecord) -> dict[str, Any]:
    return record.to_dict()


def failure_record_from_dict(data: dict[str, Any]) -> FailureLogRecord:
    return build_failure_record(
        schema_version=str(data.get("schema_version", FAILURE_LOG_SCHEMA_VERSION)),
        failure_id=str(data.get("failure_id", "")),
        created_at_utc=str(data.get("created_at_utc", "")),
        session_id=str(data.get("session_id", "")),
        query=str(data.get("query", "")),
        expected_behavior=str(data.get("expected_behavior", "")),
        actual_behavior=str(data.get("actual_behavior", "")),
        category=str(data.get("category", "")),
        severity=str(data.get("severity", "")),
        status=str(data.get("status", "")),
        source_context=dict(data.get("source_context") or {}),
        security_result=dict(data.get("security_result") or {}),
        workflow_result=dict(data.get("workflow_result") or {}),
        dry_run_result=dict(data.get("dry_run_result") or {}),
        reproduction_steps=tuple(data.get("reproduction_steps") or ()),
        proposed_fix=str(data.get("proposed_fix", "")),
        redaction_notes=str(data.get("redaction_notes", "")),
        metadata=dict(data.get("metadata") or {}),
    )


def write_failure_jsonl(
    record: FailureLogRecord,
    path: str | Path,
    append: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not append:
        raise FileExistsError(f"failure JSONL already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"failure JSONL parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with output_path.open(mode, encoding="utf-8") as handle:
        handle.write(json.dumps(failure_record_to_dict(record), ensure_ascii=False, sort_keys=True) + "\n")
    return output_path


def load_failure_jsonl(path: str | Path) -> list[FailureLogRecord]:
    records: list[FailureLogRecord] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(failure_record_from_dict(json.loads(line)))
        except Exception as exc:
            raise ValueError(f"malformed failure JSONL line {line_number}: {exc}") from exc
    return records
