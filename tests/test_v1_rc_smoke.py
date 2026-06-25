from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts.run_v1_rc_smoke import build_v1_rc_smoke_report, write_v1_rc_smoke_report


RELEASE_NOTES = "docs/releases/V1_0_0_RC1_RELEASE_NOTES.md"
MANUAL_STEPS = "docs/releases/V1_0_0_RC1_MANUAL_RELEASE_STEPS.md"
SMOKE_SCRIPT = "scripts/run_v1_rc_smoke.py"


def check_by_id(report, check_id):
    return next(check for check in report.checks if check.check_id == check_id)


def test_smoke_script_passes_with_current_modules():
    report = build_v1_rc_smoke_report()

    assert report.status == "passed"
    assert report.summary["failed_count"] == 0


def test_readiness_check_included():
    report = build_v1_rc_smoke_report()

    assert check_by_id(report, "release_readiness").status == "passed"


def test_clean_security_check_included():
    report = build_v1_rc_smoke_report()

    assert check_by_id(report, "clean_security").status == "passed"


def test_blocked_security_check_included():
    report = build_v1_rc_smoke_report()

    assert check_by_id(report, "blocked_security").status == "passed"


def test_chat_dry_run_check_included():
    report = build_v1_rc_smoke_report()

    assert check_by_id(report, "chat_dry_run").metadata["status"] == "dry_run_ready"


def test_audit_serialization_check_included():
    report = build_v1_rc_smoke_report()

    assert check_by_id(report, "audit_serialization").status == "passed"


def test_json_output_shape_stable():
    payload = build_v1_rc_smoke_report().to_dict()

    assert tuple(payload) == ("status", "version", "checks", "summary", "warnings", "errors")
    assert payload["version"] == "V1.0.0-rc1"


def test_no_output_path_writes_nothing(tmp_path):
    result = subprocess.run(
        [sys.executable, SMOKE_SCRIPT, "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "passed"
    assert list(tmp_path.iterdir()) == []


def test_explicit_output_writes_report(tmp_path):
    output = tmp_path / "v1_rc1_smoke.json"

    written = write_v1_rc_smoke_report(build_v1_rc_smoke_report(), output)

    assert written == output
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


def test_overwrite_false_blocks_existing_output(tmp_path):
    output = tmp_path / "v1_rc1_smoke.json"
    output.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_v1_rc_smoke_report(build_v1_rc_smoke_report(), output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    output = tmp_path / "missing" / "v1_rc1_smoke.json"

    with pytest.raises(FileNotFoundError):
        write_v1_rc_smoke_report(build_v1_rc_smoke_report(), output, create_dirs=False)
    assert write_v1_rc_smoke_report(build_v1_rc_smoke_report(), output, create_dirs=True) == output


def test_release_notes_contain_required_scope():
    text = open(RELEASE_NOTES, encoding="utf-8").read()

    for phrase in (
        "local/internal chat-style QA control wrapper",
        "dry-run CLI by default",
        "security guard",
        "workflow planning/run/inspection/acceptance",
        "audit trace",
        "eval/regression artifacts",
        "artifact verification",
        "release readiness checker",
    ):
        assert phrase in text


def test_release_notes_contain_required_non_scope():
    text = open(RELEASE_NOTES, encoding="utf-8").read()

    for phrase in (
        "public SaaS",
        "production customer deployment",
        "default real RAG answer provider",
        "default vector DB/reranker replacement",
        "autonomous wet-lab execution",
        "external connector automation",
        "clinical/regulatory/commercial performance claim",
    ):
        assert phrase in text


def test_manual_release_doc_includes_human_approved_only_tag_release_wording():
    text = open(MANUAL_STEPS, encoding="utf-8").read()

    assert "Human-Approved Only" in text
    assert "git tag -a v1.0.0-rc1" in text
    assert "gh release create v1.0.0-rc1" in text


def test_no_auto_tag_or_release_execution_in_script():
    text = open(SMOKE_SCRIPT, encoding="utf-8").read().lower()

    assert "git tag" not in text
    assert "gh release" not in text
    assert "subprocess" not in text


def test_no_imports_or_exec_of_retrieval_vector_reranker_external_connector():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scripts.run_v1_rc_smoke;"
                "forbidden=('asperitas_agent.rag','asperitas_agent.retrieval_tfidf',"
                "'asperitas_agent.retrieval_mvp003','asperitas_agent.embeddings',"
                "'asperitas_agent.reranking','openai','langchain','langgraph','mcp');"
                "loaded=[module for module in forbidden if module in sys.modules];"
                "print(','.join(loaded));"
                "raise SystemExit(1 if loaded else 0)"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stdout
