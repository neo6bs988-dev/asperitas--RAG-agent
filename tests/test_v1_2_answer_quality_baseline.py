from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_v1_2_answer_quality_baseline import (
    EXPECTED_DIMENSIONS,
    FAILURE_CATEGORIES,
    FIXTURE_PATH,
    RUBRIC_PATH,
    TAXONOMY_PATH,
    validate_baseline,
    validate_fixture,
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


def test_v1_2_baseline_validator_passes():
    result = validate_baseline()

    assert result["ok"] is True, result["errors"]
    assert result["checked_files"]["rubric"] == "docs/evals/V1_2_ANSWER_QUALITY_RUBRIC.md"


def test_cli_validator_emits_json_and_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_v1_2_answer_quality_baseline.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["failure_categories"] == list(FAILURE_CATEGORIES)


def test_rubric_contains_required_dimensions_and_boundaries():
    text = RUBRIC_PATH.read_text(encoding="utf-8").lower()

    for phrase in (
        "source grounding",
        "citation accuracy",
        "retrieval fit",
        "truth-boundary",
        "compliance",
        "biosafety",
        "legal",
        "scalability",
        "moat",
    ):
        assert phrase in text


def test_failure_taxonomy_contains_required_categories():
    text = TAXONOMY_PATH.read_text(encoding="utf-8")

    for category in FAILURE_CATEGORIES:
        assert category in text


def test_fixture_schema_and_case_fields_are_valid():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert validate_fixture(payload) == []
    assert payload["measurement_only"] is True
    assert len(payload["cases"]) >= 3
    for case in payload["cases"]:
        assert case["expected_rubric_dimensions"] == list(EXPECTED_DIMENSIONS)
        assert case["source_scope"]
        assert case["required_compliance_gates"]
        assert case["failure_categories_to_watch"]


def test_fixture_does_not_reference_external_sources_or_mutate_artifacts():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    forbidden_prefixes = ("http://", "https://", "01_RAW_SOURCES/", "03_PROCESSED_KB/chunks/", "data/chunks")

    for case in payload["cases"]:
        for source in case["source_scope"]:
            assert not source.startswith(forbidden_prefixes)


def test_validator_does_not_import_runtime_answer_or_retrieval_modules():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scripts.check_v1_2_answer_quality_baseline;"
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


def test_no_source_chunk_registry_or_existing_eval_fixture_files_modified():
    before = _protected_state_snapshot()

    result = subprocess.run(
        [sys.executable, "scripts/check_v1_2_answer_quality_baseline.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    after = _protected_state_snapshot()

    assert result.returncode == 0, result.stderr
    assert after == before
