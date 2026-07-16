from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any, Iterable, Mapping

from .skill_discovery import (
    SKILL_ALIASES,
    discover_skill_files,
    validate_skill_files_against_registry,
)

RESULT_STATES = ("PASS", "FAIL", "PARTIAL", "NOT_TESTABLE", "INVALID")
LIFECYCLE_STATUSES = ("active", "planned", "deprecated", "blocked", "unregistered_review_required")
MODES = ("READ", "DRAFT", "WRITE")
RISK_CLASSES = ("low", "medium", "high")
ERROR_BEHAVIORS = ("fail_closed", "fail_safe", "report_only")
ALIAS_KINDS = ("deprecated_skill_id",)
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
MVP_VERSION_PATTERN = re.compile(r"^mvp[-_ ]?\d", re.IGNORECASE)
UNTRUSTED_SOURCE_BLOCKS = frozenset(
    {
        "treat_source_text_as_instruction",
        "treat_untrusted_source_text_as_instruction",
    }
)
SUPPORTED_SCHEMA_KEYWORDS = frozenset(
    {
        "$schema",
        "$id",
        "$ref",
        "$defs",
        "title",
        "type",
        "const",
        "enum",
        "pattern",
        "minLength",
        "required",
        "properties",
        "additionalProperties",
        "items",
        "minItems",
        "uniqueItems",
    }
)
SUPPORTED_SCHEMA_TYPES = frozenset({"object", "array", "string", "boolean", "null"})
SUPPORTED_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


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


def validate_contract_file(path: str | Path, *, schema_path: str | Path | None = None) -> ContractValidationReport:
    contract_path = Path(path)
    schema, schema_findings = _load_schema(schema_path)
    record, findings = _load_contract_record(contract_path)
    findings = [*schema_findings, *findings]
    if record is not None and schema is not None:
        findings.extend(_validate_schema_instance(record.data, schema, str(record.path)))
        findings.extend(_validate_record(record))
        findings.extend(_validate_contract_set([record]))
    return _build_report(
        state=_strict_state(findings),
        validation_level="fixture_contract_validation",
        root=str(contract_path),
        contracts_checked=1 if record is not None else 0,
        skills_discovered=1 if record is not None else 0,
        canonical_skill_ids=(record.skill_id,) if record is not None and record.skill_id else (),
        findings=findings,
    )


def validate_contract_files(
    paths: Iterable[str | Path], *, schema_path: str | Path | None = None
) -> ContractValidationReport:
    records: list[SkillContractRecord] = []
    schema, findings = _load_schema(schema_path)
    path_list = [Path(path) for path in paths]
    for path in path_list:
        record, load_findings = _load_contract_record(path)
        findings.extend(load_findings)
        if record is not None:
            records.append(record)
            if schema is not None:
                findings.extend(_validate_schema_instance(record.data, schema, str(record.path)))
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


def validate_repository(
    root: str | Path, *, transition: bool = False, schema_path: str | Path | None = None
) -> ContractValidationReport:
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
    schema, findings = _load_schema(schema_path, repo_root=repo_root)

    for path in existing_contracts:
        record, load_findings = _load_contract_record(path)
        findings.extend(load_findings)
        if record is not None:
            records.append(record)
            if schema is not None:
                findings.extend(_validate_schema_instance(record.data, schema, str(record.path)))
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

    schema_blocked = any(finding.code.startswith("SCHEMA_") for finding in findings)
    if schema_blocked:
        state = _strict_state(findings)
        validation_level = "repository_transition_audit" if transition else "repository_contract_validation"
    elif transition:
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


def _default_schema_path(repo_root: Path | None = None) -> Path:
    root = repo_root if repo_root is not None else Path(__file__).resolve().parents[2]
    return root / ".agents" / "skill-contract.schema.json"


def _load_schema(
    schema_path: str | Path | None, *, repo_root: Path | None = None
) -> tuple[Mapping[str, Any] | None, list[ContractFinding]]:
    path = Path(schema_path) if schema_path is not None else _default_schema_path(repo_root)
    display_path = str(path)
    if not path.is_file():
        return None, [ContractFinding("SCHEMA_NOT_FOUND", display_path, "schema file is required")]
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        return None, [ContractFinding("SCHEMA_INVALID_JSON", display_path, str(exc))]
    if not isinstance(schema, dict):
        return None, [ContractFinding("SCHEMA_INVALID_ROOT", display_path, "schema root must be an object")]
    try:
        findings = _validate_schema_definition(schema, schema, schema_path="#")
        if not findings:
            findings.extend(_validate_schema_reference_cycles(schema))
    except (KeyError, RecursionError, TypeError, ValueError, re.error):
        findings = [
            ContractFinding(
                "SCHEMA_INVALID_DEFINITION",
                "#",
                "schema definition exceeds or violates the supported deterministic boundary",
            )
        ]
    return (None if findings else schema), findings


def _validate_schema_definition(node: Any, root: Mapping[str, Any], *, schema_path: str) -> list[ContractFinding]:
    if isinstance(node, bool):
        return [
            ContractFinding(
                "SCHEMA_UNSUPPORTED_BOOLEAN_SCHEMA",
                schema_path,
                "Boolean schema nodes are not supported",
            )
        ]
    if not isinstance(node, dict):
        return [ContractFinding("SCHEMA_INVALID_DEFINITION", schema_path, "schema definition must be an object")]
    findings: list[ContractFinding] = []
    for keyword in sorted(set(node) - SUPPORTED_SCHEMA_KEYWORDS):
        findings.append(
            ContractFinding(
                "SCHEMA_UNSUPPORTED_KEYWORD",
                f"{schema_path}/{_pointer_token(keyword)}",
                f"unsupported schema keyword: {keyword}",
            )
        )

    dialect = node.get("$schema")
    if "$schema" in node and (not isinstance(dialect, str) or dialect != SUPPORTED_SCHEMA_DIALECT):
        findings.append(
            _schema_definition_finding(
                "SCHEMA_INVALID_DIALECT",
                schema_path,
                "$schema",
                f"$schema must equal {SUPPORTED_SCHEMA_DIALECT}",
            )
        )
    for keyword in ("$id", "title"):
        if keyword in node and not _non_empty_string(node[keyword]):
            findings.append(
                _schema_definition_finding(
                    "SCHEMA_INVALID_KEYWORD_VALUE",
                    schema_path,
                    keyword,
                    f"{keyword} must be a non-empty string",
                )
            )

    reference = node.get("$ref")
    if "$ref" in node:
        reference_path = _schema_keyword_path(schema_path, "$ref")
        if not isinstance(reference, str) or not reference:
            findings.append(ContractFinding("SCHEMA_INVALID_REF", reference_path, "$ref must be a non-empty string"))
        elif not reference.startswith("#"):
            findings.append(
                ContractFinding(
                    "SCHEMA_EXTERNAL_REF",
                    reference_path,
                    "only local #/$defs/<token> references are allowed",
                )
            )
        elif not _is_supported_local_ref(reference):
            findings.append(
                ContractFinding(
                    "SCHEMA_INVALID_REF",
                    reference_path,
                    "$ref must use the supported #/$defs/<token> JSON Pointer form",
                )
            )
        elif _resolve_local_ref(root, reference) is None:
            findings.append(
                ContractFinding("SCHEMA_REF_NOT_FOUND", reference_path, f"unresolved local reference: {reference}")
            )
        if len(node) != 1:
            findings.append(
                ContractFinding(
                    "SCHEMA_UNSUPPORTED_REF_SIBLING",
                    schema_path,
                    "$ref schema nodes cannot contain sibling keywords in the bounded validator",
                )
            )

    if "type" in node:
        declared_type = node["type"]
        type_path = _schema_keyword_path(schema_path, "type")
        if isinstance(declared_type, str):
            if declared_type not in SUPPORTED_SCHEMA_TYPES:
                findings.append(ContractFinding("SCHEMA_UNSUPPORTED_TYPE", type_path, "unsupported schema type"))
        elif isinstance(declared_type, list):
            if not declared_type:
                findings.append(ContractFinding("SCHEMA_INVALID_TYPE", type_path, "type array must not be empty"))
            elif any(not isinstance(item, str) for item in declared_type):
                findings.append(ContractFinding("SCHEMA_INVALID_TYPE", type_path, "type array members must be strings"))
            else:
                if any(item not in SUPPORTED_SCHEMA_TYPES for item in declared_type):
                    findings.append(ContractFinding("SCHEMA_UNSUPPORTED_TYPE", type_path, "unsupported schema type"))
                if len(declared_type) != len(set(declared_type)):
                    findings.append(
                        ContractFinding("SCHEMA_DUPLICATE_TYPE", type_path, "schema type union must be unique")
                    )
        else:
            findings.append(
                ContractFinding("SCHEMA_INVALID_TYPE", type_path, "type must be a string or non-empty string array")
            )

    if "const" in node and not _is_json_value(node["const"]):
        findings.append(
            _schema_definition_finding(
                "SCHEMA_INVALID_CONST",
                schema_path,
                "const",
                "const must contain a finite JSON-compatible value",
            )
        )

    if "enum" in node:
        enum_values = node["enum"]
        enum_path = _schema_keyword_path(schema_path, "enum")
        if not isinstance(enum_values, list) or not enum_values:
            findings.append(ContractFinding("SCHEMA_INVALID_ENUM", enum_path, "enum must be a non-empty array"))
        elif any(not _is_json_value(value) for value in enum_values):
            findings.append(
                ContractFinding(
                    "SCHEMA_INVALID_ENUM",
                    enum_path,
                    "enum members must be finite JSON-compatible values",
                )
            )
        elif _has_json_duplicates(enum_values):
            findings.append(
                ContractFinding(
                    "SCHEMA_INVALID_ENUM",
                    enum_path,
                    "enum values must be unique using JSON type-aware equality",
                )
            )

    if "pattern" in node:
        pattern = node["pattern"]
        pattern_path = _schema_keyword_path(schema_path, "pattern")
        if not isinstance(pattern, str):
            findings.append(ContractFinding("SCHEMA_INVALID_PATTERN", pattern_path, "pattern must be a string"))
        else:
            try:
                re.compile(pattern)
            except re.error:
                findings.append(
                    ContractFinding(
                        "SCHEMA_INVALID_PATTERN",
                        pattern_path,
                        "pattern must compile under the supported Python regular-expression subset",
                    )
                )

    for keyword in ("minLength", "minItems"):
        if keyword in node:
            value = node[keyword]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                findings.append(
                    _schema_definition_finding(
                        "SCHEMA_INVALID_NON_NEGATIVE_INTEGER",
                        schema_path,
                        keyword,
                        f"{keyword} must be a non-negative integer and not Boolean",
                    )
                )

    if "required" in node:
        required = node["required"]
        required_path = _schema_keyword_path(schema_path, "required")
        if not isinstance(required, list):
            findings.append(ContractFinding("SCHEMA_INVALID_REQUIRED", required_path, "required must be an array"))
        elif any(not _non_empty_string(item) for item in required):
            findings.append(
                ContractFinding(
                    "SCHEMA_INVALID_REQUIRED",
                    required_path,
                    "required members must be non-empty strings",
                )
            )
        elif len(required) != len(set(required)):
            findings.append(
                ContractFinding("SCHEMA_INVALID_REQUIRED", required_path, "required members must be unique")
            )

    properties = node.get("properties")
    if "properties" in node:
        if not isinstance(properties, dict):
            findings.append(
                _schema_definition_finding(
                    "SCHEMA_INVALID_PROPERTIES",
                    schema_path,
                    "properties",
                    "properties must be an object",
                )
            )
        else:
            for name, child in sorted(properties.items()):
                findings.extend(
                    _validate_schema_definition(
                        child,
                        root,
                        schema_path=f"{schema_path}/properties/{_pointer_token(str(name))}",
                    )
                )

    if "additionalProperties" in node and not isinstance(node["additionalProperties"], bool):
        findings.append(
            _schema_definition_finding(
                "SCHEMA_INVALID_ADDITIONAL_PROPERTIES",
                schema_path,
                "additionalProperties",
                "additionalProperties must be Boolean",
            )
        )

    definitions = node.get("$defs")
    if "$defs" in node:
        if not isinstance(definitions, dict):
            findings.append(
                _schema_definition_finding(
                    "SCHEMA_INVALID_DEFS",
                    schema_path,
                    "$defs",
                    "$defs must be an object",
                )
            )
        else:
            for name, child in sorted(definitions.items()):
                definition_path = f"{schema_path}/$defs/{_pointer_token(str(name))}"
                if not _non_empty_string(name):
                    findings.append(
                        ContractFinding("SCHEMA_INVALID_DEFS", definition_path, "$defs keys must be non-empty strings")
                    )
                findings.extend(
                    _validate_schema_definition(
                        child,
                        root,
                        schema_path=definition_path,
                    )
                )

    if "items" in node:
        items = node["items"]
        items_path = _schema_keyword_path(schema_path, "items")
        if not isinstance(items, dict):
            if isinstance(items, bool):
                findings.append(
                    ContractFinding(
                        "SCHEMA_UNSUPPORTED_BOOLEAN_SCHEMA",
                        items_path,
                        "Boolean schema nodes are not supported",
                    )
                )
            else:
                findings.append(ContractFinding("SCHEMA_INVALID_ITEMS", items_path, "items must be a schema object"))
        else:
            findings.extend(_validate_schema_definition(items, root, schema_path=items_path))

    if "uniqueItems" in node and not isinstance(node["uniqueItems"], bool):
        findings.append(
            _schema_definition_finding(
                "SCHEMA_INVALID_UNIQUE_ITEMS",
                schema_path,
                "uniqueItems",
                "uniqueItems must be Boolean",
            )
        )
    return findings


def _schema_definition_finding(code: str, schema_path: str, keyword: str, message: str) -> ContractFinding:
    return ContractFinding(code, _schema_keyword_path(schema_path, keyword), message)


def _schema_keyword_path(schema_path: str, keyword: str) -> str:
    return f"{schema_path}/{_pointer_token(keyword)}"


def _is_supported_local_ref(reference: str) -> bool:
    if not reference.startswith("#/$defs/"):
        return False
    token = reference.removeprefix("#/$defs/")
    if not token:
        return False
    index = 0
    while index < len(token):
        if token[index] == "/":
            return False
        if token[index] == "~":
            if index + 1 >= len(token) or token[index + 1] not in {"0", "1"}:
                return False
            index += 2
        else:
            index += 1
    return True


def _validate_schema_reference_cycles(root: Mapping[str, Any]) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    references: list[tuple[str, str]] = []

    def collect(node: Any, path: str) -> None:
        if not isinstance(node, dict):
            return
        reference = node.get("$ref")
        if isinstance(reference, str):
            references.append((path, reference))
        properties = node.get("properties")
        if isinstance(properties, dict):
            for name, child in sorted(properties.items()):
                collect(child, f"{path}/properties/{_pointer_token(str(name))}")
        definitions = node.get("$defs")
        if isinstance(definitions, dict):
            for name, child in sorted(definitions.items()):
                collect(child, f"{path}/$defs/{_pointer_token(str(name))}")
        items = node.get("items")
        if isinstance(items, dict):
            collect(items, f"{path}/items")

    collect(root, "#")
    for path, reference in references:
        visited: set[int] = set()
        current = _resolve_local_ref(root, reference)
        while isinstance(current, dict) and isinstance(current.get("$ref"), str):
            identity = id(current)
            if identity in visited:
                findings.append(
                    ContractFinding(
                        "SCHEMA_REF_CYCLE",
                        _schema_keyword_path(path, "$ref"),
                        "local reference cycle is not supported",
                    )
                )
                break
            visited.add(identity)
            current = _resolve_local_ref(root, current["$ref"])
    return findings


def _validate_schema_instance(instance: Any, schema: Mapping[str, Any], display_path: str) -> list[ContractFinding]:
    return _validate_schema_node(instance, schema, schema, display_path=display_path, pointer="")


def _validate_schema_node(
    instance: Any,
    node: Mapping[str, Any],
    root: Mapping[str, Any],
    *,
    display_path: str,
    pointer: str,
) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    reference = node.get("$ref")
    if isinstance(reference, str):
        resolved = _resolve_local_ref(root, reference)
        if resolved is None:
            return [_schema_finding("SCHEMA_REF_NOT_FOUND", display_path, pointer, reference)]
        return _validate_schema_node(instance, resolved, root, display_path=display_path, pointer=pointer)

    expected = node.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not any(_matches_schema_type(instance, item) for item in expected_types):
            return [
                _schema_finding(
                    "SCHEMA_TYPE",
                    display_path,
                    pointer,
                    f"expected type {expected_types}, got {type(instance).__name__}",
                )
            ]
    if "const" in node and not _json_equal(instance, node["const"]):
        findings.append(_schema_finding("SCHEMA_CONST", display_path, pointer, "value does not match const"))
    if "enum" in node and not any(_json_equal(instance, value) for value in node["enum"]):
        findings.append(_schema_finding("SCHEMA_ENUM", display_path, pointer, "value is not in enum"))

    if isinstance(instance, str):
        minimum = node.get("minLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            findings.append(_schema_finding("SCHEMA_MIN_LENGTH", display_path, pointer, "string is too short"))
        pattern = node.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, instance) is None:
            findings.append(_schema_finding("SCHEMA_PATTERN", display_path, pointer, "string does not match pattern"))

    if isinstance(instance, dict):
        required = node.get("required", [])
        if isinstance(required, list):
            for name in sorted(required):
                if name not in instance:
                    findings.append(
                        _schema_finding(
                            "SCHEMA_REQUIRED",
                            display_path,
                            _join_pointer(pointer, str(name)),
                            f"required property is missing: {name}",
                        )
                    )
        properties = node.get("properties", {})
        if isinstance(properties, dict):
            for name in sorted(instance):
                child_pointer = _join_pointer(pointer, str(name))
                if name in properties:
                    findings.extend(
                        _validate_schema_node(
                            instance[name],
                            properties[name],
                            root,
                            display_path=display_path,
                            pointer=child_pointer,
                        )
                    )
                elif node.get("additionalProperties") is False:
                    findings.append(
                        _schema_finding(
                            "SCHEMA_ADDITIONAL_PROPERTY",
                            display_path,
                            child_pointer,
                            f"unknown property: {name}",
                        )
                    )

    if isinstance(instance, list):
        minimum = node.get("minItems")
        if isinstance(minimum, int) and len(instance) < minimum:
            findings.append(_schema_finding("SCHEMA_MIN_ITEMS", display_path, pointer, "array is too short"))
        if node.get("uniqueItems") is True:
            if _has_json_duplicates(instance):
                findings.append(
                    _schema_finding("SCHEMA_UNIQUE_ITEMS", display_path, pointer, "array items must be unique")
                )
        items = node.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(instance):
                findings.extend(
                    _validate_schema_node(
                        item,
                        items,
                        root,
                        display_path=display_path,
                        pointer=_join_pointer(pointer, str(index)),
                    )
                )
    return findings


def _resolve_local_ref(root: Mapping[str, Any], reference: str) -> Mapping[str, Any] | None:
    if not reference.startswith("#/$defs/"):
        return None
    current: Any = root
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current if isinstance(current, dict) else None


def _matches_schema_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _schema_finding(code: str, display_path: str, pointer: str, message: str) -> ContractFinding:
    return ContractFinding(code, f"{display_path}#{pointer or '/'}", message)


def _join_pointer(pointer: str, token: str) -> str:
    return f"{pointer}/{_pointer_token(token)}"


def _pointer_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left == right
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, str) or isinstance(right, str):
        return isinstance(left, str) and isinstance(right, str) and left == right
    if isinstance(left, list) or isinstance(right, list):
        return (
            isinstance(left, list)
            and isinstance(right, list)
            and len(left) == len(right)
            and all(_json_equal(left_item, right_item) for left_item, right_item in zip(left, right, strict=True))
        )
    if isinstance(left, dict) or isinstance(right, dict):
        return (
            isinstance(left, dict)
            and isinstance(right, dict)
            and set(left) == set(right)
            and all(_json_equal(left[key], right[key]) for key in left)
        )
    return False


def _has_json_duplicates(values: list[Any]) -> bool:
    return any(_json_equal(value, previous) for index, value in enumerate(values) for previous in values[:index])


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


def _is_json_value(value: Any) -> bool:
    if value is None or isinstance(value, (bool, str, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_json_value(item) for key, item in value.items())
    return False


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
    elif isinstance(version, str) and MVP_VERSION_PATTERN.match(version):
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
    deprecated_since = _optional_full_date(
        lifecycle.get("deprecated_since"), "lifecycle.deprecated_since", findings, display_path
    )
    compatibility_until = _optional_full_date(
        lifecycle.get("compatibility_until"), "lifecycle.compatibility_until", findings, display_path
    )
    replaced_by = lifecycle.get("replaced_by")
    terminal_rationale = lifecycle.get("terminal_rationale")
    if status == "deprecated":
        if deprecated_since is None:
            findings.append(
                ContractFinding("DEPRECATED_SINCE_REQUIRED", display_path, "deprecated lifecycle requires a date")
            )
        if compatibility_until is None:
            findings.append(
                ContractFinding(
                    "DEPRECATED_COMPATIBILITY_UNTIL_REQUIRED",
                    display_path,
                    "deprecated lifecycle requires a compatibility expiry",
                )
            )
        if deprecated_since is not None and compatibility_until is not None and compatibility_until < deprecated_since:
            findings.append(
                ContractFinding(
                    "INVALID_LIFECYCLE_DATE_ORDER",
                    display_path,
                    "compatibility_until must be on or after deprecated_since",
                )
            )
        dispositions = sum((_non_empty_string(replaced_by), _non_empty_string(terminal_rationale)))
        if dispositions != 1:
            findings.append(
                ContractFinding(
                    "DEPRECATED_DISPOSITION_EXCLUSIVE",
                    display_path,
                    "deprecated lifecycle requires exactly one of replaced_by or terminal_rationale",
                )
            )
        if replaced_by is not None and (
            not isinstance(replaced_by, str) or not SKILL_ID_PATTERN.fullmatch(replaced_by)
        ):
            findings.append(
                ContractFinding("INVALID_REPLACED_BY", display_path, "replaced_by must be a canonical skill_id")
            )
        if replaced_by == skill_id:
            findings.append(ContractFinding("SELF_REPLACEMENT", display_path, "deprecated skill cannot replace itself"))
    else:
        non_null_fields = {
            "deprecated_since": lifecycle.get("deprecated_since"),
            "compatibility_until": lifecycle.get("compatibility_until"),
            "replaced_by": replaced_by,
        }
        for field, value in non_null_fields.items():
            if value is not None:
                findings.append(
                    ContractFinding(
                        "NON_DEPRECATED_LIFECYCLE_METADATA",
                        display_path,
                        f"{field} must be null unless lifecycle is deprecated",
                    )
                )
        if terminal_rationale not in (None, ""):
            findings.append(
                ContractFinding(
                    "NON_DEPRECATED_TERMINAL_RATIONALE",
                    display_path,
                    "terminal_rationale must be absent, null, or empty unless deprecated",
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
    risky_capability = permissions.get("execution_allowed") is True or permissions.get("write_allowed") is True
    if risk_class == "high" and risky_capability and not human_gates:
        findings.append(
            ContractFinding(
                "HIGH_RISK_EXECUTION_REQUIRES_HUMAN_GATE",
                display_path,
                "high-risk execution or writing requires a human gate",
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
            elif not SKILL_ID_PATTERN.fullmatch(str(alias["value"])):
                findings.append(
                    ContractFinding("INVALID_ALIAS_VALUE", alias_path, "alias must match canonical skill_id grammar")
                )
            if alias.get("kind") not in ALIAS_KINDS:
                findings.append(ContractFinding("INVALID_ALIAS_KIND", alias_path, "unsupported alias kind"))
            alias_deprecated_since = _optional_full_date(
                alias.get("deprecated_since"), "deprecated_since", findings, alias_path
            )
            alias_compatibility_until = _optional_full_date(
                alias.get("compatibility_until"), "compatibility_until", findings, alias_path
            )
            if alias_deprecated_since is None:
                findings.append(
                    ContractFinding(
                        "DEPRECATED_ALIAS_REQUIRES_START",
                        alias_path,
                        "deprecated alias requires deprecated_since",
                    )
                )
            if alias_compatibility_until is None:
                findings.append(
                    ContractFinding(
                        "DEPRECATED_ALIAS_REQUIRES_EXPIRY",
                        alias_path,
                        "deprecated alias requires compatibility_until",
                    )
                )
            if (
                alias_deprecated_since is not None
                and alias_compatibility_until is not None
                and alias_compatibility_until < alias_deprecated_since
            ):
                findings.append(
                    ContractFinding(
                        "INVALID_ALIAS_DATE_ORDER",
                        alias_path,
                        "compatibility_until must be on or after deprecated_since",
                    )
                )
            alias_replaced_by = alias.get("replaced_by")
            if not isinstance(alias_replaced_by, str) or not SKILL_ID_PATTERN.fullmatch(alias_replaced_by):
                findings.append(
                    ContractFinding(
                        "INVALID_ALIAS_REPLACED_BY",
                        alias_path,
                        "alias replaced_by must be a canonical skill_id",
                    )
                )
            elif alias_replaced_by == str(alias.get("value", "")).replace("-", "_"):
                findings.append(
                    ContractFinding(
                        "ALIAS_SELF_REFERENCE",
                        alias_path,
                        "deprecated alias cannot replace itself",
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

    successor_edges: dict[str, str] = {}
    for record in records:
        lifecycle = record.data.get("lifecycle")
        if not isinstance(lifecycle, dict):
            continue
        successor = lifecycle.get("replaced_by")
        if not _non_empty_string(successor):
            continue
        successor_id = str(successor)
        successor_record = ids.get(successor_id)
        if successor_record is None:
            findings.append(
                ContractFinding(
                    "SUCCESSOR_NOT_FOUND",
                    str(record.path),
                    f"lifecycle successor does not resolve: {successor_id}",
                )
            )
            continue
        successor_lifecycle = successor_record.data.get("lifecycle")
        successor_status = successor_lifecycle.get("status") if isinstance(successor_lifecycle, dict) else None
        if successor_status not in {"active", "planned"}:
            findings.append(
                ContractFinding(
                    "INVALID_SUCCESSOR_STATUS",
                    str(record.path),
                    f"successor must be active or planned: {successor_id}",
                )
            )
        if record.skill_id:
            successor_edges[record.skill_id] = successor_id

    for record in records:
        compatibility = record.data.get("compatibility")
        if not isinstance(compatibility, dict) or not isinstance(compatibility.get("aliases"), list):
            continue
        for index, alias in enumerate(compatibility["aliases"]):
            if not isinstance(alias, dict) or not _non_empty_string(alias.get("replaced_by")):
                continue
            successor_id = str(alias["replaced_by"])
            successor_record = ids.get(successor_id)
            alias_path = f"{record.path}#compatibility.aliases[{index}]"
            if successor_record is None:
                findings.append(
                    ContractFinding(
                        "ALIAS_SUCCESSOR_NOT_FOUND",
                        alias_path,
                        f"alias successor does not resolve: {successor_id}",
                    )
                )
                continue
            successor_lifecycle = successor_record.data.get("lifecycle")
            successor_status = successor_lifecycle.get("status") if isinstance(successor_lifecycle, dict) else None
            if successor_status not in {"active", "planned"}:
                findings.append(
                    ContractFinding(
                        "INVALID_ALIAS_SUCCESSOR_STATUS",
                        alias_path,
                        f"alias successor must be active or planned: {successor_id}",
                    )
                )

    findings.extend(_find_directed_cycles(successor_edges, "SUCCESSOR_CYCLE", records))

    for start in sorted(alias_edges):
        seen: set[str] = set()
        current = start
        while current in alias_edges:
            if current in seen:
                cycle_record = aliases.get(start, (records[0], {}))[0] if records else None
                findings.append(
                    ContractFinding(
                        "ALIAS_CYCLE",
                        str(cycle_record.path) if cycle_record else "<contracts>",
                        f"alias cycle detected from {start}",
                    )
                )
                break
            seen.add(current)
            current = alias_edges[current]
    return findings


def _find_directed_cycles(
    edges: Mapping[str, str], code: str, records: list[SkillContractRecord]
) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    record_by_id = {record.skill_id: record for record in records}
    reported: set[str] = set()
    for start in sorted(edges):
        seen: set[str] = set()
        current = start
        while current in edges:
            if current in seen:
                cycle_key = min(seen)
                if cycle_key not in reported:
                    record = record_by_id.get(start)
                    findings.append(
                        ContractFinding(
                            code,
                            str(record.path) if record else "<contracts>",
                            f"successor cycle detected from {start}",
                        )
                    )
                    reported.add(cycle_key)
                break
            seen.add(current)
            current = edges[current]
    return findings


def _object(
    data: Mapping[str, Any], field: str, findings: list[ContractFinding], display_path: str
) -> Mapping[str, Any]:
    value = data.get(field)
    if not isinstance(value, dict):
        findings.append(ContractFinding("INVALID_OBJECT_FIELD", display_path, f"{field} must be an object"))
        return {}
    return value


def _string_list(data: Mapping[str, Any], field: str, findings: list[ContractFinding], display_path: str) -> list[str]:
    value = data.get(field)
    if not isinstance(value, list) or any(not _non_empty_string(item) for item in value):
        findings.append(
            ContractFinding("INVALID_STRING_LIST", display_path, f"{field} must be a list of non-empty strings")
        )
        return []
    return list(value)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _optional_full_date(value: Any, field: str, findings: list[ContractFinding], display_path: str) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        findings.append(ContractFinding("INVALID_FULL_DATE", display_path, f"{field} must be YYYY-MM-DD or null"))
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        findings.append(ContractFinding("INVALID_FULL_DATE", display_path, f"{field} must be YYYY-MM-DD"))
        return None
    if parsed.isoformat() != value:
        findings.append(ContractFinding("INVALID_FULL_DATE", display_path, f"{field} must be normalized YYYY-MM-DD"))
        return None
    return parsed


def _is_safe_relative_path(value: str, skill_directory: Path) -> bool:
    if not value or "\x00" in value:
        return False
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return False
    normalized_parts = [part for part in re.split(r"[\\/]", value) if part not in {"", "."}]
    depth = 0
    for part in normalized_parts:
        if part == "..":
            depth -= 1
            if depth < 0:
                return False
        else:
            depth += 1
    path = Path(*normalized_parts)
    try:
        candidate = (skill_directory / path).resolve()
        candidate.relative_to(skill_directory.resolve())
    except (OSError, ValueError):
        return False
    return True


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _strict_state(findings: Iterable[ContractFinding]) -> str:
    findings_tuple = tuple(findings)
    if any(finding.code in {"INVALID_CONTRACT_JSON", "SCHEMA_INVALID_JSON"} for finding in findings_tuple):
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
