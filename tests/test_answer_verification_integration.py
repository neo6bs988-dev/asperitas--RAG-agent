from __future__ import annotations

import copy
import json
from dataclasses import replace

from asperitas_agent.answer_verification_integration import (
    ANSWER_VERIFICATION_METADATA_KEY,
    INTEGRATION_NAME,
    build_answer_verification_metadata,
    expose_answer_verification_metadata,
)
from asperitas_agent.claim_verification_report_aggregator import aggregate_claim_verification_reports
from asperitas_agent.claim_verifier_schema import AtomicClaim, ClaimVerificationReport, EvidenceSpan
from asperitas_agent.schemas import (
    CitationCoverage,
    GroundedAnswer,
    GroundedAnswerMetadata,
    GuardrailDecisionSummary,
)


def answer_payload() -> dict:
    return {
        "query": "What is verified?",
        "answer_status": "answered",
        "answer_text": "The answer contract preserves citations [E1].",
        "citations_used": ["[E1]"],
        "citation_coverage": {"all_claims_cited": True},
        "metadata": {"generator_name": "fixture-generator", "generator_version": "test"},
    }


def grounded_answer() -> GroundedAnswer:
    return GroundedAnswer(
        query="What is verified?",
        answer_status="answered",
        answer_text="The answer contract preserves citations [E1].",
        citations_used=["[E1]"],
        citation_coverage=CitationCoverage(
            evidence_item_count=1,
            cited_evidence_count=1,
            uncited_evidence_count=0,
            all_claims_cited=True,
        ),
        guardrail_decision_summary=GuardrailDecisionSummary(
            decision="proceed",
            should_abstain=False,
            confidence_level="high",
            recommended_next_action="Use cited evidence only.",
            warnings=[],
            reasons=[],
        ),
        evidence_used=[],
        limitations=[],
        metadata=GroundedAnswerMetadata(generator_name="fixture-generator", generator_version="test"),
    )


def report_for_status(
    claim_id: str,
    status: str,
    *,
    failure_mode: str | None = None,
    blocking: bool | None = None,
    warnings: tuple[str, ...] = (),
    compliance_tags: tuple[str, ...] = (),
    metadata: dict | None = None,
) -> ClaimVerificationReport:
    default_failure_modes = {
        "unsupported": "cited_span_does_not_support_claim",
        "contradicted": "claim_contradicts_cited_span",
        "citation_missing": "no_citation",
        "citation_mismatch": "citation_points_to_wrong_source",
        "not_verifiable_from_context": "evidence_span_missing",
    }
    resolved_failure_mode = failure_mode if failure_mode is not None else default_failure_modes.get(status)
    resolved_blocking = status in {"unsupported", "contradicted", "citation_missing", "citation_mismatch"} if blocking is None else blocking
    suffix = claim_id[1:] if claim_id.startswith("C") else claim_id
    claim = AtomicClaim(
        claim_id=claim_id,
        answer_id="A1",
        claim_text=f"Claim {claim_id} uses citation [E{suffix}].",
        claim_type="sourced_fact",
        cited_source_ids=(f"SRC-{suffix}",),
        cited_span_ids=(f"SPAN-{suffix}",),
        required_evidence_type="retrieved_context_or_source_metadata",
        compliance_tags=compliance_tags,
        support_status=status,
        confidence=0.87,
        verifier_notes="Fixture support decision.",
        failure_mode=resolved_failure_mode,
        citation_keys=(f"[E{suffix}]",),
        blocking=resolved_blocking,
        metadata={"claim_fixture": claim_id},
    )
    span = EvidenceSpan(
        source_id=f"SRC-{suffix}",
        span_id=f"SPAN-{suffix}",
        evidence_text_hash_or_excerpt=f"Claim {claim_id} uses citation.",
        citation_key=f"[E{suffix}]",
        source_path=f"docs/source-{suffix}.md",
        metadata={"source_priority": "P1"},
    )
    return ClaimVerificationReport(
        claim=claim,
        candidate_evidence_spans=(span,),
        support_status=status,
        confidence=0.87,
        support_rationale="Fixture support decision.",
        failure_mode=resolved_failure_mode,
        blocking=resolved_blocking,
        warnings=warnings,
        metadata=metadata or {"matcher_diagnostics": ["resolved"]},
    )


def summary_for(*reports: ClaimVerificationReport):
    return aggregate_claim_verification_reports(list(reports), answer_id="A1", question="What is verified?")


def test_build_metadata_surfaces_aggregate_summary_fields():
    summary = summary_for(report_for_status("C1", "supported"))

    metadata = build_answer_verification_metadata(summary)

    assert metadata["integration_name"] == INTEGRATION_NAME
    assert metadata["deterministic"] is True
    assert metadata["answer_faithfulness_status"] == "pass"
    assert metadata["status_counts"]["supported"] == 1
    assert metadata["claim_ids"] == ["C1"]
    assert metadata["summary"]["total_claims"] == 1
    assert metadata["runtime_readiness"]["readiness_classification"] == "not_scored"
    assert metadata["runtime_readiness"]["reason_codes"] == ["runtime_diagnostics_missing"]
    assert metadata["runtime_readiness"]["production_verification_claim"] is False
    assert metadata["runtime_readiness"]["metadata_interpretation_only"] is True


def test_build_metadata_attaches_runtime_readiness_from_runtime_diagnostics():
    summary = summary_for(report_for_status("C1", "supported"))
    summary = replace(
        summary,
        metrics={
            **summary.metrics,
            "diagnostics": ["runtime_verification_completed"],
            "runtime_verifier_enabled": True,
            "runtime_verification_attempted": True,
            "runtime_verification_skipped_reason": "",
            "metadata_only_fallback_used": False,
            "verifier_input_claim_count": 1,
            "verifier_output_claim_count": 1,
            "verifier_failure_modes": [],
            "verifier_schema_version": summary.schema_version,
            "runtime_evidence_metadata": [{"source_id": "SRC-1"}],
        },
    )

    metadata = build_answer_verification_metadata(summary)

    readiness = metadata["runtime_readiness"]
    assert readiness["readiness_classification"] == "verified_metadata_present"
    assert readiness["reason_codes"] == ["runtime_verification_completed"]
    assert readiness["production_verification_claim"] is False
    assert readiness["metadata_interpretation_only"] is True
    assert json.loads(json.dumps(readiness, sort_keys=True, separators=(",", ":"))) == readiness

def test_attach_uses_existing_metadata_hook_without_rewriting_answer_text():
    summary = summary_for(report_for_status("C1", "supported"))
    answer = answer_payload()
    before = copy.deepcopy(answer)

    enriched = expose_answer_verification_metadata(answer, summary)

    assert enriched["answer_text"] == before["answer_text"]
    assert enriched["citations_used"] == before["citations_used"]
    assert enriched["metadata"]["generator_version"] == "test"
    assert ANSWER_VERIFICATION_METADATA_KEY in enriched["metadata"]
    assert answer == before


def test_attach_accepts_grounded_answer_without_changing_answer_behavior():
    summary = summary_for(report_for_status("C1", "supported"))
    answer = grounded_answer()
    before = answer.to_json()

    enriched = expose_answer_verification_metadata(answer, summary)

    assert answer.to_json() == before
    assert enriched["answer_text"] == before["answer_text"]
    assert enriched["answer_status"] == before["answer_status"]
    assert enriched["metadata"]["answer_verification"]["answer_faithfulness_status"] == "pass"


def test_contradicted_blocking_is_surfaced_in_metadata():
    summary = summary_for(
        report_for_status(
            "C1",
            "contradicted",
            metadata={
                "matcher_diagnostics": ["resolved"],
                "span_signals": [{"contradiction": True, "numeric_conflict": False, "not_verifiable": False}],
            },
        )
    )

    enriched = expose_answer_verification_metadata(answer_payload(), summary)
    verification = enriched["metadata"]["answer_verification"]

    assert verification["answer_faithfulness_status"] == "fail"
    assert verification["status_counts"]["contradicted"] == 1
    assert verification["blocking_failures"] == ["contradicted:C1:claim_contradicts_cited_span"]
    assert "span_signal:contradiction" in verification["diagnostics"]


def test_warning_statuses_are_surfaced_in_metadata():
    summary = summary_for(
        report_for_status("C1", "unsupported"),
        report_for_status("C2", "citation_missing"),
        report_for_status("C3", "citation_mismatch"),
    )

    verification = expose_answer_verification_metadata(answer_payload(), summary)["metadata"]["answer_verification"]

    assert verification["status_counts"]["unsupported"] == 1
    assert verification["status_counts"]["citation_missing"] == 1
    assert verification["status_counts"]["citation_mismatch"] == 1
    assert "unsupported:C1:cited_span_does_not_support_claim" in verification["warnings"]
    assert "citation_missing:C2:no_citation" in verification["warnings"]
    assert "citation_mismatch:C3:citation_points_to_wrong_source" in verification["warnings"]


def test_no_claims_not_verifiable_signal_is_surfaced():
    summary = aggregate_claim_verification_reports([], answer_id="A-empty", question="What is verified?")

    verification = expose_answer_verification_metadata(answer_payload(), summary)["metadata"]["answer_verification"]

    assert verification["answer_faithfulness_status"] == "not_scored"
    assert verification["total_claims"] == 0
    assert "not_verifiable_from_context:no_claims" in verification["warnings"]


def test_provenance_citation_evidence_and_compliance_ids_are_preserved():
    summary = summary_for(
        report_for_status(
            "C1",
            "supported",
            compliance_tags=("biosafety",),
            warnings=("fixture_warning",),
        )
    )

    verification = expose_answer_verification_metadata(answer_payload(), summary)["metadata"]["answer_verification"]
    detail = verification["claim_details"][0]

    assert verification["citation_keys"] == ["[E1]"]
    assert verification["evidence_span_ids"] == ["SPAN-1"]
    assert verification["source_ids"] == ["SRC-1"]
    assert verification["compliance_tags"] == ["biosafety"]
    assert detail["citation_keys"] == ["[E1]"]
    assert detail["evidence_span_ids"] == ["SPAN-1"]
    assert detail["source_ids"] == ["SRC-1"]
    assert "compliance_flag:biosafety" in verification["warnings"]


def test_enriched_payload_is_json_safe_and_deterministic():
    summary = summary_for(report_for_status("C1", "supported"))

    first = expose_answer_verification_metadata(answer_payload(), summary)
    second = expose_answer_verification_metadata(answer_payload(), summary)

    assert first == second
    assert json.loads(json.dumps(first, sort_keys=True, separators=(",", ":"))) == first


def test_rejects_empty_metadata_key():
    summary = summary_for(report_for_status("C1", "supported"))

    try:
        expose_answer_verification_metadata(answer_payload(), summary, metadata_key=" ")
    except ValueError as exc:
        assert "metadata_key" in str(exc)
    else:
        raise AssertionError("empty metadata_key should fail")
