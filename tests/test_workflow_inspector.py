from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.workflow_inspector import (
    inspect_workflow_run,
    inspect_workflow_run_dict,
    workflow_inspection_from_dict,
    workflow_inspection_to_dict,
    write_workflow_inspection_report,
)
from asperitas_agent.workflow_run import WorkflowRunInput, build_workflow_run, workflow_run_to_dict
from asperitas_agent.workflow_state import AgentWorkflowPlan, AgentWorkflowStep


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


def ready_run():
    return build_workflow_run(run_input())


def finding_ids(report):
    return tuple(finding.finding_id for finding in report.findings)


def write_run_artifact(path, run=None):
    path.write_text(json.dumps(workflow_run_to_dict(run or ready_run())), encoding="utf-8")
    return path


def test_ready_workflow_run_produces_ok_inspection():
    report = inspect_workflow_run(ready_run())

    assert report.ok is True
    assert report.run_status == "ready"
    assert report.ready_for_execution is True
    assert report.executes_plan is False
    assert finding_ids(report) == ("workflow_ready",)
    assert report.validate() == ()


def test_blocked_workflow_run_produces_blocker_findings():
    report = inspect_workflow_run(build_workflow_run(run_input(risk_flags=("blocked",))))

    assert report.ok is False
    assert report.run_status == "blocked"
    assert "run_blocked" in finding_ids(report)
    assert report.summary["blocker_count"] >= 1


def test_requires_approval_run_produces_approval_findings():
    report = inspect_workflow_run(build_workflow_run(run_input(risk_flags=("high",))))

    assert report.ok is False
    assert report.run_status == "requires_human_approval"
    assert "run_requires_human_approval" in finding_ids(report)
    assert report.summary["approval_count"] >= 1


def test_executes_plan_true_blocks_inspection():
    payload = workflow_run_to_dict(ready_run())
    payload["executes_plan"] = True
    report = inspect_workflow_run_dict(payload)

    assert report.ok is False
    assert "executes_plan_true" in finding_ids(report)
    assert report.summary["blocker_count"] >= 1


def test_malformed_run_fails_closed():
    report = inspect_workflow_run_dict({"run_id": "bad", "unexpected": True})

    assert report.ok is False
    assert report.run_status == "invalid"
    assert "malformed_run_artifact" in finding_ids(report)
    assert report.errors


def test_missing_plan_fails_closed():
    payload = workflow_run_to_dict(ready_run())
    payload["plan"] = None
    report = inspect_workflow_run_dict(payload)

    assert report.ok is False
    assert "missing_plan" in finding_ids(report)


def test_missing_audit_ready_finding_detected():
    run = ready_run()
    plan = run.plan
    assert plan is not None
    modified_plan = AgentWorkflowPlan(
        request=plan.request,
        policy=plan.policy,
        steps=tuple(step for step in plan.steps if step.step_kind != "audit_ready"),
        planner_decision=plan.planner_decision,
        ready_for_execution=False,
    )
    payload = workflow_run_to_dict(run)
    payload["plan"] = modified_plan.to_dict()
    payload["ready_for_execution"] = False
    report = inspect_workflow_run_dict(payload)

    assert "missing_audit_ready" in finding_ids(report)


def test_failed_eval_gate_finding_detected():
    report = inspect_workflow_run(build_workflow_run(run_input(eval_gate={"ok": False})))

    assert "failed_eval_gate" in finding_ids(report)
    assert "eval_gate_check_blocked" in finding_ids(report)


def test_json_roundtrip_stable():
    report = inspect_workflow_run(ready_run())
    first = json.dumps(workflow_inspection_to_dict(report), sort_keys=True, separators=(",", ":"))
    restored = workflow_inspection_from_dict(json.loads(first))
    second = json.dumps(workflow_inspection_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second


def test_explicit_output_writes_report(tmp_path):
    report = inspect_workflow_run(ready_run())
    output = tmp_path / "workflow_inspection.json"

    written = write_workflow_inspection_report(report, output)

    assert written == output
    assert json.loads(output.read_text(encoding="utf-8"))["ok"] is True


def test_no_output_path_writes_nothing(tmp_path):
    input_path = write_run_artifact(tmp_path / "workflow_run_artifact.json")

    result = subprocess.run(
        [sys.executable, "scripts/inspect_workflow_run.py", "--input", str(input_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["ok"] is True
    assert sorted(path.name for path in tmp_path.iterdir()) == ["workflow_run_artifact.json"]


def test_overwrite_false_blocks_existing_output(tmp_path):
    report = inspect_workflow_run(ready_run())
    output = tmp_path / "workflow_inspection.json"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_workflow_inspection_report(report, output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    report = inspect_workflow_run(ready_run())
    output = tmp_path / "missing" / "workflow_inspection.json"

    with pytest.raises(FileNotFoundError):
        write_workflow_inspection_report(report, output, create_dirs=False)
    assert write_workflow_inspection_report(report, output, create_dirs=True) == output


def test_cli_emits_valid_json(tmp_path):
    input_path = write_run_artifact(tmp_path / "workflow_run_artifact.json")
    result = subprocess.run(
        [sys.executable, "scripts/inspect_workflow_run.py", "--input", str(input_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["run_id"] == "local_workflow_run"
    assert payload["executes_plan"] is False


def test_inspector_does_not_import_execute_retrieval_vector_llm_or_external_connectors():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.workflow_inspector;"
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
