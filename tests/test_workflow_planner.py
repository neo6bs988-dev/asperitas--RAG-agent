from __future__ import annotations

import json
import subprocess
import sys

from asperitas_agent.workflow_planner import build_workflow_plan, build_workflow_request, summarize_workflow_plan


def step(plan, step_kind):
    return next(item for item in plan.steps if item.step_kind == step_kind)


def test_valid_low_risk_request_creates_full_plan():
    plan = build_workflow_plan(
        build_workflow_request("Summarize source-grounded evidence for X"),
        eval_gate="passed",
        source_status="available",
    )

    assert [item.step_kind for item in plan.steps] == [
        "source_check",
        "skill_selection",
        "risk_preflight",
        "eval_gate_check",
        "evidence_check",
        "answer_plan",
        "audit_ready",
    ]
    assert plan.validate() == ()


def test_missing_source_status_requires_approval():
    plan = build_workflow_plan(build_workflow_request("Summarize X"), eval_gate="passed", source_status=None)

    assert plan.planner_decision.decision == "requires_human_approval"
    assert step(plan, "source_check").status == "requires_human_approval"
    assert plan.ready_for_execution is False


def test_blocked_risk_flag_blocks_plan():
    plan = build_workflow_plan(
        build_workflow_request("Summarize X"),
        eval_gate="passed",
        source_status="available",
        risk_flags=("blocked",),
    )

    assert plan.planner_decision.decision == "blocked"
    assert all(item.status == "blocked" for item in plan.steps)


def test_high_risk_flag_requires_approval():
    plan = build_workflow_plan(
        build_workflow_request("Summarize X"),
        eval_gate="passed",
        source_status="available",
        risk_flags=("high",),
    )

    assert plan.planner_decision.decision == "requires_human_approval"
    assert step(plan, "risk_preflight").status == "requires_human_approval"
    assert summarize_workflow_plan(plan)["approval_steps"]


def test_failed_eval_gate_blocks_plan():
    plan = build_workflow_plan(build_workflow_request("Summarize X"), eval_gate="failed", source_status="available")

    assert plan.planner_decision.decision == "blocked"
    assert step(plan, "eval_gate_check").status == "blocked"


def test_missing_required_skill_requires_approval():
    plan = build_workflow_plan(
        build_workflow_request("Summarize X", required_skill_id="asperitas_workflow"),
        available_skills=("mvp_implementation",),
        eval_gate="passed",
        source_status="available",
    )

    assert plan.planner_decision.decision == "requires_human_approval"
    assert step(plan, "skill_selection").status == "requires_human_approval"


def test_available_skill_allows_skill_step():
    plan = build_workflow_plan(
        build_workflow_request("Summarize X", required_skill_id="asperitas_workflow"),
        available_skills=("asperitas_workflow",),
        eval_gate="passed",
        source_status="available",
    )

    assert step(plan, "skill_selection").status == "allowed"


def test_all_gates_allowed_makes_ready_for_execution_true():
    plan = build_workflow_plan(
        build_workflow_request("Summarize X", required_skill_id="asperitas_workflow"),
        available_skills=("asperitas_workflow",),
        eval_gate="passed",
        source_status="available",
        risk_flags=("low",),
    )

    assert plan.ready_for_execution is True
    assert plan.planner_decision.ok is True
    assert all(item.status == "allowed" for item in plan.steps)
    assert plan.executes_plan is False


def test_cli_emits_valid_json():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/plan_agent_workflow.py",
            "--request",
            "Summarize source-grounded evidence for X",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["executes_plan"] is False
    assert payload["planner_decision"]["decision"] == "allowed"


def test_planner_does_not_import_execute_retrieval_vector_llm_or_external_connectors():
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import asperitas_agent.workflow_planner;"
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
