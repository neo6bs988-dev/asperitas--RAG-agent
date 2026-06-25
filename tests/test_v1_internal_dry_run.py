from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts.run_v1_internal_dry_run import build_v1_internal_dry_run_report, write_v1_internal_dry_run_report


DRY_RUN_SCRIPT = "scripts/run_v1_internal_dry_run.py"
DRY_RUN_DOC = "docs/V1_INTERNAL_DRY_RUN.md"
ROADMAP = "docs/ROADMAP.md"


def check_by_id(report, check_id):
    return next(check for check in report.checks if check.check_id == check_id)


def test_internal_dry_run_passes_with_current_modules():
    report = build_v1_internal_dry_run_report()

    assert report.status == "passed"
    assert report.summary["failed_count"] == 0


def test_readiness_check_included():
    report = build_v1_internal_dry_run_report()

    assert check_by_id(report, "release_readiness").status == "passed"


def test_clean_security_check_included():
    report = build_v1_internal_dry_run_report()

    assert check_by_id(report, "clean_security").status == "passed"


def test_prompt_injection_blocked_check_included():
    report = build_v1_internal_dry_run_report()

    check = check_by_id(report, "prompt_injection_blocked")
    assert check.status == "passed"
    assert check.metadata["risk_level"] == "blocked"


def test_chat_dry_run_check_included():
    report = build_v1_internal_dry_run_report()

    check = check_by_id(report, "chat_dry_run")
    assert check.status == "passed"
    assert check.metadata["status"] == "dry_run_ready"
    assert check.metadata["dry_run"] is True


def test_audit_serialization_check_included():
    report = build_v1_internal_dry_run_report()

    assert check_by_id(report, "audit_serialization").status == "passed"


def test_json_output_shape_stable():
    payload = build_v1_internal_dry_run_report().to_dict()

    assert tuple(payload) == ("status", "schema_version", "created_at_utc", "checks", "summary", "warnings", "errors")
    assert payload["schema_version"] == "V1.0.0-internal-dry-run"


def test_no_output_path_writes_nothing(tmp_path):
    result = subprocess.run(
        [sys.executable, DRY_RUN_SCRIPT, "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "passed"
    assert list(tmp_path.iterdir()) == []


def test_explicit_output_writes_report(tmp_path):
    output = tmp_path / "v1_internal_dry_run.json"

    written = write_v1_internal_dry_run_report(build_v1_internal_dry_run_report(), output)

    assert written == output
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


def test_overwrite_false_blocks_existing_output(tmp_path):
    output = tmp_path / "v1_internal_dry_run.json"
    output.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_v1_internal_dry_run_report(build_v1_internal_dry_run_report(), output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    output = tmp_path / "missing" / "v1_internal_dry_run.json"

    with pytest.raises(FileNotFoundError):
        write_v1_internal_dry_run_report(build_v1_internal_dry_run_report(), output, create_dirs=False)
    assert write_v1_internal_dry_run_report(build_v1_internal_dry_run_report(), output, create_dirs=True) == output


def test_script_does_not_reference_pytest_tmp():
    text = open(DRY_RUN_SCRIPT, encoding="utf-8").read()

    assert ".pytest_tmp" not in text


def test_no_imports_or_exec_of_retrieval_vector_reranker_external_connector():
    text = open(DRY_RUN_SCRIPT, encoding="utf-8").read().lower()
    for blocked_text in ("subprocess", "requests", "urllib", "http.client", "git tag", "gh release"):
        assert blocked_text not in text

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scripts.run_v1_internal_dry_run;"
                "forbidden=('asperitas_agent.rag','asperitas_agent.retrieval_tfidf',"
                "'asperitas_agent.retrieval_mvp003','asperitas_agent.embeddings',"
                "'asperitas_agent.reranking','asperitas_agent.answer_generation',"
                "'openai','langchain','langgraph','mcp');"
                "loaded=[module for module in forbidden if module in sys.modules];"
                "print(','.join(loaded));"
                "raise SystemExit(1 if loaded else 0)"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stdout


def test_docs_include_internal_only_limitation():
    text = open(DRY_RUN_DOC, encoding="utf-8").read()

    for phrase in (
        "internal dogfood only",
        "not public SaaS",
        "not production customer deployment",
        "chat remains dry-run by default",
        "no real answer provider wired",
        "security/workflow/audit gates active",
        "V1.1",
    ):
        assert phrase in text


def test_roadmap_includes_v1_1_handoff_items():
    text = open(ROADMAP, encoding="utf-8").read()

    for phrase in (
        "V1.0.0-rc1 baseline complete",
        "v1.0.0-internal pending until internal dry-run evidence passes",
        "V1.1A failure log collector",
        "V1.1B local/internal web dogfood UI",
        "V1.1C real RAG answer provider integration",
        "V1.1D retrieval/answer baseline",
    ):
        assert phrase in text
