from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.chunking import chunk_document, read_chunks, write_chunks  # noqa: E402
from asperitas_agent.inventory import classify_source, sha256_file, sniff_file_type, source_id_for  # noqa: E402
from asperitas_agent.loaders import load_documents  # noqa: E402
from asperitas_agent.registry import read_registry, write_registry  # noqa: E402
from asperitas_agent.schemas import SourceRecord  # noqa: E402
from scripts.diagnose_v1_3a_retrieval_quality import (  # noqa: E402
    DEFAULT_CHUNKS_PATH,
    DEFAULT_FIXTURE_PATH,
    DEFAULT_REGISTRY_PATH,
    build_diagnostic_result,
    load_fixture,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "eval_results" / "v1_3b_source_coverage_backfill" / "source_coverage_before_after.json"
)
SCHEMA_VERSION = "v1.3b-1-source-coverage-backfill"
BACKFILL_DATE = "2026-06-26"
BACKFILL_MARKER = "backfill=v1.3b-1_source_coverage"


def _repo_relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def expected_source_paths(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> list[str]:
    fixture = load_fixture(fixture_path)
    paths: list[str] = []
    for case in fixture["cases"]:
        for path in case.get("source_scope", []):
            normalized = str(path).replace("\\", "/")
            if normalized not in paths:
                paths.append(normalized)
    return sorted(paths, key=str.lower)


def _source_notes(file_type: str, entries: list[Any]) -> str:
    parts = [f"file_type={file_type}", BACKFILL_MARKER]
    status_counts = Counter(entry.ingestion_status for entry in entries)
    if status_counts:
        parts.append("ingest_status_counts=" + ",".join(f"{key}:{status_counts[key]}" for key in sorted(status_counts)))
    reasons = sorted({entry.reason for entry in entries if entry.reason})[:3]
    if reasons:
        parts.append("ingest_reasons=" + " | ".join(reasons))
    return "; ".join(parts)


def build_backfill_record(rel_path: str) -> SourceRecord:
    path = REPO_ROOT / rel_path
    if rel_path == "00_ADMIN/source_priority_policy.md":
        priority, source_type, disclosure, license_status, verification, use_case = (
            "P0",
            "policy",
            "confidential",
            "internal_use",
            "verified_internal",
            "agent_development",
        )
    elif rel_path == "04_AGENT_SYSTEM/guardrails/source_truth_rules.md":
        priority, source_type, disclosure, license_status, verification, use_case = (
            "P0",
            "guardrail",
            "confidential",
            "internal_use",
            "verified_internal",
            "agent_development",
        )
    else:
        priority, source_type, disclosure, license_status, verification, use_case = classify_source(path, REPO_ROOT)
    checksum = sha256_file(path)
    return SourceRecord(
        source_id=source_id_for(priority, checksum, rel_path),
        title=path.stem,
        original_filename=path.name,
        path=rel_path,
        source_priority=priority,
        source_type=source_type,
        disclosure_level=disclosure,
        license_status=license_status,
        verification_status=verification,
        date=BACKFILL_DATE,
        author_or_owner="asperitas_repo",
        use_case=use_case,
        checksum=checksum,
        parse_status="not_attempted",
        notes=f"file_type={sniff_file_type(path)}; {BACKFILL_MARKER}",
    )


def _summary_from_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    summary = dict(diagnostic["summary"])
    summary["retrieval_miss_flag_count"] = sum(len(case["retrieval_miss_flags"]) for case in diagnostic["cases"])
    summary["cases_with_all_expected_paths_represented_in_registry"] = sum(
        1
        for case in diagnostic["cases"]
        if case["registry_represented_count"] == case["source_paths_expected"]
    )
    summary["cases_with_all_expected_paths_represented_in_chunks"] = sum(
        1
        for case in diagnostic["cases"]
        if case["chunk_represented_count"] == case["source_paths_expected"]
    )
    return summary


def _case_comparison(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    before_by_id = {case["case_id"]: case for case in before["cases"]}
    rows: list[dict[str, Any]] = []
    for after_case in after["cases"]:
        before_case = before_by_id[after_case["case_id"]]
        rows.append(
            {
                "case_id": after_case["case_id"],
                "expected_source_paths": after_case["source_paths_expected"],
                "registry_represented_before": before_case["registry_represented_count"],
                "registry_represented_after": after_case["registry_represented_count"],
                "chunk_represented_before": before_case["chunk_represented_count"],
                "chunk_represented_after": after_case["chunk_represented_count"],
                "section_metadata_present_before": before_case["section_metadata_present_count"],
                "section_metadata_present_after": after_case["section_metadata_present_count"],
                "retrieval_miss_flags_before": before_case["retrieval_miss_flags"],
                "retrieval_miss_flags_after": after_case["retrieval_miss_flags"],
                "citation_candidate_available_before": before_case["citation_candidate_available"],
                "citation_candidate_available_after": after_case["citation_candidate_available"],
            }
        )
    return rows


def _is_backfill_record(record: SourceRecord) -> bool:
    return BACKFILL_MARKER in record.notes


def _pre_backfill_diagnostic(
    records: list[SourceRecord],
    chunks: list[Any],
    fixture_path: Path,
    registry_path: Path,
    chunks_path: Path,
) -> dict[str, Any]:
    backfill_source_ids = {record.source_id for record in records if _is_backfill_record(record)}
    if not backfill_source_ids:
        return build_diagnostic_result(fixture_path=fixture_path, registry_path=registry_path, chunks_path=chunks_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        filtered_registry = tmp_root / "source_registry.csv"
        filtered_chunks = tmp_root / "chunks.jsonl"
        write_registry([record for record in records if not _is_backfill_record(record)], REPO_ROOT, filtered_registry)
        write_chunks([chunk for chunk in chunks if chunk.source_id not in backfill_source_ids], REPO_ROOT, filtered_chunks)
        return build_diagnostic_result(
            fixture_path=fixture_path,
            registry_path=filtered_registry,
            chunks_path=filtered_chunks,
        )


def run_backfill(
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    chunks_path: Path = DEFAULT_CHUNKS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    overwrite: bool = False,
) -> dict[str, Any]:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"output exists, pass --overwrite: {output_path}")

    records = read_registry(registry_path)
    chunks = read_chunks(chunks_path)
    before = _pre_backfill_diagnostic(records, chunks, fixture_path, registry_path, chunks_path)
    existing_by_path = {record.path.replace("\\", "/"): record for record in records}
    backfill_source_ids = {record.source_id for record in records if _is_backfill_record(record)}
    preserved_records = [record for record in records if not _is_backfill_record(record)]
    preserved_chunks = [chunk for chunk in chunks if chunk.source_id not in backfill_source_ids]
    missing_paths = [
        path
        for path in expected_source_paths(fixture_path)
        if (path not in existing_by_path or _is_backfill_record(existing_by_path[path])) and (REPO_ROOT / path).exists()
    ]

    backfilled_sources: list[dict[str, Any]] = []
    records_to_add: list[SourceRecord] = []
    chunks_to_add = []
    for rel_path in missing_paths:
        record = build_backfill_record(rel_path)
        bundle = load_documents(record, REPO_ROOT)
        record.parse_status = bundle.source_parse_status
        record.notes = _source_notes(sniff_file_type(REPO_ROOT / rel_path), bundle.entries)
        source_chunks = []
        for document in bundle.documents:
            source_chunks.extend(chunk_document(document))
        records_to_add.append(record)
        chunks_to_add.extend(source_chunks)
        backfilled_sources.append(
            {
                "path": rel_path,
                "source_id": record.source_id,
                "source_priority": record.source_priority,
                "source_type": record.source_type,
                "disclosure_level": record.disclosure_level,
                "license_status": record.license_status,
                "verification_status": record.verification_status,
                "parse_status": record.parse_status,
                "chunk_count": len(source_chunks),
                "section_metadata_present": any(
                    chunk.section or chunk.section_heading or chunk.section_path or chunk.heading_context
                    for chunk in source_chunks
                ),
            }
        )

    if records_to_add:
        write_registry(preserved_records + records_to_add, REPO_ROOT, registry_path)
    if chunks_to_add:
        write_chunks(preserved_chunks + chunks_to_add, REPO_ROOT, chunks_path)

    after = build_diagnostic_result(fixture_path=fixture_path, registry_path=registry_path, chunks_path=chunks_path)
    result = {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": "1970-01-01T00:00:00Z",
        "fixture_path": _repo_relative(fixture_path),
        "registry_path": _repo_relative(registry_path),
        "chunks_path": _repo_relative(chunks_path),
        "diagnostic_only": False,
        "source_artifact_backfill": True,
        "retrieval_algorithm_changed": False,
        "answer_generation_changed": False,
        "external_sources_added": False,
        "backfilled_source_count": len(backfilled_sources),
        "backfilled_sources": backfilled_sources,
        "excluded_expected_sources": [
            path
            for path in expected_source_paths(fixture_path)
            if (
                path in existing_by_path
                and not _is_backfill_record(existing_by_path[path])
            )
            or not (REPO_ROOT / path).exists()
        ],
        "before_summary": _summary_from_diagnostic(before),
        "after_summary": _summary_from_diagnostic(after),
        "case_comparison": _case_comparison(before, after),
        "artifact_mutation_statement": (
            "This backfill deterministically appends existing repository governance/eval documents required by "
            "the V1.2 fixture to data/source_registry.csv and appends their generated chunks to data/chunks.jsonl "
            "using existing registry, loader, and chunking APIs."
        ),
        "truth_boundary_statement": (
            "This is a source coverage improvement only. It is not retrieval ranking calibration, not answer-quality "
            "proof, and not evidence of production deployment, legal approval, regulatory approval, biological "
            "validation, or wet-lab capability."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill V1.3B-1 source coverage for V1.2 fixture repo docs.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = run_backfill(args.fixture, args.registry, args.chunks, args.output, args.overwrite)
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
