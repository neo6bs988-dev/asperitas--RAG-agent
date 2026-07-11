from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from scripts.run_v1_2_answer_quality_eval import (
    DEFAULT_FIXTURE_PATH,
    EXPECTED_DIMENSIONS,
    FAILURE_CATEGORIES,
    build_fixture_coverage_result,
    load_fixture,
    validate_result_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTECTED_PREFIXES = (
    "00_ADMIN/source_registry",
    "01_RAW_SOURCES/",
    "03_PROCESSED_KB/chunks/",
    "04_VECTOR_DB/",
    "data/chunks.jsonl",
    "data/source_registry",
    "eval/",
    "docs/evals/V1_2_GOLDEN_EVAL_SET.json",
)
ALLOWED_PROTECTED_CHANGES = frozenset(
    {"eval/expected_sources.jsonl", "eval/retrieval_questions.jsonl"}
)


def _protected_state_snapshot() -> tuple[tuple[str, str], ...]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    protected_paths = sorted(
        {
            path
            for raw_path in (*tracked.stdout.splitlines(), *untracked.stdout.splitlines())
            if (path := raw_path.strip().replace("\\", "/"))
            and path not in ALLOWED_PROTECTED_CHANGES
            and path.startswith(PROTECTED_PREFIXES)
        }
    )
    return tuple(
        (
            path,
            hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest()
            if (REPO_ROOT / path).is_file()
            else "<missing>",
        )
        for path in protected_paths
    )


def test_runner_loads_v1_2_fixture():
    fixture = load_fixture(DEFAULT_FIXTURE_PATH)

    assert fixture["schema_version"] == "v1.2-answer-quality-baseline"
    assert fixture["measurement_only"] is True
    assert [case["id"] for case in fixture["cases"]] == [
        "v1_2_truth_boundary_status",
        "v1_2_source_priority_company_truth",
        "v1_2_biosafety_gate_dogfood",
        "v1_2_actionable_eval_followup",
    ]


def test_fixture_coverage_result_schema_is_valid():
    result = build_fixture_coverage_result()

    assert validate_result_artifact(result) == []
    assert result["baseline_type"] == "fixture_coverage_baseline"
    assert result["behavior_score_status"] == "not_yet_behavior_scored"
    assert result["answer_generation_executed"] is False
    assert result["retrieval_executed"] is False
    assert result["model_outputs_present"] is False
    assert result["summary"]["behavior_scored_case_count"] == 0
    assert len(result["cases"]) == result["summary"]["case_count"]


def test_cases_have_no_fabricated_scores_or_model_outputs():
    result = build_fixture_coverage_result()

    for case in result["cases"]:
        assert case["required_rubric_dimensions"] == list(EXPECTED_DIMENSIONS)
        assert case["answer_output_present"] is False
        assert case["scores"] is None
        assert case["failure_category_observed"] is None
        assert case["behavior_score_status"] == "not_yet_behavior_scored"
        assert case["required_compliance_gates"]
        assert set(case["failure_categories_to_watch"]) <= set(FAILURE_CATEGORIES)


def test_cli_writes_deterministic_json_artifact(tmp_path):
    output = tmp_path / "baseline_fixture_coverage.json"
    command = [
        sys.executable,
        "scripts/run_v1_2_answer_quality_eval.py",
        "--output",
        str(output),
        "--json",
    ]

    first = subprocess.run(command, check=True, capture_output=True, text=True)
    first_payload = json.loads(first.stdout)
    output.unlink()
    second = subprocess.run(command, check=True, capture_output=True, text=True)
    second_payload = json.loads(second.stdout)

    assert first_payload == second_payload
    assert json.loads(output.read_text(encoding="utf-8")) == second_payload
    assert second_payload["created_at_utc"] == "1970-01-01T00:00:00Z"


def test_committed_artifact_matches_runner_output():
    expected = build_fixture_coverage_result()
    artifact_path = "eval_results/v1_2_answer_quality_baseline/baseline_fixture_coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_v1_2_answer_quality_eval.py",
            "--output",
            artifact_path,
            "--overwrite",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    actual = json.loads(result.stdout)

    assert actual == expected


def test_scoreboard_uses_fixture_coverage_not_performance_claims():
    text = open("docs/evals/V1_2_BASELINE_SCOREBOARD.md", encoding="utf-8").read().lower()

    assert "fixture coverage baseline" in text
    assert "not answer-performance baseline" in text
    assert "not yet behavior-scored" in text
    assert "does not prove model quality" in text
    assert "v1.3" in text


def test_runner_does_not_import_runtime_answer_or_retrieval_modules():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scripts.run_v1_2_answer_quality_eval;"
                "forbidden=('asperitas_agent.rag','asperitas_agent.retrieval_tfidf',"
                "'asperitas_agent.retrieval_mvp003','asperitas_agent.embeddings',"
                "'asperitas_agent.reranking','asperitas_agent.answer_generation',"
                "'asperitas_agent.agent_runner','openai','langchain','langgraph','mcp');"
                "loaded=[module for module in forbidden if module in sys.modules];"
                "print(','.join(loaded));"
                "raise SystemExit(1 if loaded else 0)"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stdout


def test_no_source_chunk_registry_or_existing_eval_fixture_files_modified(tmp_path):
    before = _protected_state_snapshot()
    output = tmp_path / "guard_probe_fixture_coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_v1_2_answer_quality_eval.py",
            "--output",
            str(output),
            "--json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    after = _protected_state_snapshot()

    assert result.returncode == 0, result.stderr
    assert after == before
