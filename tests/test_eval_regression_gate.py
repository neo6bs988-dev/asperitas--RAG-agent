from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from asperitas_agent.eval_artifacts import build_eval_report_artifact, write_eval_report_artifact
from asperitas_agent.eval_metrics import EvalMetricResult
from asperitas_agent.eval_regression_gate import EvalRegressionPolicy, compare_eval_artifacts
from asperitas_agent.eval_report import build_eval_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "run_eval_regression_gate.py"
REQUIRED_RESULTS = [
    EvalMetricResult("faithfulness", 0.90, True, "strict"),
    EvalMetricResult("answer_relevance", 0.90, True, "strict"),
    EvalMetricResult("context_precision", 0.90, True, "strict"),
    EvalMetricResult("context_recall", 0.90, True, "strict"),
    EvalMetricResult("unsupported_claim_rate", 0.0, True, "strict"),
]


def artifact(results=None, report_id="report"):
    report = build_eval_report(results or REQUIRED_RESULTS, metadata={"report_id": report_id})
    return build_eval_report_artifact(report)


def write_artifact(path: Path, results=None, report_id="report"):
    return write_eval_report_artifact(artifact(results, report_id), path)


def test_candidate_ok_false_fails_gate():
    candidate = artifact(
        [
            *REQUIRED_RESULTS[:-1],
            EvalMetricResult("unsupported_claim_rate", 0.2, False, "strict"),
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is False
    assert "candidate ok=false" in decision.reasons


def test_new_strict_failure_fails_gate():
    candidate = artifact(
        [
            EvalMetricResult("faithfulness", 0.90, False, "strict"),
            *REQUIRED_RESULTS[1:],
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is False
    assert any("new strict failure: faithfulness" == reason for reason in decision.reasons)


def test_strict_metric_drop_beyond_tolerance_fails_gate():
    candidate = artifact(
        [
            EvalMetricResult("faithfulness", 0.87, True, "strict"),
            *REQUIRED_RESULTS[1:],
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is False
    assert any(reason.startswith("strict metric drop beyond tolerance: faithfulness") for reason in decision.reasons)


def test_unsupported_claim_rate_increase_fails_gate():
    candidate = artifact(
        [
            *REQUIRED_RESULTS[:-1],
            EvalMetricResult("unsupported_claim_rate", 0.01, True, "strict"),
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is False
    assert any(reason.startswith("unsupported_claim_rate increase above tolerance") for reason in decision.reasons)


def test_report_only_metric_does_not_fail_gate():
    candidate = artifact(
        [
            *REQUIRED_RESULTS,
            EvalMetricResult("faithfulness_report_only_shadow", 0.1, False, "report_only"),
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is True


def test_unknown_metric_warns_only():
    candidate = artifact([*REQUIRED_RESULTS, EvalMetricResult("custom_metric", 0.1, False, "report_only")], "candidate")

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is True
    assert any("unknown metric ids in candidate: custom_metric" == warning for warning in decision.warnings)


def test_passing_candidate_returns_ok_true():
    candidate = artifact(
        [
            EvalMetricResult("faithfulness", 0.89, True, "strict"),
            *REQUIRED_RESULTS[1:],
        ],
        "candidate",
    )

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is True
    assert decision.decision == "pass"
    assert decision.reasons == ()


def test_missing_required_strict_metric_fails_gate():
    candidate = artifact(REQUIRED_RESULTS[:-1], "candidate")

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate)

    assert decision.ok is False
    assert "missing strict metric from candidate: unsupported_claim_rate" in decision.reasons


def test_malformed_artifact_inputs_fail_closed(tmp_path):
    missing = tmp_path / "missing.json"

    decision = compare_eval_artifacts(missing, artifact(report_id="candidate"))

    assert decision.ok is False
    assert any(reason.startswith("baseline malformed") for reason in decision.reasons)


def test_regression_gate_cli_emits_valid_json(tmp_path):
    baseline = write_artifact(tmp_path / "baseline.json", report_id="baseline")
    candidate = write_artifact(tmp_path / "candidate.json", report_id="candidate")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["decision"] == "pass"


def test_no_retrieval_source_or_eval_fixture_files_modified():
    diff = subprocess.run(
        ["git", "diff", "--name-only", "--", "data", "07_EVALS", "01_RAW_SOURCES", "03_PROCESSED_KB", "04_VECTOR_DB"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert diff.returncode == 0
    assert diff.stdout == ""


def test_policy_serialization_and_unknown_metric_block_option():
    policy = EvalRegressionPolicy(allow_unknown_metrics=False)
    candidate = artifact([*REQUIRED_RESULTS, EvalMetricResult("custom_metric", 0.1, False, "report_only")], "candidate")

    decision = compare_eval_artifacts(artifact(report_id="baseline"), candidate, policy)

    assert decision.ok is False
    assert decision.to_dict()["policy"]["allow_unknown_metrics"] is False
