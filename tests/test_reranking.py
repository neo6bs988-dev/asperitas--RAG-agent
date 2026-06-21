import pytest

from asperitas_agent.reranking import (
    DeterministicTestReranker,
    RERANK_SOURCE_GROUNDING_FIELDS,
    assert_rerank_metadata_preserved,
    rerank_candidates,
    rerank_candidates_fail_closed,
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

    with pytest.raises(ValueError, match="top_k"):
        rerank_candidates_fail_closed("source priority policy", [], DeterministicTestReranker(), top_k=-1)


def test_fail_closed_wrapper_returns_reranked_order_when_invariants_pass():
    candidates = [
        complete_candidate(chunk_id="weak", rank=1, text="unrelated body", section="General Governance"),
        complete_candidate(chunk_id="strong", rank=2, text="source priority policy evidence hierarchy"),
    ]

    result = rerank_candidates_fail_closed("source priority policy", candidates, DeterministicTestReranker(), top_k=2)

    assert [row["chunk_id"] for row in result.candidates] == ["strong", "weak"]
    assert result.fallback_reasons == ()


def test_fail_closed_wrapper_falls_back_on_exception():
    candidates = [complete_candidate(chunk_id="chunk-a")]

    result = rerank_candidates_fail_closed("source priority policy", candidates, RaisingReranker())

    assert [row["chunk_id"] for row in result.candidates] == ["chunk-a"]
    assert result.fallback_reasons == ("reranker_exception",)


def test_fail_closed_wrapper_returns_deterministic_fallback_diagnostics():
    candidates = source_distinct_candidates(6)

    result = rerank_candidates_fail_closed("source priority policy", candidates, Top5CoverageLossReranker(), top_k=6)

    assert result.fallback_reasons == ("top5_source_coverage_lost",)


class RaisingReranker:
    reranker_name = "raising"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        raise RuntimeError("boom")


class DroppingReranker:
    reranker_name = "dropping"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        return list(candidates)[1:]


class DuplicatingReranker:
    reranker_name = "duplicating"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        rows = [dict(row) for row in candidates]
        rows[-1] = dict(rows[0])
        return rows


class IntroducingReranker:
    reranker_name = "introducing"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        rows = [dict(row) for row in candidates]
        rows[-1] = complete_candidate(chunk_id="introduced", rank=99)
        return rows


class CountChangingReranker:
    reranker_name = "count-changing"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        return list(candidates)[:1]


class Top3SourceLossReranker:
    reranker_name = "top3-loss"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        rows = [dict(row) for row in candidates]
        return [rows[3], rows[4], rows[0], rows[1], rows[2], rows[5]]


class Top5CoverageLossReranker:
    reranker_name = "top5-loss"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        rows = [dict(row) for row in candidates]
        return [rows[0], rows[1], rows[2], rows[5], rows[3], rows[4]]


class MetadataMutatingReranker:
    reranker_name = "metadata-mutating"
    reranker_version = "test"
    deterministic = True

    def rerank(self, query, candidates, top_k=None):
        rows = [dict(row) for row in candidates]
        rows[0]["source_priority"] = "P6"
        return rows


def source_distinct_candidates(count: int):
    rows = []
    for index in range(1, count + 1):
        row = complete_candidate(
            chunk_id=f"chunk-{index}",
            rank=index,
            text=f"source priority policy {index}",
        )
        row["source_id"] = f"SRC-{index}"
        row["source_file"] = f"source-{index}.md"
        row["content_hash"] = f"{index:0<64}"[:64]
        rows.append(row)
    return rows


@pytest.mark.parametrize(
    ("reranker", "expected_reason"),
    [
        (DroppingReranker(), "candidate_dropped"),
        (DuplicatingReranker(), "candidate_duplicated"),
        (IntroducingReranker(), "candidate_introduced"),
        (CountChangingReranker(), "candidate_count_changed"),
        (Top3SourceLossReranker(), "top3_source_identity_lost"),
        (Top5CoverageLossReranker(), "top5_source_coverage_lost"),
        (MetadataMutatingReranker(), "grounding_metadata_mutated"),
    ],
)
def test_fail_closed_wrapper_falls_back_on_runtime_invariant_violations(reranker, expected_reason):
    candidates = source_distinct_candidates(6)

    result = rerank_candidates_fail_closed("source priority policy", candidates, reranker, top_k=6)

    assert [row["chunk_id"] for row in result.candidates] == [row["chunk_id"] for row in candidates]
    assert expected_reason in result.fallback_reasons
