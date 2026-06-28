from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_v1_4e_final_optimization_closeout.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_v1_4e_final_optimization_closeout", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_v1_4e_report_summarizes_expected_metrics_and_go_decision():
    module = load_module()
    report = module.build_report()

    assert report["ok"]
    assert report["summary"]["v1_4b_context_compression"]["retrieved_context_approx_token_delta"] == -5232
    assert report["summary"]["v1_4c_eval_harness_caching"]["cache_hit_count"] == 108
    assert report["summary"]["v1_4c_eval_harness_caching"]["net_runtime_delta_ms"] == 2913.355
    assert report["summary"]["v1_4c_eval_harness_caching"]["classification"] == "infra/measurement only; not a latency win"
    assert report["summary"]["v1_4d_answer_boilerplate_trimming"]["answer_approx_token_delta"] == -871
    assert report["v1_5_readiness"]["decision"] == "GO"
    assert report["scope_lock"]["measurement_reporting_only"] is True
    assert report["scope_lock"]["answer_behavior_changed"] is False
    assert report["scope_lock"]["retrieval_scoring_changed"] is False
    assert report["scope_lock"]["source_artifacts_mutated"] is False


def test_v1_4e_report_preserves_truth_boundary_and_separates_inference():
    module = load_module()
    report = module.build_report()

    truth = report["truth_boundary_statement"].casefold()
    assert "not a production deployment claim" in truth
    assert "legal or regulatory clearance" in truth
    assert "biological validation" in truth
    assert "broad answer-quality proof" in truth
    assert report["measured_facts"]
    assert report["inference_and_recommendation"]
    assert report["blocked_claim_fragments_absent"] is True


def test_v1_4e_script_writes_temp_outputs(tmp_path):
    output = tmp_path / "final_optimization_closeout.json"
    doc = tmp_path / "V1_4E_FINAL_OPTIMIZATION_CLOSEOUT.md"
    readme = tmp_path / "README.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--overwrite",
            "--json",
            "--output",
            str(output),
            "--doc-output",
            str(doc),
            "--readme-output",
            str(readme),
        ],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(output.read_text(encoding="utf-8"))
    stdout_report = json.loads(result.stdout)
    assert report["summary"] == stdout_report["summary"]
    assert "V1.4C net runtime delta: 2913.355 ms" in doc.read_text(encoding="utf-8")
    assert "measurement/reporting only" in readme.read_text(encoding="utf-8")
