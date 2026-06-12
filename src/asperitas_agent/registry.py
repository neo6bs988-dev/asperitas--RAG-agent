from __future__ import annotations

import csv
import re
from pathlib import Path

from .inventory import build_inventory, repo_root
from .schemas import (
    DISCLOSURE_LEVELS,
    LICENSE_STATUSES,
    PARSE_STATUSES,
    REGISTRY_COLUMNS,
    SOURCE_PRIORITIES,
    VERIFICATION_STATUSES,
    SourceRecord,
)


CHECKSUM_RE = re.compile(r"^[0-9a-f]{64}$")


def default_registry_path(root: Path | None = None) -> Path:
    root = repo_root(root)
    return root / "data" / "source_registry.csv"


def write_registry(records: list[SourceRecord], root: Path | None = None, path: Path | None = None) -> Path:
    output = path or default_registry_path(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())
    return output


def read_registry(path: Path) -> list[SourceRecord]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [SourceRecord(**{column: row.get(column, "") for column in REGISTRY_COLUMNS}) for row in csv.DictReader(handle)]


def validate_registry(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"Registry not found: {path}"]
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = [column for column in REGISTRY_COLUMNS if column not in columns]
        errors = [f"Missing required column: {column}" for column in missing]
        seen_source_ids: set[str] = set()
        seen_paths: set[str] = set()
        for index, row in enumerate(reader, start=2):
            for column in REGISTRY_COLUMNS:
                if column not in row:
                    continue
                if column in {"source_id", "path", "source_priority", "disclosure_level", "checksum"} and not row[column]:
                    errors.append(f"Row {index} missing {column}")
            source_id = row.get("source_id", "")
            rel_path = row.get("path", "")
            if source_id:
                if source_id in seen_source_ids:
                    errors.append(f"Row {index} duplicate source_id: {source_id}")
                seen_source_ids.add(source_id)
            if rel_path:
                if Path(rel_path).is_absolute() or "\\" in rel_path or rel_path.startswith("../") or "/../" in rel_path:
                    errors.append(f"Row {index} unsafe relative path: {rel_path}")
                if rel_path in seen_paths:
                    errors.append(f"Row {index} duplicate path: {rel_path}")
                seen_paths.add(rel_path)
            if row.get("source_priority") and row["source_priority"] not in SOURCE_PRIORITIES:
                errors.append(f"Row {index} invalid source_priority: {row['source_priority']}")
            if row.get("disclosure_level") and row["disclosure_level"] not in DISCLOSURE_LEVELS:
                errors.append(f"Row {index} invalid disclosure_level: {row['disclosure_level']}")
            if row.get("license_status") and row["license_status"] not in LICENSE_STATUSES:
                errors.append(f"Row {index} invalid license_status: {row['license_status']}")
            if row.get("verification_status") and row["verification_status"] not in VERIFICATION_STATUSES:
                errors.append(f"Row {index} invalid verification_status: {row['verification_status']}")
            if row.get("parse_status") and row["parse_status"] not in PARSE_STATUSES:
                errors.append(f"Row {index} invalid parse_status: {row['parse_status']}")
            if row.get("checksum") and not CHECKSUM_RE.match(row["checksum"]):
                errors.append(f"Row {index} invalid checksum")
    return not errors, errors


def ensure_registry(root: Path | None = None) -> Path:
    root = repo_root(root)
    path = default_registry_path(root)
    if not path.exists():
        write_registry(build_inventory(root), root, path)
    return path
