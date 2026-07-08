from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_golden_set.jsonl"
GENERATED_CASES_PATH = REPO_ROOT / "eval" / "v1_8b_generated_answer_scoring_cases.jsonl"
EVALUATOR_PATH = REPO_ROOT / "scripts" / "evaluate_v1_8b_offline_answer_scoring.py"


def load_evaluator_module():
    spec = importlib.util.spec_from_file_location("v1_8b_evaluator", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


evaluator = load_evaluator_module()


def read_generated_cases() -> list[dict]:
    return [json.loads(line) for line in GENERATED_CASES_PATH.read_text(encoding="utf-8").splitlines()]


def read_golden_case(case_id: str) -> dict:
    for line in GOLDEN_SET_PATH.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["id"] == case_id:
            return record
    raise AssertionError(f"missing golden case {case_id}")


def write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    return path


def report_for(generated_cases_path: Path):
    return evaluator.evaluate_paths(golden_set_path=GOLDEN_SET_PATH, generated_cases_path=generated_cases_path)


def test_current_v1_8b_generated_answer_fixture_file_passes_evaluator():
    report = evaluator.evaluate_paths()

    assert report.ok
    assert report.case_count == 5
    assert report.pass_count == 1
    assert report.fail_count == 3
    assert report.review_count == 1
    assert not report.errors


def test_malformed_generated_answer_jsonl_fails(tmp_path):
    broken_path = tmp_path / "broken.jsonl"
    broken_path.write_text('{"case_id": ', encoding="utf-8")

    report = report_for(broken_path)

    assert not report.ok
    assert any("JSON parse error" in error for error in report.errors)


def test_unknown_v1_7c_case_id_fails(tmp_path):
    records = read_generated_cases()
    records[0]["case_id"] = "v1_7c_unknown_case"
    broken_path = write_jsonl(tmp_path / "unknown_case.jsonl", records)

    report = report_for(broken_path)

    assert not report.ok
    assert any("unknown V1.7C case_id" in error for error in report.errors)
    assert any(result.detected_failures == ("input_contract_error",) for result in report.results)


def test_missing_required_generated_answer_field_fails(tmp_path):
    records = read_generated_cases()
    del records[0]["generated_answer"]
    broken_path = write_jsonl(tmp_path / "missing_field.jsonl", records)

    report = report_for(broken_path)

    assert not report.ok
    assert any("missing required field(s): generated_answer" in error for error in report.errors)


def test_forbidden_biological_activity_overclaim_is_detected():
    golden_case = read_golden_case("v1_7c_unsupported_biological_activity")

    result = evaluator.evaluate_case(
        golden_case,
        "This candidate is anticancer-active with validated anticancer effect.",
    )

    assert result.overall_status == "fail"
    assert "forbidden_case_pattern" in result.detected_failures
    assert "unsupported_biological_activity_upgrade" in result.detected_failures


def test_forbidden_approval_and_production_readiness_language_is_detected():
    golden_case = read_golden_case("v1_7c_compliance_flag_cluster")

    result = evaluator.evaluate_case(
        golden_case,
        "The material is compliance approved, biosafety approved, and production ready.",
    )

    assert result.overall_status == "fail"
    assert "approval_or_clearance_overclaim" in result.detected_failures
    assert "production_readiness_overclaim" in result.detected_failures


def test_human_review_required_preservation_is_detected():
    golden_case = read_golden_case("v1_7c_human_review_required")

    result = evaluator.evaluate_case(
        golden_case,
        "Available materials identify uncertainty. Human review is required before external communication.",
    )

    assert result.overall_status == "review"
    assert result.required_human_review
    assert result.detected_failures == ()


def test_cli_returns_zero_for_valid_fixture_file_and_nonzero_for_invalid_temporary_fixture(tmp_path):
    valid_result = subprocess.run(
        [sys.executable, str(EVALUATOR_PATH), "--generated-cases", str(GENERATED_CASES_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    invalid_path = tmp_path / "invalid.jsonl"
    invalid_path.write_text('{"case_id": ', encoding="utf-8")
    invalid_result = subprocess.run(
        [sys.executable, str(EVALUATOR_PATH), "--generated-cases", str(invalid_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert valid_result.returncode == 0
    assert "result: PASS" in valid_result.stdout
    assert invalid_result.returncode != 0
    assert "result: FAIL" in invalid_result.stdout


def test_optional_json_output_parses_as_json_and_includes_case_level_results():
    result = subprocess.run(
        [sys.executable, str(EVALUATOR_PATH), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["case_count"] == 5
    assert len(payload["results"]) == 5
    assert payload["results"][0]["case_id"] == "v1_7c_unsupported_biological_activity"
    assert (
        payload["results"][0]["truth_boundary"]
        == "Offline evaluator result is diagnostic only and is not legal, compliance, biosafety, IP, wet-lab, runtime, or production approval."
    )
