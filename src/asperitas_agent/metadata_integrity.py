from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .chunking import read_chunks
from .registry import read_registry
from .schemas import Chunk, SourceRecord


RISK_DERIVABLE = "derivable"
RISK_NOT_DERIVABLE = "not_derivable"
RISK_SOURCE_FORMAT_LIMITATION = "source-format limitation"
RISK_PARSER_LIMITATION = "parser limitation"
RISK_DUPLICATE_SOURCE_AMBIGUITY = "duplicate-source ambiguity"
RISK_REQUIRES_FUTURE_UPGRADE = "requires future ingestion/parser upgrade"

_NOTE_PART_RE = re.compile(r"\s*([^=;]+)=([^;]*)")


@dataclass(frozen=True)
class MetadataGapExample:
    chunk_id: str
    source_id: str
    source_file: str
    title: str
    source_priority: str
    source_type: str
    extension: str
    parser: str
    chunker: str
    char_start: int
    has_path_context: bool
    path_context: list[str]
    risk_classification: str
    safely_derivable_section: str
    derivation_basis: str
    text_preview: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _has_section_metadata(chunk: Chunk) -> bool:
    return bool(chunk.section or chunk.section_heading or chunk.heading_context or chunk.section_path)


def _parse_notes(notes: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in notes.split(";"):
        match = _NOTE_PART_RE.fullmatch(part.strip())
        if match:
            parsed[match.group(1).strip()] = match.group(2).strip()
    return parsed


def _extension(record: SourceRecord | None) -> str:
    if record is None:
        return "unknown"
    suffix = Path(record.path or record.original_filename).suffix.lower()
    return suffix.lstrip(".") or "unknown"


def _source_file(record: SourceRecord | None, chunk: Chunk) -> str:
    if record and record.path:
        return record.path
    return chunk.source_id


def _path_context(record: SourceRecord | None) -> list[str]:
    if record is None or not record.path:
        return []
    path = Path(record.path)
    return [part for part in path.parts[:-1] if part and part != "."]


def _parser(record: SourceRecord | None) -> str:
    if record is None:
        return "unknown"
    notes = _parse_notes(record.notes)
    return notes.get("ingest_reasons") or notes.get("file_type") or record.parse_status or "unknown"


def _chunker(chunk: Chunk) -> str:
    if "::chunk-" in chunk.chunk_id:
        return "fixed_window_section_marker"
    return "unknown"


def _safe_title_section(record: SourceRecord | None, chunk: Chunk) -> tuple[str, str]:
    if chunk.char_start != 0:
        return "", ""
    title = (record.title if record else chunk.title).strip()
    if not title:
        return "", ""
    return title, "source title for first chunk only"


def _classify_missing(chunk: Chunk, record: SourceRecord | None, duplicate_source_ids: set[str]) -> tuple[str, str, str]:
    if chunk.source_id in duplicate_source_ids:
        return RISK_DUPLICATE_SOURCE_AMBIGUITY, "", ""
    derived, basis = _safe_title_section(record, chunk)
    if derived:
        return RISK_DERIVABLE, derived, basis
    if record is None:
        return RISK_NOT_DERIVABLE, "", ""
    ext = _extension(record)
    parser = _parser(record)
    if record.parse_status != "parsed":
        return RISK_PARSER_LIMITATION, "", ""
    if ext in {"pdf", "pptx", "docx", "hwpx"}:
        return RISK_SOURCE_FORMAT_LIMITATION, "", ""
    if ext in {"md", "txt"}:
        return RISK_NOT_DERIVABLE, "", ""
    if "pypdf" in parser or "pdf" in parser:
        return RISK_SOURCE_FORMAT_LIMITATION, "", ""
    return RISK_REQUIRES_FUTURE_UPGRADE, "", ""


def _counter_to_sorted_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _count_missing_by(
    missing: list[Chunk],
    records_by_id: dict[str, SourceRecord],
    value_func,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for chunk in missing:
        counts[value_func(chunk, records_by_id.get(chunk.source_id))] += 1
    return _counter_to_sorted_dict(counts)


def audit_metadata_integrity(
    chunks_path: Path,
    registry_path: Path,
    *,
    example_limit: int = 20,
) -> dict[str, Any]:
    chunks = read_chunks(chunks_path)
    records = read_registry(registry_path)
    records_by_id = {record.source_id: record for record in records}
    source_id_counts = Counter(record.source_id for record in records)
    duplicate_source_ids = {source_id for source_id, count in source_id_counts.items() if count > 1}

    with_section = [chunk for chunk in chunks if _has_section_metadata(chunk)]
    missing = [chunk for chunk in chunks if not _has_section_metadata(chunk)]

    examples: list[MetadataGapExample] = []
    risk_counts: Counter[str] = Counter()
    derivable_count = 0
    path_context_counts: Counter[str] = Counter()
    missing_by_parser: Counter[str] = Counter()
    missing_by_chunker: Counter[str] = Counter()

    for chunk in missing:
        record = records_by_id.get(chunk.source_id)
        path_context = _path_context(record)
        risk, derived, basis = _classify_missing(chunk, record, duplicate_source_ids)
        risk_counts[risk] += 1
        if derived:
            derivable_count += 1
        path_context_counts["present" if path_context else "missing"] += 1
        parser = _parser(record)
        chunker = _chunker(chunk)
        missing_by_parser[parser] += 1
        missing_by_chunker[chunker] += 1
        if len(examples) < example_limit:
            examples.append(
                MetadataGapExample(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    source_file=_source_file(record, chunk),
                    title=chunk.title,
                    source_priority=chunk.source_priority,
                    source_type=chunk.source_type,
                    extension=_extension(record),
                    parser=parser,
                    chunker=chunker,
                    char_start=chunk.char_start,
                    has_path_context=bool(path_context),
                    path_context=path_context,
                    risk_classification=risk,
                    safely_derivable_section=derived,
                    derivation_basis=basis,
                    text_preview=" ".join(chunk.text.split())[:220],
                )
            )

    missing_by_source_file = _count_missing_by(missing, records_by_id, lambda chunk, record: _source_file(record, chunk))
    missing_by_source_id = _count_missing_by(missing, records_by_id, lambda chunk, record: chunk.source_id)
    missing_by_extension = _count_missing_by(missing, records_by_id, lambda chunk, record: _extension(record))
    missing_by_priority = _count_missing_by(missing, records_by_id, lambda chunk, record: chunk.source_priority or "unknown")
    missing_by_type = _count_missing_by(missing, records_by_id, lambda chunk, record: chunk.source_type or "unknown")

    unresolved = len(missing) - derivable_count
    return {
        "chunks_path": chunks_path.as_posix(),
        "registry_path": registry_path.as_posix(),
        "total_chunks": len(chunks),
        "chunks_with_section": len(with_section),
        "chunks_missing_section": len(missing),
        "missing_section_rate": round((len(missing) / len(chunks)) if chunks else 0.0, 6),
        "safe_repair_policy": {
            "artifact_mutation": False,
            "derivation_rule": "Only first chunks may report a safely derivable title-based section candidate; existing chunk artifacts are not rewritten.",
            "no_invented_metadata": True,
        },
        "derivable_missing_count": derivable_count,
        "unresolved_missing_count": unresolved,
        "missing_count_by_source_file": missing_by_source_file,
        "missing_count_by_source_id": missing_by_source_id,
        "missing_count_by_extension": missing_by_extension,
        "missing_count_by_type": missing_by_type,
        "missing_count_by_priority": missing_by_priority,
        "missing_count_by_parser": _counter_to_sorted_dict(missing_by_parser),
        "missing_count_by_chunker": _counter_to_sorted_dict(missing_by_chunker),
        "missing_count_by_path_context_availability": _counter_to_sorted_dict(path_context_counts),
        "risk_classification_counts": _counter_to_sorted_dict(risk_counts),
        "duplicate_source_ids": sorted(duplicate_source_ids),
        "examples_of_missing_chunks": [example.to_json() for example in examples],
    }


def summarize_metadata_integrity(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Metadata Integrity Audit",
            f"Chunks: {report['total_chunks']}",
            f"With section metadata: {report['chunks_with_section']}",
            f"Missing section metadata: {report['chunks_missing_section']}",
            f"Missing-section rate: {report['missing_section_rate']:.2%}",
            f"Safely derivable candidates: {report['derivable_missing_count']}",
            f"Unresolved missing: {report['unresolved_missing_count']}",
            "Risk classes:",
            *[
                f"- {risk}: {count}"
                for risk, count in report["risk_classification_counts"].items()
            ],
        ]
    )
