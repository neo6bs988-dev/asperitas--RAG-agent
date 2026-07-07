from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN_SET_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_golden_set.jsonl"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_labels.schema.json"

REQUIRED_CASE_CATEGORIES = (
    "source-grounding failure",
    "citation mismatch",
    "unsupported biological activity claim",
    "species/provenance missing",
    "Nagoya/CITES/LMO/biosafety/biosecurity/IP/licensing flag",
    "investor-facing overclaim",
    "human-review-required case",
)

DIAGNOSTIC_FORBIDDEN_ACTIONS = frozenset(
    {
        "runtime_blocking",
        "compliance_approval",
        "biosafety_approval",
        "legal_approval",
        "ip_approval",
        "wet_lab_validation_claim",
        "retrieval_generation_improvement_claim",
        "vector_db_kg_completion_claim",
        "production_readiness_claim",
    }
)

SOURCE_CONTEXT_FORBIDDEN_PHRASES = (
    "approved for external use",
    "biosafety approved",
    "cleared for commercial use",
    "compliance approved",
    "confirmed legal approval",
    "dual-use protocol",
    "foundation-model capability",
    "ignore previous instructions",
    "license cleared",
    "pathogen optimization",
    "production ready",
    "production-ready",
    "raw confidential source",
    "regulatory-ready",
    "safe to publish without review",
    "secret token",
    "step-by-step wet-lab",
    "unredacted confidential",
    "validated for production",
    "wet-lab validated",
)

ID_PATTERN = re.compile(r"^v1_7c_[a-z0-9_]+$")


@dataclass(frozen=True)
class ValidationReport:
    schema_path: Path
    golden_set_path: Path
    record_count: int
    covered_categories: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


class ValidationInputError(ValueError):
    pass


def load_schema(schema_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationInputError(f"schema file not found: {schema_path}") from exc
    except OSError as exc:
        raise ValidationInputError(f"schema file could not be read: {schema_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationInputError(f"schema JSON parse error at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValidationInputError("schema root must be a JSON object")
    return payload


def load_jsonl(golden_set_path: Path) -> tuple[list[tuple[int, Any]], list[str]]:
    records: list[tuple[int, Any]] = []
    errors: list[str] = []
    try:
        lines = golden_set_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return records, [f"golden-set file not found: {golden_set_path}"]
    except OSError as exc:
        return records, [f"golden-set file could not be read: {golden_set_path}: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"line {line_number}: blank lines are not valid JSONL fixture records")
            continue
        try:
            records.append((line_number, json.loads(line)))
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: JSON parse error at column {exc.colno}: {exc.msg}")
    return records, errors


def _resolve_ref(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    ref = node.get("$ref")
    if not isinstance(ref, str):
        return node
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise ValidationInputError(f"unsupported schema reference: {ref}")
    ref_name = ref.removeprefix(prefix)
    resolved = schema.get("$defs", {}).get(ref_name)
    if not isinstance(resolved, dict):
        raise ValidationInputError(f"schema reference not found: {ref}")
    return resolved


def _enum_values(schema: dict[str, Any], node: dict[str, Any]) -> frozenset[Any]:
    resolved = _resolve_ref(schema, node)
    enum_values = resolved.get("enum")
    if not isinstance(enum_values, list):
        raise ValidationInputError("schema node is missing enum values")
    return frozenset(enum_values)


def extract_allowed_labels(schema: dict[str, Any]) -> dict[str, frozenset[Any]]:
    try:
        label_properties = schema["properties"]["expected_labels"]["properties"]
    except KeyError as exc:
        raise ValidationInputError("schema is missing expected_labels properties") from exc
    if not isinstance(label_properties, dict):
        raise ValidationInputError("schema expected_labels properties must be an object")

    allowed: dict[str, frozenset[Any]] = {}
    for label_name, label_schema in label_properties.items():
        if not isinstance(label_schema, dict):
            raise ValidationInputError(f"schema for expected_labels.{label_name} must be an object")
        if label_schema.get("type") == "array":
            item_schema = label_schema.get("items")
            if not isinstance(item_schema, dict):
                raise ValidationInputError(f"schema for expected_labels.{label_name} array items must be an object")
            allowed[label_name] = _enum_values(schema, item_schema)
        else:
            allowed[label_name] = _enum_values(schema, label_schema)
    return allowed


def _schema_properties(schema: dict[str, Any], key_path: tuple[str, ...]) -> dict[str, Any]:
    node: Any = schema
    for key in key_path:
        if not isinstance(node, dict) or key not in node:
            dotted = ".".join(key_path)
            raise ValidationInputError(f"schema is missing {dotted}")
        node = node[key]
    if not isinstance(node, dict):
        dotted = ".".join(key_path)
        raise ValidationInputError(f"schema {dotted} must be an object")
    return node


def _required_fields(schema: dict[str, Any], key_path: tuple[str, ...] = ()) -> tuple[str, ...]:
    node = _schema_properties(schema, key_path) if key_path else schema
    required = node.get("required")
    if not isinstance(required, list) or not all(isinstance(field, str) for field in required):
        dotted = ".".join(key_path) if key_path else "root"
        raise ValidationInputError(f"schema {dotted} required fields must be a string list")
    return tuple(required)


def _allowed_properties(schema: dict[str, Any], key_path: tuple[str, ...] = ()) -> frozenset[str]:
    node = _schema_properties(schema, key_path) if key_path else schema
    properties = node.get("properties")
    if not isinstance(properties, dict):
        dotted = ".".join(key_path) if key_path else "root"
        raise ValidationInputError(f"schema {dotted} properties must be an object")
    return frozenset(properties)


def _string_is_present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_object_shape(
    *,
    value: Any,
    location: str,
    required: tuple[str, ...],
    allowed_properties: frozenset[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{location}: must be an object")
        return None

    missing = [field for field in required if field not in value]
    if missing:
        errors.append(f"{location}: missing required field(s): {', '.join(missing)}")

    unknown = sorted(set(value) - allowed_properties)
    if unknown:
        errors.append(f"{location}: unknown field(s): {', '.join(unknown)}")
    return value


def _validate_enum_value(
    *,
    value: Any,
    allowed: frozenset[Any],
    location: str,
    errors: list[str],
) -> None:
    if value not in allowed:
        errors.append(f"{location}: value {value!r} is not allowed by schema enum")


def _validate_string_array(
    *,
    value: Any,
    location: str,
    errors: list[str],
) -> list[str] | None:
    if not isinstance(value, list):
        errors.append(f"{location}: must be an array")
        return None
    if not value:
        errors.append(f"{location}: must contain at least one item")
        return None
    if len(value) != len(set(value)):
        errors.append(f"{location}: must not contain duplicate items")
    non_strings = [item for item in value if not _string_is_present(item)]
    if non_strings:
        errors.append(f"{location}: all items must be non-empty strings")
        return None
    return value


def _source_context_text(source_context: dict[str, Any]) -> str:
    return json.dumps(source_context, ensure_ascii=False, sort_keys=True).lower()


def _validate_source_context_phrases(source_context: dict[str, Any], location: str, errors: list[str]) -> None:
    normalized = _source_context_text(source_context)
    for phrase in SOURCE_CONTEXT_FORBIDDEN_PHRASES:
        if phrase in normalized:
            errors.append(f"{location}: source_context contains prohibited phrase {phrase!r}")


def _validate_labels(
    *,
    expected_labels: dict[str, Any],
    line_prefix: str,
    allowed_labels: dict[str, frozenset[Any]],
    errors: list[str],
) -> None:
    for label_name, allowed_values in allowed_labels.items():
        location = f"{line_prefix}.expected_labels.{label_name}"
        if label_name not in expected_labels:
            continue

        value = expected_labels[label_name]
        if label_name in {"allowed_consumer_action", "forbidden_consumer_action"}:
            items = _validate_string_array(value=value, location=location, errors=errors)
            if items is None:
                continue
            for item in items:
                _validate_enum_value(value=item, allowed=allowed_values, location=location, errors=errors)
        else:
            _validate_enum_value(value=value, allowed=allowed_values, location=location, errors=errors)

    forbidden_actions = expected_labels.get("forbidden_consumer_action")
    if isinstance(forbidden_actions, list):
        missing_forbidden = sorted(DIAGNOSTIC_FORBIDDEN_ACTIONS - set(forbidden_actions))
        if missing_forbidden:
            errors.append(
                f"{line_prefix}.expected_labels.forbidden_consumer_action: "
                f"missing diagnostic-only forbidden action(s): {', '.join(missing_forbidden)}"
            )


def validate_records(records: list[tuple[int, Any]], schema: dict[str, Any]) -> tuple[tuple[str, ...], list[str]]:
    errors: list[str] = []

    root_required = _required_fields(schema)
    root_allowed = _allowed_properties(schema)
    source_context_required = _required_fields(schema, ("properties", "source_context"))
    source_context_allowed = _allowed_properties(schema, ("properties", "source_context"))
    evidence_required = _required_fields(schema, ("properties", "required_evidence_conditions"))
    evidence_allowed = _allowed_properties(schema, ("properties", "required_evidence_conditions"))
    expected_labels_required = _required_fields(schema, ("properties", "expected_labels"))
    expected_labels_allowed = _allowed_properties(schema, ("properties", "expected_labels"))

    properties = _schema_properties(schema, ("properties",))
    case_categories = _enum_values(schema, properties["case_category"])
    claim_types = _enum_values(schema, properties["claim_type"])
    source_priorities = _enum_values(schema, properties["source_priority_expected"])
    source_context_properties = _schema_properties(schema, ("properties", "source_context", "properties"))
    source_statuses = _enum_values(schema, source_context_properties["source_status"])
    source_kinds = _enum_values(schema, source_context_properties["source_kind"])
    allowed_labels = extract_allowed_labels(schema)

    missing_required_categories = sorted(set(REQUIRED_CASE_CATEGORIES) - set(case_categories))
    if missing_required_categories:
        errors.append(f"schema case_category enum is missing required category/categories: {', '.join(missing_required_categories)}")

    if DIAGNOSTIC_FORBIDDEN_ACTIONS - allowed_labels.get("forbidden_consumer_action", frozenset()):
        missing_actions = sorted(DIAGNOSTIC_FORBIDDEN_ACTIONS - allowed_labels.get("forbidden_consumer_action", frozenset()))
        errors.append(
            "schema forbidden_consumer_action enum is missing diagnostic-only action(s): "
            + ", ".join(missing_actions)
        )

    covered_categories: set[str] = set()
    seen_ids: set[str] = set()

    for line_number, raw_record in records:
        line_prefix = f"line {line_number}"
        record = _validate_object_shape(
            value=raw_record,
            location=line_prefix,
            required=root_required,
            allowed_properties=root_allowed,
            errors=errors,
        )
        if record is None:
            continue

        record_id = record.get("id")
        if not _string_is_present(record_id) or not ID_PATTERN.fullmatch(record_id):
            errors.append(f"{line_prefix}.id: must be a non-empty v1_7c snake_case identifier")
        elif record_id in seen_ids:
            errors.append(f"{line_prefix}.id: duplicate fixture id {record_id!r}")
        else:
            seen_ids.add(record_id)

        case_category = record.get("case_category")
        _validate_enum_value(value=case_category, allowed=case_categories, location=f"{line_prefix}.case_category", errors=errors)
        if isinstance(case_category, str):
            covered_categories.add(case_category)

        _validate_enum_value(value=record.get("claim_type"), allowed=claim_types, location=f"{line_prefix}.claim_type", errors=errors)
        _validate_enum_value(
            value=record.get("source_priority_expected"),
            allowed=source_priorities,
            location=f"{line_prefix}.source_priority_expected",
            errors=errors,
        )

        for field_name in ("query", "expected_answer_status", "required_human_review_reason", "notes"):
            if field_name in record and not _string_is_present(record[field_name]):
                errors.append(f"{line_prefix}.{field_name}: must be a non-empty string")

        source_context = _validate_object_shape(
            value=record.get("source_context"),
            location=f"{line_prefix}.source_context",
            required=source_context_required,
            allowed_properties=source_context_allowed,
            errors=errors,
        )
        if source_context is not None:
            _validate_enum_value(
                value=source_context.get("source_kind"),
                allowed=source_kinds,
                location=f"{line_prefix}.source_context.source_kind",
                errors=errors,
            )
            _validate_enum_value(
                value=source_context.get("source_status"),
                allowed=source_statuses,
                location=f"{line_prefix}.source_context.source_status",
                errors=errors,
            )
            if source_context.get("source_status") != "synthetic_approved_safe":
                errors.append(f"{line_prefix}.source_context.source_status: must be synthetic_approved_safe")
            if not _string_is_present(source_context.get("summary")):
                errors.append(f"{line_prefix}.source_context.summary: must be a non-empty string")
            _validate_source_context_phrases(source_context, f"{line_prefix}.source_context", errors)

        expected_labels = _validate_object_shape(
            value=record.get("expected_labels"),
            location=f"{line_prefix}.expected_labels",
            required=expected_labels_required,
            allowed_properties=expected_labels_allowed,
            errors=errors,
        )
        if expected_labels is not None:
            _validate_labels(
                expected_labels=expected_labels,
                line_prefix=line_prefix,
                allowed_labels=allowed_labels,
                errors=errors,
            )
            if record.get("expected_answer_status") != expected_labels.get("expected_answer_status"):
                errors.append(
                    f"{line_prefix}.expected_answer_status: must match "
                    "expected_labels.expected_answer_status"
                )

        evidence_conditions = _validate_object_shape(
            value=record.get("required_evidence_conditions"),
            location=f"{line_prefix}.required_evidence_conditions",
            required=evidence_required,
            allowed_properties=evidence_allowed,
            errors=errors,
        )
        if evidence_conditions is not None:
            for key, value in evidence_conditions.items():
                if not isinstance(value, bool):
                    errors.append(f"{line_prefix}.required_evidence_conditions.{key}: must be boolean")

        forbidden_patterns = record.get("forbidden_answer_patterns")
        if "forbidden_answer_patterns" in record:
            _validate_string_array(
                value=forbidden_patterns,
                location=f"{line_prefix}.forbidden_answer_patterns",
                errors=errors,
            )

    missing_categories = sorted(set(REQUIRED_CASE_CATEGORIES) - covered_categories)
    if missing_categories:
        errors.append(f"golden set is missing required case category/categories: {', '.join(missing_categories)}")

    return tuple(category for category in REQUIRED_CASE_CATEGORIES if category in covered_categories), errors


def validate_paths(
    golden_set_path: Path = DEFAULT_GOLDEN_SET_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> ValidationReport:
    schema_path = Path(schema_path)
    golden_set_path = Path(golden_set_path)
    try:
        schema = load_schema(schema_path)
    except ValidationInputError as exc:
        return ValidationReport(
            schema_path=schema_path,
            golden_set_path=golden_set_path,
            record_count=0,
            covered_categories=(),
            errors=(str(exc),),
        )

    records, errors = load_jsonl(golden_set_path)
    covered_categories: tuple[str, ...] = ()
    if not errors:
        try:
            covered_categories, record_errors = validate_records(records, schema)
            errors.extend(record_errors)
        except ValidationInputError as exc:
            errors.append(str(exc))

    return ValidationReport(
        schema_path=schema_path,
        golden_set_path=golden_set_path,
        record_count=len(records),
        covered_categories=covered_categories,
        errors=tuple(errors),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the V1.7C biology/compliance golden-set static assets."
    )
    parser.add_argument("--golden-set", type=Path, default=DEFAULT_GOLDEN_SET_PATH, help="Path to V1.7C JSONL fixtures.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH, help="Path to the V1.7C label schema.")
    return parser


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def print_report(report: ValidationReport) -> None:
    print(f"schema: {_display_path(report.schema_path)}")
    print(f"golden_set: {_display_path(report.golden_set_path)}")
    print(f"records: {report.record_count}")
    covered = ", ".join(report.covered_categories) if report.covered_categories else "(none)"
    print(f"covered_categories: {covered}")
    print(f"result: {'PASS' if report.ok else 'FAIL'}")
    if report.errors:
        print("failures:")
        for error in report.errors:
            print(f"- {error}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = validate_paths(golden_set_path=args.golden_set, schema_path=args.schema)
    print_report(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
