from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTRINE_PATH = REPO_ROOT / "docs" / "V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md"


def load_scope_module():
    spec = importlib.util.spec_from_file_location(
        "check_v1_stage_gate_scope", REPO_ROOT / "scripts" / "check_v1_stage_gate_scope.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_playbook_v3_stage_gate_doctrine_preserves_full_v1_roadmap():
    text = DOCTRINE_PATH.read_text(encoding="utf-8")

    assert "Scope: Playbook v3 Absorption plus Benchmark Absorption & Stage-Gate Calibration only" in text
    assert "| 1. Playbook v3 Absorption | Completed by this process subtask |" in text
    assert "| 2. Benchmark Absorption & Stage-Gate Calibration | Completed by this process subtask |" in text
    for step in (
        "3. MVP Performance Pack Backfill",
        "4. V1 Performance Closure Matrix",
        "5. P0/P1 Gap Fix Only",
        "6. Final Pre-RC Regression",
        "7. v1.0.0-rc1",
        "8. Internal Dry-run",
        "9. v1.0.0-internal",
    ):
        assert f"| {step} | Pending |" in text


def test_playbook_v3_stage_gate_doctrine_does_not_claim_runtime_or_release_completion():
    text = DOCTRINE_PATH.read_text(encoding="utf-8").lower()

    assert "ready for next v1 step" in text
    assert "ready for internal release" not in text
    assert "production-grade" not in text
    assert "production deployment" not in text
    assert "autonomous ingestion" not in text
    assert "source expansion complete" not in text
    assert "full v1 closure" not in text


def test_stage_gate_scope_check_flags_protected_runtime_and_artifact_paths():
    module = load_scope_module()

    errors = module.check_changed_files(
        (
            "docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md",
            "data/chunks.jsonl",
            "src/asperitas_agent/retrieval_mvp003.py",
        )
    )

    assert any("data/chunks.jsonl" in error for error in errors)
    assert any("src/asperitas_agent/retrieval_mvp003.py" in error for error in errors)


def test_stage_gate_scope_check_passes_for_docs_process_and_test_paths():
    module = load_scope_module()

    assert module.check_changed_files(
        (
            "docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md",
            "docs/ROADMAP.md",
            "scripts/check_v1_stage_gate_scope.py",
            "tests/test_v1_stage_gate_scope.py",
        )
    ) == []
