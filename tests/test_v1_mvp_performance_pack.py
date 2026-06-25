from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = REPO_ROOT / "docs" / "V1_MVP_PERFORMANCE_PACK.md"


def load_pack_module():
    spec = importlib.util.spec_from_file_location(
        "check_v1_mvp_performance_pack", REPO_ROOT / "scripts" / "check_v1_mvp_performance_pack.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_performance_pack_scorecard_has_metric_threshold_command_and_go_no_go_for_each_mvp():
    module = load_pack_module()

    text_errors = module.check_pack_text(REPO_ROOT)

    assert text_errors == []


def test_performance_pack_checker_flags_protected_runtime_and_artifact_paths():
    module = load_pack_module()

    errors = module.check_changed_files(
        (
            "docs/V1_MVP_PERFORMANCE_PACK.md",
            "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/example.pdf",
            "src/asperitas_agent/answer_generation.py",
            "src/asperitas_agent/retrieval_mvp003.py",
        )
    )

    assert any("01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/example.pdf" in error for error in errors)
    assert any("src/asperitas_agent/answer_generation.py" in error for error in errors)
    assert any("src/asperitas_agent/retrieval_mvp003.py" in error for error in errors)


def test_performance_pack_preserves_v1_boundaries_and_gap_labels():
    text = PACK_PATH.read_text(encoding="utf-8").lower()

    assert "docs/tests/checks only" in text
    assert "playbook v3 and stage-gate status" in text
    assert "p0 | none introduced by this docs/tests/checks backfill." in text
    assert "v1 performance closure matrix" in text
    assert "final pre-rc regression" in text
    assert "no-go for final rc readiness" in text
    assert "production-grade" not in text
