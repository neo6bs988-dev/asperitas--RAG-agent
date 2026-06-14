import pytest

from asperitas_agent.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_VERSION,
    DeterministicOfflineEmbeddingProvider,
    build_embedding_record,
    build_embedding_records,
)
from asperitas_agent.schemas import Chunk, SourceRecord


def make_source() -> SourceRecord:
    return SourceRecord(
        source_id="ASP-P1-EMBED",
        title="Embedding Source",
        original_filename="embedding-source.md",
        path="01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/embedding-source.md",
        source_priority="P1",
        source_type="internal",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-14",
        author_or_owner="Asperitas",
        use_case="embedding_schema_test",
        checksum="a" * 64,
        parse_status="parsed",
    )


def make_chunk(source: SourceRecord) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::TEST::chunk-0001",
        source_id=source.source_id,
        title=source.title,
        text="Section-grounded source text for embedding schema tests.",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=56,
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
        section="Methods",
        section_heading="Methods",
        section_path=["Biological Intelligence", "Methods"],
        section_level=2,
        parent_section="Biological Intelligence",
        subsection="Methods",
        heading_context="Biological Intelligence > Methods",
    )


def test_embedding_record_schema_contains_required_fields_and_defaults():
    source = make_source()
    chunk = make_chunk(source)

    record = build_embedding_record(chunk, source_file=source.path)
    payload = record.to_json()

    assert set(payload) == {
        "chunk_id",
        "source_id",
        "source_file",
        "source_priority",
        "evidence_label",
        "section",
        "section_heading",
        "section_path",
        "heading_context",
        "embedding_model",
        "embedding_dim",
        "embedding_version",
        "content_hash",
    }
    assert payload["embedding_model"] == DEFAULT_EMBEDDING_MODEL
    assert payload["embedding_dim"] == 0
    assert payload["embedding_version"] == DEFAULT_EMBEDDING_VERSION


def test_embedding_record_preserves_chunk_and_registry_metadata():
    source = make_source()
    chunk = make_chunk(source)

    record = build_embedding_records([chunk], [source], embedding_model="fixture-model", embedding_dim=384, embedding_version="test-v1")[0]

    assert record.chunk_id == chunk.chunk_id
    assert record.source_id == chunk.source_id
    assert record.source_file == source.path
    assert record.source_priority == chunk.source_priority
    assert record.evidence_label == chunk.evidence_label
    assert record.section == chunk.section
    assert record.section_heading == chunk.section_heading
    assert record.section_path == chunk.section_path
    assert record.heading_context == chunk.heading_context
    assert record.content_hash == chunk.checksum
    assert record.embedding_model == "fixture-model"
    assert record.embedding_dim == 384
    assert record.embedding_version == "test-v1"


def test_embedding_record_copies_section_path_to_avoid_mutating_chunk_metadata():
    source = make_source()
    chunk = make_chunk(source)

    record = build_embedding_record(chunk, source_file=source.path)
    record.section_path.append("Mutated")

    assert chunk.section_path == ["Biological Intelligence", "Methods"]


def test_embedding_records_require_source_file_and_registry_match():
    source = make_source()
    chunk = make_chunk(source)

    with pytest.raises(ValueError, match="source_file is required"):
        build_embedding_record(chunk, source_file="")

    with pytest.raises(ValueError, match="Missing source registry records"):
        build_embedding_records([chunk], [])


def test_embedding_dim_must_not_be_negative():
    source = make_source()
    chunk = make_chunk(source)

    with pytest.raises(ValueError, match="embedding_dim must be non-negative"):
        build_embedding_record(chunk, source_file=source.path, embedding_dim=-1)


def test_offline_provider_returns_same_vector_for_same_text():
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=8)

    assert provider.embed_text("same text") == provider.embed_text("same text")


def test_offline_provider_returns_different_vectors_for_different_text():
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=8)

    assert provider.embed_text("first text") != provider.embed_text("second text")


def test_offline_provider_vector_length_matches_embedding_dim():
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=13)

    vector = provider.embed_text("dimension check")

    assert len(vector) == 13
    assert all(-1.0 <= value <= 1.0 for value in vector)


def test_offline_provider_rejects_invalid_embedding_dim():
    with pytest.raises(ValueError, match="embedding_dim must be positive"):
        DeterministicOfflineEmbeddingProvider(embedding_dim=0)

    with pytest.raises(ValueError, match="embedding_dim must be positive"):
        DeterministicOfflineEmbeddingProvider(embedding_dim=-1)


def test_offline_provider_requires_no_external_api_dependency():
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=4)

    assert provider.embedding_model == "offline-deterministic-hash"
    assert provider.embedding_version == "mvp005-phase2-offline"
    assert provider.embed_text("offline only")


def test_offline_provider_metadata_is_compatible_with_embedding_record_schema():
    source = make_source()
    chunk = make_chunk(source)
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=6)

    record = build_embedding_record(
        chunk,
        source_file=source.path,
        embedding_model=provider.embedding_model,
        embedding_dim=provider.embedding_dim,
        embedding_version=provider.embedding_version,
    )
    vector = provider.embed_text(chunk.text)

    assert len(vector) == record.embedding_dim
    assert record.source_id == chunk.source_id
    assert record.source_file == source.path
    assert record.source_priority == chunk.source_priority
    assert record.evidence_label == chunk.evidence_label
    assert record.section == chunk.section
    assert record.section_heading == chunk.section_heading
    assert record.section_path == chunk.section_path
    assert record.heading_context == chunk.heading_context
    assert record.embedding_model == provider.embedding_model
    assert record.embedding_version == provider.embedding_version

