from __future__ import annotations

import csv
import json
from pathlib import Path

from .chunking import read_chunks
from .inventory import repo_root
from .registry import default_registry_path, validate_registry


REQUIRED_CHUNK_FIELDS = (
    "chunk_id",
    "source_id",
    "source_priority",
    "disclosure_level",
    "evidence_label",
    "verification_status",
    "checksum",
)


def verify_artifacts(root: Path | None = None) -> dict[str, object]:
    root = repo_root(root)
    registry_path = default_registry_path(root)
    chunk_path = root / "data" / "chunks.jsonl"
    ok, errors = validate_registry(registry_path)
    warnings: list[str] = []

    if not registry_path.exists():
        return {
            "ok": False,
            "registry": registry_path.as_posix(),
            "chunks": chunk_path.as_posix(),
            "registry_records": 0,
            "chunk_count": 0,
            "unsupported_sources": [],
            "errors": errors,
            "warnings": warnings,
        }

    if not chunk_path.exists():
        errors.append(f"Chunks not found: {chunk_path}")
        return {
            "ok": False,
            "registry": registry_path.as_posix(),
            "chunks": chunk_path.as_posix(),
            "registry_records": 0,
            "chunk_count": 0,
            "unsupported_sources": [],
            "errors": errors,
            "warnings": warnings,
        }

    with registry_path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    source_ids = {row.get("source_id", "") for row in rows if row.get("source_id")}
    unsupported = [row.get("path", "") for row in rows if row.get("parse_status") == "unsupported"]
    try:
        chunks = read_chunks(chunk_path)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        errors.append(f"Could not read chunks: {exc.__class__.__name__}")
        chunks = []

    if ok and not rows:
        errors.append("Registry contains no records.")
    if not chunks:
        errors.append("Chunk index contains no chunks.")

    chunk_ids: set[str] = set()
    for index, chunk in enumerate(chunks, start=1):
        data = chunk.to_json()
        for field in REQUIRED_CHUNK_FIELDS:
            if not data.get(field):
                errors.append(f"Chunk {index} missing {field}")
        if chunk.chunk_id in chunk_ids:
            errors.append(f"Duplicate chunk_id: {chunk.chunk_id}")
        chunk_ids.add(chunk.chunk_id)
        if chunk.source_id not in source_ids:
            errors.append(f"Chunk {chunk.chunk_id} references unknown source_id: {chunk.source_id}")

    if unsupported:
        warnings.append(f"Unsupported registered sources: {len(unsupported)}")

    return {
        "ok": not errors,
        "registry": registry_path.as_posix(),
        "chunks": chunk_path.as_posix(),
        "registry_records": len(rows),
        "chunk_count": len(chunks),
        "unsupported_sources": unsupported,
        "errors": errors,
        "warnings": warnings,
    }
