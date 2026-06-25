from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = REPO_ROOT / "docs" / "V1_PERFORMANCE_CLOSURE_MATRIX.md"


def load_matrix_module():
    spec = importlib.util.spec_from_file_location(
        "check_v1_performance_closure_matrix", REPO_ROOT / "scripts" / "check_v1_performance_closure_matrix.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_closure_matrix_has_complete_rows_and_required_commands():
    module = load_matrix_module()

    assert module.check_matrix_text(REPO_ROOT) == []


def test_closure_matrix_preserves_roadmap_after_final_pre_rc_only():
    module = load_matrix_module()

    assert module.check_roadmap_text(REPO_ROOT) == []


def test_closure_matrix_checker_flags_protected_runtime_and_artifact_paths():
    module = load_matrix_module()

    errors = module.check_changed_files(
        (
            "docs/V1_PERFORMANCE_CLOSURE_MATRIX.md",
            "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/example.pdf",
            "data/chunks.jsonl",
            "src/asperitas_agent/retrieval_mvp003.py",
            "src/asperitas_agent/reranking.py",
        )
    )

    assert any("01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/example.pdf" in error for error in errors)
    assert any("data/chunks.jsonl" in error for error in errors)
    assert any("src/asperitas_agent/retrieval_mvp003.py" in error for error in errors)
    assert any("src/asperitas_agent/reranking.py" in error for error in errors)


def test_closure_matrix_gap_language_limits_next_step_to_p0_p1():
    text = MATRIX_PATH.read_text(encoding="utf-8").lower()

    assert "only p0/p1 items are allowed as the next remediation step." in text
    assert "p2 items stay in v1.1 or later performance-hardening work." in text
    assert "no-go for final rc readiness" in text
    assert "no-go for final rc, dry-run, internal release, or production claims" in text
    assert "production-grade" not in text
