from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .skill_discovery import SKILL_ALIASES, discover_skill_files, validate_skill_files_against_registry


RESULT_STATES = ("PASS", "FAIL", "PARTIAL", "NOT_TESTABLE", "INVALID")
LIFECYCLE_STATUSES = ("active", "planned", "deprecated", "blocked", "unregistered_review_required")
MODES = ("READ", "DRAFT", "WRITE")
RISK_CLASSES = ("low", "medium", "high")
ERROR_BEHAVIORS = ("fail_closed", "fail_safe", "report_only")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
MVP_VERSION_PATTERN = re.compile(r"^mvp[-_ ]?\d", re.IGNORECASE)
UNTRUSTED_SOURCE_BLOCKS = {
    "treat_source_text_as_instruction",
    "treat_untrusted_source_text_as_instruction",
}
BIOLOGY_MARKERS = (
    "biosecurity",
    "biosafety",
    "biological",
    "cites",
    "genetic resource",
    "lmo",
    "nagoya",
    "pathogen",
    "wet-lab",
    "wet lab",
)


@dataclass(frozen=True, order=True)
class ContractFinding:
    code: str
    path: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SkillContractRecord:
    path: Path
    skill_directory: Path
    frontmatter_name: str
    description: str
    data: Mapping[str, Any]

    @property
    def skill_id(self) -> str:
        value = self.data.get("skill_id", "")
        return value if isinstance(value, str) else ""


@dataclass(frozen=True)
class ContractValidationReport:
    state: str
    validation_level: str
    root: str
    contracts_checked: int
    skills_discovered: int
    canonical_skill_ids: tuple[str, ...]
    findings: tuple[ContractFinding, ...]

    @property
    def ok(self) -> bool:
        return self.state == "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "ok": self.ok,
            "validation_level": self.validation_level,
            "root": self.root,
            "contracts_checked": self.contracts_checked,
            "skills_discovered": self.skills_discovered,
            "canonical_skill_ids": list(self.canonical_skill_ids),
            "findings": [finding.to_dict() for finding in self.findings],
        }


def normalize_skill_id(frontmatter_name: str) -> str:
    return frontmatter_name.replace("-", "_")


def validate_contract_file(path: str | Path) -> ContractValidationReport:
    contract_path = Path(path)
    record, findings = _load_contract_record(contract_path)
    if record is not None:
        findings.extend(_validate_record(record))
    return _build_report(
        state=_strict_state(findings),
        validation_level="fixture_contract_validation",
        root=str(contract_path),
        contracts_checked=1 if record is not None else 0,
        skills_discovered=1 if record is not None else 0,
        canonical_skill_ids=(record.skill_id,) if record is not None and record.skill_id else (),
        findings=findings,
    )


def validate_contract_files(paths: Iterable[str | Path]) -> ContractValidationReport:
    records: list[SkillContractRecord] = []
    findings: list[ContractFinding] = []
    path_list = [Path(path) for path in paths]
    for path in path_list:
        record, load_findings = _load_contract_record(path)
        findings.extend(load_findings)
        if record is not None:
            records.append(record)
            findings.extend(_validate_record(record))
    findings.extend(_validate_contract_set(records))
    return _build_report(
        state=_strict_state(findings),
        validation_level="fixture_contract_validation",
        root="<multiple-contracts>",
        contracts_checked=len(records),
        skills_discovered=len(records),
        canonical_skill_ids=tuple(record.skill_id for record in records if record.skill_id),
        findings=findings,
    )


def validate_repository(root: str | Path, *, transition: bool = False) -> ContractValidationReport:
    repo_root = Path(root).resolve()
    skills_root = repo_root / ".agents" / "skills"
    if not skills_root.is_dir():
        return _build_report(
            state="NOT_TESTABLE",
            validation_level="repository_transition_audit" if transition else "repository_contract_validation",
            root=str(repo_root),
            contracts_checked=0,
            skills_discovered=0,
            canonical_skill_ids=(),
            findings=(
                ContractFinding(
                    code="SKILLS_ROOT_NOT_FOUND",
                    path=_relative_display(skills_root, repo_root),
                    message="repository skill directory is unavailable",
                ),
            ),
        )
    skills = discover_skill_files(repo_root)
    contract_paths = [repo_root / skill.relative_path for skill in skills]
    contract_paths = [path.parent / "skill.contract.json" for path in contract_paths]
    existing_contracts = [path for path in contract_paths if path.is_file()]
    records: list[SkillContractRecord] = []
    findings: list[ContractFinding] = []

    for path in existing_contracts:
        record, load_findings = _load_contract_record(path)
        findings.extend(load_findings)
        if record is not None:
            records.append(record)
            findings.extend(_validate_record(record))
    findings.extend(_validate_contract_set(records))

    missing_contracts = sorted(path for path in contract_paths if not path.is_file())
    for path in missing_contracts:
        findings.append(
            ContractFinding(
                code="MISSING_SKILL_CONTRACT",
                path=_relative_display(path, repo_root),
                message="skill.contract.json is not present for this repository skill",
                severity="candidate" if transition else "error",
            )
        )

    incumbent_report = validate_skill_files_against_registry(repo_root)
    records_by_name = {record.frontmatter_name: record for record in records}
    for skill_name in incumbent_report.missing_registry_specs:
        record = records_by_name.get(skill_name)
        lifecycle = record.data.get("lifecycle") if record is not None else None
        routing = record.data.get("routing") if record is not None else None
        explicitly_quarantined = (
            isinstance(lifecycle, dict)
            and lifecycle.get("status") == "unregistered_review_required"
            and isinstance(routing, dict)
            and routing.get("implicit_activation") is False
        )
        if explicitly_quarantined:
            continue
        findings.append(
            ContractFinding(
                code="UNREGISTERED_REPOSITORY_SKILL",
                path=f".agents/skills/{skill_name}/SKILL.md",
                message="well-formed repository skill has no incumbent Python SkillSpec",
                severity="candidate" if transition else "error",
            )
        )

    discovered_names = {skill.normalized_name for skill in skills}
    canonical_registry_ids = {skill_id.replace("_", "-") for skill_id in incumbent_report.registered_skills}
    for registry_id, aliases in sorted(SKILL_ALIASES.items()):
        canonical_name = registry_id.replace("_", "-")
        for alias in aliases:
            normalized_alias = alias.replace("_", "-")
            if normalized_alias in discovered_names and normalized_alias != canonical_name:
                code = (
                    "LEGACY_ALIAS_EQUALS_CANONICAL_SKILL"
                    if normalized_alias in canonical_registry_ids
                    else "LEGACY_ALIAS_SATISFIES_DIFFERENT_SKILL"
                )
                findings.append(
                    ContractFinding(
                        code=code,
                        path="src/asperitas_agent/skill_discovery.py",
                        message=f"{registry_id} alias {alias} points to a different live skill identity",
                        severity="candidate" if transition else "error",
                    )
                )

    if transition:
        state = "PARTIAL" if findings else "PASS"
        validation_level = "repository_transition_audit"
    else:
        state = _strict_state(findings)
        validation_level = "repository_contract_validation"
    return _build_report(
        state=state,
        validation_level=validation_level,
        root=str(repo_root),
        contracts_checked=len(records),
        skills_discovered=len(skills),
        canonical_skill_ids=tuple(record.skill_id for record in records if record.skill_id),
        findings=findings,
    )


def _load_contract_record(path: Path) -> tuple[SkillContractRecord | None, list[ContractFinding]]:
    findings: list[ContractFinding] = []
    if not path.exists():
        return None, [ContractFinding("CONTRACT_NOT_FOUND", str(path), "contract file does not exist")]
    if not path.is_file():
        return None, [ContractFinding("CONTRACT_NOT_FILE", str(path), "contract path is not a regular file")]

    skill_directory = path.parent.resolve()
    try:
        resolved_path = path.resolve(strict=True)
    except OSError as exc:
        return None, [ContractFinding("UNSAFE_CONTRACT_PATH", str(path), f"cannot resolve contract path: {exc}")]
    if resolved_path.parent != skill_directory:
        return None, [ContractFinding("UNSAFE_CONTRACT_PATH", str(path), "contract escapes its skill directory")]

    try:
        raw_data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [ContractFinding("INVALID_CONTRACT_JSON", str(path), str(exc))]
    if not isinstance(raw_data, dict):
        return None, [ContractFinding("INVALID_CONTRACT_ROOT", str(path), "contract root must be a JSON object")]

    skill_path = skill_directory / "SKILL.md"
    frontmatter, frontmatter_findings = _read_skill_frontmatter(skill_path)
    findings.extend(frontmatter_findings)
    record = SkillContractRecord(
        path=resolved_path,
        skill_directory=skill_directory,
        frontmatter_name=frontmatter.get("name", ""),
        description=frontmatter.get("description", ""),
        data=raw_data,
    )
    return record, findings


def _read_skill_frontmatter(path: Path) -> tuple[dict[str, str], list[ContractFinding]]:
    findings: list[ContractFinding] = []
    metadata = {"name": "", "description": ""}
    if not path.is_file():
        return metadata, [ContractFinding("SKILL_FILE_NOT_FOUND", str(path), "SKILL.md is required")]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return metadata, [ContractFinding("INVALID_SKILL_FILE", str(path), str(exc))]
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return metadata, [ContractFinding("INVALID_SKILL_FRONTMATTER", str(path), "opening delimiter is required")]
    try:
        closing_index = lines[1:].index("---") + 1
    except ValueError:
        return metadata, [ContractFinding("INVALID_SKILL_FRONTMATTER", str(path), "closing delimiter is required")]
    for line in lines[1:closing_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            metadata[key] = _strip_scalar(value)
    return metadata, findings


def _strip_scalar(value: str) -> str:
    clean = value.strip()
    if len(clean) >= 2 and clean[0] == clean[-1] and clean[0] in {"'", '"'}:
        return clean[1:-1].strip()
    return clean


def _validate_record(record: SkillContractRecord) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    data = record.data
    display_path = str(record.path)
    required_sections = {
        "schema_version",
        "skill_id",
        "owner",
        "lifecycle",
        "routing",
        "modes",
        "risk",
        "permissions",
        "contract",
        "verification",
        "rollback",
        "relations",
        "compatibility",
    }
    for field in sorted(required_sections - set(data)):
        findings.append(ContractFinding("MISSING_REQUIRED_FIELD", display_path, f"missing field: {field}"))

    if data.get("schema_version") != "2.0":
        findings.append(ContractFinding("INVALID_SCHEMA_VERSION", display_path, "schema_version must equal 2.0"))
    if not _non_empty_string(data.get("owner")):
        findings.append(ContractFinding("INVALID_OWNER", display_path, "owner must be a non-empty string"))

    name = record.frontmatter_name
    directory_name = record.skill_directory.name
    if directory_name != name:
        findings.append(
            ContractFinding(
                "DIRECTORY_FRONTMATTER_NAME_MISMATCH",
                display_path,
                f"directory {directory_name!r} does not equal frontmatter name {name!r}",
            )
        )
    if not 1 <= len(name) <= 64 or not SKILL_NAME_PATTERN.fullmatch(name):
        findings.append(ContractFinding("INVALID_FRONTMATTER_NAME", display_path, "invalid Agent Skills name grammar"))
    if not record.description:
        findings.append(ContractFinding("DESCRIPTION_REQUIRED", display_path, "SKILL.md description is required"))
    elif len(record.description) > 1024:
        findings.append(
            ContractFinding("DESCRIPTION_TOO_LONG", display_path, "SKILL.md description exceeds 1024 chars")
        )

    skill_id = data.get("skill_id")
    if not isinstance(skill_id, str) or not SKILL_ID_PATTERN.fullmatch(skill_id):
        findings.append(ContractFinding("INVALID_SKILL_ID", display_path, "skill_id has invalid grammar"))
    if skill_id != normalize_skill_id(name):
        findings.append(
            ContractFinding(
                "SKILL_ID_NAME_MISMATCH",
                display_path,
                "skill_id must equal deterministic hyphen-to-underscore name normalization",
            )
        )

    lifecycle = _object(data, "lifecycle", findings, display_path)
    status = lifecycle.get("status")
    if status not in LIFECYCLE_STATUSES:
        findings.append(ContractFinding("INVALID_LIFECYCLE_STATUS", display_path, "unsupported lifecycle status"))
    version = lifecycle.get("version")
    if not _non_empty_string(version):
        findings.append(ContractFinding("LIFECYCLE_VERSION_REQUIRED", display_path, "lifecycle.version is required"))
    elif MVP_VERSION_PATTERN.match(version):
        findings.append(
            ContractFinding(
                "STALE_MVP_CANONICAL_VERSION",
                display_path,
                "MVP provenance belongs in introduced_in, not lifecycle.version",
            )
        )
    if status == "deprecated" and not (
        _non_empty_string(lifecycle.get("replaced_by")) or _non_empty_string(lifecycle.get("terminal_rationale"))
    ):
        findings.append(
            ContractFinding(
                "DEPRECATED_WITHOUT_DISPOSITION",
                display_path,
                "deprecated lifecycle requires replaced_by or terminal_rationale",
            )
        )

    routing = _object(data, "routing", findings, display_path)
    implicit_activation = routing.get("implicit_activation")
    if not isinstance(implicit_activation, bool):
        findings.append(
            ContractFinding("INVALID_IMPLICIT_ACTIVATION", display_path, "implicit_activation must be boolean")
        )
    if status == "unregistered_review_required" and implicit_activation is not False:
        findings.append(
            ContractFinding(
                "UNREGISTERED_SKILL_MUST_BE_EXPLICIT_ONLY",
                display_path,
                "unregistered review skills must set implicit_activation=false",
            )
        )
    for field in ("positive_triggers", "negative_triggers", "conflicts_with"):
        _string_list(routing, field, findings, display_path)
    if not isinstance(routing.get("precedence_rule"), str):
        findings.append(ContractFinding("INVALID_PRECEDENCE_RULE", display_path, "precedence_rule must be string"))

    modes = data.get("modes")
    if not isinstance(modes, list) or not modes or any(mode not in MODES for mode in modes):
        findings.append(ContractFinding("INVALID_MODES", display_path, "modes must be a non-empty supported list"))
        modes = []
    elif len(modes) != len(set(modes)):
        findings.append(ContractFinding("DUPLICATE_MODES", display_path, "modes must be unique"))

    risk = _object(data, "risk", findings, display_path)
    risk_class = risk.get("risk_class")
    if risk_class not in RISK_CLASSES:
        findings.append(ContractFinding("INVALID_RISK_CLASS", display_path, "unsupported risk class"))
    human_gates = _string_list(risk, "human_gates", findings, display_path)

    permissions = _object(data, "permissions", findings, display_path)
    boolean_fields = (
        "approval_required",
        "external_call_allowed",
        "network_allowed",
        "execution_allowed",
        "ingestion_allowed",
        "write_allowed",
        "destructive_allowed",
    )
    for field in boolean_fields:
        if not isinstance(permissions.get(field), bool):
            findings.append(ContractFinding("INVALID_PERMISSION_FLAG", display_path, f"{field} must be boolean"))
    _string_list(permissions, "allowed_actions", findings, display_path)
    forbidden_actions = _string_list(permissions, "forbidden_actions", findings, display_path)
    approval_required = permissions.get("approval_required") is True
    if "WRITE" in modes and not (permissions.get("write_allowed") is True and approval_required):
        findings.append(
            ContractFinding(
                "WRITE_REQUIRES_APPROVAL",
                display_path,
                "WRITE mode requires write_allowed=true and approval_required=true",
            )
        )
    external_access_allowed = (
        permissions.get("external_call_allowed") is True or permissions.get("network_allowed") is True
    )
    if external_access_allowed and not approval_required:
        findings.append(
            ContractFinding(
                "EXTERNAL_ACCESS_REQUIRES_APPROVAL",
                display_path,
                "network or external calls require approval",
            )
        )
    if permissions.get("destructive_allowed") is True:
        findings.append(
            ContractFinding(
                "DESTRUCTIVE_ACTIONS_BLOCKED_BY_DEFAULT",
                display_path,
                "destructive actions are blocked in Contract v2 foundation",
            )
        )
    if risk_class == "high" and (not approval_required or not forbidden_actions):
        findings.append(
            ContractFinding(
                "HIGH_RISK_POLICY_INCOMPLETE",
                display_path,
                "high-risk contract requires approval and non-empty forbidden_actions",
            )
        )
    biology_context = " ".join(_all_strings(data)).casefold()
    risky_capability = permissions.get("execution_allowed") is True or permissions.get("write_allowed") is True
    if risk_class == "high" and risky_capability and any(marker in biology_context for marker in BIOLOGY_MARKERS):
        if not human_gates:
            findings.append(
                ContractFinding(
                    "HIGH_RISK_BIOLOGY_REQUIRES_HUMAN_GATE",
                    display_path,
                    "high-risk biological execution or writing requires a human gate",
                )
            )
    if not UNTRUSTED_SOURCE_BLOCKS.intersection(forbidden_actions):
        findings.append(
            ContractFinding(
                "UNTRUSTED_SOURCE_POLICY_REQUIRED",
                display_path,
                "forbidden_actions must block treating untrusted source text as instruction",
            )
        )

    contract = _object(data, "contract", findings, display_path)
    _string_list(contract, "required_inputs", findings, display_path)
    _string_list(contract, "output_contract", findings, display_path)
    if contract.get("error_behavior") not in ERROR_BEHAVIORS:
        findings.append(ContractFinding("INVALID_ERROR_BEHAVIOR", display_path, "unsupported error behavior"))

    verification = _object(data, "verification", findings, display_path)
    commands = _string_list(verification, "commands", findings, display_path)
    required_fixtures = _string_list(verification, "required_fixtures", findings, display_path)
    if status == "active" and not commands:
        findings.append(
            ContractFinding("ACTIVE_VERIFICATION_REQUIRED", display_path, "active contract requires commands")
        )
    for fixture in required_fixtures:
        if not _is_safe_relative_path(fixture, record.skill_directory):
            findings.append(
                ContractFinding(
                    "UNSAFE_RESOURCE_PATH",
                    display_path,
                    f"required fixture escapes skill directory: {fixture}",
                )
            )

    rollback = _object(data, "rollback", findings, display_path)
    if not _non_empty_string(rollback.get("strategy")):
        findings.append(ContractFinding("ROLLBACK_STRATEGY_REQUIRED", display_path, "rollback.strategy is required"))
    if not _non_empty_string(rollback.get("verification")):
        findings.append(
            ContractFinding("ROLLBACK_VERIFICATION_REQUIRED", display_path, "rollback.verification is required")
        )

    relations = _object(data, "relations", findings, display_path)
    _string_list(relations, "related_skills", findings, display_path)
    _string_list(relations, "supersedes", findings, display_path)

    compatibility = _object(data, "compatibility", findings, display_path)
    aliases = compatibility.get("aliases")
    if not isinstance(aliases, list):
        findings.append(ContractFinding("INVALID_ALIASES", display_path, "compatibility.aliases must be a list"))
    else:
        for index, alias in enumerate(aliases):
            alias_path = f"{display_path}#compatibility.aliases[{index}]"
            if not isinstance(alias, dict):
                findings.append(ContractFinding("INVALID_ALIAS", alias_path, "alias must be an object"))
                continue
            for field in ("value", "kind", "deprecated_since", "compatibility_until", "replaced_by"):
                if field not in alias:
                    findings.append(ContractFinding("MISSING_ALIAS_FIELD", alias_path, f"missing alias field: {field}"))
            if not _non_empty_string(alias.get("value")):
                findings.append(ContractFinding("INVALID_ALIAS_VALUE", alias_path, "alias value is required"))
            is_deprecated_alias = (
                alias.get("deprecated_since") is not None or alias.get("kind") == "deprecated_skill_id"
            )
            if is_deprecated_alias and not _non_empty_string(alias.get("compatibility_until")):
                findings.append(
                    ContractFinding(
                        "DEPRECATED_ALIAS_REQUIRES_EXPIRY",
                        alias_path,
                        "deprecated alias requires compatibility_until",
                    )
                )
            if alias.get("kind") == "deprecated_skill_id" and not _non_empty_string(alias.get("deprecated_since")):
                findings.append(
                    ContractFinding(
                        "DEPRECATED_ALIAS_REQUIRES_START",
                        alias_path,
                        "deprecated alias requires deprecated_since",
                    )
                )

    if "description" in data:
        findings.append(
            ContractFinding(
                "DUPLICATE_DESCRIPTION_AUTHORITY",
                display_path,
                "description must be read from SKILL.md and not duplicated in the contract",
            )
        )
    return findings


def _validate_contract_set(records: list[SkillContractRecord]) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    ids: dict[str, SkillContractRecord] = {}
    names: dict[str, SkillContractRecord] = {}
    aliases: dict[str, tuple[SkillContractRecord, Mapping[str, Any]]] = {}
    alias_edges: dict[str, str] = {}
    for record in records:
        if record.skill_id:
            if record.skill_id in ids:
                findings.append(
                    ContractFinding(
                        "DUPLICATE_CANONICAL_SKILL_ID",
                        str(record.path),
                        f"duplicate skill_id: {record.skill_id}",
                    )
                )
            else:
                ids[record.skill_id] = record
        if record.frontmatter_name:
            names[record.frontmatter_name] = record

    for record in records:
        compatibility = record.data.get("compatibility")
        if not isinstance(compatibility, dict) or not isinstance(compatibility.get("aliases"), list):
            continue
        for alias in compatibility["aliases"]:
            if not isinstance(alias, dict) or not _non_empty_string(alias.get("value")):
                continue
            value = str(alias["value"])
            normalized_id = value.replace("-", "_")
            normalized_name = value.replace("_", "-")
            if value in aliases:
                findings.append(ContractFinding("DUPLICATE_ALIAS", str(record.path), f"duplicate alias: {value}"))
            else:
                aliases[value] = (record, alias)
            if normalized_id in ids:
                findings.append(
                    ContractFinding(
                        "ALIAS_EQUALS_CANONICAL_ID",
                        str(record.path),
                        f"alias {value} equals canonical skill_id {normalized_id}",
                    )
                )
            if normalized_name in names:
                findings.append(
                    ContractFinding(
                        "ALIAS_EQUALS_CANONICAL_NAME",
                        str(record.path),
                        f"alias {value} equals canonical frontmatter name {normalized_name}",
                    )
                )
            replaced_by = alias.get("replaced_by")
            if _non_empty_string(replaced_by):
                alias_edges[normalized_id] = str(replaced_by).replace("-", "_")

    for start in sorted(alias_edges):
        seen: set[str] = set()
        current = start
        while current in alias_edges:
            if current in seen:
                record = aliases.get(start, (records[0], {}))[0] if records else None
                findings.append(
                    ContractFinding(
                        "ALIAS_CYCLE",
                        str(record.path) if record else "<contracts>",
                        f"alias cycle detected from {start}",
                    )
                )
                break
            seen.add(current)
            current = alias_edges[current]
    return findings


def _object(
    data: Mapping[str, Any], field: str, findings: list[ContractFinding], display_path: str
) -> Mapping[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        findings.append(ContractFinding("INVALID_OBJECT_FIELD", display_path, f"{field} must be an object"))
        return {}
    return value


def _string_list(
    data: Mapping[str, Any], field: str, findings: list[ContractFinding], display_path: str
) -> list[str]:
    value = data.get(field)
    if not isinstance(value, list) or any(not _non_empty_string(item) for item in value):
        findings.append(
            ContractFinding("INVALID_STRING_LIST", display_path, f"{field} must be a list of non-empty strings")
        )
        return []
    return list(value)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_safe_relative_path(value: str, skill_directory: Path) -> bool:
    path = Path(value)
    if path.is_absolute():
        return False
    try:
        candidate = (skill_directory / path).resolve()
        candidate.relative_to(skill_directory.resolve())
    except (OSError, ValueError):
        return False
    return True


def _all_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            result.extend((str(key), *_all_strings(item)))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_all_strings(item))
        return result
    return []


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _strict_state(findings: Iterable[ContractFinding]) -> str:
    findings_tuple = tuple(findings)
    if any(finding.code.startswith("INVALID_CONTRACT_JSON") for finding in findings_tuple):
        return "INVALID"
    if any(finding.severity == "error" for finding in findings_tuple):
        return "FAIL"
    return "PASS"


def _build_report(
    *,
    state: str,
    validation_level: str,
    root: str,
    contracts_checked: int,
    skills_discovered: int,
    canonical_skill_ids: Iterable[str],
    findings: Iterable[ContractFinding],
) -> ContractValidationReport:
    if state not in RESULT_STATES:
        raise ValueError(f"unsupported result state: {state}")
    return ContractValidationReport(
        state=state,
        validation_level=validation_level,
        root=root,
        contracts_checked=contracts_checked,
        skills_discovered=skills_discovered,
        canonical_skill_ids=tuple(sorted(canonical_skill_ids)),
        findings=tuple(sorted(set(findings))),
    )
