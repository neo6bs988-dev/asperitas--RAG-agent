from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.audit_trace import (
    AuditTracePolicy,
    audit_event_from_dict,
    audit_event_to_dict,
    audit_record_from_dict,
    audit_record_to_dict,
    build_audit_event,
    build_audit_record,
    load_audit_jsonl,
    redact_audit_payload,
    summarize_audit_record,
    write_audit_jsonl,
)


def test_build_valid_audit_event():
    event = build_audit_event("local_trace", "workflow_accepted", payload={"decision": "accepted"})

    assert event.validate() == ()
    assert event.trace_id == "local_trace"
    assert event.event_type == "workflow_accepted"
    assert event.actor == "system"


def test_missing_trace_id_fails_closed():
    event = build_audit_event("", "workflow_accepted")

    assert "trace_id is required" in event.validate()


def test_missing_event_type_fails_closed():
    event = build_audit_event("local_trace", "")

    assert "invalid event_type: " in event.validate()


def test_sensitive_keys_redacted():
    result = redact_audit_payload(
        {
            "api_key": "abc",
            "nested": {"password": "pw", "safe": "ok"},
            "credential_id": "secretish",
        }
    )

    assert result["payload"]["api_key"] == "[REDACTED]"
    assert result["payload"]["nested"]["password"] == "[REDACTED]"
    assert result["payload"]["nested"]["safe"] == "ok"
    assert "api_key" in result["redactions"]


def test_raw_text_redacted_by_default():
    result = redact_audit_payload({"raw_text": "x" * 300})

    assert result["payload"]["raw_text"] == "[REDACTED]"
    assert result["redactions"] == ["raw_text"]


def test_allow_raw_text_preserves_raw_text():
    result = redact_audit_payload({"raw_text": "x" * 300}, AuditTracePolicy(allow_raw_text=True))

    assert result["payload"]["raw_text"] == "x" * 300
    assert result["redactions"] == []


def test_write_jsonl_explicit_output(tmp_path):
    event = build_audit_event("local_trace", "workflow_accepted")
    output = tmp_path / "audit.jsonl"

    written = write_audit_jsonl([event], output)

    assert written == output
    assert len(output.read_text(encoding="utf-8").splitlines()) == 1


def test_no_output_path_writes_nothing(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/write_audit_trace.py",
            "--event-type",
            "workflow_accepted",
            "--trace-id",
            "local_trace",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["event_count"] == 1
    assert list(tmp_path.iterdir()) == []


def test_append_false_blocks_existing_file(tmp_path):
    output = tmp_path / "audit.jsonl"
    output.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_audit_jsonl([build_audit_event("local_trace", "workflow_accepted")], output, append=False)


def test_append_true_appends(tmp_path):
    output = tmp_path / "audit.jsonl"
    event = build_audit_event("local_trace", "workflow_accepted")
    write_audit_jsonl([event], output)
    write_audit_jsonl([event], output, append=True)

    assert len(output.read_text(encoding="utf-8").splitlines()) == 2


def test_create_dirs_behavior(tmp_path):
    output = tmp_path / "missing" / "audit.jsonl"
    event = build_audit_event("local_trace", "workflow_accepted")

    with pytest.raises(FileNotFoundError):
        write_audit_jsonl([event], output, create_dirs=False)
    assert write_audit_jsonl([event], output, create_dirs=True) == output


def test_load_jsonl_roundtrip_stable(tmp_path):
    event = build_audit_event("local_trace", "workflow_accepted")
    output = tmp_path / "audit.jsonl"
    write_audit_jsonl([event], output)

    loaded = load_audit_jsonl(output)

    assert json.dumps(audit_event_to_dict(loaded[0]), sort_keys=True) == json.dumps(
        audit_event_to_dict(event),
        sort_keys=True,
    )
    record = build_audit_record(loaded)
    restored = audit_record_from_dict(audit_record_to_dict(record))
    assert audit_record_to_dict(restored) == audit_record_to_dict(record)


def test_malformed_jsonl_strict_fails(tmp_path):
    output = tmp_path / "audit.jsonl"
    output.write_text("{bad-json\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_audit_jsonl(output, strict=True)


def test_malformed_jsonl_non_strict_warns(tmp_path):
    output = tmp_path / "audit.jsonl"
    output.write_text("{bad-json\n", encoding="utf-8")

    loaded = load_audit_jsonl(output, strict=False)

    assert loaded[0].warnings == ("malformed JSONL line 1",)
    assert loaded[0].errors


def test_summary_counts_event_types_and_severities():
    record = build_audit_record(
        (
            build_audit_event("local_trace", "workflow_accepted", severity="info"),
            build_audit_event("local_trace", "security_guard_triggered", severity="blocked"),
        )
    )

    summary = summarize_audit_record(record)

    assert summary["event_type_counts"]["workflow_accepted"] == 1
    assert summary["event_type_counts"]["security_guard_triggered"] == 1
    assert summary["severity_counts"]["blocked"] == 1


def test_cli_emits_valid_json(tmp_path):
    output = tmp_path / "audit.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/write_audit_trace.py",
            "--event-type",
            "workflow_accepted",
            "--trace-id",
            "local_trace",
            "--output",
            str(output),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["events"][0]["event_type"] == "workflow_accepted"
    assert output.exists()


def test_unknown_extra_fields_warn_not_block():
    event = audit_event_from_dict(
        {
            "trace_id": "local_trace",
            "event_id": "event_1",
            "event_type": "workflow_accepted",
            "created_at_utc": "1970-01-01T00:00:00Z",
            "severity": "info",
            "actor": "system",
            "extra": "ignored",
        }
    )

    assert event.validate() == ()
    assert "unknown audit event field: extra" in event.warnings


def test_no_retrieval_vector_llm_or_external_connector_imports_or_execution():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.audit_trace;"
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


def test_no_source_chunk_or_eval_fixture_files_modified():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    protected_prefixes = (
        "01_RAW_SOURCES/",
        "03_PROCESSED_KB/chunks/",
        "04_VECTOR_DB/",
        "07_EVALS/",
        "tests/fixtures/",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path.startswith(protected_prefixes)]
