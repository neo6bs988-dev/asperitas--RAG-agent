from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "eval" / "v1_10b_answer_sample_manifest.jsonl"
GENERATED_CASES_PATH = REPO_ROOT / "eval" / "v1_8b_generated_answer_scoring_cases.jsonl"
REPORT_SCRIPT = REPO_ROOT / "scripts" / "report_v1_10b_answer_sample_results.py"

REQUIRED_FIELDS = {
    "sample_id",
    "evaluator_case_id",
    "evaluator_sample_case_id",
    "sample_class",
    "prompt_id",
    "answer_text_source",
    "source_context_ids",
    "risk_domain",
    "expected_outcome",
    "expected_failure_labels",
    "requires_human_review",
    "contains_sensitive_info",
    "public_or_internal",
    "review_owner",
    "notes",
}
HIGH_RISK_DOMAINS = {
    "biology",
    "biodiversity",
    "nagoya_cites_lmo_gmo",
    "biosafety_biosecurity",
    "ip_licensing",
    "investor_public_claim",
}
STDLIB_IMPORTS = {"argparse", "json", "subprocess", "sys", "collections", "pathlib", "typing", "__future__"}


def load_report_module():
    spec = importlib.util.spec_from_file_location("v1_10b_report", REPORT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


report_module = load_report_module()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_manifest_loads_as_valid_jsonl_and_required_fields_exist():
    records = read_jsonl(MANIFEST_PATH)

    assert records
    for record in records:
        assert REQUIRED_FIELDS <= set(record)


def test_manifest_sample_ids_are_unique():
    records = read_jsonl(MANIFEST_PATH)
    sample_ids = [record["sample_id"] for record in records]

    assert len(sample_ids) == len(set(sample_ids))


def test_manifest_stable_ids_reference_every_evaluator_row_once_and_preserve_category():
    manifest = read_jsonl(MANIFEST_PATH)
    generated_cases = read_jsonl(GENERATED_CASES_PATH)
    generated_by_sample_case_id = {record["sample_case_id"]: record for record in generated_cases}
    manifest_sample_case_ids = [sample["evaluator_sample_case_id"] for sample in manifest]

    assert len(manifest) == len(generated_cases) == 13
    assert len(manifest_sample_case_ids) == len(set(manifest_sample_case_ids))
    assert set(manifest_sample_case_ids) == set(generated_by_sample_case_id)
    for sample in manifest:
        generated = generated_by_sample_case_id[sample["evaluator_sample_case_id"]]
        assert sample["evaluator_case_id"] == generated["case_id"]


def test_high_risk_domains_require_human_review():
    for sample in read_jsonl(MANIFEST_PATH):
        if sample["risk_domain"] in HIGH_RISK_DOMAINS:
            assert sample["requires_human_review"] is True


def test_report_json_preserves_diagnostic_only_boundary():
    report, errors = report_module.build_report(MANIFEST_PATH)

    assert not errors
    assert report["diagnostic_only"] is True
    assert report["approval_authority"] is False
    assert report["runtime_behavior_changed"] is False
    assert report["truth_boundary"] == (
        "Diagnostic report only. Not compliance, biosafety, legal, IP, wet-lab, "
        "runtime, or production approval."
    )


def test_report_includes_risk_and_failure_label_distributions():
    report, errors = report_module.build_report(MANIFEST_PATH)

    assert not errors
    assert "risk_domain_distribution" in report
    assert "failure_label_distribution" in report
    assert report["total_samples"] == 13
    assert report["matched_samples"] == 13
    assert report["unmatched_evaluator_cases"] == []
    assert report["outcome_counts"] == {"fail": 10, "pass": 2, "review": 1}
    assert report["risk_domain_distribution"]["biology"] == 4
    assert report["failure_label_distribution"]["citation_mismatch"] == 1
    assert report["failure_label_distribution"]["forbidden_case_pattern"] == 5
    assert report["failure_label_distribution"]["missing_human_review_preservation"] == 5
    assert report["failure_label_distribution"]["unsupported_biological_activity_upgrade"] == 3
    assert report["failure_label_distribution"]["production_readiness_overclaim"] == 1


def test_report_tracks_human_review_and_examples():
    report, errors = report_module.build_report(MANIFEST_PATH)

    assert not errors
    assert report["human_review_required_count"] == report["total_samples"]
    assert report["high_risk_samples"]
    assert report["unsupported_claim_examples"]
    assert report["overclaim_examples"]
    assert report["safe_wording_examples"]
    assert len(report["unsupported_claim_examples"]) == 3
    assert len(report["overclaim_examples"]) == 4
    assert len(report["safe_wording_examples"]) == 2


def test_report_is_invariant_to_evaluator_result_row_order(tmp_path):
    baseline, baseline_errors = report_module.build_report(MANIFEST_PATH)
    evaluator_result = subprocess.run(
        [sys.executable, str(report_module.DEFAULT_EVALUATOR_SCRIPT), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert evaluator_result.returncode == 0
    evaluator_payload = json.loads(evaluator_result.stdout)
    evaluator_payload["results"].reverse()
    evaluator_json_path = tmp_path / "reordered_evaluator.json"
    evaluator_json_path.write_text(json.dumps(evaluator_payload), encoding="utf-8")

    reordered, reordered_errors = report_module.build_report(MANIFEST_PATH, evaluator_json_path)

    assert not baseline_errors
    assert not reordered_errors
    assert reordered == baseline


def test_report_json_cli_outputs_parseable_json():
    result = subprocess.run(
        [sys.executable, str(REPORT_SCRIPT), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["version"] == "v1.10b"
    assert payload["matched_samples"] == payload["total_samples"]
    assert payload["unmatched_manifest_samples"] == []
    assert payload["unmatched_evaluator_cases"] == []


def test_human_readable_cli_includes_truth_boundary_and_counts():
    result = subprocess.run(
        [sys.executable, str(REPORT_SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "diagnostic_only: true" in result.stdout
    assert "approval_authority: false" in result.stdout
    assert "runtime_behavior_changed: false" in result.stdout
    assert "truth_boundary: Diagnostic report only." in result.stdout


def test_script_exits_nonzero_on_bad_manifest_input(tmp_path):
    bad_manifest = tmp_path / "bad_manifest.jsonl"
    bad_manifest.write_text(
        json.dumps(
            {
                "sample_id": "bad_sample",
                "evaluator_case_id": "missing_case",
                "evaluator_sample_case_id": "v1_8b_missing_case_001",
                "sample_class": "synthetic_fixture",
                "prompt_id": "existing_v1_8b_fixture",
                "answer_text_source": "eval/v1_8b_generated_answer_scoring_cases.jsonl::missing_case",
                "source_context_ids": [],
                "risk_domain": "biology",
                "expected_outcome": "fail",
                "expected_failure_labels": [],
                "requires_human_review": True,
                "contains_sensitive_info": False,
                "public_or_internal": "internal",
                "review_owner": "human_reviewer_required",
                "notes": "Synthetic diagnostic evaluator sample. Not approval evidence.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(REPORT_SCRIPT), "--manifest", str(bad_manifest)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unknown evaluator_sample_case_id" in result.stderr


def test_report_rejects_duplicate_manifest_evaluator_sample_case_id(tmp_path):
    records = read_jsonl(MANIFEST_PATH)
    records[1]["evaluator_sample_case_id"] = records[0]["evaluator_sample_case_id"]
    duplicate_manifest = tmp_path / "duplicate_evaluator_sample_case_id.jsonl"
    duplicate_manifest.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )

    report, errors = report_module.build_report(duplicate_manifest)

    assert report is None
    assert any("duplicate evaluator_sample_case_id" in error for error in errors)


def test_report_rejects_manifest_category_conflict_for_stable_row_id(tmp_path):
    records = read_jsonl(MANIFEST_PATH)
    records[0]["evaluator_case_id"] = "v1_7c_source_grounding_failure"
    conflicting_manifest = tmp_path / "category_conflict.jsonl"
    conflicting_manifest.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )

    report, errors = report_module.build_report(conflicting_manifest)

    assert report is None
    assert any("conflicts with evaluator row case_id" in error for error in errors)


def test_report_does_not_present_runtime_or_approval_authority():
    report, errors = report_module.build_report(MANIFEST_PATH)
    serialized = json.dumps(report, sort_keys=True).casefold()

    assert not errors
    assert report["approval_authority"] is False
    assert report["runtime_behavior_changed"] is False
    assert "approval_authority\": true" not in serialized
    assert "runtime_behavior_changed\": true" not in serialized
    assert "production readiness" not in serialized


def test_report_script_uses_only_stdlib_imports():
    tree = ast.parse(REPORT_SCRIPT.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports <= STDLIB_IMPORTS
