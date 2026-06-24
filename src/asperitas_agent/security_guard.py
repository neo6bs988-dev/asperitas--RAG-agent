from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.audit_trace import AuditTraceEvent, AuditTracePolicy, build_audit_event


SecurityRiskLevel = str
SecurityFindingSeverity = str
SecurityFindingCategory = str

SECURITY_RISK_LEVELS = ("low", "medium", "high", "blocked")
SECURITY_FINDING_SEVERITIES = ("info", "warning", "error", "blocked")
SECURITY_FINDING_CATEGORIES = (
    "prompt_injection",
    "source_instruction",
    "secret_exposure",
    "tool_execution_request",
    "external_connector_request",
    "policy_bypass",
    "unsafe_operational_request",
    "schema",
)
DEFAULT_SECURITY_GUARD_VERSION = "MVP-019C"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"
KNOWN_SECURITY_INPUT_FIELDS = ("request_id", "user_request", "source_texts", "control_artifacts", "metadata")


@dataclass(frozen=True)
class SecurityGuardFinding:
    finding_id: str
    category: SecurityFindingCategory
    severity: SecurityFindingSeverity
    location: str
    message: str
    evidence: str = ""
    source_id: str | None = None
    requires_human_approval: bool = False
    blocked: bool = False
    metadata: dict[str, Any] | None = None

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.finding_id.strip():
            errors.append("finding_id is required")
        if self.category not in SECURITY_FINDING_CATEGORIES:
            errors.append(f"invalid category: {self.category}")
        if self.severity not in SECURITY_FINDING_SEVERITIES:
            errors.append(f"invalid severity: {self.severity}")
        if not self.location.strip():
            errors.append("location is required")
        if not self.message.strip():
            errors.append("message is required")
        if self.blocked and self.severity != "blocked":
            errors.append("blocked finding requires severity=blocked")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "severity": self.severity,
            "location": self.location,
            "message": self.message,
            "evidence": self.evidence,
            "source_id": self.source_id,
            "requires_human_approval": self.requires_human_approval,
            "blocked": self.blocked,
            "metadata": dict(self.metadata or {}),
        }


@dataclass(frozen=True)
class SecurityGuardPolicy:
    block_on_prompt_injection: bool = True
    block_on_secret_exposure: bool = True
    block_on_tool_execution_request: bool = True
    block_on_policy_bypass: bool = True
    require_approval_on_unsafe_operational_request: bool = True
    treat_source_text_as_untrusted: bool = True
    include_clean_event: bool = False
    evidence_max_chars: int = 160
    audit_policy: AuditTracePolicy = AuditTracePolicy()
    policy_id: str = "asperitas_security_guard_policy"
    schema_version: str = DEFAULT_SECURITY_GUARD_VERSION
    created_at_utc: str = DEFAULT_CREATED_AT_UTC

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.evidence_max_chars < 0:
            errors.append("evidence_max_chars must be non-negative")
        errors.extend(f"audit_policy: {error}" for error in self.audit_policy.validate())
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["audit_policy"] = self.audit_policy.to_dict()
        return data


@dataclass(frozen=True)
class SecurityGuardInput:
    request_id: str
    user_request: str
    source_texts: tuple[dict[str, Any], ...] = ()
    control_artifacts: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.request_id.strip():
            errors.append("request_id is required")
        if not self.user_request.strip():
            errors.append("user_request is required")
        if not isinstance(self.source_texts, tuple):
            errors.append("source_texts must be a tuple")
        for index, source in enumerate(self.source_texts):
            if not isinstance(source, dict):
                errors.append(f"source_texts[{index}] must be an object")
            elif "text" not in source:
                errors.append(f"source_texts[{index}].text is required")
        if self.control_artifacts is not None and not isinstance(self.control_artifacts, dict):
            errors.append("control_artifacts must be an object")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user_request": self.user_request,
            "source_texts": [dict(source) for source in self.source_texts],
            "control_artifacts": dict(self.control_artifacts or {}),
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class SecurityGuardReport:
    request_id: str
    schema_version: str
    created_at_utc: str
    ok: bool
    risk_level: SecurityRiskLevel
    blocked: bool
    requires_human_approval: bool
    findings: tuple[SecurityGuardFinding, ...]
    summary: dict[str, Any]
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.request_id.strip():
            errors.append("request_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.risk_level not in SECURITY_RISK_LEVELS:
            errors.append(f"invalid risk_level: {self.risk_level}")
        if self.ok and self.blocked:
            errors.append("ok=true cannot be blocked")
        if self.ok and self.errors:
            errors.append("ok=true cannot include errors")
        for finding in self.findings:
            errors.extend(f"{finding.finding_id}: {error}" for error in finding.validate())
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "ok": self.ok,
            "risk_level": self.risk_level,
            "blocked": self.blocked,
            "requires_human_approval": self.requires_human_approval,
            "findings": [finding.to_dict() for finding in self.findings],
            "summary": dict(self.summary),
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def build_security_guard_input(
    request_id: str,
    user_request: str,
    source_texts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    control_artifacts: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> SecurityGuardInput:
    return SecurityGuardInput(
        request_id=str(request_id),
        user_request=str(user_request),
        source_texts=tuple(dict(source) for source in (source_texts or ())),
        control_artifacts=dict(control_artifacts or {}),
        metadata=dict(metadata or {}),
    )


def _compact(text: str, max_chars: int) -> str:
    compacted = " ".join(str(text).split())
    if len(compacted) <= max_chars:
        return compacted
    return compacted[: max(0, max_chars - 3)] + "..."


def _finding(
    finding_id: str,
    category: str,
    severity: str,
    location: str,
    message: str,
    evidence: str = "",
    source_id: str | None = None,
    requires_human_approval: bool = False,
    blocked: bool = False,
    policy: SecurityGuardPolicy | None = None,
) -> SecurityGuardFinding:
    active_policy = policy or SecurityGuardPolicy()
    return SecurityGuardFinding(
        finding_id=finding_id,
        category=category,
        severity=severity,
        location=location,
        message=message,
        evidence=_compact(evidence, active_policy.evidence_max_chars),
        source_id=source_id,
        requires_human_approval=requires_human_approval,
        blocked=blocked,
    )


def _contains_any(text: str, patterns: tuple[str, ...]) -> str | None:
    normalized = text.lower()
    for pattern in patterns:
        if pattern in normalized:
            return pattern
    return None


def _regex_match(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return pattern
    return None


PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget your instructions",
    "override system prompt",
    "act as developer mode",
    "jailbreak",
    "do not follow the above",
)
POLICY_BYPASS_PATTERNS = (
    "reveal your system prompt",
    "show the system prompt",
    "show developer instructions",
    "reveal developer instructions",
    "print internal instructions",
    "hidden instructions",
    "confidential instructions",
)
TOOL_EXECUTION_PATTERNS = (
    "run shell",
    "execute shell",
    "run powershell",
    "run bash",
    "execute command",
    "call tool",
    "use a tool to",
    "write to disk",
    "delete files",
)
EXTERNAL_CONNECTOR_PATTERNS = (
    "send email",
    "post to slack",
    "call github",
    "open a pull request",
    "use gmail",
    "use google drive",
    "use airtable",
    "external connector",
    "mcp connector",
)
UNSAFE_OPERATIONAL_PATTERNS = (
    "wet-lab protocol",
    "step-by-step protocol",
    "automate the lab",
    "execute the experiment",
    "transform bacteria",
    "culture pathogen",
    "genetic engineering protocol",
    "biosafety bypass",
    "scale up fermentation",
)
SECRET_PATTERNS = (
    r"\b(?:sk|pk)_[A-Za-z0-9_\-]{12,}\b",
    r"\b[A-Za-z0-9._%+\-]+:[A-Za-z0-9_\-]{12,}\b",
    r"\b(?:api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^'\"\s]{8,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
)


def _find_text_risks(
    text: str,
    location: str,
    source_id: str | None,
    is_source_text: bool,
    policy: SecurityGuardPolicy,
    start_index: int,
) -> list[SecurityGuardFinding]:
    findings: list[SecurityGuardFinding] = []

    def add(category: str, severity: str, message: str, evidence: str, approval: bool = False, blocked: bool = False) -> None:
        findings.append(
            _finding(
                f"finding_{start_index + len(findings) + 1}",
                category,
                severity,
                location,
                message,
                evidence,
                source_id=source_id,
                requires_human_approval=approval,
                blocked=blocked,
                policy=policy,
            )
        )

    prompt_match = _contains_any(text, PROMPT_INJECTION_PATTERNS)
    if prompt_match:
        if is_source_text:
            add("source_instruction", "warning", "source text contains instruction-like prompt-injection text", prompt_match, approval=True)
        else:
            add("prompt_injection", "blocked", "user request contains prompt-injection text", prompt_match, blocked=policy.block_on_prompt_injection)

    policy_match = _contains_any(text, POLICY_BYPASS_PATTERNS)
    if policy_match:
        add("policy_bypass", "blocked", "request attempts to reveal or bypass internal instructions", policy_match, blocked=policy.block_on_policy_bypass)

    tool_match = _contains_any(text, TOOL_EXECUTION_PATTERNS)
    if tool_match:
        add("tool_execution_request", "blocked", "request asks for shell, tool, or file-system execution", tool_match, blocked=policy.block_on_tool_execution_request)

    connector_match = _contains_any(text, EXTERNAL_CONNECTOR_PATTERNS)
    if connector_match:
        add("external_connector_request", "blocked", "request asks for external connector action", connector_match, blocked=True)

    secret_match = _regex_match(text, SECRET_PATTERNS)
    if secret_match:
        add("secret_exposure", "blocked", "text appears to contain a secret or credential-like value", secret_match, blocked=policy.block_on_secret_exposure)

    unsafe_match = _contains_any(text, UNSAFE_OPERATIONAL_PATTERNS)
    if unsafe_match:
        add(
            "unsafe_operational_request",
            "error",
            "request may require biosafety or operational human approval",
            unsafe_match,
            approval=policy.require_approval_on_unsafe_operational_request,
        )
    return findings


def _risk_level(findings: tuple[SecurityGuardFinding, ...], errors: tuple[str, ...]) -> str:
    if errors or any(finding.blocked or finding.severity == "blocked" for finding in findings):
        return "blocked"
    if any(finding.severity == "error" or finding.requires_human_approval for finding in findings):
        return "high"
    if any(finding.severity == "warning" for finding in findings):
        return "medium"
    return "low"


def _summary(findings: tuple[SecurityGuardFinding, ...]) -> dict[str, Any]:
    categories: dict[str, int] = {}
    severities: dict[str, int] = {}
    for finding in findings:
        categories[finding.category] = categories.get(finding.category, 0) + 1
        severities[finding.severity] = severities.get(finding.severity, 0) + 1
    return {
        "finding_count": len(findings),
        "category_counts": categories,
        "severity_counts": severities,
    }


def inspect_security_input(input_data: SecurityGuardInput, policy: SecurityGuardPolicy | None = None) -> SecurityGuardReport:
    active_policy = policy or SecurityGuardPolicy()
    warnings = list(input_data.warnings)
    errors = list(input_data.validate()) + list(active_policy.validate())
    findings: list[SecurityGuardFinding] = []
    if errors:
        findings.append(
            _finding(
                "finding_1",
                "schema",
                "blocked",
                "input",
                "security guard input failed schema validation",
                "; ".join(errors),
                blocked=True,
                policy=active_policy,
            )
        )
    else:
        findings.extend(_find_text_risks(input_data.user_request, "user_request", None, False, active_policy, len(findings)))
        for index, source in enumerate(input_data.source_texts):
            source_id = str(source.get("source_id") or f"source_{index + 1}")
            text = str(source.get("text") or "")
            if active_policy.treat_source_text_as_untrusted:
                findings.extend(_find_text_risks(text, f"source_texts[{index}].text", source_id, True, active_policy, len(findings)))
        artifact_text = json.dumps(input_data.control_artifacts or {}, ensure_ascii=False, sort_keys=True)
        if artifact_text and artifact_text != "{}":
            findings.extend(_find_text_risks(artifact_text, "control_artifacts", None, False, active_policy, len(findings)))

    finding_tuple = tuple(findings)
    blocked = bool(errors) or any(finding.blocked or finding.severity == "blocked" for finding in finding_tuple)
    requires_approval = any(finding.requires_human_approval for finding in finding_tuple)
    risk_level = _risk_level(finding_tuple, tuple(errors))
    if any(finding.severity == "warning" for finding in finding_tuple):
        warnings.append("warning-level security findings present")
    return SecurityGuardReport(
        request_id=input_data.request_id or "invalid_request",
        schema_version=active_policy.schema_version,
        created_at_utc=active_policy.created_at_utc,
        ok=not blocked,
        risk_level=risk_level,
        blocked=blocked,
        requires_human_approval=requires_approval,
        findings=finding_tuple,
        summary=_summary(finding_tuple),
        metadata=dict(input_data.metadata or {}),
        warnings=tuple(dict.fromkeys(warnings)),
        errors=tuple(dict.fromkeys(errors)),
    )


def inspect_security_dict(data: dict[str, Any], policy: SecurityGuardPolicy | None = None) -> SecurityGuardReport:
    warnings = tuple(f"unknown security input field: {key}" for key in sorted(set(data) - set(KNOWN_SECURITY_INPUT_FIELDS)))
    input_data = SecurityGuardInput(
        request_id=str(data.get("request_id", "")),
        user_request=str(data.get("user_request", "")),
        source_texts=tuple(dict(source) for source in data.get("source_texts") or ()),
        control_artifacts=dict(data.get("control_artifacts") or {}),
        metadata=dict(data.get("metadata") or {}),
        warnings=warnings,
    )
    return inspect_security_input(input_data, policy=policy)


def security_guard_report_to_dict(report: SecurityGuardReport) -> dict[str, Any]:
    return report.to_dict()


def security_guard_report_from_dict(data: dict[str, Any]) -> SecurityGuardReport:
    return SecurityGuardReport(
        request_id=str(data.get("request_id", "")),
        schema_version=str(data.get("schema_version", DEFAULT_SECURITY_GUARD_VERSION)),
        created_at_utc=str(data.get("created_at_utc", DEFAULT_CREATED_AT_UTC)),
        ok=bool(data.get("ok", False)),
        risk_level=str(data.get("risk_level", "blocked")),
        blocked=bool(data.get("blocked", True)),
        requires_human_approval=bool(data.get("requires_human_approval", False)),
        findings=tuple(
            SecurityGuardFinding(
                finding_id=str(finding.get("finding_id", "")),
                category=str(finding.get("category", "")),
                severity=str(finding.get("severity", "blocked")),
                location=str(finding.get("location", "")),
                message=str(finding.get("message", "")),
                evidence=str(finding.get("evidence", "")),
                source_id=finding.get("source_id"),
                requires_human_approval=bool(finding.get("requires_human_approval", False)),
                blocked=bool(finding.get("blocked", False)),
                metadata=dict(finding.get("metadata") or {}),
            )
            for finding in data.get("findings", ())
        ),
        summary=dict(data.get("summary") or {}),
        metadata=dict(data.get("metadata") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
    )


def write_security_guard_report(
    report: SecurityGuardReport,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"security guard report already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"security guard report parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(security_guard_report_to_dict(report), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def build_security_audit_events(
    report: SecurityGuardReport,
    trace_id: str,
    metadata: dict[str, Any] | None = None,
    policy: SecurityGuardPolicy | None = None,
) -> list[AuditTraceEvent]:
    active_policy = policy or SecurityGuardPolicy()
    if not report.findings and not active_policy.include_clean_event:
        return []
    if report.blocked:
        severity = "blocked"
    elif report.requires_human_approval or report.findings:
        severity = "warning"
    else:
        severity = "info"
    return [
        build_audit_event(
            trace_id=trace_id,
            event_type="security_guard_triggered",
            event_id=f"{trace_id}_security_guard_{report.request_id}",
            severity=severity,
            actor="system",
            request_id=report.request_id,
            payload={
                "request_id": report.request_id,
                "risk_level": report.risk_level,
                "blocked": report.blocked,
                "requires_human_approval": report.requires_human_approval,
                "finding_count": len(report.findings),
                "categories": report.summary.get("category_counts", {}),
                "metadata": dict(metadata or {}),
            },
            created_at_utc=active_policy.created_at_utc,
            policy=active_policy.audit_policy,
        )
    ]


def summarize_security_guard(report: SecurityGuardReport) -> dict[str, Any]:
    return {
        "request_id": report.request_id,
        "ok": report.ok,
        "risk_level": report.risk_level,
        "blocked": report.blocked,
        "requires_human_approval": report.requires_human_approval,
        "finding_count": len(report.findings),
        "category_counts": dict(report.summary.get("category_counts", {})),
        "severity_counts": dict(report.summary.get("severity_counts", {})),
        "warning_count": len(report.warnings),
        "error_count": len(report.errors),
    }
