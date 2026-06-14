from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_FILE = REPO_ROOT / "eval" / "golden_agent_queries.jsonl"
SCRIPT = REPO_ROOT / "scripts" / "run_golden_agent_eval.py"


def load_golden_eval_module():
    spec = importlib.util.spec_from_file_location("run_golden_agent_eval", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_golden_records() -> list[dict]:
    records = []
    with GOLDEN_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def test_golden_query_file_exists_and_is_valid_jsonl():
    assert GOLDEN_FILE.exists()
    records = load_golden_records()

    assert 5 <= len(records) <= 8
    assert len({record["id"] for record in records}) == len(records)
    required = {
        "id",
        "category",
        "query",
        "top_k",
        "expected_status",
        "min_evidence_count",
        "min_citation_count",
        "required_answer_substrings",
        "forbidden_answer_substrings",
    }
    assert all(required <= set(record) for record in records)


def test_golden_query_file_represents_required_categories():
    categories = {record["category"] for record in load_golden_records()}

    assert "company_identity" in categories
    assert "technology_platform" in categories
    assert "source_priority_sensitive" in categories
    assert "compliance_biosafety_caution" in categories
    assert "unsupported_abstention" in categories
    assert "citation_stress" in categories


def test_golden_eval_script_returns_valid_json_and_passes():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(result.stdout)
    assert report["ok"]
    assert report["total_cases"] == len(load_golden_records())
    assert report["passed_cases"] == report["total_cases"]
    assert report["failed_cases"] == 0
    assert report["protected_files_unchanged"]
    assert {"ok", "total_cases", "passed_cases", "failed_cases", "protected_files_unchanged", "cases"} <= set(report)
    assert all(
        {
            "schema",
            "status",
            "guardrail",
            "evidence_count",
            "citation_count",
            "citation_subset_integrity",
            "required_answer_substrings",
            "forbidden_answer_substrings",
            "required_evidence_labels",
            "source_priority",
            "determinism",
        }
        <= set(case["checks"])
        for case in report["cases"]
    )


def test_golden_eval_pretty_mode_outputs_valid_json():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pretty"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(result.stdout)
    assert report["ok"]
    assert "\n  " in result.stdout


def test_golden_eval_rejects_invalid_temp_golden_file(tmp_path):
    invalid = tmp_path / "golden_agent_queries.jsonl"
    invalid.write_text(json.dumps({"id": "BROKEN", "query": "missing fields"}) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--golden-file", str(invalid)],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert not report["ok"]
    assert "missing required fields" in report["error"]


def test_golden_eval_helpers_check_determinism_citations_and_protected_hashing():
    module = load_golden_eval_module()

    assert callable(module.protected_file_hashes)
    assert callable(module._citation_subset_ok)
    assert callable(module.evaluate_case)

    hashes = module.protected_file_hashes()
    assert "data/chunks.jsonl" in hashes
    assert "data/source_registry.csv" in hashes
    assert "eval/retrieval_questions.jsonl" in hashes
    assert "eval/expected_sources.jsonl" in hashes
    assert "eval/golden_agent_queries.jsonl" in hashes
    assert all(len(value) == 64 for value in hashes.values())

    source = SCRIPT.read_text(encoding="utf-8")
    assert '"determinism"' in source
    assert "citation_subset_integrity" in source
    assert "protected_file_hashes" in source
