from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from asperitas_agent.eval_artifacts import build_eval_report_artifact, write_eval_report_artifact
from asperitas_agent.eval_manifest import (
    EvalManifestError,
    build_eval_manifest,
    load_eval_manifest,
    write_eval_manifest,
)
from asperitas_agent.eval_metrics import EvalMetricResult
from asperitas_agent.eval_report import build_eval_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_eval_manifest.py"


def write_artifact(path: Path, results=None):
    report = build_eval_report(
        results
        or [
            EvalMetricResult("context_precision", 0.9, True, "strict"),
            EvalMetricResult("faithfulness", 0.8, True, "report_only"),
        ],
        metadata={"report_id": path.stem},
    )
    artifact = build_eval_report_artifact(report)
    return write_eval_report_artifact(artifact, path)


def test_manifest_builds_from_explicit_artifact_paths(tmp_path):
    first = write_artifact(tmp_path / "first.json")
    second = write_artifact(tmp_path / "second.json")

    manifest = build_eval_manifest([first, second], metadata={"run": "unit"})

    assert len(manifest.entries) == 2
    assert manifest.metadata == {"run": "unit"}
    assert manifest.entries[0].artifact_path == str(first)
    assert manifest.validate() == ()


def test_manifest_write_load_roundtrip_stable(tmp_path):
    artifact_path = write_artifact(tmp_path / "artifact.json")
    manifest = build_eval_manifest([artifact_path])
    path = write_eval_manifest(manifest, tmp_path / "manifest.json")

    loaded = load_eval_manifest(path)

    assert loaded.to_dict() == manifest.to_dict()
    assert json.dumps(loaded.to_dict(), sort_keys=True) == json.dumps(manifest.to_dict(), sort_keys=True)


def test_manifest_no_default_write(tmp_path):
    artifact_path = write_artifact(tmp_path / "artifact.json")
    build_eval_manifest([artifact_path])

    assert sorted(path.name for path in tmp_path.iterdir()) == ["artifact.json"]
    with pytest.raises(EvalManifestError, match="explicit output path is required"):
        write_eval_manifest(build_eval_manifest([artifact_path]), "")


def test_missing_artifact_path_fails_closed(tmp_path):
    with pytest.raises(EvalManifestError, match="could not load artifact"):
        build_eval_manifest([tmp_path / "missing.json"])


def test_malformed_artifact_fails_closed(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"artifact_id": "bad"}), encoding="utf-8")

    with pytest.raises(EvalManifestError, match="could not load artifact"):
        build_eval_manifest([path])


def test_manifest_cli_emits_valid_json(tmp_path):
    artifact_path = write_artifact(tmp_path / "artifact.json")
    manifest_path = tmp_path / "manifest.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--artifact",
            str(artifact_path),
            "--output",
            str(manifest_path),
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
    assert payload["entry_count"] == 1
    assert manifest_path.exists()
