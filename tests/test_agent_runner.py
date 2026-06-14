from __future__ import annotations

import pytest

from asperitas_agent.agent_runner import ask_agent
from asperitas_agent.schemas import Chunk, SourceRecord


def record(source_id: str) -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        title=f"Asperitas Source {source_id}",
        original_filename=f"{source_id}.md",
        path=f"01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/{source_id}.md",
        source_priority="P1",
        source_type="internal",
        disclosure_level="internal",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-14",
        author_or_owner="Asperitas",
        use_case="agent_testing",
        checksum="a" * 64,
        parse_status="parsed",
    )


def chunk(source: SourceRecord, index: int) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::chunk-{index:04d}",
        source_id=source.source_id,
        title=source.title,
        text="Asperitas is described through source-grounded evidence and deterministic agent testing.",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=88,
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
        section="Overview",
        section_heading="Overview",
        section_path=["Overview"],
        section_level=1,
    )


def sample_inputs() -> tuple[list[SourceRecord], list[Chunk]]:
    records = [record("ASP-P1-ONE"), record("ASP-P1-TWO")]
    chunks = [chunk(records[0], 1), chunk(records[1], 2)]
    return records, chunks


def test_ask_agent_returns_valid_agent_response_structure():
    records, chunks = sample_inputs()

    response = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()

    assert response["query"] == "What is Asperitas?"
    assert response["top_k"] == 2
    assert response["status"] in {"answered", "caution", "abstained"}
    assert response["answer"]
    assert response["evidence_count"] == 2
    assert response["evidence"]
    assert response["guardrail"]["decision"] in {"proceed", "caution", "abstain"}
    assert response["metadata"]["runner_version"] == "MVP-008"


def test_citations_used_are_subset_of_evidence_keys():
    records, chunks = sample_inputs()
    response = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    evidence_keys = {item["citation_key"] for item in response["evidence"]}

    assert set(response["citations_used"]) <= evidence_keys
    assert response["metadata"]["citation_integrity"]["citations_subset_of_evidence"]


def test_ask_agent_output_is_deterministic_for_same_inputs():
    records, chunks = sample_inputs()

    first = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    second = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()

    assert first == second


def test_abstention_path_does_not_produce_unsupported_answer():
    response = ask_agent("No evidence query", top_k=5, records=[], chunks=[]).to_json()

    assert response["status"] == "abstained"
    assert response["evidence_count"] == 0
    assert response["citations_used"] == []
    assert "cannot answer" in response["answer"]
    assert response["guardrail"]["should_abstain"]


def test_invalid_empty_query_fails_cleanly():
    with pytest.raises(ValueError, match="query must not be empty"):
        ask_agent("   ", top_k=5, records=[], chunks=[])


def test_invalid_top_k_fails_cleanly():
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        ask_agent("What is Asperitas?", top_k=0, records=[], chunks=[])
