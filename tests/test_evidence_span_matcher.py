from __future__ import annotations

from asperitas_agent.claim_extractor import extract_atomic_claims
from asperitas_agent.claim_verifier_schema import AtomicClaim, EvidenceSpan
from asperitas_agent.evidence_span_matcher import (
    ClaimCitationResolution,
    EvidenceSpanMatcherConfig,
    build_evidence_span_index,
    normalize_citation_key,
    resolve_answer_claim_citations,
    resolve_claim_citations,
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
        "metadata": {"fixture": "matcher"},
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


def test_normalize_citation_key_handles_brackets_case_and_whitespace():
    assert normalize_citation_key("[E1]") == "E1"
    assert normalize_citation_key(" E1 ") == "E1"
    assert normalize_citation_key("[ e1 ]") == "E1"


def test_direct_citation_key_to_span_id_match():
    resolution = resolve_claim_citations(valid_claim(citation_keys=("[E1]",)), [valid_span(span_id="E1")])

    assert isinstance(resolution, ClaimCitationResolution)
    assert resolution.blocking is False
    assert resolution.unresolved_keys == ()
    assert resolution.ambiguous_keys == ()
    assert resolution.diagnostics == ("resolved",)
    assert len(resolution.matched_spans) == 1
    assert resolution.matched_spans[0].span_id == "E1"
    assert resolution.matched_spans[0].match_fields == ("span_id",)


def test_metadata_label_match_accepts_evidence_span_objects():
    span = valid_span(span_id="S2", metadata={"citation_label": "[S2]"})

    resolution = resolve_claim_citations(valid_claim(citation_keys=("[s2]",)), [span])

    assert resolution.blocking is False
    assert resolution.matched_spans[0].span_id == "S2"
    assert resolution.matched_spans[0].match_fields == ("span_id", "metadata:citation_label")


def test_dict_records_are_accepted_and_normalized():
    record = {
        "source_id": "SRC-2",
        "chunk_id": "chunk-7",
        "citation_key": "[E7]",
        "text_excerpt": "Evidence records may carry citation labels.",
        "citation_label": "[E7]",
    }

    resolution = resolve_claim_citations(valid_claim(citation_keys=("[e7]",)), [record])

    assert resolution.blocking is False
    assert resolution.matched_spans[0].span_id == "chunk-7"
    assert "citation_key" in resolution.matched_spans[0].match_fields
    assert resolution.matched_spans[0].evidence_span.evidence_text_hash_or_excerpt == "Evidence records may carry citation labels."


def test_multiple_keys_preserve_claim_order_before_evidence_order():
    claim = valid_claim(citation_keys=("[E2]", "[E1]"))
    spans = [valid_span(span_id="E1", source_id="SRC-1"), valid_span(span_id="E2", source_id="SRC-2")]

    resolution = resolve_claim_citations(claim, spans)

    assert [match.span_id for match in resolution.matched_spans] == ["E2", "E1"]
    assert [match.rank for match in resolution.matched_spans] == [2, 1]
    assert resolution.blocking is False


def test_unresolved_key_is_reported_without_support_classification():
    claim = valid_claim(citation_keys=("[E9]",), support_status="not_verifiable_from_context")

    resolution = resolve_claim_citations(claim, [valid_span(span_id="E1")])

    assert resolution.blocking is True
    assert resolution.unresolved_keys == ("[E9]",)
    assert resolution.diagnostics == ("unresolved",)
    assert claim.support_status == "not_verifiable_from_context"
    assert claim.confidence is None


def test_duplicate_matches_are_ambiguous_and_explicit():
    claim = valid_claim(citation_keys=("[E1]",))
    spans = [valid_span(span_id="S1", citation_key="[E1]"), valid_span(span_id="S2", source_id="SRC-2", citation_key="[E1]")]

    resolution = resolve_claim_citations(claim, spans)

    assert resolution.blocking is True
    assert resolution.ambiguous_keys == ("[E1]",)
    assert resolution.unresolved_keys == ()
    assert resolution.diagnostics == ("ambiguous", "duplicate_key")
    assert [match.span_id for match in resolution.matched_spans] == ["S1", "S2"]
    assert all("citation_key" in match.match_fields for match in resolution.matched_spans)


def test_malformed_key_and_missing_keys_have_diagnostics():
    malformed = resolve_claim_citations(valid_claim(citation_keys=("not a citation",)), [valid_span()])
    missing = resolve_claim_citations(valid_claim(citation_keys=()), [valid_span()])

    assert malformed.blocking is True
    assert malformed.unresolved_keys == ("not a citation",)
    assert malformed.diagnostics == ("malformed_citation_key",)
    assert missing.blocking is True
    assert missing.diagnostics == ("missing_citation_keys",)


def test_invalid_evidence_span_is_reported_without_crashing():
    invalid_span = valid_span(span_id="", evidence_text_hash_or_excerpt="")

    resolution = resolve_claim_citations(valid_claim(citation_keys=("[E1]",)), [invalid_span])

    assert resolution.blocking is True
    assert resolution.unresolved_keys == ("[E1]",)
    assert resolution.diagnostics == ("evidence_span_invalid", "unresolved")
    assert "evidence span 1 invalid" in resolution.warnings[0]


def test_config_can_disable_span_id_matching_and_limit_duplicates():
    claim = valid_claim(citation_keys=("[E1]",))
    spans = [valid_span(span_id="E1"), valid_span(span_id="S2", citation_key="[E1]")]
    config = EvidenceSpanMatcherConfig(allow_span_id_match=False, max_matches_per_key=1)

    resolution = resolve_claim_citations(claim, spans, config=config)

    assert resolution.blocking is False
    assert [match.span_id for match in resolution.matched_spans] == ["S2"]
    assert resolution.diagnostics == ("resolved",)


def test_case_sensitive_config_preserves_exact_case_keys():
    claim = valid_claim(citation_keys=("[e1]",))
    span = valid_span(span_id="e1")
    config = EvidenceSpanMatcherConfig(case_sensitive=True)

    resolution = resolve_claim_citations(claim, [span], config=config)

    assert resolution.blocking is False
    assert resolution.matched_spans[0].normalized_key == "e1"


def test_resolution_serialization_is_deterministic():
    claim = valid_claim(citation_keys=("[E1]", "[E2]"))
    spans = [valid_span(span_id="E1"), valid_span(span_id="E2", source_id="SRC-2")]

    first = resolve_claim_citations(claim, spans)
    second = resolve_claim_citations(claim, spans)

    assert first.to_dict() == second.to_dict()


def test_resolve_answer_claim_citations_reuses_stable_index_behavior():
    claims = [
        valid_claim(claim_id="C1", citation_keys=("[E1]",)),
        valid_claim(claim_id="C2", citation_keys=("[E2]",)),
    ]
    spans = [valid_span(span_id="E1"), valid_span(span_id="E2", source_id="SRC-2")]

    resolutions = resolve_answer_claim_citations(claims, spans)

    assert [resolution.claim_id for resolution in resolutions] == ["C1", "C2"]
    assert [resolution.matched_spans[0].span_id for resolution in resolutions] == ["E1", "E2"]


def test_build_evidence_span_index_preserves_valid_entries_and_invalid_warnings():
    index = build_evidence_span_index([valid_span(span_id="E1"), {"source_id": "", "text_excerpt": ""}])

    assert len(index.entries) == 1
    assert index.entries[0].evidence_span.span_id == "E1"
    assert len(index.invalid_spans) == 1


def test_integration_with_extracted_claim_output():
    claims = extract_atomic_claims("The answer contract includes citation keys [E1].", answer_id="A77")

    resolution = resolve_claim_citations(claims[0], [valid_span(span_id="E1")])

    assert claims[0].citation_keys == ("[E1]",)
    assert resolution.claim_id == "A77-C1"
    assert resolution.blocking is False
    assert resolution.matched_spans[0].span_id == "E1"
