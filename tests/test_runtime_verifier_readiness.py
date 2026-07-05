from __future__ import annotations

import json

from asperitas_agent.runtime_verifier_readiness import interpret_runtime_verifier_readiness


def runtime_metadata(**overrides):
    payload = {
        "answer_faithfulness_status": "pass",
        "total_claims": 1,
        "status_counts": {
            "supported": 1,
            "partially_supported": 0,
            "unsupported": 0,
            "contradicted": 0,
            "citation_missing": 0,
            "citation_mismatch": 0,
            "ambiguous": 0,
            "not_verifiable_from_context": 0,
            "compliance_blocked": 0,
        },
        "blocking_failures": [],
        "warnings": [],
        "failure_modes": [],
        "compliance_tags": [],
        "diagnostics": ["runtime_verification_completed"],
        "runtime_verifier_enabled": True,
        "runtime_verification_attempted": True,
        "runtime_verification_skipped_reason": "",
        "metadata_only_fallback_used": False,
        "verifier_input_claim_count": 1,
        "verifier_output_claim_count": 1,
        "verifier_failure_modes": [],
        "verifier_schema_version": "V1.5C-schema-taxonomy",
        "runtime_evidence_metadata": [{"source_id": "SRC-1"}],
    }
    payload.update(overrides)
    return payload


def assert_result(payload, classification, reason):
    result = interpret_runtime_verifier_readiness(payload)

    assert result["readiness_classification"] == classification
    assert reason in result["reason_codes"]
    assert result["production_verification_claim"] is False
    assert result["metadata_interpretation_only"] is True
    assert result["recommended_next_action"]
    assert json.loads(json.dumps(result, sort_keys=True, separators=(",", ":"))) == result


def test_missing_metadata_is_not_scored():
    assert_result(None, "not_scored", "answer_verification_metadata_missing")


def test_legacy_metadata_without_runtime_diagnostics_is_not_scored():
    assert_result(
        {"answer_faithfulness_status": "pass", "total_claims": 1, "status_counts": {"supported": 1}},
        "not_scored",
        "runtime_diagnostics_missing",
    )


def test_successful_runtime_pass_is_verified_metadata_present():
    assert_result(runtime_metadata(), "verified_metadata_present", "runtime_verification_completed")


def test_metadata_only_fallback_is_classified_without_blocking():
    assert_result(
        runtime_metadata(
            answer_faithfulness_status="not_scored",
            total_claims=0,
            metadata_only_fallback_used=True,
            runtime_verification_skipped_reason="missing_answer",
            verifier_input_claim_count=0,
            verifier_output_claim_count=0,
            diagnostics=["metadata_only_runtime_integration_fallback", "missing_answer"],
        ),
        "metadata_only_fallback",
        "metadata_only_fallback_used",
    )


def test_missing_runtime_evidence_is_insufficient_evidence():
    assert_result(
        runtime_metadata(
            answer_faithfulness_status="not_scored",
            total_claims=0,
            metadata_only_fallback_used=True,
            runtime_verification_skipped_reason="no_runtime_evidence_items",
            verifier_input_claim_count=1,
            verifier_output_claim_count=0,
            diagnostics=["metadata_only_runtime_integration_fallback", "no_runtime_evidence_items"],
        ),
        "insufficient_evidence",
        "runtime_evidence_insufficient",
    )


def test_unsupported_or_citation_failures_are_called_out():
    assert_result(
        runtime_metadata(
            answer_faithfulness_status="fail",
            status_counts={
                "supported": 0,
                "unsupported": 1,
                "contradicted": 0,
                "citation_missing": 0,
                "citation_mismatch": 1,
                "compliance_blocked": 0,
            },
            warnings=[
                "unsupported:C1:cited_span_does_not_support_claim",
                "citation_mismatch:C2:citation_points_to_wrong_source",
            ],
        ),
        "unsupported_claims_present",
        "status_count:unsupported",
    )


def test_verifier_error_takes_precedence():
    assert_result(
        runtime_metadata(
            answer_faithfulness_status="not_scored",
            total_claims=0,
            metadata_only_fallback_used=True,
            runtime_verification_skipped_reason="runtime_verifier_exception",
            runtime_verifier_error_type="ValueError",
            verifier_output_claim_count=0,
        ),
        "verifier_error",
        "runtime_verifier_error",
    )


def test_human_review_signals_are_classified():
    assert_result(
        runtime_metadata(
            answer_faithfulness_status="caution",
            status_counts={
                "supported": 0,
                "partially_supported": 1,
                "unsupported": 0,
                "contradicted": 0,
                "citation_missing": 0,
                "citation_mismatch": 0,
                "ambiguous": 0,
                "not_verifiable_from_context": 0,
                "compliance_blocked": 0,
            },
            compliance_tags=["biosafety"],
            warnings=["compliance_flag:biosafety"],
        ),
        "human_review_recommended",
        "status_count:partially_supported",
    )
