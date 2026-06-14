from __future__ import annotations

from collections.abc import Mapping
from typing import Any


PROTECTED_FILE_MUTATION = "protected_file_mutation"
FORBIDDEN_DEPENDENCY_FAILURE = "forbidden_dependency_failure"
ANTI_CHEATING_FAILURE = "anti_cheating_failure"
DETERMINISM_FAILURE = "determinism_failure"
SCHEMA_FAILURE = "schema_failure"
STATUS_MISMATCH = "status_mismatch"
GUARDRAIL_MISMATCH = "guardrail_mismatch"
CITATION_INTEGRITY_FAILURE = "citation_integrity_failure"
EVIDENCE_COUNT_FAILURE = "evidence_count_failure"
RETRIEVAL_REGRESSION_FAILURE = "retrieval_regression_failure"
REQUIRED_SUBSTRING_MISSING = "required_substring_missing"
FORBIDDEN_SUBSTRING_PRESENT = "forbidden_substring_present"
SOURCE_PRIORITY_FAILURE = "source_priority_failure"
EVIDENCE_LABEL_FAILURE = "evidence_label_failure"
UNKNOWN_FAILURE = "unknown_failure"

FAILURE_PRIORITY = (
    PROTECTED_FILE_MUTATION,
    FORBIDDEN_DEPENDENCY_FAILURE,
    ANTI_CHEATING_FAILURE,
    DETERMINISM_FAILURE,
    SCHEMA_FAILURE,
    STATUS_MISMATCH,
    GUARDRAIL_MISMATCH,
    CITATION_INTEGRITY_FAILURE,
    EVIDENCE_COUNT_FAILURE,
    RETRIEVAL_REGRESSION_FAILURE,
    REQUIRED_SUBSTRING_MISSING,
    FORBIDDEN_SUBSTRING_PRESENT,
    SOURCE_PRIORITY_FAILURE,
    EVIDENCE_LABEL_FAILURE,
    UNKNOWN_FAILURE,
)

FAILURE_CATEGORIES = FAILURE_PRIORITY

_EXPLANATIONS = {
    PROTECTED_FILE_MUTATION: "A protected source, registry, benchmark, or artifact file changed during evaluation.",
    FORBIDDEN_DEPENDENCY_FAILURE: "The static scan found a forbidden dependency or API reference.",
    ANTI_CHEATING_FAILURE: "The static scan found benchmark leakage or test-runner/query special-casing risk.",
    DETERMINISM_FAILURE: "Repeated deterministic evaluation runs produced different outputs.",
    SCHEMA_FAILURE: "The evaluation output is missing required fields or has an invalid schema.",
    STATUS_MISMATCH: "The actual answer status differs from the expected status.",
    GUARDRAIL_MISMATCH: "The guardrail decision or abstention behavior differs from the expectation.",
    CITATION_INTEGRITY_FAILURE: "Citations are malformed, dangling, or not a subset of evidence citation keys.",
    EVIDENCE_COUNT_FAILURE: "The response did not meet the required evidence-count threshold.",
    RETRIEVAL_REGRESSION_FAILURE: "The retrieval regression check failed or fell below its threshold.",
    REQUIRED_SUBSTRING_MISSING: "A required answer substring was absent.",
    FORBIDDEN_SUBSTRING_PRESENT: "A forbidden answer substring was present.",
    SOURCE_PRIORITY_FAILURE: "The response did not satisfy the required source-priority constraint.",
    EVIDENCE_LABEL_FAILURE: "The response did not include the required evidence label.",
    UNKNOWN_FAILURE: "The result failed, but no known failure category matched.",
}


def explain_failure_category(category: str) -> str:
    return _EXPLANATIONS.get(category, _EXPLANATIONS[UNKNOWN_FAILURE])


def classify_failures(result: Mapping[str, Any]) -> list[str]:
    categories = [category for category in FAILURE_PRIORITY[:-1] if _matches_category(category, result)]
    return categories or [UNKNOWN_FAILURE]


def classify_failure(result: Mapping[str, Any]) -> str:
    for category in FAILURE_PRIORITY:
        if category == UNKNOWN_FAILURE or _matches_category(category, result):
            return category
    return UNKNOWN_FAILURE


def _matches_category(category: str, result: Mapping[str, Any]) -> bool:
    checks = _mapping(result.get("checks"))
    text = _failure_text(result)

    if category == PROTECTED_FILE_MUTATION:
        return _is_false(result.get("protected_files_unchanged")) or _check_false(checks, "protected_files_unchanged") or _has_any(text, ("protected", "hash", "mutat", "changed"))
    if category == FORBIDDEN_DEPENDENCY_FAILURE:
        return _check_false(checks, "forbidden_imports", "forbidden_dependencies") or bool(_static_matches(result, "forbidden_matches")) or _has_any(text, ("forbidden import", "forbidden dependency", "forbidden api"))
    if category == ANTI_CHEATING_FAILURE:
        return _check_false(checks, "anti_cheating") or bool(_static_matches(result, "anti_cheating_matches")) or _has_any(text, ("anti-cheating", "anti_cheating", "benchmark leakage", "special-casing", "golden query"))
    if category == DETERMINISM_FAILURE:
        return _check_false(checks, "determinism") or _has_any(text, ("determinism", "deterministic", "repeated run", "differs"))
    if category == SCHEMA_FAILURE:
        return _check_false(checks, "schema") or _has_any(text, ("schema", "missing field", "required field", "wrong type", "validation error"))
    if category == STATUS_MISMATCH:
        return _check_false(checks, "status") or _status_mismatch(result) or _has_any(text, ("expected status", "status mismatch", "invalid status"))
    if category == GUARDRAIL_MISMATCH:
        return _check_false(checks, "guardrail", "guardrails") or _guardrail_mismatch(result) or _has_any(text, ("guardrail", "abstention", "should_abstain"))
    if category == CITATION_INTEGRITY_FAILURE:
        return _check_false(checks, "citation_subset_integrity", "citations") or _has_any(text, ("citation", "dangling", "malformed", "evidence marker"))
    if category == EVIDENCE_COUNT_FAILURE:
        return _check_false(checks, "evidence_count") or _evidence_count_below_threshold(result) or _has_any(text, ("evidence count", "minimum evidence"))
    if category == RETRIEVAL_REGRESSION_FAILURE:
        return _check_false(checks, "retrieval_regression_unchanged") or _retrieval_failed(result) or _has_any(text, ("retrieval regression", "metric threshold", "below threshold"))
    if category == REQUIRED_SUBSTRING_MISSING:
        return _check_false(checks, "required_answer_substrings") or _has_any(text, ("required substring", "substring missing"))
    if category == FORBIDDEN_SUBSTRING_PRESENT:
        return _check_false(checks, "forbidden_answer_substrings") or _has_any(text, ("forbidden substring", "substring present"))
    if category == SOURCE_PRIORITY_FAILURE:
        return _check_false(checks, "source_priority") or _has_any(text, ("source priority", "source_priority"))
    if category == EVIDENCE_LABEL_FAILURE:
        return _check_false(checks, "required_evidence_labels", "evidence_label", "evidence_labels") or _has_any(text, ("evidence label", "evidence_label"))
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _check_false(checks: Mapping[str, Any], *names: str) -> bool:
    return any(_is_false(checks.get(name)) for name in names)


def _is_false(value: Any) -> bool:
    return value is False


def _status_mismatch(result: Mapping[str, Any]) -> bool:
    status = result.get("status")
    expected = result.get("expected_status")
    return status is not None and expected is not None and status != expected


def _guardrail_mismatch(result: Mapping[str, Any]) -> bool:
    decision = result.get("guardrail_decision")
    expected = result.get("expected_guardrail_decision")
    return decision is not None and expected not in (None, "") and decision != expected


def _evidence_count_below_threshold(result: Mapping[str, Any]) -> bool:
    evidence_count = result.get("evidence_count")
    minimum = result.get("min_evidence_count")
    return isinstance(evidence_count, (int, float)) and isinstance(minimum, (int, float)) and evidence_count < minimum


def _retrieval_failed(result: Mapping[str, Any]) -> bool:
    regression = _mapping(result.get("retrieval_regression"))
    return _is_false(regression.get("ok")) or _is_false(regression.get("mvp003", {}).get("ok") if isinstance(regression.get("mvp003"), Mapping) else None)


def _static_matches(result: Mapping[str, Any], key: str) -> list[Any]:
    static_scan = _mapping(result.get("static_scan"))
    matches = static_scan.get(key, [])
    return matches if isinstance(matches, list) else []


def _failure_text(result: Mapping[str, Any]) -> str:
    values: list[str] = []
    for key in ("errors", "failures", "failure", "error", "pass_fail_reason"):
        _collect_text(result.get(key), values)
    regression = _mapping(result.get("retrieval_regression"))
    _collect_text(regression.get("pass_fail_reason"), values)
    return " ".join(values).casefold()


def _collect_text(value: Any, values: list[str]) -> None:
    if isinstance(value, str):
        values.append(value)
    elif isinstance(value, list):
        for item in value:
            _collect_text(item, values)
    elif isinstance(value, Mapping):
        for item in value.values():
            _collect_text(item, values)


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle.casefold() in text for needle in needles)
