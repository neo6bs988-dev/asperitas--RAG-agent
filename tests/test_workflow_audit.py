from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.workflow_acceptance import (
    accept_workflow_artifacts,
    workflow_acceptance_to_dict,
)
from asperitas_agent.workflow_audit import (
    audit_workflow_artifact_dicts,
    build_workflow_audit_events,
    build_workflow_audit_input,
    build_workflow_audit_record,
    summarize_workflow_audit,
    workflow_audit_result_from_dict,
    workflow_audit_result_to_dict,
    write_workflow_audit_jsonl,
)
from asperitas_agent.workflow_inspector import inspect_workflow_run, workflow_inspection_to_dict
from asperitas_agent.workflow_run import WorkflowRunInput, build_workflow_run, workflow_run_to_dict


def run_input(**overrides):
    payload = {
        "run_id": "local_workflow_run",
        "user_request": "Summarize source-grounded evidence for X",
        "required_skills": ("source-grounding-check",),
        "available_skills": ("source-grounding-check",),
        "source_status": {"available": True, "source_count": 1},
        "eval_gate": {"ok": True},
        "risk_flags": (),
        "metadata": {},
    }
    payload.update(overrides)
    return WorkflowRunInput(**payload)


def artifact_triplet(run=None):
    run_artifact = run or build_workflow_run(run_input())
    inspection = inspect_workflow_run(run_artifact)
    acceptance = accept_workflow_artifacts(run_artifact, inspection)
    return run_artifact, inspection, acceptance


def result_for(run=None, metadata=None):
    run_artifact, inspection, acceptance = artifact_triplet(run)
    return audit_workflow_artifact_dicts(
        workflow_run_to_dict(run_artifact),
        workflow_inspection_to_dict(inspection),
        workflow_acceptance_to_dict(acceptance),
        metadata=metadata or {"trace_id": "local_trace"},
    )


def event_types(result):
    return tuple(event.event_type for event in result.events)


def write_triplet(tmp_path, run=None):
    run_artifact, inspection, acceptance = artifact_triplet(run)
    run_path = tmp_path / "workflow_run.json"
    inspection_path = tmp_path / "workflow_inspection.json"
    acceptance_path = tmp_path / "workflow_acceptance.json"
    run_path.write_text(json.dumps(workflow_run_to_dict(run_artifact)), encoding="utf-8")
    inspection_path.write_text(json.dumps(workflow_inspection_to_dict(inspection)), encoding="utf-8")
    acceptance_path.write_text(json.dumps(workflow_acceptance_to_dict(acceptance)), encoding="utf-8")
    return run_path, inspection_path, acceptance_path


def test_accepted_workflow_emits_workflow_accepted_audit_event():
    result = result_for()

    assert result.status == "recorded"
    assert result.ok is True
    assert event_types(result)[0] == "workflow_accepted"
    assert result.events[0].severity == "info"
    assert result.validate() == ()


def test_rejected_workflow_emits_workflow_rejected_audit_event():
    run = build_workflow_run(run_input(risk_flags=("blocked",)))
    result = result_for(run)

    assert result.status == "rejected"
    assert result.ok is False
    assert event_types(result)[0] == "workflow_rejected"
    assert result.events[0].severity == "blocked"


def test_approval_workflow_emits_human_approval_required_audit_event():
    run = build_workflow_run(run_input(risk_flags=("high",)))
    result = result_for(run)

    assert result.status == "requires_human_approval"
    assert result.ok is False
    assert event_types(result)[0] == "human_approval_required"
    assert result.events[0].severity == "warning"


def test_eval_and_source_status_emit_corresponding_audit_events():
    result = result_for()

    assert "eval_gate_checked" in event_types(result)
    assert "source_gate_checked" in event_types(result)


def test_executes_plan_true_emits_security_guard_and_rejects():
    run_artifact, inspection, acceptance = artifact_triplet()
    run_data = workflow_run_to_dict(run_artifact)
    run_data["executes_plan"] = True
    result = audit_workflow_artifact_dicts(
        run_data,
        workflow_inspection_to_dict(inspection),
        workflow_acceptance_to_dict(acceptance),
        metadata={"trace_id": "local_trace"},
    )

    assert result.status == "rejected"
    assert "security_guard_triggered" in event_types(result)


def test_malformed_run_invalid_fail_closed():
    _, inspection, acceptance = artifact_triplet()
    result = audit_workflow_artifact_dicts(
        {"run_id": "bad"},
        workflow_inspection_to_dict(inspection),
        workflow_acceptance_to_dict(acceptance),
        metadata={"trace_id": "local_trace"},
    )

    assert result.status == "invalid"
    assert "security_guard_triggered" in event_types(result)
    assert result.errors


def test_malformed_inspection_invalid_fail_closed():
    run_artifact, _, acceptance = artifact_triplet()
    result = audit_workflow_artifact_dicts(
        workflow_run_to_dict(run_artifact),
        {"report_id": "bad"},
        workflow_acceptance_to_dict(acceptance),
        metadata={"trace_id": "local_trace"},
    )

    assert result.status == "invalid"
    assert result.errors


def test_malformed_acceptance_invalid_fail_closed():
    run_artifact, inspection, _ = artifact_triplet()
    result = audit_workflow_artifact_dicts(
        workflow_run_to_dict(run_artifact),
        workflow_inspection_to_dict(inspection),
        {"decision_id": "bad"},
        metadata={"trace_id": "local_trace"},
    )

    assert result.status == "invalid"
    assert result.errors


def test_run_id_mismatch_rejected():
    run_artifact, inspection, acceptance = artifact_triplet()
    acceptance_data = workflow_acceptance_to_dict(acceptance)
    acceptance_data["run_id"] = "other_run"
    result = audit_workflow_artifact_dicts(
        workflow_run_to_dict(run_artifact),
        workflow_inspection_to_dict(inspection),
        acceptance_data,
        metadata={"trace_id": "local_trace"},
    )

    assert result.status == "rejected"
    assert "run_id mismatch across workflow artifacts" in result.warnings


def test_sensitive_payload_keys_redacted():
    result = result_for(metadata={"trace_id": "local_trace", "secret_note": "hide me"})

    assert result.events[0].payload["secret_note"] == "[REDACTED]"
    assert "secret_note" in result.events[0].redactions


def test_no_output_path_writes_nothing(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    run_path, inspection_path, acceptance_path = write_triplet(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_workflow_artifacts.py",
            "--run",
            str(run_path),
            "--inspection",
            str(inspection_path),
            "--acceptance",
            str(acceptance_path),
            "--trace-id",
            "local_trace",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "recorded"
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "workflow_acceptance.json",
        "workflow_inspection.json",
        "workflow_run.json",
    ]


def test_explicit_output_writes_jsonl(tmp_path):
    output = tmp_path / "audit.jsonl"
    result = result_for()

    written = write_workflow_audit_jsonl(result, output)

    assert written == output
    assert len(output.read_text(encoding="utf-8").splitlines()) == len(result.events)


def test_append_false_blocks_existing_output(tmp_path):
    output = tmp_path / "audit.jsonl"
    output.write_text("existing\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_workflow_audit_jsonl(result_for(), output, append=False)


def test_append_true_appends(tmp_path):
    output = tmp_path / "audit.jsonl"
    result = result_for()
    write_workflow_audit_jsonl(result, output)
    write_workflow_audit_jsonl(result, output, append=True)

    assert len(output.read_text(encoding="utf-8").splitlines()) == len(result.events) * 2


def test_create_dirs_behavior(tmp_path):
    output = tmp_path / "missing" / "audit.jsonl"

    with pytest.raises(FileNotFoundError):
        write_workflow_audit_jsonl(result_for(), output, create_dirs=False)
    assert write_workflow_audit_jsonl(result_for(), output, create_dirs=True) == output


def test_json_roundtrip_stable():
    result = result_for()
    first = json.dumps(workflow_audit_result_to_dict(result), sort_keys=True, separators=(",", ":"))
    restored = workflow_audit_result_from_dict(json.loads(first))
    second = json.dumps(workflow_audit_result_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second


def test_cli_emits_valid_json(tmp_path):
    run_path, inspection_path, acceptance_path = write_triplet(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_workflow_artifacts.py",
            "--run",
            str(run_path),
            "--inspection",
            str(inspection_path),
            "--acceptance",
            str(acceptance_path),
            "--trace-id",
            "local_trace",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["trace_id"] == "local_trace"
    assert payload["events"][0]["event_type"] == "workflow_accepted"


def test_build_workflow_audit_input_and_record_summary():
    run_artifact, inspection, acceptance = artifact_triplet()
    audit_input = build_workflow_audit_input(
        "local_trace",
        workflow_run_to_dict(run_artifact),
        workflow_inspection_to_dict(inspection),
        workflow_acceptance_to_dict(acceptance),
    )
    record = build_workflow_audit_record(run_artifact, inspection, acceptance, metadata={"trace_id": "local_trace"})
    summary = summarize_workflow_audit(result_for())

    assert audit_input.validate() == ()
    assert record.validate() == ()
    assert summary["event_type_counts"]["workflow_accepted"] == 1


def test_bridge_does_not_import_execute_retrieval_vector_llm_or_external_connector():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.workflow_audit;"
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
