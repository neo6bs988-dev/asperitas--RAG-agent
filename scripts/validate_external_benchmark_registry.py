from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "00_ADMIN/source_registries/external_benchmark_source_registry.csv"
DEFAULT_SCHEMA = ROOT / "00_ADMIN/source_registries/external_benchmark_source_registry.schema.json"
DEFAULT_CANONICAL_SCHEMA = ROOT / "00_ADMIN/metadata_schema.yaml"

LIST_FIELDS = ("risk_flags", "allowed_use_cases", "prohibited_use_cases")
CANONICAL_ENUM_FIELDS = (
    "source_priority",
    "source_type",
    "disclosure_level",
    "origin",
    "jurisdiction",
    "license_status",
    "verification_status",
    "ingestion_status",
    "evidence_label",
    "risk_flags",
    "allowed_use_cases",
)


def _strip_scalar(value: str) -> str:
    clean = value.strip()
    if len(clean) >= 2 and clean[0] == clean[-1] and clean[0] in {"'", '"'}:
        return clean[1:-1].strip()
    return clean


def _parse_inline_list(value: str) -> list[str]:
    return [_strip_scalar(item) for item in value.split(",") if _strip_scalar(item)]


def parse_canonical_enum_values(path: Path) -> dict[str, set[str]]:
    """Parse the small enum subset used by 00_ADMIN/metadata_schema.yaml.

    The repository intentionally avoids adding a YAML dependency for this
    validator. This parser supports the current canonical schema's inline list
    and indented list forms and fails closed when a required enum cannot be
    resolved.
    """

    values: dict[str, set[str]] = {}
    current_field: str | None = None
    collecting_multiline = False
    in_required_fields = False

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        if raw_line == "required_fields:":
            in_required_fields = True
            current_field = None
            collecting_multiline = False
            continue

        if in_required_fields and raw_line and not raw_line.startswith(" "):
            break

        if not in_required_fields:
            continue

        field_match = re.match(r"^  ([A-Za-z0-9_]+):\s*$", raw_line)
        if field_match:
            current_field = field_match.group(1)
            collecting_multiline = False
            continue

        if current_field is None:
            continue

        inline_match = re.match(r"^    values:\s*\[(.*)\]\s*$", raw_line)
        if inline_match:
            values[current_field] = set(_parse_inline_list(inline_match.group(1)))
            collecting_multiline = False
            continue

        if re.match(r"^    values:\s*$", raw_line):
            values[current_field] = set()
            collecting_multiline = True
            continue

        if collecting_multiline:
            item_match = re.match(r"^      -\s+(.+?)\s*$", raw_line)
            if item_match:
                values[current_field].add(_strip_scalar(item_match.group(1)))
            elif raw_line.startswith("    ") and raw_line.strip():
                collecting_multiline = False

    return values


def _split_list(value: str, separator: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(separator) if item.strip())


def _valid_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return header, rows


def validate_registry(
    registry_path: Path = DEFAULT_REGISTRY,
    schema_path: Path = DEFAULT_SCHEMA,
    canonical_schema_path: Path = DEFAULT_CANONICAL_SCHEMA,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for label, path in (
        ("registry", registry_path),
        ("registry schema", schema_path),
        ("canonical metadata schema", canonical_schema_path),
    ):
        if not path.is_file():
            errors.append(f"missing {label}: {path.as_posix()}")

    if errors:
        return {
            "ok": False,
            "record_count": 0,
            "errors": errors,
            "warnings": warnings,
        }

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "record_count": 0,
            "errors": [f"invalid registry schema: {exc}"],
            "warnings": warnings,
        }

    required_fields = schema.get("required_fields")
    allowed_values = schema.get("allowed_values")
    list_separator = schema.get("list_separator")
    canonical_topology = schema.get("canonical_benchmark_topology")

    if not isinstance(required_fields, list) or not required_fields:
        errors.append("schema.required_fields must be a non-empty list")
        required_fields = []
    if not isinstance(allowed_values, dict):
        errors.append("schema.allowed_values must be an object")
        allowed_values = {}
    if not isinstance(list_separator, str) or len(list_separator) != 1:
        errors.append("schema.list_separator must be one character")
        list_separator = "|"
    if not isinstance(canonical_topology, str) or not canonical_topology:
        errors.append("schema.canonical_benchmark_topology is required")
        canonical_topology = "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/"

    header, rows = _load_rows(registry_path)
    if header != required_fields:
        errors.append("registry header does not exactly match schema.required_fields")
    if not rows:
        errors.append("registry must contain at least one metadata record")

    canonical_values = parse_canonical_enum_values(canonical_schema_path)
    for field in CANONICAL_ENUM_FIELDS:
        local_values = set(allowed_values.get(field, []))
        upstream_values = canonical_values.get(field, set())
        if not upstream_values:
            errors.append(f"canonical enum could not be resolved: {field}")
        elif not local_values:
            errors.append(f"registry schema enum is missing: {field}")
        elif not local_values <= upstream_values:
            invalid = sorted(local_values - upstream_values)
            errors.append(f"registry schema enum is outside canonical metadata schema for {field}: {invalid}")

    source_ids: set[str] = set()
    source_urls: set[str] = set()

    for row_number, row in enumerate(rows, start=2):
        for field in required_fields:
            if not str(row.get(field, "")).strip():
                errors.append(f"row {row_number}: required field is empty: {field}")

        for field, valid_values in allowed_values.items():
            if field not in row:
                continue
            valid_set = set(valid_values)
            if field in LIST_FIELDS:
                parsed_values = _split_list(row[field], list_separator)
                if not parsed_values:
                    errors.append(f"row {row_number}: list field is empty: {field}")
                invalid_values = sorted(set(parsed_values) - valid_set)
                if invalid_values:
                    errors.append(f"row {row_number}: invalid {field}: {invalid_values}")
            elif row[field] not in valid_set:
                errors.append(f"row {row_number}: invalid {field}: {row[field]!r}")

        source_id = row.get("source_id", "")
        if source_id in source_ids:
            errors.append(f"row {row_number}: duplicate source_id: {source_id}")
        source_ids.add(source_id)

        source_url = row.get("source_url", "")
        if not _valid_https_url(source_url):
            errors.append(f"row {row_number}: source_url must be an absolute HTTPS URL")
        if source_url in source_urls:
            errors.append(f"row {row_number}: duplicate source_url: {source_url}")
        source_urls.add(source_url)

        provenance = row.get("provenance", "")
        if not provenance.startswith(canonical_topology):
            errors.append(f"row {row_number}: provenance must use canonical benchmark topology")
        if "P6_EXTERNAL_BENCHMARK/" in provenance:
            errors.append(f"row {row_number}: singular legacy benchmark topology is forbidden")

        if row.get("source_priority") == "P5" and row.get("source_family") != "ai_bio_platform_benchmark":
            errors.append(f"row {row_number}: P5 records must be AI-bio platform benchmarks")
        if row.get("source_family") == "ai_bio_platform_benchmark" and row.get("source_priority") != "P5":
            errors.append(f"row {row_number}: AI-bio platform benchmarks must use P5")

        if row.get("ingestion_status") != "registered":
            errors.append(f"row {row_number}: metadata-only registry requires ingestion_status=registered")
        if row.get("verification_status") != "needs_external_verification":
            errors.append(
                f"row {row_number}: candidate URL metadata requires verification_status=needs_external_verification"
            )
        if row.get("license_status") != "needs_review":
            errors.append(f"row {row_number}: unreviewed external source requires license_status=needs_review")
        if row.get("notes") != "url_inherited_from_current_main_manifest_external_content_not_refetched":
            warnings.append(f"row {row_number}: review notes before promoting or ingesting this candidate")

    invariants = schema.get("invariants", {})
    required_false = (
        "raw_acquisition_performed",
        "processing_performed",
        "chunking_performed",
        "embedding_performed",
        "indexing_performed",
        "evaluation_performed",
        "production_ingestion_allowed",
    )
    if invariants.get("metadata_only") is not True:
        errors.append("schema invariant metadata_only must be true")
    for invariant in required_false:
        if invariants.get(invariant) is not False:
            errors.append(f"schema invariant must be false: {invariant}")

    return {
        "ok": not errors,
        "record_count": len(rows),
        "registry": registry_path.relative_to(ROOT).as_posix(),
        "schema": schema_path.relative_to(ROOT).as_posix(),
        "canonical_schema": canonical_schema_path.relative_to(ROOT).as_posix(),
        "errors": errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the metadata-only external benchmark registry v2")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--canonical-schema", type=Path, default=DEFAULT_CANONICAL_SCHEMA)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = validate_registry(args.registry, args.schema, args.canonical_schema)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
