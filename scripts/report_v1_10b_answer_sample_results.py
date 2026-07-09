from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.10b"
DEFAULT_MANIFEST_PATH = REPO_ROOT / "eval" / "v1_10b_answer_sample_manifest.jsonl"
DEFAULT_EVALUATOR_SCRIPT = REPO_ROOT / "scripts" / "evaluate_v1_8b_offline_answer_scoring.py"
EVALUATOR_SCRIPT_DISPLAY = "scripts/evaluate_v1_8b_offline_answer_scoring.py"
MANIFEST_DISPLAY = "eval/v1_10b_answer_sample_manifest.jsonl"
TRUTH_BOUNDARY = (
    "Diagnostic report only. Not compliance, biosafety, legal, IP, wet-lab, "
    "runtime, or production approval."
)

REQUIRED_MANIFEST_FIELDS = frozenset(
    {
        "sample_id",
        "evaluator_case_id",
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
)
ALLOWED_MANIFEST_FIELDS = REQUIRED_MANIFEST_FIELDS
ALLOWED_SAMPLE_CLASSES = frozenset(
    {"synthetic_fixture", "staged_generated_answer", "manual_review_capture", "future_runtime_capture"}
)
ALLOWED_RISK_DOMAINS = frozenset(
    {
        "biology",
        "biodiversity",
        "nagoya_cites_lmo_gmo",
        "biosafety_biosecurity",
        "ip_licensing",
        "investor_public_claim",
        "general_rag",
        "unknown",
    }
)
HIGH_RISK_DOMAINS = frozenset(
    {
        "biology",
        "biodiversity",
        "nagoya_cites_lmo_gmo",
        "biosafety_biosecurity",
        "ip_licensing",
        "investor_public_claim",
    }
)
ALLOWED_PUBLIC_OR_INTERNAL = frozenset({"internal", "public_candidate", "public"})
ALLOWED_OUTCOMES = frozenset({"pass", "fail", "review"})
AUTHORITY_TERMS = (
    "approval authority",
    "compliance approved",
    "biosafety approved",
    "legal approved",
    "ip approved",
    "production ready",
    "runtime safe",
)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def load_jsonl(path: Path, label: str) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    records: list[tuple[int, dict[str, Any]]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return records, [f"{label} file not found: {_display_path(path)}"]
    except OSError as exc:
        return records, [f"{label} file could not be read: {_display_path(path)}: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"{label} line {line_number}: blank lines are not valid JSONL records")
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{label} line {line_number}: JSON parse error at column {exc.colno}: {exc.msg}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{label} line {line_number}: record must be a JSON object")
            continue
        records.append((line_number, payload))
    return records, errors


def load_manifest(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records, errors = load_jsonl(path, "manifest")
    manifest: list[dict[str, Any]] = []
    sample_ids: Counter[str] = Counter()
    evaluator_ids: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for line_number, record in records:
        missing = sorted(REQUIRED_MANIFEST_FIELDS - set(record))
        unknown = sorted(set(record) - ALLOWED_MANIFEST_FIELDS)
        if missing:
            errors.append(f"manifest line {line_number}: missing required field(s): {', '.join(missing)}")
        if unknown:
            errors.append(f"manifest line {line_number}: unknown field(s): {', '.join(unknown)}")

        sample_id = record.get("sample_id")
        evaluator_case_id = record.get("evaluator_case_id")
        if not isinstance(sample_id, str) or not sample_id.strip():
            errors.append(f"manifest line {line_number}: sample_id must be a non-empty string")
        else:
            sample_ids[sample_id] += 1
        if not isinstance(evaluator_case_id, str) or not evaluator_case_id.strip():
            errors.append(f"manifest line {line_number}: evaluator_case_id must be a non-empty string")
        else:
            evaluator_ids[evaluator_case_id].append(record)

        if record.get("sample_class") not in ALLOWED_SAMPLE_CLASSES:
            errors.append(f"manifest line {line_number}: sample_class is not allowed")
        if record.get("sample_class") == "future_runtime_capture":
            errors.append(f"manifest line {line_number}: future_runtime_capture is not allowed in V1.10B MVP")
        if record.get("risk_domain") not in ALLOWED_RISK_DOMAINS:
            errors.append(f"manifest line {line_number}: risk_domain is not allowed")
        if record.get("public_or_internal") not in ALLOWED_PUBLIC_OR_INTERNAL:
            errors.append(f"manifest line {line_number}: public_or_internal is not allowed")
        if record.get("expected_outcome") not in ALLOWED_OUTCOMES:
            errors.append(f"manifest line {line_number}: expected_outcome is not allowed")
        if not isinstance(record.get("source_context_ids"), list):
            errors.append(f"manifest line {line_number}: source_context_ids must be a list")
        if not isinstance(record.get("expected_failure_labels"), list) or not all(
            isinstance(label, str) for label in record.get("expected_failure_labels", [])
        ):
            errors.append(f"manifest line {line_number}: expected_failure_labels must be a list of strings")
        for field in ("requires_human_review", "contains_sensitive_info"):
            if not isinstance(record.get(field), bool):
                errors.append(f"manifest line {line_number}: {field} must be a boolean")
        for field in ("prompt_id", "answer_text_source", "review_owner", "notes"):
            if not isinstance(record.get(field), str) or not record.get(field, "").strip():
                errors.append(f"manifest line {line_number}: {field} must be a non-empty string")
        if record.get("risk_domain") in HIGH_RISK_DOMAINS and record.get("requires_human_review") is not True:
            errors.append(f"manifest line {line_number}: high-risk domain must require human review")

        notes = str(record.get("notes", ""))
        notes_normalized = notes.casefold()
        if any(term in notes_normalized for term in AUTHORITY_TERMS):
            errors.append(f"manifest line {line_number}: notes contain authority wording")
        if "not approval evidence" not in notes_normalized:
            errors.append(f"manifest line {line_number}: notes must preserve not-approval boundary")

        manifest.append(record)

    for sample_id, count in sample_ids.items():
        if count > 1:
            errors.append(f"manifest: duplicate sample_id {sample_id!r}")
    for evaluator_case_id, duplicates in evaluator_ids.items():
        if len(duplicates) > 1 and not all("duplicate evaluator_case_id justified" in str(row.get("notes", "")).casefold() for row in duplicates):
            errors.append(f"manifest: duplicate evaluator_case_id {evaluator_case_id!r} lacks notes justification")

    return manifest, errors


def run_evaluator_json() -> tuple[dict[str, Any] | None, list[str]]:
    completed = subprocess.run(
        [sys.executable, str(DEFAULT_EVALUATOR_SCRIPT), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None, [
            f"evaluator command failed with exit code {completed.returncode}",
            completed.stderr.strip() or completed.stdout.strip(),
        ]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, [f"evaluator JSON parse error at column {exc.colno}: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, ["evaluator JSON payload must be an object"]
    return payload, []


def load_evaluator_json(path: Path | None) -> tuple[dict[str, Any] | None, list[str]]:
    if path is None:
        return run_evaluator_json()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"evaluator JSON file not found: {_display_path(path)}"]
    except json.JSONDecodeError as exc:
        return None, [f"evaluator JSON parse error at column {exc.colno}: {exc.msg}"]
    except OSError as exc:
        return None, [f"evaluator JSON file could not be read: {_display_path(path)}: {exc}"]
    if not isinstance(payload, dict):
        return None, ["evaluator JSON payload must be an object"]
    return payload, []


def validate_evaluator_payload(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    results = payload.get("results")
    if not isinstance(results, list):
        return [], ["evaluator payload missing results list"]
    normalized_results: list[dict[str, Any]] = []
    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            errors.append(f"evaluator result {index}: must be an object")
            continue
        case_id = result.get("case_id")
        status = result.get("overall_status")
        failures = result.get("detected_failures")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"evaluator result {index}: case_id must be a non-empty string")
        if status not in ALLOWED_OUTCOMES:
            errors.append(f"evaluator result {index}: overall_status is not allowed")
        if not isinstance(failures, list) or not all(isinstance(label, str) for label in failures):
            errors.append(f"evaluator result {index}: detected_failures must be a list of strings")
        if not isinstance(result.get("required_human_review"), bool):
            errors.append(f"evaluator result {index}: required_human_review must be a boolean")
        normalized_results.append(result)
    return normalized_results, errors


def _count_by_case_id(results: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(result["case_id"]) for result in results if isinstance(result.get("case_id"), str))


def build_report(manifest_path: Path, evaluator_json_path: Path | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    manifest, manifest_errors = load_manifest(manifest_path)
    evaluator_payload, evaluator_errors = load_evaluator_json(evaluator_json_path)
    errors = [*manifest_errors, *evaluator_errors]
    if evaluator_payload is None:
        return None, errors

    evaluator_results, evaluator_result_errors = validate_evaluator_payload(evaluator_payload)
    errors.extend(evaluator_result_errors)
    evaluator_counts = _count_by_case_id(evaluator_results)
    evaluator_by_case_id = {str(result["case_id"]): result for result in evaluator_results if evaluator_counts[str(result["case_id"])] == 1}

    matched_results: list[tuple[dict[str, Any], dict[str, Any]]] = []
    unmatched_manifest_samples: list[dict[str, Any]] = []
    for sample in manifest:
        evaluator_case_id = str(sample.get("evaluator_case_id", ""))
        if evaluator_case_id not in evaluator_counts:
            unmatched_manifest_samples.append({"sample_id": sample.get("sample_id"), "evaluator_case_id": evaluator_case_id})
            errors.append(f"manifest sample {sample.get('sample_id')!r}: unknown evaluator_case_id {evaluator_case_id!r}")
            continue
        if evaluator_counts[evaluator_case_id] != 1:
            errors.append(
                f"manifest sample {sample.get('sample_id')!r}: evaluator_case_id {evaluator_case_id!r} "
                f"appears {evaluator_counts[evaluator_case_id]} times in evaluator output; "
                "V1.10B does not infer row indexes"
            )
            continue
        result = evaluator_by_case_id[evaluator_case_id]
        if sample.get("expected_outcome") != result.get("overall_status"):
            errors.append(
                f"manifest sample {sample.get('sample_id')!r}: expected_outcome {sample.get('expected_outcome')!r} "
                f"does not match evaluator status {result.get('overall_status')!r}"
            )
        expected_labels = sorted(str(label) for label in sample.get("expected_failure_labels", []))
        actual_labels = sorted(str(label) for label in result.get("detected_failures", []))
        if expected_labels != actual_labels:
            errors.append(
                f"manifest sample {sample.get('sample_id')!r}: expected_failure_labels {expected_labels!r} "
                f"do not match evaluator detected_failures {actual_labels!r}"
            )
        matched_results.append((sample, result))

    manifest_case_ids = {str(sample.get("evaluator_case_id", "")) for sample in manifest}
    unmatched_evaluator_cases = [
        {"evaluator_case_id": case_id, "count": count}
        for case_id, count in sorted(evaluator_counts.items())
        if case_id not in manifest_case_ids
    ]

    if errors:
        return None, errors

    outcome_counts = Counter(str(result["overall_status"]) for _, result in matched_results)
    failure_label_distribution: Counter[str] = Counter()
    risk_domain_distribution = Counter(str(sample["risk_domain"]) for sample, _ in matched_results)
    high_risk_samples: list[dict[str, Any]] = []
    unsupported_claim_examples: list[dict[str, Any]] = []
    overclaim_examples: list[dict[str, Any]] = []
    safe_wording_examples: list[dict[str, Any]] = []

    for sample, result in matched_results:
        failures = [str(label) for label in result.get("detected_failures", [])]
        failure_label_distribution.update(failures)
        sample_ref = {
            "sample_id": sample["sample_id"],
            "evaluator_case_id": sample["evaluator_case_id"],
            "risk_domain": sample["risk_domain"],
            "overall_status": result["overall_status"],
            "detected_failures": failures,
        }
        if sample["risk_domain"] in HIGH_RISK_DOMAINS or sample["requires_human_review"] is True:
            high_risk_samples.append(sample_ref)
        if any(label in {"unsupported_biological_activity_upgrade", "missing_source_context"} for label in failures):
            unsupported_claim_examples.append(sample_ref)
        if any("overclaim" in label or label in {"approval_or_clearance_overclaim", "production_readiness_overclaim"} for label in failures):
            overclaim_examples.append(sample_ref)
        if result["overall_status"] == "pass" and not failures:
            safe_wording_examples.append(sample_ref)

    report = {
        "version": VERSION,
        "diagnostic_only": True,
        "approval_authority": False,
        "runtime_behavior_changed": False,
        "evaluator_script": EVALUATOR_SCRIPT_DISPLAY,
        "manifest_path": _display_path(manifest_path),
        "total_samples": len(manifest),
        "evaluator_total_cases": int(evaluator_payload.get("case_count", len(evaluator_results))),
        "matched_samples": len(matched_results),
        "unmatched_manifest_samples": unmatched_manifest_samples,
        "unmatched_evaluator_cases": unmatched_evaluator_cases,
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "failure_label_distribution": dict(sorted(failure_label_distribution.items())),
        "risk_domain_distribution": dict(sorted(risk_domain_distribution.items())),
        "human_review_required_count": sum(1 for sample, _ in matched_results if sample["requires_human_review"] is True),
        "high_risk_samples": high_risk_samples,
        "unsupported_claim_examples": unsupported_claim_examples,
        "overclaim_examples": overclaim_examples,
        "safe_wording_examples": safe_wording_examples,
        "truth_boundary": TRUTH_BOUNDARY,
    }
    return report, []


def print_human_report(report: dict[str, Any]) -> None:
    print("V1.10B answer-sample diagnostic report")
    print("diagnostic_only: true")
    print("approval_authority: false")
    print("runtime_behavior_changed: false")
    print(f"manifest: {report['manifest_path']}")
    print(f"evaluator_script: {report['evaluator_script']}")
    print(f"total_samples: {report['total_samples']}")
    print(f"evaluator_total_cases: {report['evaluator_total_cases']}")
    print(f"matched_samples: {report['matched_samples']}")
    print(f"outcome_counts: {json.dumps(report['outcome_counts'], sort_keys=True)}")
    print(f"risk_domain_distribution: {json.dumps(report['risk_domain_distribution'], sort_keys=True)}")
    print(f"failure_label_distribution: {json.dumps(report['failure_label_distribution'], sort_keys=True)}")
    print(f"human_review_required_count: {report['human_review_required_count']}")
    print(f"high_risk_samples: {len(report['high_risk_samples'])}")
    print(f"unsupported_claim_examples: {len(report['unsupported_claim_examples'])}")
    print(f"overclaim_examples: {len(report['overclaim_examples'])}")
    print(f"safe_wording_examples: {len(report['safe_wording_examples'])}")
    print(f"unmatched_evaluator_cases: {json.dumps(report['unmatched_evaluator_cases'], sort_keys=True)}")
    print(f"truth_boundary: {report['truth_boundary']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Report V1.10B answer-sample metadata over V1.8B evaluator JSON.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Path to V1.10B manifest JSONL.")
    parser.add_argument("--evaluator-json", type=Path, default=None, help="Optional precomputed evaluator JSON file.")
    parser.add_argument("--json", action="store_true", help="Emit the V1.10B report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report, errors = build_report(manifest_path=args.manifest, evaluator_json_path=args.evaluator_json)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    assert report is not None
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
