from __future__ import annotations

import importlib.util
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ReleaseReadinessStatus = str

RELEASE_READINESS_STATUSES = ("ready_for_internal_rc", "blocked", "requires_human_review", "invalid")
RELEASE_CHECK_STATUSES = ("passed", "warning", "blocked")
DEFAULT_RELEASE_READINESS_VERSION = "MVP-019E"
DEFAULT_CREATED_AT_UTC = "1970-01-01T00:00:00Z"

DEFAULT_REQUIRED_MODULES = {
    "security_guard_present": "asperitas_agent.security_guard",
    "chat_workflow_present": "asperitas_agent.chat_workflow",
}
DEFAULT_REQUIRED_PATHS = {
    "skills_layer_present": ".agents/skills",
    "eval_layer_present": "docs/MVP017_EVAL_LAYER_CLOSEOUT.md",
    "workflow_layer_present": "docs/MVP018_WORKFLOW_LAYER_CLOSEOUT.md",
    "audit_layer_present": "docs/MVP019A_AUDIT_TRACE_LAYER.md",
    "chat_cli_dry_run_present": "scripts/ask_asperitas_agent.py",
    "artifact_verifier_available": "scripts/verify_artifacts.py",
    "internal_deploy_guide_present": "docs/V1_INTERNAL_DEPLOY_GUIDE.md",
    "known_limitations_present": "docs/V1_KNOWN_LIMITATIONS.md",
    "v1_1_handoff_present": "docs/V1_1_PERFORMANCE_HANDOFF.md",
}
CLAIM_DOC_PATHS = (
    "docs/V1_INTERNAL_DEPLOY_GUIDE.md",
    "docs/V1_RELEASE_CLOSEOUT.md",
    "docs/V1_KNOWN_LIMITATIONS.md",
    "docs/V1_1_PERFORMANCE_HANDOFF.md",
)
BLOCKED_CLAIM_PATTERNS = {
    "no_default_real_answer_provider_claim": (
        "real rag answer provider is wired by default",
        "real rag answer provider default is enabled",
        "default real answer provider",
    ),
    "no_public_saas_claim": (
        "public saas is ready",
        "public saas ready",
        "public saas chatbot",
        "production public saas",
    ),
    "no_autonomous_wet_lab_claim": (
        "autonomous wet-lab execution is ready",
        "autonomous wet lab execution is ready",
        "autonomous wet-lab execution enabled",
        "autonomous lab execution",
    ),
}


@dataclass(frozen=True)
class ReleaseReadinessCheck:
    check_id: str
    status: str
    message: str
    critical: bool = True
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if not self.check_id.strip():
            errors.append("check_id is required")
        if self.status not in RELEASE_CHECK_STATUSES:
            errors.append(f"invalid check status: {self.status}")
        if not self.message.strip():
            errors.append("message is required")
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "message": self.message,
            "critical": self.critical,
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class ReleaseReadinessPolicy:
    repo_root: str = "."
    required_modules: dict[str, str] | None = None
    required_paths: dict[str, str] | None = None
    claim_doc_paths: tuple[str, ...] = CLAIM_DOC_PATHS
    blocked_claim_patterns: dict[str, tuple[str, ...]] | None = None
    allow_warnings_as_ready: bool = True
    policy_id: str = "asperitas_v1_release_readiness_policy"
    schema_version: str = DEFAULT_RELEASE_READINESS_VERSION
    created_at_utc: str = DEFAULT_CREATED_AT_UTC

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if not self.repo_root.strip():
            errors.append("repo_root is required")
        return tuple(errors)

    def module_checks(self) -> dict[str, str]:
        return dict(DEFAULT_REQUIRED_MODULES if self.required_modules is None else self.required_modules)

    def path_checks(self) -> dict[str, str]:
        return dict(DEFAULT_REQUIRED_PATHS if self.required_paths is None else self.required_paths)

    def claim_patterns(self) -> dict[str, tuple[str, ...]]:
        return dict(BLOCKED_CLAIM_PATTERNS if self.blocked_claim_patterns is None else self.blocked_claim_patterns)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["required_modules"] = self.module_checks()
        data["required_paths"] = self.path_checks()
        data["blocked_claim_patterns"] = {key: list(value) for key, value in self.claim_patterns().items()}
        return data


@dataclass(frozen=True)
class ReleaseReadinessReport:
    status: ReleaseReadinessStatus
    ok: bool
    schema_version: str
    created_at_utc: str
    checks: tuple[ReleaseReadinessCheck, ...]
    summary: dict[str, Any]
    metadata: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = list(self.errors)
        if self.status not in RELEASE_READINESS_STATUSES:
            errors.append(f"invalid readiness status: {self.status}")
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        if not self.created_at_utc.strip():
            errors.append("created_at_utc is required")
        if self.ok and self.status != "ready_for_internal_rc":
            errors.append("ok=true requires status=ready_for_internal_rc")
        for check in self.checks:
            errors.extend(f"{check.check_id}: {error}" for error in check.validate())
        return tuple(dict.fromkeys(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ok": self.ok,
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "checks": [check.to_dict() for check in self.checks],
            "summary": dict(self.summary),
            "metadata": dict(self.metadata or {}),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def _check(check_id: str, status: str, message: str, critical: bool = True, metadata: dict[str, Any] | None = None) -> ReleaseReadinessCheck:
    return ReleaseReadinessCheck(check_id=check_id, status=status, message=message, critical=critical, metadata=metadata or {})


def _repo_path(repo_root: Path, relative: str) -> Path:
    return repo_root / relative


def _module_present(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _path_present(path: Path) -> bool:
    return path.exists()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _claim_allowed(text: str, pattern: str) -> bool:
    normalized = " ".join(text.lower().split())
    negative_prefixes = ("not ", "no ", "non-scope: ", "does not ", "without ")
    index = normalized.find(pattern)
    if index < 0:
        return True
    prefix = normalized[max(0, index - 40) : index]
    return any(prefix.endswith(prefix_item) or prefix_item in prefix[-20:] for prefix_item in negative_prefixes)


def _claim_checks(repo_root: Path, policy: ReleaseReadinessPolicy) -> list[ReleaseReadinessCheck]:
    checks: list[ReleaseReadinessCheck] = []
    combined = ""
    missing_docs: list[str] = []
    for relative in policy.claim_doc_paths:
        path = _repo_path(repo_root, relative)
        if not path.exists():
            missing_docs.append(relative)
            continue
        combined += "\n" + _read_text(path)
    for check_id, patterns in policy.claim_patterns().items():
        blocked_patterns = tuple(pattern for pattern in patterns if not _claim_allowed(combined, pattern))
        if missing_docs:
            checks.append(
                _check(
                    check_id,
                    "warning",
                    "claim scan skipped missing release docs",
                    critical=False,
                    metadata={"missing_docs": missing_docs},
                )
            )
        elif blocked_patterns:
            checks.append(
                _check(
                    check_id,
                    "blocked",
                    "blocked release-readiness claim pattern found",
                    metadata={"patterns": blocked_patterns},
                )
            )
        else:
            checks.append(_check(check_id, "passed", "blocked claim pattern absent"))
    return checks


def _summary(checks: tuple[ReleaseReadinessCheck, ...]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    return {
        "check_count": len(checks),
        "status_counts": status_counts,
        "blocked_count": status_counts.get("blocked", 0),
        "warning_count": status_counts.get("warning", 0),
        "passed_count": status_counts.get("passed", 0),
    }


def _report_status(checks: tuple[ReleaseReadinessCheck, ...], policy: ReleaseReadinessPolicy, errors: tuple[str, ...]) -> str:
    if errors:
        return "invalid"
    if any(check.status == "blocked" and check.critical for check in checks):
        return "blocked"
    if any(check.status == "warning" for check in checks) and not policy.allow_warnings_as_ready:
        return "requires_human_review"
    return "ready_for_internal_rc"


def build_v1_release_readiness_report(metadata: dict[str, Any] | None = None, policy: ReleaseReadinessPolicy | None = None) -> ReleaseReadinessReport:
    active_policy = policy or ReleaseReadinessPolicy()
    repo_root = Path(active_policy.repo_root)
    errors = active_policy.validate()
    checks: list[ReleaseReadinessCheck] = []
    for check_id, module_name in active_policy.module_checks().items():
        checks.append(
            _check(
                check_id,
                "passed" if _module_present(module_name) else "blocked",
                f"module {'present' if _module_present(module_name) else 'missing'}: {module_name}",
                metadata={"module": module_name},
            )
        )
    for check_id, relative in active_policy.path_checks().items():
        path = _repo_path(repo_root, relative)
        checks.append(
            _check(
                check_id,
                "passed" if _path_present(path) else "blocked",
                f"path {'present' if _path_present(path) else 'missing'}: {relative}",
                metadata={"path": relative},
            )
        )
    checks.extend(_claim_checks(repo_root, active_policy))
    check_tuple = tuple(checks)
    status = _report_status(check_tuple, active_policy, errors)
    return ReleaseReadinessReport(
        status=status,
        ok=status == "ready_for_internal_rc",
        schema_version=active_policy.schema_version,
        created_at_utc=active_policy.created_at_utc,
        checks=check_tuple,
        summary=_summary(check_tuple),
        metadata=metadata or {},
        warnings=tuple(check.message for check in check_tuple if check.status == "warning"),
        errors=errors,
    )


def release_readiness_to_dict(report: ReleaseReadinessReport) -> dict[str, Any]:
    return report.to_dict()


def release_readiness_from_dict(data: dict[str, Any]) -> ReleaseReadinessReport:
    return ReleaseReadinessReport(
        status=str(data.get("status", "invalid")),
        ok=bool(data.get("ok", False)),
        schema_version=str(data.get("schema_version", DEFAULT_RELEASE_READINESS_VERSION)),
        created_at_utc=str(data.get("created_at_utc", DEFAULT_CREATED_AT_UTC)),
        checks=tuple(
            ReleaseReadinessCheck(
                check_id=str(check.get("check_id", "")),
                status=str(check.get("status", "blocked")),
                message=str(check.get("message", "")),
                critical=bool(check.get("critical", True)),
                metadata=dict(check.get("metadata") or {}),
                warnings=tuple(check.get("warnings") or ()),
                errors=tuple(check.get("errors") or ()),
            )
            for check in data.get("checks", ())
        ),
        summary=dict(data.get("summary") or {}),
        metadata=dict(data.get("metadata") or {}),
        warnings=tuple(data.get("warnings") or ()),
        errors=tuple(data.get("errors") or ()),
    )


def write_release_readiness_report(
    report: ReleaseReadinessReport,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"release readiness report already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise FileNotFoundError(f"release readiness report parent does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(release_readiness_to_dict(report), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def summarize_release_readiness(report: ReleaseReadinessReport) -> dict[str, Any]:
    return {
        "status": report.status,
        "ok": report.ok,
        "check_count": len(report.checks),
        "blocked_count": report.summary.get("blocked_count", 0),
        "warning_count": report.summary.get("warning_count", 0),
        "passed_count": report.summary.get("passed_count", 0),
        "error_count": len(report.errors),
    }
