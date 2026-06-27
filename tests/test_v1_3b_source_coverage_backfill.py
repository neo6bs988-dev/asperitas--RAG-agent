from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from scripts.backfill_v1_3b_source_coverage import (
    SCHEMA_VERSION,
    build_backfill_record,
    expected_source_paths,
    run_backfill,
)


def _copy_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    registry = tmp_path / "source_registry.csv"
    chunks = tmp_path / "chunks.jsonl"
    registry.write_bytes(Path("data/source_registry.csv").read_bytes())
    chunks.write_bytes(Path("data/chunks.jsonl").read_bytes())
    return registry, chunks


def _copy_pre_backfill_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    registry, chunks = _copy_artifacts(tmp_path)
    expected_missing = set(expected_source_paths()) - {"AGENTS.md"}
    with registry.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames
    removed_source_ids = {row["source_id"] for row in rows if row["path"] in expected_missing}
    kept_rows = [row for row in rows if row["path"] not in expected_missing]
    with registry.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

    kept_chunk_lines = []
    for line in chunks.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("source_id") not in removed_source_ids:
            kept_chunk_lines.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
    chunks.write_text("\n".join(kept_chunk_lines) + "\n", encoding="utf-8")
    return registry, chunks


def test_expected_source_paths_are_v1_2_fixture_scope_only():
    paths = expected_source_paths()

    assert len(paths) == 10
    assert "AGENTS.md" in paths
    assert "docs/evals/V1_2_ANSWER_QUALITY_RUBRIC.md" in paths
    assert "04_AGENT_SYSTEM/guardrails/biosafety_compliance_checklist.md" in paths


def test_backfill_record_preserves_governance_priority_override():
    record = build_backfill_record("04_AGENT_SYSTEM/guardrails/source_truth_rules.md")

    assert record.source_priority == "P0"
    assert record.source_type == "guardrail"
    assert record.disclosure_level == "confidential"
    assert record.verification_status == "verified_internal"
    assert record.parse_status == "not_attempted"


def test_backfill_is_deterministic_and_improves_tmp_artifacts(tmp_path: Path):
    first_registry, first_chunks = _copy_pre_backfill_artifacts(tmp_path / "first")
    second_registry, second_chunks = _copy_pre_backfill_artifacts(tmp_path / "second")
    output_one = tmp_path / "first.json"
    output_two = tmp_path / "second.json"

    first = run_backfill(registry_path=first_registry, chunks_path=first_chunks, output_path=output_one, overwrite=True)
    second = run_backfill(registry_path=second_registry, chunks_path=second_chunks, output_path=output_two, overwrite=True)

    assert first["schema_version"] == SCHEMA_VERSION
    assert first["backfilled_source_count"] == 9
    assert first["before_summary"]["registry_represented_source_count"] == 1
    assert first["after_summary"]["registry_represented_source_count"] == 12
    assert first["after_summary"]["chunk_represented_source_count"] == 12
    assert first_registry.read_bytes() == second_registry.read_bytes()
    assert first_chunks.read_bytes() == second_chunks.read_bytes()


def test_backfilled_registry_schema_and_paths_are_valid(tmp_path: Path):
    registry, chunks = _copy_pre_backfill_artifacts(tmp_path)
    run_backfill(registry_path=registry, chunks_path=chunks, output_path=tmp_path / "report.json", overwrite=True)

    with registry.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    by_path = {row["path"]: row for row in rows}

    for path in expected_source_paths():
        assert path in by_path
        assert by_path[path]["source_id"]
        assert by_path[path]["source_priority"]
        assert by_path[path]["disclosure_level"]
        assert by_path[path]["parse_status"] in {"parsed", "partial", "failed", "unsupported"}


def test_report_avoids_forbidden_overclaim_language():
    text = Path("docs/evals/V1_3B_SOURCE_COVERAGE_BACKFILL_REPORT.md").read_text(encoding="utf-8").lower()

    forbidden = (
        "proves answer quality",
        "production deployed",
        "legal approval achieved",
        "regulatory approval achieved",
        "biologically validated",
        "wet-lab capability",
    )
    assert not [phrase for phrase in forbidden if phrase in text]


def test_no_retrieval_or_answer_generation_source_changed():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    protected = (
        "src/asperitas_agent/retrieval_mvp003.py",
        "src/asperitas_agent/retrieval_tfidf.py",
        "src/asperitas_agent/reranking.py",
        "src/asperitas_agent/rag.py",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path in protected]


def test_cli_writes_json_report_for_tmp_artifacts(tmp_path: Path):
    registry, chunks = _copy_artifacts(tmp_path)
    output = tmp_path / "source_coverage_before_after.json"
    command = [
        sys.executable,
        "scripts/backfill_v1_3b_source_coverage.py",
        "--registry",
        str(registry),
        "--chunks",
        str(chunks),
        "--output",
        str(output),
        "--overwrite",
        "--json",
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    payload = json.loads(completed.stdout)

    assert payload == json.loads(output.read_text(encoding="utf-8"))
    assert payload["created_at_utc"] == "1970-01-01T00:00:00Z"
