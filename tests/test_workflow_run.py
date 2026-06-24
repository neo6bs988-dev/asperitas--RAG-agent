from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.workflow_run import (
    WorkflowRunInput,
    build_workflow_run,
    load_workflow_run_input,
    workflow_run_from_dict,
    workflow_run_to_dict,
    write_workflow_run_artifact,
)


def valid_input(**overrides):
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


def write_input(path, **overrides):
    payload = {
        "run_id": "local_workflow_run",
        "request": {
            "user_request": "Summarize source-grounded evidence for X",
            "required_skills": ["source-grounding-check"],
            "metadata": {},
        },
        "available_skills": ["source-grounding-check"],
        "source_status": {"available": True, "source_count": 1},
        "eval_gate": {"ok": True},
        "risk_flags": [],
        "metadata": {},
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_input_creates_ready_workflow_run_artifact():
    run = build_workflow_run(valid_input())

    assert run.status == "ready"
    assert run.ok is True
    assert run.executes_plan is False
    assert run.ready_for_execution is True
    assert run.plan is not None
    assert run.plan.executes_plan is False
    assert run.validate() == ()


def test_blocked_risk_creates_blocked_artifact():
    run = build_workflow_run(valid_input(risk_flags=("blocked",)))

    assert run.status == "blocked"
    assert run.ok is False
    assert run.ready_for_execution is False


def test_high_risk_creates_requires_human_approval_artifact():
    run = build_workflow_run(valid_input(risk_flags=("high",)))

    assert run.status == "requires_human_approval"
    assert run.ok is False
    assert run.summary["approval_steps"]


def test_failed_eval_gate_creates_blocked_artifact():
    run = build_workflow_run(valid_input(eval_gate={"ok": False}))

    assert run.status == "blocked"
    assert run.summary["blocked_steps"] == ["eval_gate_check"]


def test_missing_source_status_requires_approval():
    run = build_workflow_run(valid_input(source_status=None))

    assert run.status == "requires_human_approval"
    assert "source_check" in run.summary["approval_steps"]


def test_missing_required_skill_requires_approval():
    run = build_workflow_run(valid_input(available_skills=()))

    assert run.status == "requires_human_approval"
    assert "skill_selection" in run.summary["approval_steps"]


def test_malformed_input_invalid_fail_closed(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")

    input_data = load_workflow_run_input(path)
    run = build_workflow_run(input_data)

    assert run.status == "invalid"
    assert run.ok is False
    assert run.executes_plan is False
    assert run.errors


def test_json_roundtrip_stable():
    run = build_workflow_run(valid_input())
    first = json.dumps(workflow_run_to_dict(run), sort_keys=True, separators=(",", ":"))
    restored = workflow_run_from_dict(json.loads(first))
    second = json.dumps(workflow_run_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second


def test_explicit_output_writes_artifact(tmp_path):
    run = build_workflow_run(valid_input())
    output = tmp_path / "workflow_run_artifact.json"

    written = write_workflow_run_artifact(run, output)

    assert written == output
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "ready"


def test_no_output_path_writes_nothing(tmp_path):
    input_path = write_input(tmp_path / "workflow_run_input.json")

    result = subprocess.run(
        [sys.executable, "scripts/run_agent_workflow.py", "--input", str(input_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "ready"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["workflow_run_input.json"]


def test_overwrite_false_blocks_existing_output(tmp_path):
    run = build_workflow_run(valid_input())
    output = tmp_path / "workflow_run_artifact.json"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_workflow_run_artifact(run, output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    run = build_workflow_run(valid_input())
    output = tmp_path / "missing" / "workflow_run_artifact.json"

    with pytest.raises(FileNotFoundError):
        write_workflow_run_artifact(run, output, create_dirs=False)
    assert write_workflow_run_artifact(run, output, create_dirs=True) == output
    assert output.exists()


def test_cli_emits_valid_json(tmp_path):
    input_path = write_input(tmp_path / "workflow_run_input.json")
    result = subprocess.run(
        [sys.executable, "scripts/run_agent_workflow.py", "--input", str(input_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "ready"
    assert payload["executes_plan"] is False


def test_wrapper_does_not_import_execute_retrieval_vector_llm_or_external_connectors():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.workflow_run;"
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
