from __future__ import annotations

import importlib
import json
import subprocess
import sys

import pytest

from apps.internal_dogfood_app import (
    DEFAULT_FAILURE_LOG_PATH,
    build_dogfood_payload,
    build_failure_record_from_dogfood_result,
    run_internal_dogfood_once,
    save_failure_record_explicit,
)
from asperitas_agent.failure_log import load_failure_jsonl


def test_app_helper_builds_stable_payload():
    payload = build_dogfood_payload(" What is Asperitas? ", " Session One ", "Dry-run should pass.", "local note")

    assert payload["question"] == "What is Asperitas?"
    assert payload["request_id"] == "session_one_dogfood_request"
    assert payload["trace_id"] == "session_one_dogfood_trace"
    assert payload["source_status"]["dry_run_only"] is True
    assert payload["metadata"]["answer_provider_wired"] is False
    assert payload["metadata"]["expected_behavior"] == "Dry-run should pass."


def test_dry_run_result_can_be_converted_into_failure_log_record():
    payload = build_dogfood_payload("What is Asperitas?", "dogfood_session", "Expected dry-run status.", "")
    result = run_internal_dogfood_once(payload)

    record = build_failure_record_from_dogfood_result(
        payload,
        result,
        category="dry_run_provider_needed",
        severity="medium",
        status="open",
    )

    assert result["status"] == "dry_run_ready"
    assert result["dry_run"] is True
    assert record["query"] == "What is Asperitas?"
    assert record["category"] == "dry_run_provider_needed"
    assert record["dry_run_result"]["status"] == "dry_run_ready"
    assert "status=dry_run_ready" in record["actual_behavior"]


def test_redaction_acknowledgement_required_before_save(tmp_path):
    payload = build_dogfood_payload("What is Asperitas?", "dogfood_session")
    result = run_internal_dogfood_once(payload)
    record = build_failure_record_from_dogfood_result(payload, result, "internal_dogfood_feedback", "low", "open")

    with pytest.raises(PermissionError, match="redaction acknowledgement"):
        save_failure_record_explicit(record, tmp_path / "failure.jsonl", redaction_acknowledged=False)


def test_no_implicit_write_without_save_or_output(tmp_path):
    payload = build_dogfood_payload("What is Asperitas?", "dogfood_session")
    result = run_internal_dogfood_once(payload)
    build_failure_record_from_dogfood_result(payload, result, "internal_dogfood_feedback", "low", "open")

    assert list(tmp_path.iterdir()) == []
    with pytest.raises(ValueError, match="output_path is required"):
        save_failure_record_explicit({}, "", redaction_acknowledged=True)


def test_explicit_save_writes_jsonl(tmp_path):
    payload = build_dogfood_payload("What is Asperitas?", "dogfood_session")
    result = run_internal_dogfood_once(payload)
    record = build_failure_record_from_dogfood_result(payload, result, "internal_dogfood_feedback", "low", "open")
    output = tmp_path / "logs" / "failure.jsonl"

    saved_path = save_failure_record_explicit(record, output, redaction_acknowledged=True)

    assert saved_path == output
    records = load_failure_jsonl(output)
    assert len(records) == 1
    assert records[0].query == "What is Asperitas?"


def test_app_imports_without_retrieval_vector_reranker_default_answer_side_effects():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import apps.internal_dogfood_app;"
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


def test_docs_include_internal_only_dry_run_no_provider_limitations():
    doc = "docs/V1_1B_STREAMLIT_INTERNAL_DOGFOOD_UI.md"
    text = open(doc, encoding="utf-8").read().lower()

    assert "internal/local" in text
    assert "dry-run only" in text
    assert "no real answer provider" in text
    assert "not public saas" in text
    assert "not production deployment" in text
    assert DEFAULT_FAILURE_LOG_PATH.lower() in text


def test_app_module_reload_does_not_write_default_failure_log():
    import apps.internal_dogfood_app as app

    importlib.reload(app)

    assert not open(__file__, encoding="utf-8").read().endswith(json.dumps({"unexpected": True}))
