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


def test_p6_benchmark_does_not_outrank_internal_fact_source():
    internal = chunk("synthetic biology based drug development status and outlook")
    benchmark = Chunk(
        **{
            **chunk("synthetic biology based drug development status and outlook " * 20).to_json(),
            "chunk_id": "c2",
            "source_id": "ASP-P6-BENCHMARK",
            "title": "AI Bio-AI Benchmark",
            "source_priority": "P6",
            "source_type": "benchmark_operating_intelligence",
            "evidence_label": "Inference",
        }
    )

    results = search_chunks(
        "Which document covers synthetic biology based drug development status and outlook?",
        [benchmark, internal],
        limit=2,
    )

    assert results[0].chunk.source_priority == "P0"


def test_p6_benchmark_allowed_for_benchmark_workflow_queries():
    internal = chunk("synthetic biology based drug development status and outlook")
    benchmark = Chunk(
        **{
            **chunk("benchmark workflow process comparison for AI Bio-AI development patterns").to_json(),
            "chunk_id": "c2",
            "source_id": "ASP-P6-BENCHMARK",
            "title": "AI Bio-AI Benchmark",
            "source_priority": "P6",
            "source_type": "benchmark_operating_intelligence",
            "evidence_label": "Inference",
        }
    )

    results = search_chunks("benchmark workflow process comparison", [internal, benchmark], limit=2)

    assert results[0].chunk.source_priority == "P6"


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
