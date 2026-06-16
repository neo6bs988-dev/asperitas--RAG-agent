import pytest

from asperitas_agent.reranking import (
    DeterministicTestReranker,
    RERANK_SOURCE_GROUNDING_FIELDS,
    assert_rerank_metadata_preserved,
    rerank_candidates,
)


def complete_candidate(
    chunk_id: str = "chunk-001",
    rank: int = 1,
    text: str = "source priority policy",
    section: str = "Source Priority Policy",
):
    return {
        "rank": rank,
        "chunk_id": chunk_id,
        "source_id": "ASP-P0-RERANK",
        "source_file": "01_RAW_SOURCES/P0_ACTIVE_PROMPT/AGENTS.md",
        "source_priority": "P0",
        "evidence_label": "Document-Supported Fact",
        "section": section,
        "section_heading": section,
        "section_path": ["Governance", section],
        "heading_context": f"Governance > {section}",
        "embedding_model": "offline-lexical-semantic-hash",
        "embedding_dim": 1024,
        "embedding_version": "mvp005-phase5-lexical-semantic",
        "content_hash": "a" * 64,
        "score": 0.42,
        "score_components": {"mvp003_score": 0.4, "vector_score": 0.5},
        "title": "AGENTS",
        "text": text,
    }


def test_disabled_reranker_returns_deep_copied_original_order():
    candidates = [
        complete_candidate(chunk_id="chunk-a", rank=1, text="unrelated body"),
        complete_candidate(chunk_id="chunk-b", rank=2, text="source priority policy body"),
    ]

    rows = rerank_candidates("source priority policy", candidates)

    assert [row["chunk_id"] for row in rows] == ["chunk-a", "chunk-b"]
    assert rows == candidates
    assert rows is not candidates
    rows[0]["section_path"].append("mutated copy")
    assert candidates[0]["section_path"] == ["Governance", "Source Priority Policy"]


def test_deterministic_test_reranker_reorders_by_query_overlap_and_preserves_rank():
    candidates = [
        complete_candidate(chunk_id="weak", rank=1, text="unrelated body", section="General Governance"),
        complete_candidate(chunk_id="strong", rank=2, text="source priority policy evidence hierarchy"),
    ]
    reranker = DeterministicTestReranker()

    rows = rerank_candidates("source priority policy", candidates, reranker=reranker)

    assert [row["chunk_id"] for row in rows] == ["strong", "weak"]
    assert rows[0]["rank"] == 2
    assert rows[0]["score"] == candidates[1]["score"]
    assert rows[0]["score_components"] == candidates[1]["score_components"]
    assert rows[0]["reranker_metadata"]["input_rank"] == 2
    assert rows[0]["reranker_metadata"]["reranked_rank"] == 1
    assert rows[0]["reranker_metadata"]["reranker_name"] == "deterministic-test-reranker"
    assert rows[0]["reranker_metadata"]["deterministic"] is True
    assert rows[0]["reranker_metadata"]["reranker_score"] > rows[1]["reranker_metadata"]["reranker_score"]


def test_deterministic_test_reranker_supports_top_k_without_mutating_input():
    candidates = [
        complete_candidate(chunk_id="weak", rank=1, text="unrelated body", section="General Governance"),
        complete_candidate(chunk_id="strong", rank=2, text="source priority policy"),
    ]
    reranker = DeterministicTestReranker()

    rows = rerank_candidates("source priority policy", candidates, reranker=reranker, top_k=1)

    assert [row["chunk_id"] for row in rows] == ["strong"]
    assert "reranker_metadata" not in candidates[0]
    assert "reranker_metadata" not in candidates[1]


def test_deterministic_test_reranker_preserves_required_metadata_fields():
    candidates = [
        complete_candidate(chunk_id="weak", rank=1, text="unrelated body", section="General Governance"),
        complete_candidate(chunk_id="strong", rank=2, text="source priority policy"),
    ]
    reranker = DeterministicTestReranker()

    rows = rerank_candidates("source priority policy", candidates, reranker=reranker)
    original_by_chunk = {row["chunk_id"]: row for row in candidates}

    for row in rows:
        original = original_by_chunk[row["chunk_id"]]
        for field_name in RERANK_SOURCE_GROUNDING_FIELDS:
            assert row[field_name] == original[field_name]


def test_metadata_preservation_check_rejects_mutated_source_fields():
    original = [complete_candidate(chunk_id="chunk-a")]
    mutated = [complete_candidate(chunk_id="chunk-a")]
    mutated[0]["source_priority"] = "P5"

    with pytest.raises(ValueError, match="source_priority"):
        assert_rerank_metadata_preserved(original, mutated)


def test_metadata_preservation_check_rejects_unknown_candidates():
    original = [complete_candidate(chunk_id="chunk-a")]
    unknown = [complete_candidate(chunk_id="chunk-b")]

    with pytest.raises(ValueError, match="unknown candidate"):
        assert_rerank_metadata_preserved(original, unknown)


def test_reranker_rejects_negative_top_k():
    with pytest.raises(ValueError, match="top_k"):
        rerank_candidates("source priority policy", [], top_k=-1)

    with pytest.raises(ValueError, match="top_k"):
        DeterministicTestReranker().rerank("source priority policy", [], top_k=-1)
