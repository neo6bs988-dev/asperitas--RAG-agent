from __future__ import annotations

import json
import subprocess
import sys

import pytest

from asperitas_agent.workflow_acceptance import (
    accept_workflow_artifact_dicts,
    accept_workflow_artifacts,
    workflow_acceptance_from_dict,
    workflow_acceptance_to_dict,
    write_workflow_acceptance_decision,
)
from asperitas_agent.workflow_inspector import (
    WorkflowInspectionFinding,
    WorkflowInspectionReport,
    inspect_workflow_run,
    workflow_inspection_to_dict,
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


def ready_inspection(run=None):
    return inspect_workflow_run(run or ready_run())


def reason_ids(decision):
    return tuple(reason.reason_id for reason in decision.reasons)


def write_artifacts(tmp_path, run=None, inspection=None):
    run_artifact = run or ready_run()
    inspection_report = inspection or inspect_workflow_run(run_artifact)
    run_path = tmp_path / "workflow_run_artifact.json"
    inspection_path = tmp_path / "workflow_inspection.json"
    run_path.write_text(json.dumps(workflow_run_to_dict(run_artifact)), encoding="utf-8")
    inspection_path.write_text(json.dumps(workflow_inspection_to_dict(inspection_report)), encoding="utf-8")
    return run_path, inspection_path


def with_modified_plan(run, steps):
    plan = run.plan
    assert plan is not None
    modified_plan = AgentWorkflowPlan(
        request=plan.request,
        policy=plan.policy,
        steps=tuple(steps),
        planner_decision=plan.planner_decision,
        ready_for_execution=False,
    )
    payload = workflow_run_to_dict(run)
    payload["plan"] = modified_plan.to_dict()
    payload["ready_for_execution"] = False
    return payload


def test_valid_ready_run_and_ok_inspection_accepted():
    run = ready_run()
    decision = accept_workflow_artifacts(run, inspect_workflow_run(run))

    assert decision.status == "accepted"
    assert decision.ok is True
    assert decision.executes_plan is False
    assert reason_ids(decision) == ("workflow_acceptance_passed",)
    assert decision.validate() == ()


def test_malformed_run_invalid():
    decision = accept_workflow_artifact_dicts({"run_id": "bad"}, workflow_inspection_to_dict(ready_inspection()))

    assert decision.status == "invalid"
    assert "malformed_run_artifact" in reason_ids(decision)


def test_malformed_inspection_invalid():
    decision = accept_workflow_artifact_dicts(workflow_run_to_dict(ready_run()), {"report_id": "bad"})

    assert decision.status == "invalid"
    assert "malformed_inspection_report" in reason_ids(decision)


def test_run_id_mismatch_rejected():
    inspection = workflow_inspection_to_dict(ready_inspection())
    inspection["run_id"] = "other_run"
    decision = accept_workflow_artifact_dicts(workflow_run_to_dict(ready_run()), inspection)

    assert decision.status == "rejected"
    assert "run_id_mismatch" in reason_ids(decision)


def test_executes_plan_true_rejected():
    payload = workflow_run_to_dict(ready_run())
    payload["executes_plan"] = True
    decision = accept_workflow_artifact_dicts(payload, workflow_inspection_to_dict(ready_inspection()))

    assert decision.status == "rejected"
    assert "executes_plan_true" in reason_ids(decision)


def test_blocked_run_rejected():
    run = build_workflow_run(run_input(risk_flags=("blocked",)))
    decision = accept_workflow_artifacts(run, inspect_workflow_run(run))

    assert decision.status == "rejected"
    assert "run_status_blocked" in reason_ids(decision)


def test_approval_run_returns_requires_human_approval():
    run = build_workflow_run(run_input(risk_flags=("high",)))
    decision = accept_workflow_artifacts(run, inspect_workflow_run(run))

    assert decision.status == "requires_human_approval"
    assert decision.ok is False
    assert "run_requires_human_approval" in reason_ids(decision)


def test_inspection_error_finding_rejected():
    run = ready_run()
    inspection = WorkflowInspectionReport(
        report_id="local_workflow_run_inspection",
        schema_version="MVP-018C",
        created_at_utc="1970-01-01T00:00:00Z",
        ok=False,
        run_id=run.run_id,
        run_status=run.status,
        ready_for_execution=run.ready_for_execution,
        executes_plan=False,
        findings=(
            WorkflowInspectionFinding(
                finding_id="manual_error",
                severity="error",
                category="audit",
                message="manual error finding",
            ),
        ),
        summary={},
        run=run,
    )
    decision = accept_workflow_artifacts(run, inspection)

    assert decision.status == "rejected"
    assert "inspection_finding_manual_error" in reason_ids(decision)


def test_missing_audit_ready_rejected():
    run = ready_run()
    plan = run.plan
    assert plan is not None
    payload = with_modified_plan(run, tuple(step for step in plan.steps if step.step_kind != "audit_ready"))
    decision = accept_workflow_artifact_dicts(payload, workflow_inspection_to_dict(inspect_workflow_run_dict_payload(payload)))

    assert decision.status == "rejected"
    assert "missing_audit_ready" in reason_ids(decision)


def inspect_workflow_run_dict_payload(payload):
    from asperitas_agent.workflow_inspector import inspect_workflow_run_dict

    return inspect_workflow_run_dict(payload)


def test_missing_required_step_rejected():
    run = ready_run()
    plan = run.plan
    assert plan is not None
    payload = with_modified_plan(run, tuple(step for step in plan.steps if step.step_kind != "answer_plan"))
    decision = accept_workflow_artifact_dicts(payload, workflow_inspection_to_dict(inspect_workflow_run_dict_payload(payload)))

    assert decision.status == "rejected"
    assert "missing_answer_plan" in reason_ids(decision)


def test_failed_eval_gate_rejected():
    run = build_workflow_run(run_input(eval_gate={"ok": False}))
    decision = accept_workflow_artifacts(run, inspect_workflow_run(run))

    assert decision.status == "rejected"
    assert "failed_eval_gate_check" in reason_ids(decision)


def test_failed_evidence_or_source_step_rejected():
    run = ready_run()
    plan = run.plan
    assert plan is not None
    replacement = AgentWorkflowStep(
        step_kind="evidence_check",
        status="blocked",
        reason="evidence gate failed",
        risk_level="blocked",
        blocks_execution=True,
    )
    steps = tuple(replacement if step.step_kind == "evidence_check" else step for step in plan.steps)
    payload = with_modified_plan(run, steps)
    decision = accept_workflow_artifact_dicts(payload, workflow_inspection_to_dict(inspect_workflow_run_dict_payload(payload)))

    assert decision.status == "rejected"
    assert "failed_evidence_check" in reason_ids(decision)


def test_json_roundtrip_stable():
    decision = accept_workflow_artifacts(ready_run(), ready_inspection())
    first = json.dumps(workflow_acceptance_to_dict(decision), sort_keys=True, separators=(",", ":"))
    restored = workflow_acceptance_from_dict(json.loads(first))
    second = json.dumps(workflow_acceptance_to_dict(restored), sort_keys=True, separators=(",", ":"))

    assert restored.validate() == ()
    assert first == second


def test_explicit_output_writes_decision(tmp_path):
    decision = accept_workflow_artifacts(ready_run(), ready_inspection())
    output = tmp_path / "workflow_acceptance.json"

    written = write_workflow_acceptance_decision(decision, output)

    assert written == output
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "accepted"


def test_no_output_path_writes_nothing(tmp_path):
    run_path, inspection_path = write_artifacts(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_workflow_acceptance_gate.py",
            "--run",
            str(run_path),
            "--inspection",
            str(inspection_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout)["status"] == "accepted"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["workflow_inspection.json", "workflow_run_artifact.json"]


def test_overwrite_false_blocks_existing_output(tmp_path):
    decision = accept_workflow_artifacts(ready_run(), ready_inspection())
    output = tmp_path / "workflow_acceptance.json"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_workflow_acceptance_decision(decision, output, overwrite=False)


def test_create_dirs_behavior(tmp_path):
    decision = accept_workflow_artifacts(ready_run(), ready_inspection())
    output = tmp_path / "missing" / "workflow_acceptance.json"

    with pytest.raises(FileNotFoundError):
        write_workflow_acceptance_decision(decision, output, create_dirs=False)
    assert write_workflow_acceptance_decision(decision, output, create_dirs=True) == output


def test_cli_emits_valid_json(tmp_path):
    run_path, inspection_path = write_artifacts(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_workflow_acceptance_gate.py",
            "--run",
            str(run_path),
            "--inspection",
            str(inspection_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "accepted"
    assert payload["executes_plan"] is False


def test_no_retrieval_vector_llm_or_external_connector_imports_or_execution():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.workflow_acceptance;"
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
