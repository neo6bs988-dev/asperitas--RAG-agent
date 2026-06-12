from __future__ import annotations

import csv
import datetime as dt
import hashlib
from pathlib import Path

from .schemas import SourceRecord


PRIORITY_DIR_RULES = {
    "P0_ACTIVE_PROMPT": ("P0", "prompt", "confidential", "internal_use", "verified_internal", "agent_development"),
    "P1_ASPERITAS_INTERNAL": ("P1", "internal", "confidential", "internal_use", "unverified", "strategy"),
    "P1_BIOLOGICAL_ASSETS": ("P1", "internal", "confidential", "internal_use", "unverified", "science"),
    "P1_COMPLIANCE_INTERNAL": ("P1", "internal", "confidential", "internal_use", "unverified", "compliance"),
    "P1_RND_PROJECTS": ("P1", "internal", "confidential", "internal_use", "unverified", "science"),
    "P2_OFFICIAL_ASPERITAS": ("P2", "official", "external_safe", "needs_review", "verified_official", "external_communication"),
    "P3_SCIENTIFIC_LITERATURE": ("P3", "paper", "external_safe", "needs_review", "externally_verified", "science"),
    "P3_SCIENCE_DATABASES": ("P3", "dataset", "external_safe", "needs_review", "externally_verified", "science"),
    "P4_REGULATORY_GOVERNMENT": ("P4", "regulatory", "external_safe", "needs_review", "needs_review", "compliance"),
    "P5_INDUSTRY_INTELLIGENCE": ("P5", "market", "internal", "needs_review", "unverified", "market"),
    "P6_BENCHMARK_OPERATING": ("P6", "benchmark", "external_safe", "needs_review", "externally_verified", "strategy"),
}


def repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "01_RAW_SOURCES").exists():
            return candidate
    return current


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sniff_file_type(path: Path) -> str:
    try:
        header = path.read_bytes()[:8]
    except OSError:
        return "unreadable"
    if header.startswith(b"%PDF"):
        return "pdf"
    if header.startswith(b"PK\x03\x04"):
        return "zip"
    if header.startswith(b"\xff\xfe") or header.startswith(b"\xfe\xff"):
        return "utf16_text"
    if b"\x00" in header:
        return "binary"
    return "text_or_binary"


def source_id_for(priority: str, checksum: str, rel_path: str) -> str:
    identity = hashlib.sha256(f"{checksum}:{rel_path}".encode("utf-8")).hexdigest()
    return f"ASP-{priority}-{identity[:12].upper()}"


def classify_source(path: Path, root: Path) -> tuple[str, str, str, str, str, str]:
    rel_parts = Path(relative_path(path, root)).parts
    for part in rel_parts:
        if part in PRIORITY_DIR_RULES:
            return PRIORITY_DIR_RULES[part]
    if path.name in {"AGENTS.md", "README.md"}:
        return ("P0", "prompt", "confidential", "internal_use", "verified_internal", "agent_development")
    if rel_parts and rel_parts[0] == "04_AGENT_SYSTEM":
        return ("P1", "internal", "confidential", "internal_use", "verified_internal", "agent_development")
    return ("P1", "internal", "confidential", "unknown", "unverified", "operations")


def discover_raw_sources(root: Path | None = None) -> list[Path]:
    root = repo_root(root)
    source_root = root / "01_RAW_SOURCES"
    if not source_root.exists():
        return []
    return sorted([p for p in source_root.rglob("*") if p.is_file()], key=lambda p: relative_path(p, root).lower())


def discover_inventory_files(root: Path | None = None) -> list[Path]:
    root = repo_root(root)
    candidates: list[Path] = []
    for rel in ("AGENTS.md", "README.md"):
        path = root / rel
        if path.exists():
            candidates.append(path)
    candidates.extend(discover_raw_sources(root))
    return sorted(set(candidates), key=lambda p: relative_path(p, root).lower())


def build_inventory(root: Path | None = None) -> list[SourceRecord]:
    root = repo_root(root)
    records: list[SourceRecord] = []
    today = dt.date.today().isoformat()
    for path in discover_inventory_files(root):
        priority, source_type, disclosure, license_status, verification, use_case = classify_source(path, root)
        checksum = sha256_file(path)
        rel_path = relative_path(path, root)
        records.append(
            SourceRecord(
                source_id=source_id_for(priority, checksum, rel_path),
                title=path.stem,
                original_filename=path.name,
                path=rel_path,
                source_priority=priority,
                source_type=source_type,
                disclosure_level=disclosure,
                license_status=license_status,
                verification_status=verification,
                date=today,
                author_or_owner="unknown",
                use_case=use_case,
                checksum=checksum,
                parse_status="not_attempted",
                notes=f"file_type={sniff_file_type(path)}",
            )
        )
    return records


def write_inventory_csv(records: list[SourceRecord], root: Path | None = None, path: Path | None = None) -> Path:
    root = repo_root(root)
    output = path or root / "00_ADMIN" / "file_inventory.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["source_id", "path", "original_filename", "checksum", "source_priority", "disclosure_level", "parse_status", "notes"]
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = record.to_row()
            writer.writerow({field: row[field] for field in fields})
    return output
