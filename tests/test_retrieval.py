from asperitas_agent.retrieval_tfidf import search_chunks
from asperitas_agent.schemas import Chunk


def chunk(text="AOS source hierarchy") -> Chunk:
    return Chunk(
        chunk_id="c1",
        source_id="ASP-P0-1",
        title="AOS",
        text=text,
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=len(text),
        source_priority="P0",
        source_type="prompt",
        disclosure_level="confidential",
        evidence_label="Document-Supported Fact",
        verification_status="verified_internal",
        risk_tags=[],
        checksum="abc",
    )


def test_search_returns_chunks_with_source_metadata():
    results = search_chunks("source hierarchy", [chunk()], limit=1)

    assert results
    assert results[0].chunk.source_id == "ASP-P0-1"
    assert results[0].score > 0


def test_empty_index_fails_gracefully():
    assert search_chunks("anything", []) == []


def test_non_positive_limit_returns_no_results():
    assert search_chunks("source hierarchy", [chunk()], limit=0) == []
    assert search_chunks("source hierarchy", [chunk()], limit=-1) == []
