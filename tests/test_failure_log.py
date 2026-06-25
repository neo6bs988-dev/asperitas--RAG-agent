from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.failure_log import (
    FAILURE_CATEGORIES,
    build_failure_record,
    deterministic_failure_id,
    failure_record_from_dict,
    failure_record_to_dict,
    load_failure_jsonl,
    redact_failure_payload,
    write_failure_jsonl,
)


def test_build_valid_failure_record_with_deterministic_id():
    record = build_failure_record(
        query="What is Asperitas RAG Agent?",
        expected_behavior="Should return dry-run status or source-grounded answer when provider exists.",
        actual_behavior="dry_run_ready; no answer provider wired.",
        category="dry_run_provider_needed",
        severity="medium",
        status="open",
        created_at_utc="2026-06-25T00:00:00Z",
        session_id="dogfood_session_1",
    )

    assert record.validate() == ()
    assert record.failure_id == deterministic_failure_id(
        "What is Asperitas RAG Agent?",
        "dry_run_provider_needed",
        "2026-06-25T00:00:00Z",
        "dogfood_session_1",
    )
    assert "dry_run_provider_needed" in FAILURE_CATEGORIES


def test_unknown_category_severity_status_rejected():
    with pytest.raises(ValueError, match="invalid category"):
        build_failure_record("q", "expected", "actual", "unknown", "medium", "open")
    with pytest.raises(ValueError, match="invalid severity"):
        build_failure_record("q", "expected", "actual", "other", "urgent", "open")
    with pytest.raises(ValueError, match="invalid status"):
        build_failure_record("q", "expected", "actual", "other", "medium", "new")


def test_roundtrip_json_safe_record():
    record = build_failure_record(
        query="q",
        expected_behavior="expected",
        actual_behavior="actual",
        category="source_gap",
        severity="high",
        source_context={"path": {"nested": object()}},
        reproduction_steps=["run CLI", "inspect JSONL"],
    )

    restored = failure_record_from_dict(failure_record_to_dict(record))

    assert failure_record_to_dict(restored) == failure_record_to_dict(record)
    assert isinstance(restored.source_context["path"]["nested"], str)


def test_redact_failure_payload_redacts_sensitive_keys():
    payload, redactions = redact_failure_payload({"api_key": "abc", "nested": {"password": "pw", "safe": "ok"}})

    assert payload["api_key"] == "[REDACTED]"
    assert payload["nested"]["password"] == "[REDACTED]"
    assert payload["nested"]["safe"] == "ok"
    assert redactions == ("api_key", "nested.password")


def test_write_jsonl_requires_explicit_append_for_existing_file(tmp_path):
    output = tmp_path / "failure.jsonl"
    record = build_failure_record("q", "expected", "actual", "other", "low")

    write_failure_jsonl(record, output)
    with pytest.raises(FileExistsError):
        write_failure_jsonl(record, output)
    write_failure_jsonl(record, output, append=True)

    assert len(output.read_text(encoding="utf-8").splitlines()) == 2
    assert load_failure_jsonl(output)[0].failure_id == record.failure_id


def test_create_dirs_must_be_explicit(tmp_path):
    output = tmp_path / "missing" / "failure.jsonl"
    record = build_failure_record("q", "expected", "actual", "other", "low")

    with pytest.raises(FileNotFoundError):
        write_failure_jsonl(record, output)
    assert write_failure_jsonl(record, output, create_dirs=True) == output


def test_cli_prints_json_without_file_write(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/record_failure_log.py",
            "--query",
            "What is Asperitas RAG Agent?",
            "--expected-behavior",
            "Should return dry-run status or source-grounded answer when provider exists.",
            "--actual-behavior",
            "dry_run_ready; no answer provider wired.",
            "--category",
            "dry_run_provider_needed",
            "--severity",
            "medium",
            "--status",
            "open",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["category"] == "dry_run_provider_needed"
    assert list(tmp_path.iterdir()) == []


def test_cli_appends_to_explicit_output_with_create_dirs(tmp_path):
    output = tmp_path / "logs" / "failures.jsonl"
    command = [
        sys.executable,
        "scripts/record_failure_log.py",
        "--query",
        "What is Asperitas RAG Agent?",
        "--expected-behavior",
        "Should return dry-run status or source-grounded answer when provider exists.",
        "--actual-behavior",
        "dry_run_ready; no answer provider wired.",
        "--category",
        "dry_run_provider_needed",
        "--severity",
        "medium",
        "--status",
        "open",
        "--output",
        str(output),
        "--create-dirs",
        "--append",
        "--json",
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    subprocess.run(command, check=True, capture_output=True, text=True)

    assert len(output.read_text(encoding="utf-8").splitlines()) == 2


def test_cli_rejects_unknown_category():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/record_failure_log.py",
            "--query",
            "q",
            "--expected-behavior",
            "expected",
            "--actual-behavior",
            "actual",
            "--category",
            "unknown",
            "--severity",
            "medium",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0


def test_no_retrieval_vector_reranker_answer_or_default_runtime_imports_or_execution():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.failure_log;"
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


def test_no_source_chunk_registry_or_eval_fixture_files_modified():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    protected_prefixes = (
        "00_ADMIN/source_registry",
        "01_RAW_SOURCES/",
        "03_PROCESSED_KB/chunks/",
        "04_VECTOR_DB/",
        "data/chunks.jsonl",
        "data/source_registry",
        "eval/",
        "tests/fixtures/",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path.startswith(protected_prefixes)]
