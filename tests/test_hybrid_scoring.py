import pytest

from asperitas_agent.hybrid_scoring import (
    DEFAULT_HYBRID_SCORE_WEIGHTS,
    HYBRID_SOURCE_GROUNDING_FIELDS,
    HybridScoreInputs,
    HybridScoreWeights,
    combine_hybrid_score,
    normalize_cosine_similarity,
    score_metadata_preservation,
)


def complete_payload():
    return {
        "source_id": "ASP-P1-001",
        "source_file": "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/source.md",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": "Strategy",
        "section_heading": "Strategy",
        "section_path": ["Company", "Strategy"],
        "heading_context": "Company > Strategy",
        "embedding_model": "offline-lexical-semantic-hash",
        "embedding_dim": 1024,
        "embedding_version": "mvp005-phase5-lexical-semantic",
        "content_hash": "a" * 64,
    }


def test_default_weights_keep_mvp003_as_reference_signal():
    weights = DEFAULT_HYBRID_SCORE_WEIGHTS.normalized()

    assert weights.mvp003 == pytest.approx(0.70)
    assert weights.vector == pytest.approx(0.20)
    assert weights.section == pytest.approx(0.05)
    assert weights.metadata == pytest.approx(0.05)
    assert weights.mvp003 > weights.vector


def test_weights_reject_negative_or_zero_total_values():
    with pytest.raises(ValueError, match="non-negative"):
        HybridScoreWeights(mvp003=-1.0)

    with pytest.raises(ValueError, match="positive total"):
        HybridScoreWeights(mvp003=0.0, vector=0.0, section=0.0, metadata=0.0)


def test_combine_hybrid_score_uses_weighted_normalized_components():
    result = combine_hybrid_score(
        HybridScoreInputs(
            mvp003_score=1.0,
            vector_score=0.5,
            section_score=1.0,
            metadata_score=1.0,
        )
    )

    assert result.components["mvp003"] == pytest.approx(0.70)
    assert result.components["vector"] == pytest.approx(0.10)
    assert result.components["section"] == pytest.approx(0.05)
    assert result.components["metadata"] == pytest.approx(0.05)
    assert result.hybrid_score == pytest.approx(0.90)


def test_combine_hybrid_score_clamps_inputs_to_unit_interval():
    result = combine_hybrid_score(
        HybridScoreInputs(
            mvp003_score=2.0,
            vector_score=-3.0,
            section_score=0.5,
            metadata_score=10.0,
        )
    )

    assert result.components["mvp003"] == pytest.approx(0.70)
    assert result.components["vector"] == pytest.approx(0.0)
    assert result.components["section"] == pytest.approx(0.025)
    assert result.components["metadata"] == pytest.approx(0.05)
    assert result.hybrid_score == pytest.approx(0.775)


def test_normalize_cosine_similarity_maps_to_unit_interval():
    assert normalize_cosine_similarity(-1.0) == 0.0
    assert normalize_cosine_similarity(0.0) == 0.5
    assert normalize_cosine_similarity(1.0) == 1.0
    assert normalize_cosine_similarity(3.0) == 1.0


def test_metadata_preservation_score_requires_all_source_grounding_fields():
    payload = complete_payload()

    assert tuple(payload) == HYBRID_SOURCE_GROUNDING_FIELDS
    assert score_metadata_preservation(payload) == 1.0


def test_metadata_preservation_score_penalizes_missing_fields():
    payload = complete_payload()
    payload["embedding_version"] = ""
    payload["section_path"] = []

    assert score_metadata_preservation(payload) == pytest.approx(10 / 12)

