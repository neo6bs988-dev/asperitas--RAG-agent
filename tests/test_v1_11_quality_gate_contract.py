from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "quality-gates.yml"
V1_11_STEP_NAME = "V1.11B public-safe development evaluation regression check"


def workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def step_block(text: str, step_name: str) -> str:
    marker = f"      - name: {step_name}\n"
    start = text.index(marker)
    next_step = text.find("\n      - name: ", start + len(marker))
    return text[start:] if next_step == -1 else text[start:next_step]


def test_v1_11_quality_gate_runs_validator_and_focused_tests():
    block = step_block(workflow_text(), V1_11_STEP_NAME)

    assert "python scripts/validate_v1_11b_representative_biology_compliance_dev.py" in block
    assert "python scripts/validate_v1_11b_representative_biology_compliance_dev.py --json" in block
    assert "python -m pytest -q tests/test_v1_11b_representative_biology_compliance_dev.py" in block


def test_v1_11_quality_gate_preserves_required_existing_gates_and_read_only_security():
    text = workflow_text()
    block = step_block(text, V1_11_STEP_NAME)

    assert "permissions:\n  contents: read" in text
    assert "pull_request_target:" not in text
    assert "V1.7D validator regression check" in text
    assert "V1.8B offline evaluator regression check" in text
    assert "- name: Run unit tests" in text
    assert "- name: Verify artifacts" in text
    assert "- name: Run baseline retrieval eval" in text
    assert "- name: Run MVP-003 metadata-aware retrieval eval" in text
    assert "- name: Run hybrid retrieval eval" in text
    assert "continue-on-error" not in block
    assert "${{ secrets." not in block
    assert "secrets." not in block
