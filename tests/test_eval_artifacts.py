from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from asperitas_agent.eval_artifacts import (
    EvalArtifactError,
    EvalReportArtifact,
    build_eval_report_artifact,
    load_eval_report_artifact,
    write_eval_report_artifact,
)
from asperitas_agent.eval_metrics import EvalMetricResult
from asperitas_agent.eval_report import build_eval_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate_eval_report.py"


def report_with_results(results):
    return build_eval_report(results, metadata={"report_id": "artifact_test_report"})


def test_build_artifact_from_valid_report():
    report = report_with_results([EvalMetricResult("context_precision", 0.9, True, "strict")])

    artifact = build_eval_report_artifact(report, metadata={"run_id": "unit-test"})

    assert artifact.report_id == "artifact_test_report"
    assert artifact.ok is True
    assert artifact.metadata == {"run_id": "unit-test"}
    assert artifact.summary["strict_count"] == 1
    assert artifact.validate() == ()


def test_write_artifact_to_temp_path(tmp_path):
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("context_precision", 0.9, True, "strict")])
    )
    path = tmp_path / "report_artifact.json"

    written = write_eval_report_artifact(artifact, path)

    assert written == path
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["artifact_id"] == artifact.artifact_id


def test_load_artifact_roundtrip(tmp_path):
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("context_precision", 0.9, True, "strict")])
    )
    path = write_eval_report_artifact(artifact, tmp_path / "roundtrip.json")

    loaded = load_eval_report_artifact(path)

    assert loaded.to_dict() == artifact.to_dict()
    assert json.dumps(loaded.to_dict(), sort_keys=True) == json.dumps(artifact.to_dict(), sort_keys=True)


def test_overwrite_false_blocks_existing_file(tmp_path):
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("context_precision", 0.9, True, "strict")])
    )
    path = write_eval_report_artifact(artifact, tmp_path / "exists.json")

    with pytest.raises(EvalArtifactError, match="already exists"):
        write_eval_report_artifact(artifact, path)

    assert write_eval_report_artifact(artifact, path, overwrite=True) == path


def test_create_dirs_behavior(tmp_path):
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("context_precision", 0.9, True, "strict")])
    )
    nested_path = tmp_path / "missing" / "dir" / "artifact.json"

    with pytest.raises(EvalArtifactError, match="parent directory does not exist"):
        write_eval_report_artifact(artifact, nested_path)

    assert write_eval_report_artifact(artifact, nested_path, create_dirs=True) == nested_path


def test_malformed_artifact_fails(tmp_path):
    path = tmp_path / "malformed.json"
    path.write_text(json.dumps({"artifact_id": "missing-fields"}), encoding="utf-8")

    with pytest.raises(EvalArtifactError, match="artifact missing fields"):
        load_eval_report_artifact(path)

    broken = EvalReportArtifact(
        artifact_id="bad",
        schema_version="bad-version",
        created_at_utc="2026-06-24T00:00:00Z",
        report_id="report",
        ok=True,
        summary={},
        report={},
        metadata={},
        provenance={},
        warnings=[],
        errors=[],
    )
    assert "unsupported schema_version: bad-version" in broken.validate()


def test_strict_fail_preserved():
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("context_precision", 0.2, False, "strict")])
    )

    assert artifact.ok is False
    assert artifact.summary["failed_count"] == 1
    assert artifact.report["aggregate"]["failed_strict_metric_ids"] == ["context_precision"]


def test_report_only_preserved():
    artifact = build_eval_report_artifact(
        report_with_results([EvalMetricResult("faithfulness", 0.1, False, "report_only")])
    )

    assert artifact.ok is True
    assert artifact.summary["report_only_count"] == 1
    assert artifact.summary["failed_count"] == 0


def test_script_output_writes_artifact(tmp_path):
    input_path = tmp_path / "metric_results.json"
    output_path = tmp_path / "artifact.json"
    input_path.write_text(
        json.dumps(
            {
                "report_id": "script_artifact",
                "metadata": {"run_id": "script-test"},
                "results": [
                    {
                        "metric_id": "context_precision",
                        "value": 0.9,
                        "passed": True,
                        "mode": "strict",
                        "notes": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(input_path), "--output", str(output_path), "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["metadata"]["artifact_path"] == str(output_path)
    loaded = load_eval_report_artifact(output_path)
    assert loaded.report_id == "script_artifact"


def test_no_default_output_path_write(tmp_path):
    input_path = tmp_path / "metric_results.json"
    input_path.write_text(
        json.dumps(
            {
                "report_id": "no_default_write",
                "metadata": {},
                "results": [
                    {
                        "metric_id": "context_precision",
                        "value": 0.9,
                        "passed": True,
                        "mode": "strict",
                        "notes": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(input_path), "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.glob("*.json")) == [input_path]
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
