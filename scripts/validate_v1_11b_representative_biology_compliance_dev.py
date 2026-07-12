from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "eval" / "v1_11b_representative_biology_compliance_dev.schema.json"
DEFAULT_FIXTURES_PATH = REPO_ROOT / "eval" / "v1_11b_representative_biology_compliance_dev.jsonl"
DEFAULT_MANIFEST_PATH = REPO_ROOT / "eval" / "v1_11b_representative_biology_compliance_dev_manifest.json"

DATASET_ID = "asperitas_representative_biology_compliance_eval"
DATASET_VERSION = "0.1.0-dev"
DATASET_STATUS = "draft_public_safe_development_only"
EXPECTED_RECORD_COUNT = 20
TRUTH_BOUNDARY = (
    "Deterministic public-safe development fixture and validation scaffold only; "
    "not protected-holdout evidence, human-approved gold, runtime behavior, or production approval."
)

EXPECTED_FAMILY_DISTRIBUTION = {
    "biodiversity_species_provenance": 2,
    "compliance_cites_nagoya_lmo_biosafety": 4,
    "genome_protein_pathway_biological_claims": 3,
    "dbtl_planning_validation_honesty": 2,
    "ip_licensing_commercial_investor_claims": 2,
    "source_grounding_citation_contradiction_reasoning": 4,
    "security_adversarial_prompt_injection_source_poisoning": 3,
}
SUPPORT_STATUS_VALUES = frozenset(
    {"supported", "unsupported", "contradicted", "insufficient", "conflicting", "not_applicable"}
)
RESPONSE_DISPOSITION_VALUES = frozenset({"answer", "answer_with_limits", "abstain", "refuse", "escalate"})
LANGUAGE_VALUES = frozenset({"ko", "en", "ko_en"})

RECORD_FIELDS = frozenset(
    {
        "dataset_id",
        "dataset_version",
        "task_id",
        "sample_id",
        "split",
        "task_family",
        "subdomain",
        "language",
        "query",
        "source_refs",
        "expected_support_status",
        "expected_response_disposition",
        "risk_class",
        "compliance_tags",
        "human_review_required",
        "review_status",
        "review_role",
        "reviewer_id_or_placeholder",
        "reviewed_at",
        "dataset_provenance",
        "change_reason",
        "adversarial_tags",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset(
    {
        "source_id",
        "source_kind",
        "source_status",
        "verification_status",
        "license_status",
        "allowed_use",
        "evidence_locator",
        "evidence_summary",
        "evidence_limitations",
    }
)
MANIFEST_FIELDS = frozenset(
    {
        "dataset_id",
        "dataset_version",
        "status",
        "public_safe_development_only",
        "protected_holdout_present",
        "expected_record_count",
        "actual_record_count",
        "expected_family_distribution",
        "language_requirements",
        "support_status_values",
        "response_disposition_values",
        "schema_path",
        "fixture_path",
        "source_policy",
        "review_policy",
        "truth_boundary",
        "generated_at_or_version_date",
        "notes",
    }
)
LANGUAGE_REQUIREMENT_FIELDS = frozenset(
    {"allowed_values", "minimum_ko", "minimum_en", "minimum_multi_sample_task_groups"}
)

FORBIDDEN_RECORD_FIELDS = frozenset(
    {
        "protected_holdout",
        "expected_source_file",
        "expected_chunk_or_section",
        "expected_answer_text",
        "answer_key_retrieval_hint",
        "runtime_route",
        "runtime_routing",
        "row_number_identity",
    }
)
FORBIDDEN_REVIEW_STATUSES = (
    "approved_gold",
    "human_review_complete",
    "legal_approved",
    "compliance_approved",
    "biosafety_approved",
    "publication_approved",
    "release_approved",
)
PRIVATE_MARKERS = (
    "protected_holdout",
    "protected-holdout",
    "private specimen",
    "private partner",
    "confidential source excerpt",
    "unpublished assay data",
    "restricted permit record",
)
INSTRUCTION_MARKERS = (
    "ignore previous instructions",
    "reveal the system prompt",
    "bypass repository policy",
    "execute this source instruction",
)
UNSAFE_BIOLOGY_PATTERNS = (
    re.compile(r"step[- ]by[- ]step.{0,80}(?:pathogen|culture|synthesi[sz]e|optimi[sz]e)", re.IGNORECASE),
    re.compile(r"단계별.{0,80}(?:병원체|배양|합성|최적화)"),
    re.compile(r"pathogen optimi[sz]ation", re.IGNORECASE),
    re.compile(r"regulatory evasion", re.IGNORECASE),
)
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
)

TASK_ID_PATTERN = re.compile(r"^v1_11_task_[a-z0-9_]+$")
SAMPLE_ID_PATTERN = re.compile(r"^v1_11_sample_[a-z0-9_]+_[0-9]{3}$")
SOURCE_ID_PATTERN = re.compile(r"^v1_11_synth_source_[a-z0-9_]+$")
EVIDENCE_LOCATOR_PATTERN = re.compile(r"^synthetic://v1_11b/[a-z0-9_/-]+#[a-z0-9_-]+$")


@dataclass(frozen=True)
class ValidationReport:
    schema_path: Path
    fixtures_path: Path
    manifest_path: Path
    dataset_id: str
    dataset_version: str
    record_count: int
    family_counts: dict[str, int]
    language_counts: dict[str, int]
    task_count: int
    sample_count: int
    multi_sample_task_groups: int
    support_status_coverage: tuple[str, ...]
    response_disposition_coverage: tuple[str, ...]
    source_eligibility_ok: bool
    review_status_ok: bool
    leakage_control_ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    truth_boundary: str = TRUTH_BOUNDARY

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "result": "PASS" if self.ok else "FAIL",
            "ok": self.ok,
            "dataset_id": self.dataset_id,
            "dataset_version": self.dataset_version,
            "record_count": self.record_count,
            "family_counts": self.family_counts,
            "language_counts": self.language_counts,
            "task_count": self.task_count,
            "sample_count": self.sample_count,
            "multi_sample_task_groups": self.multi_sample_task_groups,
            "support_status_coverage": list(self.support_status_coverage),
            "response_disposition_coverage": list(self.response_disposition_coverage),
            "source_eligibility_result": "PASS" if self.source_eligibility_ok else "FAIL",
            "review_status_result": "PASS" if self.review_status_ok else "FAIL",
            "leakage_control_result": "PASS" if self.leakage_control_ok else "FAIL",
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "truth_boundary": self.truth_boundary,
        }


@dataclass
class RecordStats:
    family_counts: Counter[str]
    language_counts: Counter[str]
    task_counts: Counter[str]
    sample_ids: set[str]
    support_statuses: set[str]
    response_dispositions: set[str]
    source_eligibility_ok: bool = True
    review_status_ok: bool = True
    leakage_control_ok: bool = True


class ValidationInputError(ValueError):
    pass


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _load_json_object(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"{label} file not found: {_display_path(path)}"]
    except OSError as exc:
        return None, [f"{label} file could not be read: {_display_path(path)}: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{label} JSON parse error at line {exc.lineno}, column {exc.colno}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"{label} root must be a JSON object"]
    return payload, []


def _load_jsonl(path: Path) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    records: list[tuple[int, dict[str, Any]]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return records, [f"fixtures file not found: {_display_path(path)}"]
    except OSError as exc:
        return records, [f"fixtures file could not be read: {_display_path(path)}: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"line {line_number}: blank lines are not valid JSONL records")
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: JSON parse error at column {exc.colno}: {exc.msg}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"line {line_number}: record must be a JSON object")
            continue
        records.append((line_number, payload))
    return records, errors


def _schema_properties(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise ValidationInputError("schema properties must be an object")
    return properties


def _schema_source_definition(schema: dict[str, Any]) -> dict[str, Any]:
    defs = schema.get("$defs")
    source_ref = defs.get("source_ref") if isinstance(defs, dict) else None
    if not isinstance(source_ref, dict):
        raise ValidationInputError("schema is missing $defs.source_ref")
    return source_ref


def _required_set(node: dict[str, Any], label: str) -> frozenset[str]:
    value = node.get("required")
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationInputError(f"{label} required fields must be a string list")
    return frozenset(value)


def _property_set(node: dict[str, Any], label: str) -> frozenset[str]:
    value = node.get("properties")
    if not isinstance(value, dict):
        raise ValidationInputError(f"{label} properties must be an object")
    return frozenset(value)


def _schema_values(properties: dict[str, Any], field: str, key: str) -> frozenset[Any]:
    node = properties.get(field)
    value = node.get(key) if isinstance(node, dict) else None
    if key == "const" and value is not None:
        return frozenset({value})
    if key == "enum" and isinstance(value, list):
        return frozenset(value)
    raise ValidationInputError(f"schema property {field!r} is missing {key}")


def _validate_schema_contract(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        properties = _schema_properties(schema)
        source_ref = _schema_source_definition(schema)
        root_required = _required_set(schema, "schema root")
        source_required = _required_set(source_ref, "schema source_ref")
        source_properties = _property_set(source_ref, "schema source_ref")
    except ValidationInputError as exc:
        return [str(exc)]

    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema must use JSON Schema draft 2020-12")
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        errors.append("schema root must be an object with additionalProperties false")
    if root_required != RECORD_FIELDS or frozenset(properties) != RECORD_FIELDS:
        errors.append("schema root required/properties must match the V1.11B record contract exactly")
    if source_ref.get("type") != "object" or source_ref.get("additionalProperties") is not False:
        errors.append("schema source_ref must be an object with additionalProperties false")
    if source_required != SOURCE_REF_FIELDS or source_properties != SOURCE_REF_FIELDS:
        errors.append("schema source_ref required/properties must match the source contract exactly")
    forbidden = sorted((set(properties) | set(source_properties)) & FORBIDDEN_RECORD_FIELDS)
    if forbidden:
        errors.append(f"schema exposes forbidden holdout/runtime field(s): {', '.join(forbidden)}")

    try:
        if _schema_values(properties, "dataset_id", "const") != {DATASET_ID}:
            errors.append("schema dataset_id const does not match the V1.11B contract")
        if _schema_values(properties, "dataset_version", "const") != {DATASET_VERSION}:
            errors.append("schema dataset_version const does not match the V1.11B contract")
        if _schema_values(properties, "split", "const") != {"development"}:
            errors.append("schema split must allow development only")
        if _schema_values(properties, "task_family", "enum") != frozenset(EXPECTED_FAMILY_DISTRIBUTION):
            errors.append("schema task_family enum does not match the required family distribution")
        if _schema_values(properties, "language", "enum") != LANGUAGE_VALUES:
            errors.append("schema language enum does not match the V1.11B contract")
        if _schema_values(properties, "expected_support_status", "enum") != SUPPORT_STATUS_VALUES:
            errors.append("schema support-status enum does not match the V1.11B contract")
        if _schema_values(properties, "expected_response_disposition", "enum") != RESPONSE_DISPOSITION_VALUES:
            errors.append("schema response-disposition enum does not match the V1.11B contract")
    except ValidationInputError as exc:
        errors.append(str(exc))
    return errors


def _normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_array(value: Any, location: str, errors: list[str], *, allow_empty: bool) -> list[str] | None:
    if not isinstance(value, list):
        errors.append(f"{location}: must be an array")
        return None
    if not allow_empty and not value:
        errors.append(f"{location}: must contain at least one item")
    if not all(_non_empty_string(item) for item in value):
        errors.append(f"{location}: all items must be non-empty strings")
        return None
    if len(value) != len(set(value)):
        errors.append(f"{location}: must not contain duplicate items")
    return value


def _scan_leakage(record: dict[str, Any], line_prefix: str, errors: list[str]) -> bool:
    ok = True
    serialized = json.dumps(record, ensure_ascii=False, sort_keys=True).casefold()
    keys = set(record)
    forbidden_fields = sorted(keys & FORBIDDEN_RECORD_FIELDS)
    if forbidden_fields:
        errors.append(f"{line_prefix}: forbidden field(s): {', '.join(forbidden_fields)}")
        ok = False
    for marker in PRIVATE_MARKERS:
        if marker.casefold() in serialized:
            errors.append(f"{line_prefix}: protected/private marker detected: {marker!r}")
            ok = False
    for marker in INSTRUCTION_MARKERS:
        if marker.casefold() in serialized:
            errors.append(f"{line_prefix}: source instruction marker detected as fixture content: {marker!r}")
            ok = False
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            errors.append(f"{line_prefix}: secret-like fixture content detected")
            ok = False
            break
    for pattern in UNSAFE_BIOLOGY_PATTERNS:
        if pattern.search(serialized):
            errors.append(f"{line_prefix}: unsafe operational biological instruction detected")
            ok = False
            break
    return ok


def _validate_source_ref(
    source: Any,
    *,
    location: str,
    source_properties: dict[str, Any],
    errors: list[str],
) -> bool:
    ok = True
    if not isinstance(source, dict):
        errors.append(f"{location}: must be an object")
        return False
    missing = sorted(SOURCE_REF_FIELDS - set(source))
    unknown = sorted(set(source) - SOURCE_REF_FIELDS)
    if missing:
        errors.append(f"{location}: missing required field(s): {', '.join(missing)}")
        ok = False
    if unknown:
        errors.append(f"{location}: unknown field(s): {', '.join(unknown)}")
        ok = False

    for field in SOURCE_REF_FIELDS:
        if field in source and not _non_empty_string(source[field]):
            errors.append(f"{location}.{field}: must be a non-empty string")
            ok = False
    source_id = source.get("source_id")
    if isinstance(source_id, str) and not SOURCE_ID_PATTERN.fullmatch(source_id):
        errors.append(f"{location}.source_id: invalid stable synthetic source ID")
        ok = False
    locator = source.get("evidence_locator")
    if isinstance(locator, str) and not EVIDENCE_LOCATOR_PATTERN.fullmatch(locator):
        errors.append(f"{location}.evidence_locator: invalid synthetic evidence locator")
        ok = False

    expected_constants = {
        "source_kind": "synthetic_public_eval_summary",
        "source_status": "synthetic_public_safe",
        "verification_status": "synthetic_fixture_verified",
        "license_status": "synthetic_fixture_public_use",
        "allowed_use": "public_test_fixture_only",
    }
    for field, expected in expected_constants.items():
        if source.get(field) != expected:
            errors.append(f"{location}.{field}: ineligible value {source.get(field)!r}; expected {expected!r}")
            ok = False
        node = source_properties.get(field)
        if not isinstance(node, dict) or node.get("const") != expected:
            errors.append(f"schema source_ref.{field}: const must be {expected!r}")
            ok = False
    return ok


def _validate_records(records: list[tuple[int, dict[str, Any]]], schema: dict[str, Any]) -> tuple[RecordStats, list[str]]:
    errors: list[str] = []
    stats = RecordStats(Counter(), Counter(), Counter(), set(), set(), set())
    properties = _schema_properties(schema)
    source_ref = _schema_source_definition(schema)
    source_properties = source_ref.get("properties")
    if not isinstance(source_properties, dict):
        raise ValidationInputError("schema source_ref properties must be an object")

    enum_fields = {
        "task_family": _schema_values(properties, "task_family", "enum"),
        "language": _schema_values(properties, "language", "enum"),
        "expected_support_status": _schema_values(properties, "expected_support_status", "enum"),
        "expected_response_disposition": _schema_values(properties, "expected_response_disposition", "enum"),
        "risk_class": _schema_values(properties, "risk_class", "enum"),
        "review_role": _schema_values(properties, "review_role", "enum"),
    }
    seen_queries: dict[str, int] = {}

    for line_number, record in records:
        line_prefix = f"line {line_number}"
        missing = sorted(RECORD_FIELDS - set(record))
        unknown = sorted(set(record) - RECORD_FIELDS)
        if missing:
            errors.append(f"{line_prefix}: missing required field(s): {', '.join(missing)}")
        if unknown:
            errors.append(f"{line_prefix}: unknown field(s): {', '.join(unknown)}")
        if not _scan_leakage(record, line_prefix, errors):
            stats.leakage_control_ok = False

        for field in (
            "dataset_id",
            "dataset_version",
            "task_id",
            "sample_id",
            "split",
            "task_family",
            "subdomain",
            "language",
            "query",
            "expected_support_status",
            "expected_response_disposition",
            "risk_class",
            "review_status",
            "review_role",
            "reviewer_id_or_placeholder",
            "dataset_provenance",
            "change_reason",
            "notes",
        ):
            if field in record and not _non_empty_string(record[field]):
                errors.append(f"{line_prefix}.{field}: must be a non-empty string")

        if record.get("dataset_id") != DATASET_ID:
            errors.append(f"{line_prefix}.dataset_id: must be {DATASET_ID!r}")
        if record.get("dataset_version") != DATASET_VERSION:
            errors.append(f"{line_prefix}.dataset_version: must be {DATASET_VERSION!r}")
        if record.get("split") != "development":
            errors.append(f"{line_prefix}.split: protected/holdout or non-development split is forbidden")
            stats.leakage_control_ok = False

        task_id = record.get("task_id")
        if isinstance(task_id, str):
            if not TASK_ID_PATTERN.fullmatch(task_id):
                errors.append(f"{line_prefix}.task_id: invalid stable task ID")
            else:
                stats.task_counts[task_id] += 1
        sample_id = record.get("sample_id")
        if isinstance(sample_id, str):
            if not SAMPLE_ID_PATTERN.fullmatch(sample_id):
                errors.append(f"{line_prefix}.sample_id: invalid stable sample ID")
            elif sample_id in stats.sample_ids:
                errors.append(f"{line_prefix}.sample_id: duplicate sample ID {sample_id!r}")
            else:
                stats.sample_ids.add(sample_id)

        query = record.get("query")
        if isinstance(query, str) and query.strip():
            normalized_query = _normalize_query(query)
            if normalized_query in seen_queries:
                errors.append(
                    f"{line_prefix}.query: duplicate normalized query; first seen at line {seen_queries[normalized_query]}"
                )
                stats.leakage_control_ok = False
            else:
                seen_queries[normalized_query] = line_number

        for field, allowed in enum_fields.items():
            if record.get(field) not in allowed:
                errors.append(f"{line_prefix}.{field}: value {record.get(field)!r} is not allowed by schema enum")
        family = record.get("task_family")
        if isinstance(family, str):
            stats.family_counts[family] += 1
        language = record.get("language")
        if isinstance(language, str):
            stats.language_counts[language] += 1
        support = record.get("expected_support_status")
        if isinstance(support, str):
            stats.support_statuses.add(support)
        disposition = record.get("expected_response_disposition")
        if isinstance(disposition, str):
            stats.response_dispositions.add(disposition)

        compliance_tags = _validate_string_array(
            record.get("compliance_tags"), f"{line_prefix}.compliance_tags", errors, allow_empty=False
        )
        adversarial_tags = _validate_string_array(
            record.get("adversarial_tags"), f"{line_prefix}.adversarial_tags", errors, allow_empty=True
        )
        if compliance_tags is None or adversarial_tags is None:
            stats.leakage_control_ok = False

        if not isinstance(record.get("human_review_required"), bool):
            errors.append(f"{line_prefix}.human_review_required: must be boolean")
        if record.get("risk_class") == "high" and record.get("human_review_required") is not True:
            errors.append(f"{line_prefix}.human_review_required: high-risk records must require human review")

        review_status = record.get("review_status")
        serialized_review = json.dumps(
            {
                "review_status": review_status,
                "reviewer_id_or_placeholder": record.get("reviewer_id_or_placeholder"),
                "reviewed_at": record.get("reviewed_at"),
            },
            ensure_ascii=False,
            sort_keys=True,
        ).casefold()
        if review_status != "draft_unreviewed":
            errors.append(f"{line_prefix}.review_status: must remain draft_unreviewed")
            stats.review_status_ok = False
        if any(status in serialized_review for status in FORBIDDEN_REVIEW_STATUSES):
            errors.append(f"{line_prefix}: forbidden approval or completed-review claim detected")
            stats.review_status_ok = False
        if record.get("reviewer_id_or_placeholder") != "unassigned_role_placeholder":
            errors.append(f"{line_prefix}.reviewer_id_or_placeholder: must use the unassigned role placeholder")
            stats.review_status_ok = False
        if record.get("reviewed_at") is not None:
            errors.append(f"{line_prefix}.reviewed_at: must be null while the record is draft/unreviewed")
            stats.review_status_ok = False
        if record.get("dataset_provenance") != "synthetic_public_safe_v1_11b_design":
            errors.append(f"{line_prefix}.dataset_provenance: must preserve the synthetic public-safe provenance")

        source_refs = record.get("source_refs")
        if not isinstance(source_refs, list) or not source_refs:
            errors.append(f"{line_prefix}.source_refs: must contain at least one synthetic source reference")
            stats.source_eligibility_ok = False
        else:
            serialized_sources: set[str] = set()
            for source_index, source in enumerate(source_refs):
                location = f"{line_prefix}.source_refs[{source_index}]"
                if not _validate_source_ref(
                    source,
                    location=location,
                    source_properties=source_properties,
                    errors=errors,
                ):
                    stats.source_eligibility_ok = False
                serialized_source = json.dumps(source, ensure_ascii=False, sort_keys=True)
                if serialized_source in serialized_sources:
                    errors.append(f"{line_prefix}.source_refs: duplicate source reference")
                    stats.source_eligibility_ok = False
                serialized_sources.add(serialized_source)

    return stats, errors


def _validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(MANIFEST_FIELDS - set(manifest))
    unknown = sorted(set(manifest) - MANIFEST_FIELDS)
    if missing:
        errors.append(f"manifest: missing required field(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"manifest: unknown field(s): {', '.join(unknown)}")

    expected_values = {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "status": DATASET_STATUS,
        "public_safe_development_only": True,
        "protected_holdout_present": False,
        "expected_record_count": EXPECTED_RECORD_COUNT,
        "actual_record_count": EXPECTED_RECORD_COUNT,
        "schema_path": "eval/v1_11b_representative_biology_compliance_dev.schema.json",
        "fixture_path": "eval/v1_11b_representative_biology_compliance_dev.jsonl",
        "truth_boundary": TRUTH_BOUNDARY,
    }
    for field, expected in expected_values.items():
        if manifest.get(field) != expected:
            errors.append(f"manifest.{field}: expected {expected!r}, got {manifest.get(field)!r}")
    if manifest.get("expected_family_distribution") != EXPECTED_FAMILY_DISTRIBUTION:
        errors.append("manifest.expected_family_distribution: does not match the required 20-case distribution")
    if set(manifest.get("support_status_values", [])) != SUPPORT_STATUS_VALUES:
        errors.append("manifest.support_status_values: does not match the required support-status values")
    if set(manifest.get("response_disposition_values", [])) != RESPONSE_DISPOSITION_VALUES:
        errors.append("manifest.response_disposition_values: does not match the required disposition values")

    language_requirements = manifest.get("language_requirements")
    if not isinstance(language_requirements, dict):
        errors.append("manifest.language_requirements: must be an object")
    else:
        missing_language = sorted(LANGUAGE_REQUIREMENT_FIELDS - set(language_requirements))
        unknown_language = sorted(set(language_requirements) - LANGUAGE_REQUIREMENT_FIELDS)
        if missing_language:
            errors.append(
                f"manifest.language_requirements: missing required field(s): {', '.join(missing_language)}"
            )
        if unknown_language:
            errors.append(f"manifest.language_requirements: unknown field(s): {', '.join(unknown_language)}")
        if set(language_requirements.get("allowed_values", [])) != LANGUAGE_VALUES:
            errors.append("manifest.language_requirements.allowed_values: must contain ko, en, and ko_en")
        for field, expected in (
            ("minimum_ko", 8),
            ("minimum_en", 8),
            ("minimum_multi_sample_task_groups", 3),
        ):
            if language_requirements.get(field) != expected:
                errors.append(f"manifest.language_requirements.{field}: expected {expected}")

    for field in ("source_policy", "review_policy", "generated_at_or_version_date", "notes"):
        if field in manifest and not _non_empty_string(manifest[field]):
            errors.append(f"manifest.{field}: must be a non-empty string")
    return errors


def _validate_alignment(records: list[tuple[int, dict[str, Any]]], stats: RecordStats, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if len(records) != EXPECTED_RECORD_COUNT:
        errors.append(f"fixtures: expected exactly {EXPECTED_RECORD_COUNT} records, got {len(records)}")
    if manifest.get("actual_record_count") != len(records):
        errors.append(
            f"manifest/record count mismatch: manifest actual_record_count={manifest.get('actual_record_count')!r}, "
            f"fixtures={len(records)}"
        )
    actual_family_counts = dict(sorted(stats.family_counts.items()))
    if actual_family_counts != EXPECTED_FAMILY_DISTRIBUTION:
        errors.append(
            "fixture family distribution mismatch: "
            + json.dumps(actual_family_counts, ensure_ascii=False, sort_keys=True)
        )
    if manifest.get("expected_family_distribution") != actual_family_counts:
        errors.append("manifest/family distribution mismatch")
    if stats.language_counts.get("ko", 0) < 8:
        errors.append(f"language coverage: expected at least 8 ko records, got {stats.language_counts.get('ko', 0)}")
    if stats.language_counts.get("en", 0) < 8:
        errors.append(f"language coverage: expected at least 8 en records, got {stats.language_counts.get('en', 0)}")
    multi_sample_task_groups = sum(count > 1 for count in stats.task_counts.values())
    if multi_sample_task_groups < 3:
        errors.append(
            f"semantic variant coverage: expected at least 3 multi-sample task groups, got {multi_sample_task_groups}"
        )
    missing_support = sorted(SUPPORT_STATUS_VALUES - stats.support_statuses)
    if missing_support:
        errors.append(f"support-status coverage missing: {', '.join(missing_support)}")
    missing_dispositions = sorted(RESPONSE_DISPOSITION_VALUES - stats.response_dispositions)
    if missing_dispositions:
        errors.append(f"response-disposition coverage missing: {', '.join(missing_dispositions)}")
    return errors


def validate_paths(
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    fixtures_path: Path = DEFAULT_FIXTURES_PATH,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> ValidationReport:
    schema_path = Path(schema_path)
    fixtures_path = Path(fixtures_path)
    manifest_path = Path(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    schema, schema_load_errors = _load_json_object(schema_path, "schema")
    manifest, manifest_load_errors = _load_json_object(manifest_path, "manifest")
    records, fixture_load_errors = _load_jsonl(fixtures_path)
    errors.extend(schema_load_errors)
    errors.extend(manifest_load_errors)
    errors.extend(fixture_load_errors)

    stats = RecordStats(Counter(), Counter(), Counter(), set(), set(), set())
    if schema is not None:
        schema_errors = _validate_schema_contract(schema)
        errors.extend(schema_errors)
        if not schema_errors:
            try:
                stats, record_errors = _validate_records(records, schema)
                errors.extend(record_errors)
            except ValidationInputError as exc:
                errors.append(str(exc))
    if manifest is not None:
        errors.extend(_validate_manifest(manifest))
        if schema is not None:
            errors.extend(_validate_alignment(records, stats, manifest))

    multi_sample_task_groups = sum(count > 1 for count in stats.task_counts.values())
    return ValidationReport(
        schema_path=schema_path,
        fixtures_path=fixtures_path,
        manifest_path=manifest_path,
        dataset_id=manifest.get("dataset_id", "") if manifest else "",
        dataset_version=manifest.get("dataset_version", "") if manifest else "",
        record_count=len(records),
        family_counts=dict(sorted(stats.family_counts.items())),
        language_counts=dict(sorted(stats.language_counts.items())),
        task_count=len(stats.task_counts),
        sample_count=len(stats.sample_ids),
        multi_sample_task_groups=multi_sample_task_groups,
        support_status_coverage=tuple(sorted(stats.support_statuses)),
        response_disposition_coverage=tuple(sorted(stats.response_dispositions)),
        source_eligibility_ok=stats.source_eligibility_ok,
        review_status_ok=stats.review_status_ok,
        leakage_control_ok=stats.leakage_control_ok,
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the V1.11B public-safe representative biology/compliance development pack."
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH, help="Path to the V1.11B JSON schema.")
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES_PATH, help="Path to the V1.11B JSONL fixtures.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Path to the V1.11B manifest.")
    parser.add_argument("--json", action="store_true", help="Emit a deterministic JSON validation report.")
    return parser


def print_human_report(report: ValidationReport) -> None:
    print(f"result: {'PASS' if report.ok else 'FAIL'}")
    print(f"dataset_id: {report.dataset_id}")
    print(f"dataset_version: {report.dataset_version}")
    print(f"schema: {_display_path(report.schema_path)}")
    print(f"fixtures: {_display_path(report.fixtures_path)}")
    print(f"manifest: {_display_path(report.manifest_path)}")
    print(f"record_count: {report.record_count}")
    print("family_counts: " + json.dumps(report.family_counts, ensure_ascii=False, sort_keys=True))
    print("language_counts: " + json.dumps(report.language_counts, ensure_ascii=False, sort_keys=True))
    print(f"task_count: {report.task_count}")
    print(f"sample_count: {report.sample_count}")
    print(f"multi_sample_task_groups: {report.multi_sample_task_groups}")
    print("support_status_coverage: " + ", ".join(report.support_status_coverage))
    print("response_disposition_coverage: " + ", ".join(report.response_disposition_coverage))
    print(f"source_eligibility_result: {'PASS' if report.source_eligibility_ok else 'FAIL'}")
    print(f"review_status_result: {'PASS' if report.review_status_ok else 'FAIL'}")
    print(f"leakage_control_result: {'PASS' if report.leakage_control_ok else 'FAIL'}")
    print(f"truth_boundary: {report.truth_boundary}")
    if report.errors:
        print("errors:")
        for error in report.errors:
            print(f"- {error}")
    else:
        print("errors: (none)")
    if report.warnings:
        print("warnings:")
        for warning in report.warnings:
            print(f"- {warning}")
    else:
        print("warnings: (none)")


def _configure_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    args = build_parser().parse_args(argv)
    report = validate_paths(args.schema, args.fixtures, args.manifest)
    if args.json:
        print(json.dumps(report.as_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print_human_report(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
