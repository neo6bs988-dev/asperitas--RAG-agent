from __future__ import annotations

import copy
import json

from asperitas_agent.answer_verification_integration import expose_answer_verification_metadata
from asperitas_agent.claim_verification_report_aggregator import aggregate_claim_verification_reports
from asperitas_agent.support_status_classifier import classify_answer_claim_support
from fixtures.claim_verification_biology_compliance_golden_set import (
    ANSWER_ID,
    EXPECTED_COMPLIANCE_TAGS,
    EXPECTED_FAILURE_MODE_BY_CLAIM_ID,
    EXPECTED_STATUS_BY_CLAIM_ID,
    EXPECTED_SUMMARY_COUNTS,
    GOLDEN_SET_ID,
    QUESTION,
    biology_compliance_golden_set_cases,
    golden_set_claims,
    golden_set_evidence_by_claim_id,
)


def _reports():
    return classify_answer_claim_support(golden_set_claims(), golden_set_evidence_by_claim_id())


def _summary():
    return aggregate_claim_verification_reports(_reports(), answer_id=ANSWER_ID, question=QUESTION)


def _answer_payload() -> dict:
    return {
        "query": QUESTION,
        "answer_status": "answered",
        "answer_text": "Fixture answer used only to expose passive verifier metadata.",
        "citations_used": [f"[E{index}]" for index in range(1, 10)],
        "metadata": {"generator_name": "fixture-generator"},
    }


def test_biology_compliance_golden_set_classifies_expected_fixture_labels():
    reports = _reports()

    assert [report.claim.claim_id for report in reports] == [f"C{index}" for index in range(1, 10)]
    assert {report.claim.claim_id: report.support_status for report in reports} == EXPECTED_STATUS_BY_CLAIM_ID
    assert {report.claim.claim_id: report.failure_mode for report in reports} == EXPECTED_FAILURE_MODE_BY_CLAIM_ID
    assert all(report.validate() == () for report in reports)


def test_fixture_source_provenance_and_biology_metadata_are_preserved():
    reports_by_claim_id = {report.claim.claim_id: report for report in _reports()}

    for case in biology_compliance_golden_set_cases():
        report = reports_by_claim_id[case.claim.claim_id]
        assert report.claim.metadata["golden_set_id"] == GOLDEN_SET_ID
        assert report.claim.metadata["truth_boundary_notes"] == case.truth_boundary_notes
        assert report.claim.detected_entities == case.claim.detected_entities
        assert tuple(sorted(report.claim.metadata["biology_entity_types"])) == report.claim.metadata["biology_entity_types"]
        for entity in report.claim.detected_entities:
            assert entity.validate() == ()
            assert entity.source_span_ids

        for span in report.candidate_evidence_spans:
            assert span.source_id
            assert span.span_id
            assert span.citation_key
            assert span.source_path.startswith("tests/fixtures/")
            assert span.chunk_id
            assert span.section_path
            assert span.license_tags
            assert span.metadata["fixture_source_rights"] == "synthetic_fixture_text"
            assert span.validate() == ()


def test_compliance_tags_surface_as_metadata_only_not_legal_or_regulatory_conclusions():
    reports = _reports()
    compliance_reports = [report for report in reports if report.claim.compliance_tags]
    summary = aggregate_claim_verification_reports(reports, answer_id=ANSWER_ID, question=QUESTION)

    assert [report.claim.claim_id for report in compliance_reports] == ["C7", "C8", "C9"]
    assert all(report.support_status == "supported" for report in compliance_reports)
    assert all(report.failure_mode is None for report in compliance_reports)
    assert summary.compliance_blocked_claims == 0
    assert summary.metrics["compliance_tags"] == list(EXPECTED_COMPLIANCE_TAGS)
    for tag in EXPECTED_COMPLIANCE_TAGS:
        assert f"compliance_flag:{tag}" in summary.warnings
    assert "legal_regulatory_approval_claim" not in summary.metrics["compliance_tags"]
    assert not any("legal_regulatory_approval_claim" in item for item in summary.warnings)


def test_aggregated_answer_summary_preserves_biology_compliance_diagnostics():
    summary = _summary()

    for field_name, expected_value in EXPECTED_SUMMARY_COUNTS.items():
        assert getattr(summary, field_name) == expected_value
    assert summary.answer_faithfulness_status == "fail"
    assert summary.metrics["claim_ids"] == [f"C{index}" for index in range(1, 10)]
    assert summary.metrics["citation_keys"] == [f"[E{index}]" for index in range(1, 10)]
    assert summary.metrics["evidence_span_ids"] == [
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "E6",
        "E6_SUPPORT",
        "E7",
        "E8",
        "E9",
    ]
    assert "resolved" in summary.metrics["diagnostics"]
    assert "span_signal:contradiction" in summary.metrics["diagnostics"]
    assert "span_signal:not_verifiable" in summary.metrics["diagnostics"]
    assert summary.metrics["claim_details"][0]["claim_metadata"]["golden_set_id"] == GOLDEN_SET_ID
    assert summary.metrics["claim_details"][6]["compliance_tags"] == ["biosafety"]
    assert summary.validate() == ()


def test_answer_metadata_integration_exposes_golden_set_summary_passively():
    summary = _summary()
    answer = _answer_payload()
    before = copy.deepcopy(answer)

    enriched = expose_answer_verification_metadata(answer, summary)
    verification = enriched["metadata"]["answer_verification"]

    assert answer == before
    assert enriched["answer_text"] == before["answer_text"]
    assert enriched["answer_status"] == before["answer_status"]
    assert enriched["citations_used"] == before["citations_used"]
    assert verification["answer_id"] == ANSWER_ID
    assert verification["status_counts"] == {
        "supported": 4,
        "partially_supported": 1,
        "unsupported": 1,
        "contradicted": 1,
        "citation_missing": 0,
        "citation_mismatch": 1,
        "ambiguous": 0,
        "not_verifiable_from_context": 1,
        "compliance_blocked": 0,
    }
    assert verification["summary"]["metrics"]["claim_details"][0]["claim_metadata"]["golden_set_id"] == GOLDEN_SET_ID
    assert verification["compliance_tags"] == list(EXPECTED_COMPLIANCE_TAGS)


def test_golden_set_pipeline_does_not_mutate_inputs_and_serializes_deterministically():
    claims = golden_set_claims()
    evidence_by_claim_id = golden_set_evidence_by_claim_id()
    before_claims = copy.deepcopy([claim.to_dict() for claim in claims])
    before_evidence = copy.deepcopy(
        {claim_id: [span.to_dict() for span in spans] for claim_id, spans in evidence_by_claim_id.items()}
    )

    first_reports = classify_answer_claim_support(claims, evidence_by_claim_id)
    second_reports = classify_answer_claim_support(claims, evidence_by_claim_id)
    first_summary = aggregate_claim_verification_reports(first_reports, answer_id=ANSWER_ID, question=QUESTION)
    second_summary = aggregate_claim_verification_reports(second_reports, answer_id=ANSWER_ID, question=QUESTION)
    first_encoded = json.dumps(
        {
            "reports": [report.to_dict() for report in first_reports],
            "summary": first_summary.to_dict(),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    second_encoded = json.dumps(
        {
            "reports": [report.to_dict() for report in second_reports],
            "summary": second_summary.to_dict(),
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    assert [claim.to_dict() for claim in claims] == before_claims
    assert {claim_id: [span.to_dict() for span in spans] for claim_id, spans in evidence_by_claim_id.items()} == before_evidence
    assert first_encoded == second_encoded
    assert json.loads(first_encoded)["summary"] == first_summary.to_dict()
