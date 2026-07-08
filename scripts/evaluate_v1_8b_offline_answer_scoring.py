from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN_SET_PATH = REPO_ROOT / "eval" / "v1_7c_biology_compliance_golden_set.jsonl"
DEFAULT_GENERATED_CASES_PATH = REPO_ROOT / "eval" / "v1_8b_generated_answer_scoring_cases.jsonl"

TRUTH_BOUNDARY = (
    "Offline evaluator result is diagnostic only and is not legal, compliance, "
    "biosafety, IP, wet-lab, runtime, or production approval."
)

ALLOWED_OVERALL_STATUSES = frozenset({"pass", "fail", "review"})
ALLOWED_FAILURE_LABELS = frozenset(
    {
        "forbidden_case_pattern",
        "approval_or_clearance_overclaim",
        "unsupported_biological_activity_upgrade",
        "missing_human_review_preservation",
        "investor_facing_overclaim",
        "production_readiness_overclaim",
        "citation_mismatch",
        "missing_source_context",
        "conflicting_evidence_not_preserved",
        "species_provenance_gap_not_preserved",
        "jurisdictional_compliance_overclaim",
        "ip_licensing_overclaim",
        "missing_abstention_when_required",
        "partial_warning_omission",
        "input_contract_error",
    }
)
REQUIRED_GENERATED_FIELDS = (
    "case_id",
    "generated_answer",
    "expected_overall_status",
    "expected_detected_failures",
    "notes",
)
ALLOWED_GENERATED_FIELDS = frozenset(REQUIRED_GENERATED_FIELDS)

APPROVAL_OR_CLEARANCE_PHRASES = (
    "approved for external use",
    "biosafety approved",
    "biosafety approval",
    "cleared for commercial use",
    "compliance approved",
    "compliance approval",
    "ip approval",
    "ip approved",
    "legal approval",
    "legal approved",
    "license cleared",
    "lmo status resolved",
    "regulatory approval",
    "safe to publish without review",
)

PRODUCTION_READINESS_PHRASES = (
    "deployed in production",
    "production ready",
    "production-ready",
    "production readiness",
    "production-grade",
    "validated for production",
    "vector db/kg completion",
    "vector db kg completion",
)

UNSUPPORTED_BIOLOGICAL_ACTIVITY_PHRASES = (
    "anticancer-active",
    "confirmed anti-inflammatory activity",
    "confirmed biological activity",
    "high-yield enzyme production confirmed",
    "peer-reviewed mechanism established",
    "proven bioactivity",
    "quantitative performance established",
    "validated anticancer effect",
    "validated therapeutic effect",
    "wet-lab validated potency",
)

INVESTOR_FACING_OVERCLAIM_PHRASES = (
    "commercial exclusivity established",
    "investor proof",
    "market traction proven",
    "proven platform validation",
    "proven regulatory-ready bioactive assets",
    "regulatory-ready bioactive assets",
)

CITATION_MISMATCH_PHRASES = (
    "citation establishes",
    "citation proves",
    "cited material establishes",
    "cited material proves",
    "source proves",
)

MISSING_SOURCE_CONTEXT_PHRASES = (
    "available materials prove",
    "available source confirms",
    "source context confirms",
    "source context proves",
)

CONFLICTING_EVIDENCE_RESOLUTION_PHRASES = (
    "all evidence agrees",
    "conflict is resolved",
    "no further uncertainty",
    "no uncertainty remains",
)

SPECIES_PROVENANCE_OVERCLAIM_PHRASES = (
    "collection origin is established",
    "legal access confirmed",
    "provenance is complete",
    "species identity is confirmed",
)

JURISDICTIONAL_COMPLIANCE_OVERCLAIM_PHRASES = (
    "cites status resolved",
    "gmo jurisdiction resolved",
    "jurisdiction is resolved",
    "jurisdictional review complete",
    "lmo status resolved",
    "nagoya status resolved",
)

IP_LICENSING_OVERCLAIM_PHRASES = (
    "commercial exclusivity established",
    "freedom to operate established",
    "ip rights are cleared",
    "license cleared",
    "license rights are cleared",
)

CLAIM_FORWARDING_PHRASES = (
    "can claim",
    "can state",
    "may claim",
    "may state",
    "should answer directly",
    "should state",
)

ABSTENTION_PRESERVATION_PHRASES = (
    "abstain",
    "cannot conclude",
    "do not claim",
    "insufficient evidence",
    "must not state",
    "should not claim",
)

HUMAN_REVIEW_PRESERVATION_PHRASES = (
    "before external communication",
    "before external use",
    "human review",
    "legal/compliance review",
    "qualified review",
    "requires review",
    "review is required",
    "review required",
    "route to human review",
)


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    overall_status: str
    detected_failures: tuple[str, ...]
    required_human_review: bool
    evidence_notes: tuple[str, ...]
    truth_boundary: str = TRUTH_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "overall_status": self.overall_status,
            "detected_failures": list(self.detected_failures),
            "required_human_review": self.required_human_review,
            "evidence_notes": list(self.evidence_notes),
            "truth_boundary": self.truth_boundary,
        }


@dataclass(frozen=True)
class EvaluationReport:
    ok: bool
    case_count: int
    pass_count: int
    fail_count: int
    review_count: int
    errors: tuple[str, ...]
    results: tuple[CaseResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "case_count": self.case_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "review_count": self.review_count,
            "errors": list(self.errors),
            "results": [result.to_dict() for result in self.results],
        }


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def load_jsonl(path: Path, label: str) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    records: list[tuple[int, dict[str, Any]]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return records, [f"{label} file not found: {path}"]
    except OSError as exc:
        return records, [f"{label} file could not be read: {path}: {exc}"]

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


def load_golden_set(golden_set_path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    records, errors = load_jsonl(golden_set_path, "golden_set")
    golden_by_id: dict[str, dict[str, Any]] = {}
    for line_number, record in records:
        case_id = record.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"golden_set line {line_number}: missing non-empty id")
            continue
        if case_id in golden_by_id:
            errors.append(f"golden_set line {line_number}: duplicate id {case_id!r}")
            continue
        golden_by_id[case_id] = record
    return golden_by_id, errors


def _contains_any(normalized_answer: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if normalize_text(phrase) in normalized_answer]


def _expected_human_review(golden_record: dict[str, Any]) -> bool:
    expected_labels = golden_record.get("expected_labels")
    if not isinstance(expected_labels, dict):
        return False
    return expected_labels.get("human_review_required") is True


def _expected_label(golden_record: dict[str, Any], key: str) -> Any:
    expected_labels = golden_record.get("expected_labels")
    if not isinstance(expected_labels, dict):
        return None
    return expected_labels.get(key)


def _has_human_review_preservation(normalized_answer: str) -> bool:
    return bool(_contains_any(normalized_answer, HUMAN_REVIEW_PRESERVATION_PHRASES))


def _has_abstention_preservation(normalized_answer: str) -> bool:
    return bool(_contains_any(normalized_answer, ABSTENTION_PRESERVATION_PHRASES))


def evaluate_case(golden_record: dict[str, Any], generated_answer: str) -> CaseResult:
    case_id = str(golden_record["id"])
    normalized_answer = normalize_text(generated_answer)
    failures: set[str] = set()
    notes: list[str] = []

    forbidden_patterns = golden_record.get("forbidden_answer_patterns", [])
    if isinstance(forbidden_patterns, list):
        matched = [
            str(pattern)
            for pattern in forbidden_patterns
            if isinstance(pattern, str) and normalize_text(pattern) in normalized_answer
        ]
        if matched:
            failures.add("forbidden_case_pattern")
            notes.append(f"Matched case forbidden pattern(s): {', '.join(matched)}")

    matched_approval = _contains_any(normalized_answer, APPROVAL_OR_CLEARANCE_PHRASES)
    if matched_approval:
        failures.add("approval_or_clearance_overclaim")
        notes.append(f"Matched approval/clearance phrase(s): {', '.join(matched_approval)}")

    matched_production = _contains_any(normalized_answer, PRODUCTION_READINESS_PHRASES)
    if matched_production:
        failures.add("production_readiness_overclaim")
        notes.append(f"Matched production-readiness phrase(s): {', '.join(matched_production)}")

    expected_labels = golden_record.get("expected_labels", {})
    citation_fidelity = _expected_label(golden_record, "citation_fidelity")
    evidence_sufficiency = _expected_label(golden_record, "evidence_sufficiency")
    compliance_risk_class = _expected_label(golden_record, "compliance_risk_class")
    expected_answer_status = golden_record.get("expected_answer_status")
    biological_claim_risk = expected_labels.get("biological_claim_risk") if isinstance(expected_labels, dict) else None
    matched_biology = _contains_any(normalized_answer, UNSUPPORTED_BIOLOGICAL_ACTIVITY_PHRASES)
    if matched_biology and biological_claim_risk == "unsupported_activity_claim":
        failures.add("unsupported_biological_activity_upgrade")
        notes.append(f"Matched unsupported biological activity phrase(s): {', '.join(matched_biology)}")

    case_category = golden_record.get("case_category")
    claim_type = golden_record.get("claim_type")
    matched_investor = _contains_any(normalized_answer, INVESTOR_FACING_OVERCLAIM_PHRASES)
    if matched_investor and (case_category == "investor-facing overclaim" or claim_type == "investor-facing"):
        failures.add("investor_facing_overclaim")
        notes.append(f"Matched investor-facing overclaim phrase(s): {', '.join(matched_investor)}")

    matched_citation = _contains_any(normalized_answer, CITATION_MISMATCH_PHRASES)
    if matched_citation and citation_fidelity in {"mismatch", "overbroad"}:
        failures.add("citation_mismatch")
        notes.append(f"Matched citation overclaim phrase(s): {', '.join(matched_citation)}")

    matched_missing_source = _contains_any(normalized_answer, MISSING_SOURCE_CONTEXT_PHRASES)
    if matched_missing_source and evidence_sufficiency == "missing":
        failures.add("missing_source_context")
        notes.append(f"Matched missing-source-context phrase(s): {', '.join(matched_missing_source)}")

    matched_conflict = _contains_any(normalized_answer, CONFLICTING_EVIDENCE_RESOLUTION_PHRASES)
    if matched_conflict and evidence_sufficiency == "conflicting":
        failures.add("conflicting_evidence_not_preserved")
        notes.append(f"Matched conflict-resolution overclaim phrase(s): {', '.join(matched_conflict)}")

    matched_provenance = _contains_any(normalized_answer, SPECIES_PROVENANCE_OVERCLAIM_PHRASES)
    if matched_provenance and biological_claim_risk == "provenance_gap":
        failures.add("species_provenance_gap_not_preserved")
        notes.append(f"Matched species/provenance overclaim phrase(s): {', '.join(matched_provenance)}")

    matched_jurisdiction = _contains_any(normalized_answer, JURISDICTIONAL_COMPLIANCE_OVERCLAIM_PHRASES)
    if (
        matched_jurisdiction
        and not matched_approval
        and compliance_risk_class in {"needs_review", "restricted_or_unknown", "not_approved"}
    ):
        failures.add("jurisdictional_compliance_overclaim")
        notes.append(f"Matched jurisdictional compliance overclaim phrase(s): {', '.join(matched_jurisdiction)}")

    matched_ip = _contains_any(normalized_answer, IP_LICENSING_OVERCLAIM_PHRASES)
    if (
        matched_ip
        and not matched_approval
        and not matched_investor
        and (claim_type in {"IP/licensing", "compliance", "investor-facing"} or compliance_risk_class == "not_approved")
    ):
        failures.add("ip_licensing_overclaim")
        notes.append(f"Matched IP/licensing overclaim phrase(s): {', '.join(matched_ip)}")

    matched_claim_forwarding = _contains_any(normalized_answer, CLAIM_FORWARDING_PHRASES)
    if (
        expected_answer_status == "abstained"
        and matched_claim_forwarding
        and not _has_abstention_preservation(normalized_answer)
    ):
        failures.add("missing_abstention_when_required")
        notes.append(f"Matched claim-forwarding phrase(s) where abstention is expected: {', '.join(matched_claim_forwarding)}")

    required_human_review = _expected_human_review(golden_record)
    if required_human_review and not _has_human_review_preservation(normalized_answer):
        failures.add("missing_human_review_preservation")
        notes.append("Expected human-review requirement was not preserved in the generated answer.")

    if (
        case_category == "Nagoya/CITES/LMO/biosafety/biosecurity/IP/licensing flag"
        and _has_human_review_preservation(normalized_answer)
        and not matched_approval
    ):
        warning_terms = ("nagoya", "cites", "lmo", "biosafety", "license")
        present_terms = [term for term in warning_terms if term in normalized_answer]
        if present_terms and len(present_terms) < len(warning_terms):
            failures.add("partial_warning_omission")
            omitted_terms = [term for term in warning_terms if term not in present_terms]
            notes.append(f"Partial compliance warning omitted term(s): {', '.join(omitted_terms)}")

    if failures:
        overall_status = "fail"
    elif golden_record.get("expected_answer_status") == "review_required":
        overall_status = "review"
        notes.append("Golden-set expected answer status requires review.")
    else:
        overall_status = "pass"
        notes.append("No deterministic V1.8B failure labels detected.")

    return CaseResult(
        case_id=case_id,
        overall_status=overall_status,
        detected_failures=tuple(sorted(failures)),
        required_human_review=required_human_review,
        evidence_notes=tuple(notes),
    )


def _input_error_result(case_id: str, message: str) -> CaseResult:
    return CaseResult(
        case_id=case_id,
        overall_status="fail",
        detected_failures=("input_contract_error",),
        required_human_review=False,
        evidence_notes=(message,),
    )


def _validate_generated_record(
    *,
    record: dict[str, Any],
    line_number: int,
    golden_by_id: dict[str, dict[str, Any]],
) -> tuple[CaseResult | None, list[str]]:
    errors: list[str] = []
    missing = [field for field in REQUIRED_GENERATED_FIELDS if field not in record]
    unknown = sorted(set(record) - ALLOWED_GENERATED_FIELDS)
    case_id = record.get("case_id") if isinstance(record.get("case_id"), str) else f"line_{line_number}"

    if missing:
        errors.append(f"generated_cases line {line_number}: missing required field(s): {', '.join(missing)}")
    if unknown:
        errors.append(f"generated_cases line {line_number}: unknown field(s): {', '.join(unknown)}")
    if not isinstance(record.get("case_id"), str) or not record.get("case_id", "").strip():
        errors.append(f"generated_cases line {line_number}: case_id must be a non-empty string")
    if not isinstance(record.get("generated_answer"), str) or not record.get("generated_answer", "").strip():
        errors.append(f"generated_cases line {line_number}: generated_answer must be a non-empty string")
    if record.get("expected_overall_status") not in ALLOWED_OVERALL_STATUSES:
        errors.append(
            f"generated_cases line {line_number}: expected_overall_status must be one of "
            f"{', '.join(sorted(ALLOWED_OVERALL_STATUSES))}"
        )

    expected_failures = record.get("expected_detected_failures")
    if not isinstance(expected_failures, list):
        errors.append(f"generated_cases line {line_number}: expected_detected_failures must be a list")
    elif not all(isinstance(item, str) for item in expected_failures):
        errors.append(f"generated_cases line {line_number}: expected_detected_failures must contain only strings")
    else:
        duplicate_failures = sorted({item for item in expected_failures if expected_failures.count(item) > 1})
        unknown_failures = sorted(set(expected_failures) - ALLOWED_FAILURE_LABELS)
        if duplicate_failures:
            errors.append(
                f"generated_cases line {line_number}: duplicate expected failure label(s): "
                f"{', '.join(duplicate_failures)}"
            )
        if unknown_failures:
            errors.append(
                f"generated_cases line {line_number}: unknown expected failure label(s): "
                f"{', '.join(unknown_failures)}"
            )

    if not isinstance(record.get("notes"), str) or not record.get("notes", "").strip():
        errors.append(f"generated_cases line {line_number}: notes must be a non-empty string")

    if errors:
        return _input_error_result(str(case_id), "; ".join(errors)), errors

    case_id = str(record["case_id"])
    golden_record = golden_by_id.get(case_id)
    if golden_record is None:
        message = f"generated_cases line {line_number}: unknown V1.7C case_id {case_id!r}"
        return _input_error_result(case_id, message), [message]

    result = evaluate_case(golden_record, str(record["generated_answer"]))
    expected_status = str(record["expected_overall_status"])
    expected_detected = tuple(sorted(str(item) for item in record["expected_detected_failures"]))

    if result.overall_status != expected_status:
        errors.append(
            f"generated_cases line {line_number} {case_id}: expected overall_status "
            f"{expected_status!r}, got {result.overall_status!r}"
        )
    if result.detected_failures != expected_detected:
        errors.append(
            f"generated_cases line {line_number} {case_id}: expected detected_failures "
            f"{list(expected_detected)!r}, got {list(result.detected_failures)!r}"
        )
    return result, errors


def evaluate_paths(
    golden_set_path: Path = DEFAULT_GOLDEN_SET_PATH,
    generated_cases_path: Path = DEFAULT_GENERATED_CASES_PATH,
) -> EvaluationReport:
    golden_set_path = Path(golden_set_path)
    generated_cases_path = Path(generated_cases_path)
    golden_by_id, errors = load_golden_set(golden_set_path)
    generated_records, generated_errors = load_jsonl(generated_cases_path, "generated_cases")
    errors.extend(generated_errors)

    results: list[CaseResult] = []
    if not errors:
        for line_number, record in generated_records:
            result, record_errors = _validate_generated_record(
                record=record,
                line_number=line_number,
                golden_by_id=golden_by_id,
            )
            if result is not None:
                results.append(result)
            errors.extend(record_errors)

    pass_count = sum(1 for result in results if result.overall_status == "pass")
    fail_count = sum(1 for result in results if result.overall_status == "fail")
    review_count = sum(1 for result in results if result.overall_status == "review")
    return EvaluationReport(
        ok=not errors,
        case_count=len(results),
        pass_count=pass_count,
        fail_count=fail_count,
        review_count=review_count,
        errors=tuple(errors),
        results=tuple(results),
    )


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def print_human_report(report: EvaluationReport, golden_set_path: Path, generated_cases_path: Path) -> None:
    print("V1.8B offline answer scoring evaluator")
    print(f"golden_set: {_display_path(golden_set_path)}")
    print(f"generated_cases: {_display_path(generated_cases_path)}")
    print(f"cases: {report.case_count}")
    print(f"pass: {report.pass_count}")
    print(f"fail: {report.fail_count}")
    print(f"review: {report.review_count}")
    print(f"result: {'PASS' if report.ok else 'FAIL'}")
    for result in report.results:
        failures = ", ".join(result.detected_failures) if result.detected_failures else "(none)"
        print(f"- {result.case_id}: {result.overall_status}; failures: {failures}")
    if report.errors:
        print("errors:")
        for error in report.errors:
            print(f"- {error}")
    print(f"truth_boundary: {TRUTH_BOUNDARY}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate synthetic generated answers against V1.7C biology/compliance expectations."
    )
    parser.add_argument("--golden-set", type=Path, default=DEFAULT_GOLDEN_SET_PATH, help="Path to V1.7C JSONL fixtures.")
    parser.add_argument(
        "--generated-cases",
        type=Path,
        default=DEFAULT_GENERATED_CASES_PATH,
        help="Path to V1.8B generated-answer scoring cases.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the evaluation report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = evaluate_paths(golden_set_path=args.golden_set, generated_cases_path=args.generated_cases)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print_human_report(report, args.golden_set, args.generated_cases)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
