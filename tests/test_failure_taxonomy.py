from __future__ import annotations

from copy import deepcopy

from asperitas_agent.failure_taxonomy import (
    FAILURE_CATEGORIES,
    ANTI_CHEATING_FAILURE,
    CITATION_INTEGRITY_FAILURE,
    DETERMINISM_FAILURE,
    EVIDENCE_COUNT_FAILURE,
    EVIDENCE_LABEL_FAILURE,
    FORBIDDEN_DEPENDENCY_FAILURE,
    FORBIDDEN_SUBSTRING_PRESENT,
    GUARDRAIL_MISMATCH,
    PROTECTED_FILE_MUTATION,
    REQUIRED_SUBSTRING_MISSING,
    RETRIEVAL_REGRESSION_FAILURE,
    SCHEMA_FAILURE,
    SOURCE_PRIORITY_FAILURE,
    STATUS_MISMATCH,
    UNKNOWN_FAILURE,
    classify_failure,
    classify_failures,
    explain_failure_category,
)


def test_failure_categories_are_stable_and_complete():
    assert FAILURE_CATEGORIES == (
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
    assert explain_failure_category(STATUS_MISMATCH)
    assert explain_failure_category("not_real") == explain_failure_category(UNKNOWN_FAILURE)


def test_all_categories_from_structured_checks():
    cases = {
        PROTECTED_FILE_MUTATION: {"protected_files_unchanged": False},
        FORBIDDEN_DEPENDENCY_FAILURE: {"checks": {"forbidden_imports": False}},
        ANTI_CHEATING_FAILURE: {"checks": {"anti_cheating": False}},
        DETERMINISM_FAILURE: {"checks": {"determinism": False}},
        SCHEMA_FAILURE: {"checks": {"schema": False}},
        STATUS_MISMATCH: {"checks": {"status": False}},
        GUARDRAIL_MISMATCH: {"checks": {"guardrail": False}},
        CITATION_INTEGRITY_FAILURE: {"checks": {"citation_subset_integrity": False}},
        EVIDENCE_COUNT_FAILURE: {"checks": {"evidence_count": False}},
        RETRIEVAL_REGRESSION_FAILURE: {"checks": {"retrieval_regression_unchanged": False}},
        REQUIRED_SUBSTRING_MISSING: {"checks": {"required_answer_substrings": False}},
        FORBIDDEN_SUBSTRING_PRESENT: {"checks": {"forbidden_answer_substrings": False}},
        SOURCE_PRIORITY_FAILURE: {"checks": {"source_priority": False}},
        EVIDENCE_LABEL_FAILURE: {"checks": {"required_evidence_labels": False}},
    }

    for expected, result in cases.items():
        assert classify_failure(result) == expected


def test_unknown_fallback_for_unclassified_failed_result():
    assert classify_failure({"ok": False, "errors": ["not enough context"]}) == UNKNOWN_FAILURE


def test_deterministic_priority_order_when_multiple_failures_match():
    result = {
        "protected_files_unchanged": False,
        "checks": {
            "schema": False,
            "status": False,
            "citation_subset_integrity": False,
        },
    }

    assert classify_failure(result) == PROTECTED_FILE_MUTATION
    assert classify_failures(result)[:4] == [
        PROTECTED_FILE_MUTATION,
        SCHEMA_FAILURE,
        STATUS_MISMATCH,
        CITATION_INTEGRITY_FAILURE,
    ]


def test_classification_does_not_mutate_input():
    result = {"checks": {"status": False}, "errors": ["expected answered, got caution"]}
    before = deepcopy(result)

    assert classify_failure(result) == STATUS_MISMATCH
    assert result == before


def test_existing_mvp009_case_report_shape_classifies_from_errors():
    result = {
        "case_id": "normal_grounded_answer",
        "status": "abstained",
        "expected_status": "answered",
        "ok": False,
        "errors": ["normal_grounded_answer expected answered, got abstained"],
    }

    assert classify_failure(result) == STATUS_MISMATCH


def test_existing_mvp010_golden_case_shape_classifies_from_checks():
    result = {
        "id": "GOLDEN-X",
        "status": "answered",
        "expected_status": "answered",
        "guardrail_decision": "proceed",
        "expected_guardrail_decision": "proceed",
        "checks": {
            "schema": True,
            "status": True,
            "guardrail": True,
            "evidence_count": True,
            "citation_count": True,
            "citation_subset_integrity": True,
            "required_answer_substrings": False,
            "forbidden_answer_substrings": True,
            "required_evidence_labels": True,
            "source_priority": True,
            "determinism": True,
        },
        "failures": ["required_answer_substrings"],
    }

    assert classify_failure(result) == REQUIRED_SUBSTRING_MISSING


def test_text_fallbacks_cover_common_failure_messages():
    assert classify_failure({"errors": ["dangling citation: [E9]"]}) == CITATION_INTEGRITY_FAILURE
    assert classify_failure({"failures": ["forbidden substring present: production-ready"]}) == FORBIDDEN_SUBSTRING_PRESENT
    assert classify_failure({"pass_fail_reason": "mvp003 overall_pass_rate below threshold"}) == RETRIEVAL_REGRESSION_FAILURE


def test_static_scan_shapes_classify_without_external_behavior():
    forbidden = {"static_scan": {"forbidden_matches": [{"path": "x.py", "match": "openai"}]}}
    cheating = {"static_scan": {"anti_cheating_matches": [{"path": "x.py", "pattern": "pytest"}]}}

    assert classify_failure(forbidden) == FORBIDDEN_DEPENDENCY_FAILURE
    assert classify_failure(cheating) == ANTI_CHEATING_FAILURE
