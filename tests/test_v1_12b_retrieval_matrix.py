from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_v1_12b_retrieval_matrix.py"


def load_matrix_module():
    spec = importlib.util.spec_from_file_location("run_v1_12b_retrieval_matrix", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_matrix_declares_exact_stable_mode_order():
    module = load_matrix_module()
    assert module.mode_names() == (
        "baseline", "mvp003", "vector", "legacy-hybrid",
        "legacy-hybrid+deterministic-test", "legacy-hybrid+deterministic-test+fail-closed",
    )


def test_matrix_command_uses_current_python_and_opt_in_diagnostics():
    module = load_matrix_module()
    args = SimpleNamespace(limit=5, measure_diagnostics=True)
    command = module.build_command(module.MODE_SPECS[4], args)
    assert command[0] == sys.executable
    assert "--measure-diagnostics" in command
    assert command[command.index("--retriever") + 1] == "hybrid"
    assert command[command.index("--reranker-policy") + 1] == "direct"


def test_matrix_oracle_affected_mode_is_non_promotable(monkeypatch):
    module = load_matrix_module()
    payload = {"total_questions": 1, "per_question": [{"question_id": "Q1"}], "diagnostics": {"retrieval_latency_ms": {"count": 1}}}
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr=""))
    record = module.mode_record(module.MODE_SPECS[3], SimpleNamespace(limit=5, measure_diagnostics=False, timeout_seconds=1))
    assert record["status"] == "non_promotable"
    assert record["promotion_eligible"] is False
    assert record["promotion_blockers"] == ["oracle_affected_legacy_hybrid"]


def test_matrix_subprocess_contract_forces_utf8(monkeypatch):
    module = load_matrix_module()
    captured = {}

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(returncode=1, stdout="", stderr="failure")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    module.mode_record(module.MODE_SPECS[0], SimpleNamespace(limit=5, measure_diagnostics=False, timeout_seconds=1))

    assert captured["encoding"] == "utf-8"
    assert captured["errors"] == "replace"


def test_matrix_atomic_output_round_trips(tmp_path):
    module = load_matrix_module()
    output = tmp_path / "matrix.json"
    module.write_json_atomically(output, {"schema_version": "test"})
    assert json.loads(output.read_text(encoding="utf-8")) == {"schema_version": "test"}
