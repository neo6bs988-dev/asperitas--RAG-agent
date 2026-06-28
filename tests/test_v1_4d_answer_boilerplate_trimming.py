from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from asperitas_agent.agent_runner import ask_agent


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_v1_4d_answer_boilerplate_trimming.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_v1_4d_answer_boilerplate_trimming", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_v1_4d_answer_keeps_required_sections_and_trims_repeated_caveat():
    response = ask_agent(
        "Can we describe Asperitas as production deployed and biologically validated?",
        top_k=2,
    ).to_json()
    answer = response["answer"]

    for heading in (
        "Bottom line:",
        "Internal facts:",
        "Key evidence:",
        "Inference:",
        "Speculation:",
        "Verification needed:",
        "Missing evidence:",
        "Limitations/truth-boundary:",
        "Next action:",
    ):
        assert heading in answer
    assert "this draft is based only on the retrieved evidence" not in answer
    assert "supports this evidence item" not in answer
    assert response["citations_used"]


def test_v1_4d_report_builder_detects_token_reduction_and_preservation():
    module = load_module()
    report = module.build_report()

    assert report["ok"]
    assert report["summary"]["answer_approx_token_delta"] < 0
    assert report["summary"]["section_count_delta"] == 0
    assert report["summary"]["citation_count_preserved"] is True
    assert report["summary"]["evidence_count_preserved"] is True
    assert report["summary"]["source_paths_preserved"] is True
    assert report["summary"]["retrieval_scoring_changed"] is False
    assert report["summary"]["source_artifacts_mutated"] is False


def test_v1_4d_script_writes_temp_outputs(tmp_path):
    output = tmp_path / "answer_boilerplate_trimming.json"
    doc = tmp_path / "V1_4D_ANSWER_BOILERPLATE_TRIMMING_REPORT.md"
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
    assert doc.exists()
    assert readme.exists()
