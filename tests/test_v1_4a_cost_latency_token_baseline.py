from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "measure_v1_4_cost_latency_token_baseline.py"
PROTECTED = (
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "eval/expected_sources.jsonl",
    "eval/golden_agent_queries.jsonl",
    "eval/retrieval_questions.jsonl",
)


def load_module():
    spec = importlib.util.spec_from_file_location("measure_v1_4_cost_latency_token_baseline", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_measurement_helpers_are_deterministic_and_count_duplicates():
    module = load_module()

    assert module.approx_tokens("") == 0
    assert module.approx_tokens("abcd") == 1
    assert module.approx_tokens("abcde") == 2
    assert module.answer_section_count("Bottom line:\nNext action:") == 2

    duplicates = module.duplicate_counts(
        [
            {"chunk_id": "a", "source_path": "same.md"},
            {"chunk_id": "a", "source_path": "same.md"},
            {"chunk_id": "b", "source_path": "same.md"},
        ]
    )
    assert duplicates["duplicate_evidence_count"] == 1
    assert duplicates["duplicate_source_count"] == 2


def test_measurement_script_source_contains_no_behavior_change_import_targets():
    source = SCRIPT.read_text(encoding="utf-8")

    assert "search_chunks_mvp003" in source
    assert "answer_behavior_changed" in source
    assert "source_artifacts_mutated" in source
    assert "retrieval_scoring_changed" in source
    assert "write_text(args.output" in source


def test_measurement_script_writes_temp_outputs_and_preserves_protected_files(tmp_path):
    module = load_module()
    before = module.hashes(PROTECTED)
    output = tmp_path / "baseline.json"
    doc = tmp_path / "baseline.md"
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
    after = module.hashes(PROTECTED)
    assert before == after

    report = json.loads(output.read_text(encoding="utf-8"))
    stdout_report = json.loads(result.stdout)
    assert report["summary"] == stdout_report["summary"]
    assert report["ok"]
    assert report["scope_lock"]["measurement_only"] is True
    assert report["scope_lock"]["answer_behavior_changed"] is False
    assert report["scope_lock"]["retrieval_scoring_changed"] is False
    assert report["scope_lock"]["source_artifacts_mutated"] is False
    assert report["summary"]["case_count"] >= 20
    assert report["summary"]["suite_counts"]["golden_eval"] == 6
    assert "answer_char_count" in report["measurement_fields"]
    assert "retrieved_context_approx_token_count" in report["measurement_fields"]
    assert doc.exists()
    assert readme.exists()
