from __future__ import annotations

import json

from asperitas_agent.claim_extractor import (
    EXTRACTOR_NAME,
    UNVERIFIED_FAILURE_MODE,
    UNVERIFIED_SUPPORT_STATUS,
    extract_atomic_claims,
)
from asperitas_agent.claim_verifier_schema import atomic_claim_from_dict


def claim_texts(answer_text: str) -> list[str]:
    return [claim.claim_text for claim in extract_atomic_claims(answer_text)]


def test_simple_factual_sentence_extraction_returns_valid_atomic_claim():
    claims = extract_atomic_claims("The source registry preserves source IDs.", answer_id="A1")

    assert len(claims) == 1
    claim = claims[0]
    assert claim.claim_id == "A1-C1"
    assert claim.answer_id == "A1"
    assert claim.claim_text == "The source registry preserves source IDs."
    assert claim.claim_type == "sourced_fact"
    assert claim.support_status == UNVERIFIED_SUPPORT_STATUS
    assert claim.failure_mode == UNVERIFIED_FAILURE_MODE
    assert claim.cited_source_ids == ()
    assert claim.cited_span_ids == ()
    assert claim.metadata["extractor_name"] == EXTRACTOR_NAME
    assert claim.validate() == ()


def test_paragraph_with_multiple_sentences_extracts_stable_claims():
    text = "The answer contract includes citation keys. It preserves evidence labels [E1]."

    claims = extract_atomic_claims(text, answer_id="ANS-9")

    assert [claim.claim_id for claim in claims] == ["ANS-9-C1", "ANS-9-C2"]
    assert [claim.claim_text for claim in claims] == [
        "The answer contract includes citation keys.",
        "It preserves evidence labels [E1].",
    ]
    assert claims[1].citation_keys == ("[E1]",)


def test_bullet_list_extraction_keeps_clear_factual_claims():
    text = """
    - Source metadata includes source priority.
    - Evidence labels are preserved in answer records.
    - [E2]
    """

    assert claim_texts(text) == [
        "Source metadata includes source priority.",
        "Evidence labels are preserved in answer records.",
    ]


def test_numbered_list_extraction_keeps_clear_factual_claims():
    text = """
    1. Atomic claims are candidates for later verification.
    2. Evidence spans have stable span IDs.
    """

    assert claim_texts(text) == [
        "Atomic claims are candidates for later verification.",
        "Evidence spans have stable span IDs.",
    ]


def test_non_claim_headers_greetings_and_filler_are_filtered():
    text = """
    Hello
    Summary:
    Here are the key points:
    Key evidence:
    - The schema includes AtomicClaim contracts.
    Thanks.
    [E1]
    """

    assert claim_texts(text) == ["The schema includes AtomicClaim contracts."]


def test_empty_and_filler_only_answer_returns_no_claims():
    assert extract_atomic_claims("") == []
    assert extract_atomic_claims("Here are the key points:\nSummary:\n[E1]\nThanks.") == []


def test_claim_id_stability_is_deterministic():
    text = "The schema includes AtomicClaim. The report includes warnings."

    first = extract_atomic_claims(text, answer_id="answer 42")
    second = extract_atomic_claims(text, answer_id="answer 42")

    assert [claim.claim_id for claim in first] == [claim.claim_id for claim in second]
    assert [claim.claim_id for claim in first] == ["answer-42-C1", "answer-42-C2"]
    assert [claim.to_dict() for claim in first] == [claim.to_dict() for claim in second]


def test_semicolon_and_simple_list_like_claims_split_conservatively():
    semicolon_text = "The registry preserves source IDs; the answer contract includes citation keys."
    list_text = "The registry preserves source IDs and the answer contract includes citation keys."

    assert claim_texts(semicolon_text) == [
        "The registry preserves source IDs.",
        "the answer contract includes citation keys.",
    ]
    assert claim_texts(list_text) == [
        "The registry preserves source IDs.",
        "the answer contract includes citation keys.",
    ]


def test_biology_specific_factual_sentence_is_preserved():
    text = "Arabidopsis thaliana expresses FLC, and the FLC protein regulates flowering time."

    claims = extract_atomic_claims(text)

    assert len(claims) == 1
    assert claims[0].claim_text == text
    assert claims[0].claim_type == "biology_relation"


def test_sentence_splitter_avoids_decimals_citations_and_common_abbreviations():
    text = "E. coli grows at 37.0 C [E3]. The assay includes two replicates."

    assert claim_texts(text) == [
        "E. coli grows at 37.0 C [E3].",
        "The assay includes two replicates.",
    ]


def test_atomic_claim_serialization_round_trip_compatibility():
    claim = extract_atomic_claims("The verifier schema includes failure modes.", answer_id="A2")[0]
    payload = claim.to_dict()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    restored = atomic_claim_from_dict(json.loads(encoded))

    assert restored.validate() == ()
    assert restored.to_dict() == payload
