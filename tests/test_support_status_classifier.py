from __future__ import annotations

import copy
import json

from asperitas_agent.claim_extractor import extract_atomic_claims
from asperitas_agent.claim_verifier_schema import (
    AtomicClaim,
    EvidenceSpan,
    claim_verification_report_from_dict,
)
from asperitas_agent.evidence_span_matcher import resolve_claim_citations
from asperitas_agent.support_status_classifier import (
    CLASSIFIER_NAME,
    classify_answer_claim_support,
    classify_claim_support,
)


def valid_claim(**overrides) -> AtomicClaim:
    kwargs = {
        "claim_id": "C1",
        "answer_id": "A1",
        "claim_text": "The answer contract includes citation keys [E1].",
        "claim_type": "sourced_fact",
        "source_sentence": "The answer contract includes citation keys [E1].",
        "sentence_index": 0,
        "cited_source_ids": (),
        "cited_span_ids": (),
        "citation_keys": ("[E1]",),
        "required_evidence_type": "retrieved_context_or_source_metadata",
        "detected_entities": (),
        "compliance_tags": (),
        "support_status": "not_verifiable_from_context",
        "confidence": None,
        "verifier_notes": "Support has not been verified.",
        "failure_mode": "verifier_not_applicable",
        "blocking": False,
        "metadata": {"fixture": "classifier"},
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
        "citation_key": "",
        "chunk_id": "chunk-1",
        "source_path": "docs/example.md",
        "section_heading": "Contracts",
        "section_path": ("Contracts",),
    }
    return EvidenceSpan(**{**kwargs, **overrides})


def test_citation_missing_without_claim_citation_keys():
    report = classify_claim_support(valid_claim(citation_keys=()), [])

    assert report.support_status == "citation_missing"
    assert report.failure_mode == "no_citation"
    assert report.blocking is True
    assert report.claim.support_status == "citation_missing"
    assert report.validate() == ()


def test_citation_mismatch_from_unresolved_matcher_diagnostic():
    report = classify_claim_support(valid_claim(citation_keys=("[E9]",)), [valid_span(span_id="E1")])

    assert report.support_status == "citation_mismatch"
    assert report.failure_mode == "citation_points_to_wrong_source"
    assert "matcher_diagnostic:unresolved" in report.warnings
    assert report.validate() == ()


def test_supported_when_claim_strongly_overlaps_cited_span():
    report = classify_claim_support(valid_claim(), [valid_span()])

    assert report.support_status == "supported"
    assert report.failure_mode is None
    assert report.blocking is False
    assert report.claim.cited_source_ids == ("SRC-1",)
    assert report.claim.cited_span_ids == ("E1",)
    assert report.claim.metadata["support_classifier_name"] == CLASSIFIER_NAME
    assert report.validate() == ()


def test_partially_supported_for_some_important_overlap():
    claim = valid_claim(claim_text="The answer contract includes citation keys and blocking warnings [E1].")
    span = valid_span(evidence_text_hash_or_excerpt="The answer contract includes citation keys.")

    report = classify_claim_support(claim, [span])

    assert report.support_status == "partially_supported"
    assert report.failure_mode == "overgeneralization"
    assert report.blocking is False
    assert report.validate() == ()


def test_unsupported_for_unrelated_evidence():
    claim = valid_claim(claim_text="The source registry preserves source priority [E1].")
    span = valid_span(evidence_text_hash_or_excerpt="The workflow planner creates ordered task steps.")

    report = classify_claim_support(claim, [span])

    assert report.support_status == "unsupported"
    assert report.failure_mode == "cited_span_does_not_support_claim"
    assert report.blocking is True
    assert report.validate() == ()


def test_contradicted_increase_decrease_signal():
    claim = valid_claim(claim_text="Treatment increases pathway activity [E1].")
    span = valid_span(evidence_text_hash_or_excerpt="Treatment decreases pathway activity in the assay.")

    report = classify_claim_support(claim, [span])

    assert report.support_status == "contradicted"
    assert report.failure_mode == "claim_contradicts_cited_span"
    assert report.blocking is True
    assert report.validate() == ()


def test_contradicted_present_absent_signal():
    claim = valid_claim(claim_text="The FLC protein is detected in the assay [E1].")
    span = valid_span(evidence_text_hash_or_excerpt="The FLC protein is not detected in the assay.")

    report = classify_claim_support(claim, [span])

    assert report.support_status == "contradicted"
    assert report.failure_mode == "claim_contradicts_cited_span"
    assert report.validate() == ()


def test_numeric_mismatch_blocks_supported_status():
    claim = valid_claim(claim_text="The assay reports 25 percent inhibition [E1].")
    span = valid_span(evidence_text_hash_or_excerpt="The assay reports 15 percent inhibition.")

    report = classify_claim_support(claim, [span])

    assert report.support_status == "contradicted"
    assert report.failure_mode == "numeric_or_unit_mismatch"
    assert report.support_status != "supported"
    assert report.validate() == ()


def test_duplicate_citation_matches_remain_citation_mismatch_before_classification():
    claim = valid_claim(claim_text="Treatment increases pathway activity [E1].")
    spans = [
        valid_span(span_id="S1", citation_key="[E1]", evidence_text_hash_or_excerpt="Treatment increases pathway activity."),
        valid_span(span_id="S2", source_id="SRC-2", citation_key="[E1]", evidence_text_hash_or_excerpt="Treatment decreases pathway activity."),
    ]

    report = classify_claim_support(claim, spans)

    assert report.support_status == "citation_mismatch"
    assert report.failure_mode == "citation_points_to_wrong_source"


def test_ambiguous_for_supplied_conflicting_candidate_spans_without_duplicate_key():
    claim = valid_claim(claim_text="Treatment increases pathway activity [E1].", citation_keys=("[E1]",))
    spans = [
        valid_span(span_id="E1", evidence_text_hash_or_excerpt="Treatment increases pathway activity."),
        valid_span(span_id="S2", source_id="SRC-2", evidence_text_hash_or_excerpt="Treatment decreases pathway activity."),
    ]

    report = classify_claim_support(claim, spans)

    assert report.support_status == "ambiguous"
    assert report.failure_mode == "verifier_not_applicable"
    assert "conflicting_support_signals" in report.warnings
    assert report.validate() == ()


def test_not_verifiable_from_context_for_too_short_evidence_text():
    report = classify_claim_support(valid_claim(), [valid_span(evidence_text_hash_or_excerpt="N/A")])

    assert report.support_status == "not_verifiable_from_context"
    assert report.failure_mode == "evidence_span_missing"
    assert "evidence_text_not_verifiable" in report.warnings
    assert report.validate() == ()


def test_mapping_evidence_records_are_accepted():
    record = {
        "source_id": "SRC-1",
        "span_id": "E1",
        "text_excerpt": "The answer contract includes citation keys.",
        "source_priority": "P3",
    }

    report = classify_claim_support(valid_claim(), [record])

    assert report.support_status == "supported"
    assert report.candidate_evidence_spans[0].metadata["source_priority"] == "P3"
    assert report.validate() == ()


def test_no_input_mutation():
    claim = valid_claim()
    span = valid_span()
    before_claim = copy.deepcopy(claim.to_dict())
    before_span = copy.deepcopy(span.to_dict())

    classify_claim_support(claim, [span])

    assert claim.to_dict() == before_claim
    assert span.to_dict() == before_span


def test_claim_verification_report_serialization_compatibility():
    report = classify_claim_support(valid_claim(), [valid_span()])
    payload = report.to_dict()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    restored = claim_verification_report_from_dict(json.loads(encoded))

    assert restored.validate() == ()
    assert restored.to_dict() == payload


def test_classify_answer_claim_support_preserves_deterministic_order():
    claims = [
        valid_claim(claim_id="C1", citation_keys=("[E1]",)),
        valid_claim(claim_id="C2", claim_text="The source registry preserves source priority [E2].", citation_keys=("[E2]",)),
    ]
    evidence_by_claim_id = {
        "C2": [valid_span(span_id="E2", source_id="SRC-2", evidence_text_hash_or_excerpt="The source registry preserves source priority.")],
        "C1": [valid_span(span_id="E1")],
    }

    first = classify_answer_claim_support(claims, evidence_by_claim_id)
    second = classify_answer_claim_support(claims, evidence_by_claim_id)

    assert [report.claim.claim_id for report in first] == ["C1", "C2"]
    assert [report.to_dict() for report in first] == [report.to_dict() for report in second]


def test_smoke_path_with_extractor_matcher_output():
    claims = extract_atomic_claims("The answer contract includes citation keys [E1].", answer_id="A77")
    resolution = resolve_claim_citations(claims[0], [valid_span(span_id="E1")])

    report = classify_claim_support(
        claims[0],
        [match.evidence_span for match in resolution.matched_spans],
    )

    assert report.claim.claim_id == "A77-C1"
    assert report.support_status == "supported"
    assert report.validate() == ()
