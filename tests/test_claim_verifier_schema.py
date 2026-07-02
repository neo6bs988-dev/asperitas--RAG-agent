from __future__ import annotations

import json

import pytest

from asperitas_agent.claim_verifier_schema import (
    ANSWER_FAITHFULNESS_STATUSES,
    BIOLOGY_ENTITY_TYPES,
    CLAIM_TYPES,
    COMPLIANCE_TRUTH_BOUNDARY_TAGS,
    FAILURE_MODES,
    SCHEMA_VERSION,
    SUPPORT_STATUSES,
    AnswerVerificationSummary,
    AtomicClaim,
    BiologyEntity,
    ClaimVerificationReport,
    EvidenceSpan,
    answer_verification_summary_from_dict,
    claim_verification_report_from_dict,
)


EXPECTED_SUPPORT_STATUSES = (
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "citation_missing",
    "citation_mismatch",
    "ambiguous",
    "not_verifiable_from_context",
    "compliance_blocked",
)

EXPECTED_BIOLOGY_ENTITY_TYPES = (
    "species",
    "gene",
    "protein",
    "compound",
    "pathway",
    "assay",
    "phenotype",
    "tissue_or_cell_type",
    "disease_or_condition",
    "organism_or_source_material",
    "experimental_method",
    "measurement_value_unit",
    "biological_relation_type",
)

EXPECTED_COMPLIANCE_TAGS = (
    "cites",
    "nagoya_abs",
    "lmo_gmo",
    "biosafety",
    "ip_license",
    "human_clinical_sensitivity",
    "export_or_security_sensitive_biology",
    "production_db_claim",
    "production_kg_claim",
    "production_vector_db_claim",
    "wet_lab_validation_claim",
    "legal_regulatory_approval_claim",
    "autonomous_lab_claim",
    "foundation_model_completion_claim",
)

EXPECTED_FAILURE_MODES = (
    "no_citation",
    "citation_points_to_wrong_source",
    "cited_span_does_not_support_claim",
    "claim_contradicts_cited_span",
    "answer_uses_parametric_memory_over_context",
    "entity_mismatch",
    "numeric_or_unit_mismatch",
    "overgeneralization",
    "compliance_sensitive_unverified_claim",
    "source_metadata_missing",
    "evidence_span_missing",
    "verifier_not_applicable",
)


def valid_entity(**overrides) -> BiologyEntity:
    kwargs = {
        "entity_text": "Arabidopsis thaliana",
        "entity_type": "species",
        "normalized_label": "Arabidopsis thaliana",
        "source_span_ids": ("S1",),
        "confidence": 0.91,
        "metadata": {"detector": "fixture"},
    }
    return BiologyEntity(**{**kwargs, **overrides})


def valid_claim(**overrides) -> AtomicClaim:
    kwargs = {
        "claim_id": "C1",
        "answer_id": "A1",
        "claim_text": "Arabidopsis thaliana is used as a model plant species.",
        "claim_type": "sourced_fact",
        "source_sentence": "Arabidopsis thaliana is used as a model plant species. [E1]",
        "sentence_index": 0,
        "cited_source_ids": ("SRC-1",),
        "cited_span_ids": ("S1",),
        "citation_keys": ("[E1]",),
        "required_evidence_type": "exact_text",
        "detected_entities": (valid_entity(),),
        "compliance_tags": (),
        "support_status": "supported",
        "confidence": 0.88,
        "verifier_notes": "The cited span directly supports the claim.",
        "failure_mode": None,
        "blocking": False,
        "metadata": {"schema_step": "v1.5c"},
    }
    return AtomicClaim(**{**kwargs, **overrides})


def valid_span(**overrides) -> EvidenceSpan:
    kwargs = {
        "source_id": "SRC-1",
        "span_id": "S1",
        "document_title": "Plant model systems",
        "section": "Background",
        "locator": "p. 1",
        "evidence_text_hash_or_excerpt": "Arabidopsis thaliana is a model plant species.",
        "metadata": {"source_priority": "P3"},
        "license_tags": ("public",),
        "compliance_tags": (),
        "retrieval_rank": 1,
        "retrieval_score": 0.73,
        "citation_key": "[E1]",
        "chunk_id": "chunk-1",
        "source_path": "docs/example.md",
        "section_heading": "Background",
        "section_path": ("Background",),
    }
    return EvidenceSpan(**{**kwargs, **overrides})


def valid_report(**overrides) -> ClaimVerificationReport:
    kwargs = {
        "claim": valid_claim(),
        "candidate_evidence_spans": (valid_span(),),
        "support_status": "supported",
        "confidence": 0.88,
        "support_rationale": "Direct evidence match.",
        "failure_mode": None,
        "blocking": False,
        "warnings": (),
        "metadata": {"deterministic": True},
    }
    return ClaimVerificationReport(**{**kwargs, **overrides})


def valid_summary(**overrides) -> AnswerVerificationSummary:
    kwargs = {
        "answer_id": "A1",
        "question": "What model plant is referenced?",
        "total_claims": 2,
        "supported_claims": 1,
        "partially_supported_claims": 0,
        "unsupported_claims": 0,
        "contradicted_claims": 0,
        "citation_missing_claims": 0,
        "citation_mismatch_claims": 0,
        "compliance_blocked_claims": 1,
        "ambiguous_claims": 0,
        "not_verifiable_from_context_claims": 0,
        "answer_faithfulness_status": "caution",
        "blocking_failures": ("compliance_sensitive_unverified_claim",),
        "warnings": ("Human review required for compliance-sensitive claim.",),
        "metrics": {"claim_support_rate": 0.5},
    }
    return AnswerVerificationSummary(**{**kwargs, **overrides})


def test_taxonomy_values_are_stable_and_complete():
    assert SUPPORT_STATUSES == EXPECTED_SUPPORT_STATUSES
    assert BIOLOGY_ENTITY_TYPES == EXPECTED_BIOLOGY_ENTITY_TYPES
    assert COMPLIANCE_TRUTH_BOUNDARY_TAGS == EXPECTED_COMPLIANCE_TAGS
    assert FAILURE_MODES == EXPECTED_FAILURE_MODES
    assert "sourced_fact" in CLAIM_TYPES
    assert ANSWER_FAITHFULNESS_STATUSES == ("pass", "caution", "fail", "not_scored")


def test_valid_claim_report_and_summary_validate():
    assert valid_entity().validate() == ()
    assert valid_claim().validate() == ()
    assert valid_span().validate() == ()
    assert valid_report().validate() == ()
    assert valid_summary().validate() == ()


def test_claim_report_round_trip_serialization_is_json_safe():
    report = valid_report()
    payload = report.to_dict()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    restored = claim_verification_report_from_dict(json.loads(encoded))

    assert payload["schema_version"] == SCHEMA_VERSION
    assert restored.validate() == ()
    assert restored.to_dict() == payload


def test_answer_summary_round_trip_serialization_is_json_safe():
    summary = valid_summary()
    payload = summary.to_dict()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    restored = answer_verification_summary_from_dict(json.loads(encoded))

    assert restored.validate() == ()
    assert restored.to_dict() == payload


def test_invalid_claim_enum_and_failure_mode_are_rejected():
    claim = valid_claim(
        claim_type="unsupported_claim_type",
        support_status="too_vague",
        failure_mode="unknown_failure",
        compliance_tags=("not_a_tag",),
    )
    errors = claim.validate()

    assert "invalid claim_type: unsupported_claim_type" in errors
    assert "invalid support_status: too_vague" in errors
    assert "invalid failure_mode: unknown_failure" in errors
    assert "invalid compliance_tags: not_a_tag" in errors


def test_unsupported_claim_requires_normalized_failure_mode():
    claim = valid_claim(support_status="unsupported", failure_mode=None)

    assert "failure_mode is required when support_status is not supported" in claim.validate()


def test_evidence_span_validation_rejects_bad_rank_score_and_tags():
    span = valid_span(
        evidence_text_hash_or_excerpt="",
        compliance_tags=("not_a_tag",),
        retrieval_rank=0,
        retrieval_score=-0.1,
    )
    errors = span.validate()

    assert "evidence_text_hash_or_excerpt is required" in errors
    assert "invalid compliance_tags: not_a_tag" in errors
    assert "retrieval_rank must be >= 1" in errors
    assert "retrieval_score must be non-negative" in errors


def test_numeric_validation_returns_errors_without_typeerror():
    claim_errors = valid_claim(sentence_index="first").validate()
    span_errors = valid_span(retrieval_rank="1", retrieval_score="high").validate()
    summary_errors = valid_summary(total_claims="2").validate()

    assert "sentence_index must be a non-negative integer" in claim_errors
    assert "retrieval_rank must be an integer" in span_errors
    assert "retrieval_score must be numeric" in span_errors
    assert "total_claims must be a non-negative integer" in summary_errors


def test_report_validation_rejects_mismatched_claim_status():
    claim = valid_claim(support_status="citation_missing", failure_mode="no_citation", blocking=True)
    report = valid_report(claim=claim, support_status="supported")

    assert "support_status must match claim.support_status" in report.validate()


def test_summary_validation_rejects_invalid_status_and_count_overflow():
    summary = valid_summary(total_claims=1, answer_faithfulness_status="green")
    errors = summary.validate()

    assert "invalid answer_faithfulness_status: green" in errors
    assert "status claim counts cannot exceed total_claims" in errors


def test_require_valid_raises_value_error_for_invalid_schema():
    with pytest.raises(ValueError, match="invalid support_status"):
        valid_claim(support_status="not_real").require_valid()
