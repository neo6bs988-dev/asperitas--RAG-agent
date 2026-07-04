from __future__ import annotations

import copy
import json

from asperitas_agent.claim_verification_report_aggregator import (
    AGGREGATOR_NAME,
    aggregate_claim_verification_reports,
)
from asperitas_agent.claim_verifier_schema import (
    AtomicClaim,
    ClaimVerificationReport,
    EvidenceSpan,
    answer_verification_summary_from_dict,
)
from asperitas_agent.support_status_classifier import classify_claim_support


def valid_claim(**overrides) -> AtomicClaim:
    kwargs = {
        "claim_id": "C1",
        "answer_id": "A1",
        "claim_text": "The answer contract includes citation keys [E1].",
        "claim_type": "sourced_fact",
        "source_sentence": "The answer contract includes citation keys [E1].",
        "sentence_index": 0,
        "cited_source_ids": ("SRC-1",),
        "cited_span_ids": ("E1",),
        "citation_keys": ("[E1]",),
        "required_evidence_type": "retrieved_context_or_source_metadata",
        "detected_entities": (),
        "compliance_tags": (),
        "support_status": "supported",
        "confidence": 0.9,
        "verifier_notes": "Supported by deterministic fixture.",
        "failure_mode": None,
        "blocking": False,
        "metadata": {"fixture": "aggregator"},
    }
    return AtomicClaim(**{**kwargs, **overrides})


def valid_span(**overrides) -> EvidenceSpan:
    kwargs = {
        "source_id": "SRC-1",
        "span_id": "E1",
        "document_title": "Verifier notes",
        "section": "Contracts",
        "locator": "line 1",
        "evidence_text_hash_or_excerpt": "The answer contract includes citation keys.",
        "metadata": {"source_priority": "P3"},
        "license_tags": (),
        "compliance_tags": (),
        "retrieval_rank": 1,
        "retrieval_score": 0.73,
        "citation_key": "[E1]",
        "chunk_id": "chunk-1",
        "source_path": "docs/example.md",
        "section_heading": "Contracts",
        "section_path": ("Contracts",),
    }
    return EvidenceSpan(**{**kwargs, **overrides})


def valid_report(**overrides) -> ClaimVerificationReport:
    status = overrides.pop("support_status", "supported")
    failure_mode = overrides.pop("failure_mode", None if status == "supported" else "cited_span_does_not_support_claim")
    blocking = overrides.pop("blocking", status in {"unsupported", "contradicted", "citation_missing", "citation_mismatch"})
    claim = overrides.pop(
        "claim",
        valid_claim(
            support_status=status,
            failure_mode=failure_mode,
            blocking=blocking,
        ),
    )
    kwargs = {
        "claim": claim,
        "candidate_evidence_spans": (valid_span(),),
        "support_status": status,
        "confidence": 0.88,
        "support_rationale": "Deterministic fixture rationale.",
        "failure_mode": failure_mode,
        "blocking": blocking,
        "warnings": (),
        "metadata": {"matcher_diagnostics": ["resolved"], "deterministic": True},
    }
    return ClaimVerificationReport(**{**kwargs, **overrides})


def report_for_status(claim_id: str, status: str, failure_mode: str | None = None, **overrides) -> ClaimVerificationReport:
    default_failure_modes = {
        "partially_supported": "overgeneralization",
        "unsupported": "cited_span_does_not_support_claim",
        "contradicted": "claim_contradicts_cited_span",
        "citation_missing": "no_citation",
        "citation_mismatch": "citation_points_to_wrong_source",
        "ambiguous": "verifier_not_applicable",
        "not_verifiable_from_context": "evidence_span_missing",
        "compliance_blocked": "compliance_sensitive_unverified_claim",
    }
    resolved_failure_mode = failure_mode if failure_mode is not None else default_failure_modes.get(status)
    claim = valid_claim(
        claim_id=claim_id,
        citation_keys=(f"[E{claim_id[1:]}]",),
        cited_span_ids=(f"E{claim_id[1:]}",),
        support_status=status,
        failure_mode=resolved_failure_mode,
        blocking=status in {"unsupported", "contradicted", "citation_missing", "citation_mismatch", "compliance_blocked"},
        **overrides.pop("claim_overrides", {}),
    )
    span = valid_span(span_id=f"E{claim_id[1:]}", citation_key=f"[E{claim_id[1:]}]")
    return valid_report(
        claim=claim,
        candidate_evidence_spans=(span,),
        support_status=status,
        failure_mode=resolved_failure_mode,
        blocking=claim.blocking,
        **overrides,
    )


def test_empty_report_list_returns_not_scored_summary_with_no_claim_diagnostic():
    summary = aggregate_claim_verification_reports([], answer_id="A-empty", question="What is supported?")

    assert summary.total_claims == 0
    assert summary.answer_faithfulness_status == "not_scored"
    assert summary.not_verifiable_from_context_claims == 0
    assert "not_verifiable_from_context:no_claims" in summary.warnings
    assert summary.metrics["claim_details"] == []
    assert summary.validate() == ()


def test_all_supported_claims_pass_and_preserve_ids():
    reports = [report_for_status("C1", "supported"), report_for_status("C2", "supported")]

    summary = aggregate_claim_verification_reports(reports, question="What is supported?")

    assert summary.answer_id == "A1"
    assert summary.answer_faithfulness_status == "pass"
    assert summary.total_claims == 2
    assert summary.supported_claims == 2
    assert summary.metrics["claim_ids"] == ["C1", "C2"]
    assert summary.metrics["aggregator_name"] == AGGREGATOR_NAME
    assert summary.validate() == ()


def test_mixed_supported_partial_and_unsupported_counts():
    reports = [
        report_for_status("C1", "supported"),
        report_for_status("C2", "partially_supported"),
        report_for_status("C3", "unsupported"),
    ]

    summary = aggregate_claim_verification_reports(reports, question="What is mixed?")

    assert summary.supported_claims == 1
    assert summary.partially_supported_claims == 1
    assert summary.unsupported_claims == 1
    assert summary.answer_faithfulness_status == "fail"
    assert summary.blocking_failures == ()
    assert "unsupported:C3:cited_span_does_not_support_claim" in summary.warnings
    assert summary.validate() == ()


def test_contradicted_creates_blocking_diagnostic():
    summary = aggregate_claim_verification_reports(
        [report_for_status("C1", "contradicted")],
        question="What is contradicted?",
    )

    assert summary.contradicted_claims == 1
    assert summary.answer_faithfulness_status == "fail"
    assert summary.blocking_failures == ("contradicted:C1:claim_contradicts_cited_span",)
    assert summary.validate() == ()


def test_citation_missing_and_mismatch_counts_and_warnings():
    reports = [
        report_for_status("C1", "citation_missing"),
        report_for_status("C2", "citation_mismatch"),
    ]

    summary = aggregate_claim_verification_reports(reports, question="What has citation issues?")

    assert summary.citation_missing_claims == 1
    assert summary.citation_mismatch_claims == 1
    assert "citation_missing:C1:no_citation" in summary.warnings
    assert "citation_mismatch:C2:citation_points_to_wrong_source" in summary.warnings
    assert summary.validate() == ()


def test_ambiguous_and_not_verifiable_counts():
    reports = [
        report_for_status("C1", "ambiguous"),
        report_for_status("C2", "not_verifiable_from_context"),
    ]

    summary = aggregate_claim_verification_reports(reports, question="What is unclear?")

    assert summary.ambiguous_claims == 1
    assert summary.not_verifiable_from_context_claims == 1
    assert summary.answer_faithfulness_status == "caution"
    assert summary.validate() == ()


def test_compliance_truth_boundary_tags_are_preserved_as_warnings_only():
    claim = valid_claim(
        claim_id="C1",
        compliance_tags=("biosafety", "legal_regulatory_approval_claim"),
        support_status="supported",
    )
    report = valid_report(claim=claim)

    summary = aggregate_claim_verification_reports([report], question="What has flags?")

    assert summary.compliance_blocked_claims == 0
    assert summary.metrics["compliance_tags"] == ["biosafety", "legal_regulatory_approval_claim"]
    assert "compliance_flag:biosafety" in summary.warnings
    assert "compliance_flag:legal_regulatory_approval_claim" in summary.warnings
    assert summary.blocking_failures == ()
    assert summary.validate() == ()


def test_failure_modes_and_diagnostics_are_preserved():
    report = report_for_status(
        "C1",
        "unsupported",
        metadata={
            "matcher_diagnostics": ["resolved"],
            "span_signals": [{"not_verifiable": True, "numeric_conflict": False, "contradiction": False}],
        },
    )

    summary = aggregate_claim_verification_reports([report], question="What failed?")

    assert summary.metrics["failure_modes"] == ["cited_span_does_not_support_claim"]
    assert summary.metrics["diagnostics"] == ["resolved", "span_signal:not_verifiable"]
    assert summary.metrics["claim_details"][0]["failure_mode"] == "cited_span_does_not_support_claim"
    assert summary.validate() == ()


def test_deterministic_aggregate_lists_and_claim_order():
    reports = [
        report_for_status("C2", "unsupported"),
        report_for_status("C1", "supported"),
    ]

    first = aggregate_claim_verification_reports(reports, question="What order?")
    second = aggregate_claim_verification_reports(reports, question="What order?")

    assert first.to_dict() == second.to_dict()
    assert [detail["claim_id"] for detail in first.metrics["claim_details"]] == ["C2", "C1"]
    assert first.metrics["citation_keys"] == ["[E1]", "[E2]"]
    assert first.metrics["evidence_span_ids"] == ["E1", "E2"]
    assert first.validate() == ()


def test_inputs_are_not_mutated():
    reports = [report_for_status("C1", "supported"), report_for_status("C2", "unsupported")]
    before = copy.deepcopy([report.to_dict() for report in reports])

    aggregate_claim_verification_reports(reports, question="Mutation?")

    assert [report.to_dict() for report in reports] == before


def test_summary_serialization_is_json_safe():
    summary = aggregate_claim_verification_reports(
        [report_for_status("C1", "supported")],
        question="Can this serialize?",
    )
    payload = summary.to_dict()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    restored = answer_verification_summary_from_dict(json.loads(encoded))

    assert restored.validate() == ()
    assert restored.to_dict() == payload


def test_integration_with_support_status_classifier_output():
    claim = valid_claim(
        claim_id="C1",
        claim_text="The answer contract includes citation keys [E1].",
        citation_keys=("[E1]",),
        cited_source_ids=(),
        cited_span_ids=(),
        support_status="not_verifiable_from_context",
        confidence=None,
        failure_mode="verifier_not_applicable",
    )
    span = valid_span(evidence_text_hash_or_excerpt="The answer contract includes citation keys.")
    report = classify_claim_support(claim, [span])

    summary = aggregate_claim_verification_reports([report], question="What is supported?")

    assert summary.supported_claims == 1
    assert summary.answer_faithfulness_status == "pass"
    assert summary.metrics["claim_details"][0]["claim_id"] == "C1"
    assert summary.metrics["claim_details"][0]["diagnostics"] == ["resolved"]
    assert summary.validate() == ()
