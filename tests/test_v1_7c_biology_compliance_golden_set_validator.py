from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_golden_set.jsonl"
SCHEMA_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_labels.schema.json"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_v1_7c_biology_compliance_golden_set.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("v1_7c_validator", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator_module()


def read_records() -> list[dict]:
    return [json.loads(line) for line in GOLDEN_SET_PATH.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    return path


def errors_for(golden_set_path: Path) -> tuple[str, ...]:
    return validator.validate_paths(golden_set_path=golden_set_path, schema_path=SCHEMA_PATH).errors


def test_current_repo_assets_pass_validation():
    report = validator.validate_paths(golden_set_path=GOLDEN_SET_PATH, schema_path=SCHEMA_PATH)

    assert report.ok
    assert report.record_count == 7
    assert set(report.covered_categories) == set(validator.REQUIRED_CASE_CATEGORIES)


def test_malformed_jsonl_fails(tmp_path):
    broken_path = tmp_path / "broken.jsonl"
    broken_path.write_text('{"id": ', encoding="utf-8")

    errors = errors_for(broken_path)

    assert any("JSON parse error" in error for error in errors)


def test_missing_required_field_fails(tmp_path):
    records = read_records()
    del records[0]["query"]
    broken_path = write_jsonl(tmp_path / "missing_required.jsonl", records)

    errors = errors_for(broken_path)

    assert any("missing required field(s): query" in error for error in errors)


def test_unknown_expected_label_outside_schema_enum_fails(tmp_path):
    records = read_records()
    records[0]["expected_labels"]["evidence_sufficiency"] = "unsupported_schema_label"
    broken_path = write_jsonl(tmp_path / "unknown_label.jsonl", records)

    errors = errors_for(broken_path)

    assert any("expected_labels.evidence_sufficiency" in error and "not allowed" in error for error in errors)


def test_missing_required_coverage_category_fails(tmp_path):
    records = [record for record in read_records() if record["case_category"] != "citation mismatch"]
    broken_path = write_jsonl(tmp_path / "missing_category.jsonl", records)

    errors = errors_for(broken_path)

    assert any("golden set is missing required case category/categories: citation mismatch" in error for error in errors)


def test_non_synthetic_source_context_status_fails(tmp_path):
    records = read_records()
    records[0]["source_context"]["source_status"] = "raw_unreviewed"
    broken_path = write_jsonl(tmp_path / "bad_source_status.jsonl", records)

    errors = errors_for(broken_path)

    assert any("source_context.source_status" in error and "synthetic_approved_safe" in error for error in errors)


def test_source_context_overclaim_phrase_fails(tmp_path):
    records = read_records()
    records[0]["source_context"]["summary"] = "Synthetic summary: production ready and compliance approved."
    broken_path = write_jsonl(tmp_path / "source_overclaim.jsonl", records)

    errors = errors_for(broken_path)

    assert any("source_context contains prohibited phrase" in error for error in errors)


def test_cli_returns_zero_for_valid_assets_and_nonzero_for_invalid_temporary_assets(tmp_path):
    valid_result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--golden-set", str(GOLDEN_SET_PATH), "--schema", str(SCHEMA_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    invalid_path = tmp_path / "invalid.jsonl"
    invalid_path.write_text('{"id": ', encoding="utf-8")
    invalid_result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--golden-set", str(invalid_path), "--schema", str(SCHEMA_PATH)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert valid_result.returncode == 0
    assert "result: PASS" in valid_result.stdout
    assert invalid_result.returncode != 0
    assert "result: FAIL" in invalid_result.stdout
