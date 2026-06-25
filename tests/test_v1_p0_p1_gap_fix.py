from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_gap_fix_module():
    spec = importlib.util.spec_from_file_location(
        "check_v1_p0_p1_gap_fix", REPO_ROOT / "scripts" / "check_v1_p0_p1_gap_fix.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_release_docs(root: Path, text: str) -> None:
    docs = (
        root / "docs" / "V1_RELEASE_CLOSEOUT.md",
        root / "docs" / "releases" / "V1_0_0_RC1_RELEASE_NOTES.md",
        root / "docs" / "releases" / "V1_0_0_RC1_CLOSEOUT_PACKET.md",
        root / "docs" / "releases" / "V1_0_0_RC1_MANUAL_RELEASE_STEPS.md",
    )
    for path in docs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_gap_fix_checker_passes_current_release_posture_docs():
    module = load_gap_fix_module()

    assert module.check_release_posture_docs(REPO_ROOT) == []


def test_gap_fix_checker_blocks_old_internal_rc_status(tmp_path):
    module = load_gap_fix_module()
    write_release_docs(
        tmp_path,
        "Status: internal release candidate\n"
        "fresh command output is required before final RC, internal dry-run, internal release, publish release notes, or claim GO.\n",
    )

    errors = module.check_release_posture_docs(tmp_path)

    assert any("Status: internal release candidate" in error for error in errors)


def test_gap_fix_checker_requires_fresh_output_guard(tmp_path):
    module = load_gap_fix_module()
    write_release_docs(tmp_path, "Status: draft only; final RC and internal release remain pending\n")

    errors = module.check_release_posture_docs(tmp_path)

    assert any("fresh command output" in error for error in errors)
    assert any("release notes" in error for error in errors)
    assert any("GO claims" in error for error in errors)


def test_gap_fix_checker_blocks_unguarded_go_claim(tmp_path):
    module = load_gap_fix_module()
    write_release_docs(
        tmp_path,
        "Status: draft only; final RC and internal release remain pending\n"
        "fresh command output is required before publish release notes or claim GO.\n"
        "internal dry-run remains pending.\n"
        "GO for final RC.\n",
    )

    errors = module.check_release_posture_docs(tmp_path)

    assert any("GO for final RC" in error for error in errors)
