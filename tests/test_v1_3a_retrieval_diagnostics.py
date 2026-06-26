from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.diagnose_v1_3a_retrieval_quality import (
    DEFAULT_FIXTURE_PATH,
    SCHEMA_VERSION,
    build_diagnostic_result,
    load_fixture,
)


def test_loads_v1_2_golden_eval_cases():
    fixture = load_fixture(DEFAULT_FIXTURE_PATH)

    assert fixture["schema_version"] == "v1.2-answer-quality-baseline"
    assert [case["id"] for case in fixture["cases"]] == [
        "v1_2_truth_boundary_status",
        "v1_2_source_priority_company_truth",
        "v1_2_biosafety_gate_dogfood",
        "v1_2_actionable_eval_followup",
    ]


def test_diagnostic_output_schema_and_non_mutation_flags():
    result = build_diagnostic_result()

    assert result["schema_version"] == SCHEMA_VERSION
    assert result["diagnostic_only"] is True
    assert result["answer_generation_executed"] is False
    assert result["retrieval_behavior_changed"] is False
    assert result["registry_or_chunk_mutation"] is False
    assert result["summary"]["case_count"] == len(result["cases"])
    for case in result["cases"]:
        assert set(
            [
                "case_id",
                "question",
                "expected_source_scope",
                "expected_sources",
                "retrieval_execution_available",
                "diagnostic_status",
                "retrieved",
                "retrieval_miss_flags",
                "wrong_source_priority_flags",
                "citation_candidate_available",
            ]
        ) <= set(case)


def test_source_path_existence_checks_are_reported():
    result = build_diagnostic_result()

    by_case = {case["case_id"]: case for case in result["cases"]}
    truth_case = by_case["v1_2_truth_boundary_status"]
    paths = {row["path"]: row["exists"] for row in truth_case["expected_sources"]}

    assert paths["docs/V1_KNOWN_LIMITATIONS.md"] is True
    assert paths["docs/V1_RELEASE_CLOSEOUT.md"] is True
    assert paths["docs/EVALS.md"] is True


def test_missing_artifacts_record_retrieval_unavailable(tmp_path: Path):
    result = build_diagnostic_result(
        fixture_path=DEFAULT_FIXTURE_PATH,
        registry_path=tmp_path / "missing_registry.csv",
        chunks_path=tmp_path / "missing_chunks.jsonl",
    )

    assert result["retrieval_execution_available"] is False
    assert result["retrieval_execution_status"] == "retrieval_execution_not_available"
    assert {case["diagnostic_status"] for case in result["cases"]} == {"retrieval_execution_not_available"}
    assert all(case["retrieved"] == [] for case in result["cases"])


def test_cli_writes_deterministic_json(tmp_path: Path):
    output = tmp_path / "retrieval_diagnostic_baseline.json"
    command = [
        sys.executable,
        "scripts/diagnose_v1_3a_retrieval_quality.py",
        "--output",
        str(output),
        "--overwrite",
        "--json",
    ]

    first = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    second = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")

    assert json.loads(first.stdout) == json.loads(second.stdout)
    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(second.stdout)
    assert json.loads(second.stdout)["created_at_utc"] == "1970-01-01T00:00:00Z"


def test_no_source_chunk_registry_or_existing_eval_fixture_files_modified():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    protected_prefixes = (
        "00_ADMIN/source_registry",
        "01_RAW_SOURCES/",
        "03_PROCESSED_KB/chunks/",
        "04_VECTOR_DB/",
        "data/chunks.jsonl",
        "data/source_registry",
        "eval/",
        "docs/evals/V1_2_GOLDEN_EVAL_SET.json",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path.startswith(protected_prefixes)]
