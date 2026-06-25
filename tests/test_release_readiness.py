from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.release_readiness import (
    ReleaseReadinessPolicy,
    build_v1_release_readiness_report,
    release_readiness_from_dict,
    release_readiness_to_dict,
    summarize_release_readiness,
    write_release_readiness_report,
)


def minimal_policy(tmp_path, required_paths=None, claim_text=""):
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in ("deploy.md", "closeout.md", "limits.md", "handoff.md"):
        (docs / name).write_text(claim_text or "internal only; no production claim\n", encoding="utf-8")
    return ReleaseReadinessPolicy(
        repo_root=str(tmp_path),
        required_modules={},
        required_paths=required_paths or {},
        claim_doc_paths=("docs/deploy.md", "docs/closeout.md", "docs/limits.md", "docs/handoff.md"),
    )


def check_status(report, check_id):
    return next(check.status for check in report.checks if check.check_id == check_id)


def test_readiness_report_passes_when_required_modules_and_docs_exist():
    report = build_v1_release_readiness_report()

    assert report.status == "ready_for_internal_rc"
    assert report.ok is True
    assert check_status(report, "security_guard_present") == "passed"
    assert check_status(report, "internal_deploy_guide_present") == "passed"


def test_missing_critical_module_blocks(tmp_path):
    policy = minimal_policy(tmp_path)
    policy = ReleaseReadinessPolicy(
        repo_root=str(tmp_path),
        required_modules={"missing_module": "asperitas_agent.not_real"},
        required_paths={},
        claim_doc_paths=policy.claim_doc_paths,
    )

    report = build_v1_release_readiness_report(policy=policy)

    assert report.status == "blocked"
    assert check_status(report, "missing_module") == "blocked"


def test_missing_deploy_guide_blocks(tmp_path):
    report = build_v1_release_readiness_report(
        policy=minimal_policy(tmp_path, required_paths={"internal_deploy_guide_present": "docs/missing.md"})
    )

    assert report.status == "blocked"
    assert check_status(report, "internal_deploy_guide_present") == "blocked"


def test_missing_known_limitations_blocks(tmp_path):
    report = build_v1_release_readiness_report(
        policy=minimal_policy(tmp_path, required_paths={"known_limitations_present": "docs/missing.md"})
    )

    assert report.status == "blocked"
    assert check_status(report, "known_limitations_present") == "blocked"


def test_missing_v1_1_handoff_blocks(tmp_path):
    report = build_v1_release_readiness_report(
        policy=minimal_policy(tmp_path, required_paths={"v1_1_handoff_present": "docs/missing.md"})
    )

    assert report.status == "blocked"
    assert check_status(report, "v1_1_handoff_present") == "blocked"


def test_public_saas_claim_pattern_blocks(tmp_path):
    report = build_v1_release_readiness_report(policy=minimal_policy(tmp_path, claim_text="public SaaS is ready"))

    assert report.status == "blocked"
    assert check_status(report, "no_public_saas_claim") == "blocked"


def test_autonomous_wet_lab_claim_pattern_blocks(tmp_path):
    report = build_v1_release_readiness_report(policy=minimal_policy(tmp_path, claim_text="autonomous wet-lab execution is ready"))

    assert report.status == "blocked"
    assert check_status(report, "no_autonomous_wet_lab_claim") == "blocked"


def test_real_answer_provider_default_claim_blocks(tmp_path):
    report = build_v1_release_readiness_report(policy=minimal_policy(tmp_path, claim_text="real RAG answer provider is wired by default"))

    assert report.status == "blocked"
    assert check_status(report, "no_default_real_answer_provider_claim") == "blocked"


def test_json_roundtrip_stable():
    report = build_v1_release_readiness_report()
    first = json.dumps(release_readiness_to_dict(report), sort_keys=True, separators=(",", ":"))
    restored = release_readiness_from_dict(json.loads(first))
    second = json.dumps(release_readiness_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second


def test_explicit_output_writes_report(tmp_path):
    output = tmp_path / "readiness.json"
    report = build_v1_release_readiness_report()

    written = write_release_readiness_report(report, output)

    assert written == output
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "ready_for_internal_rc"


def test_no_output_path_writes_nothing(tmp_path):
    result = subprocess.run(
        [sys.executable, "scripts/check_v1_release_readiness.py", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "ready_for_internal_rc"
    assert list(tmp_path.iterdir()) == []


def test_overwrite_false_blocks_existing_output(tmp_path):
    output = tmp_path / "readiness.json"
    output.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_release_readiness_report(build_v1_release_readiness_report(), output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    output = tmp_path / "missing" / "readiness.json"

    with pytest.raises(FileNotFoundError):
        write_release_readiness_report(build_v1_release_readiness_report(), output, create_dirs=False)
    assert write_release_readiness_report(build_v1_release_readiness_report(), output, create_dirs=True) == output


def test_cli_emits_valid_json():
    result = subprocess.run(
        [sys.executable, "scripts/check_v1_release_readiness.py", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "ready_for_internal_rc"
    assert payload["summary"]["blocked_count"] == 0


def test_release_checker_does_not_import_execute_retrieval_vector_reranker_external_connector():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.release_readiness;"
                "forbidden=('asperitas_agent.rag','asperitas_agent.retrieval_tfidf',"
                "'asperitas_agent.retrieval_mvp003','asperitas_agent.embeddings',"
                "'asperitas_agent.reranking','openai','langchain','langgraph','mcp','subprocess');"
                "loaded=[module for module in forbidden if module in sys.modules];"
                "print(','.join(loaded));"
                "raise SystemExit(1 if loaded else 0)"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stdout


def test_no_source_chunk_or_eval_fixture_files_modified():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    protected_prefixes = (
        "01_RAW_SOURCES/",
        "03_PROCESSED_KB/chunks/",
        "04_VECTOR_DB/",
        "07_EVALS/",
        "tests/fixtures/",
        "data/source_registry.csv",
        "data/chunks.jsonl",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path.startswith(protected_prefixes)]


def test_summary_counts_checks():
    summary = summarize_release_readiness(build_v1_release_readiness_report())

    assert summary["status"] == "ready_for_internal_rc"
    assert summary["blocked_count"] == 0
