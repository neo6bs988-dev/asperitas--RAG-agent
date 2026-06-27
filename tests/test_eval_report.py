from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from asperitas_agent.eval_report import (
    EvalReportError,
    build_eval_report,
    load_metric_results,
    summarize_eval_report,
)
from asperitas_agent.eval_metrics import EvalMetricResult


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate_eval_report.py"


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def valid_payload(results=None):
    return {
        "report_id": "local_eval_report",
        "metadata": {"run_id": "unit-test"},
        "results": results
        if results is not None
        else [
            {
                "metric_id": "context_precision",
                "value": 0.9,
                "passed": True,
                "mode": "strict",
                "notes": [],
            }
        ],
    }


def test_load_valid_metric_result_json(tmp_path):
    path = write_json(tmp_path / "metric_results.json", valid_payload())

    results = load_metric_results(path)

    assert results == [EvalMetricResult("context_precision", 0.9, True, "strict")]


def test_malformed_json_fails(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(EvalReportError, match="malformed JSON"):
        load_metric_results(path)


def test_empty_results_fail(tmp_path):
    path = write_json(tmp_path / "empty.json", valid_payload(results=[]))

    with pytest.raises(EvalReportError, match="results must not be empty"):
        load_metric_results(path)
    with pytest.raises(EvalReportError, match="results must not be empty"):
        build_eval_report([])


def test_strict_pass_report_ok_true():
    report = build_eval_report([EvalMetricResult("context_precision", 0.9, True, "strict")])

    summary = summarize_eval_report(report)

    assert summary["ok"] is True
    assert summary["passed_count"] == 1
    assert summary["failed_count"] == 0


def test_strict_fail_report_ok_false():
    report = build_eval_report([EvalMetricResult("context_precision", 0.4, False, "strict")])

    summary = summarize_eval_report(report)

    assert summary["ok"] is False
    assert summary["failed_count"] == 1


def test_report_only_result_does_not_fail_gate():
    report = build_eval_report([EvalMetricResult("faithfulness", 0.2, False, "report_only")])

    summary = summarize_eval_report(report)

    assert summary["ok"] is True
    assert summary["report_only_count"] == 1
    assert summary["failed_count"] == 0


def test_unknown_metric_warns():
    report = build_eval_report([EvalMetricResult("custom_metric", 1.0, False, "report_only")])

    summary = summarize_eval_report(report)

    assert summary["ok"] is True
    assert summary["warnings"] == ["unknown metric_id: custom_metric"]
    assert summary["errors"] == []


def test_summary_counts_correct():
    report = build_eval_report(
        [
            EvalMetricResult("context_precision", 0.9, True, "strict"),
            EvalMetricResult("context_recall", 0.7, False, "strict"),
            EvalMetricResult("faithfulness", None, None, "report_only"),
        ],
        metadata={"report_id": "count_report"},
    )

    summary = summarize_eval_report(report)

    assert summary["report_id"] == "count_report"
    assert summary["passed_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["strict_count"] == 2
    assert summary["report_only_count"] == 1
    assert summary["metadata"]["unsupported_claim_rate_higher_is_better"] is False


def test_script_emits_json(tmp_path):
    path = write_json(tmp_path / "metric_results.json", valid_payload())
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(path), "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["report_id"] == "local_eval_report"
    assert payload["strict_count"] == 1


def test_no_retrieval_or_source_artifact_files_modified():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
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
