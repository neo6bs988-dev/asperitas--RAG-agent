import pytest

from asperitas_agent.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_VERSION,
    DEFAULT_LEXICAL_SEMANTIC_EMBEDDING_MODEL,
    DEFAULT_LEXICAL_SEMANTIC_EMBEDDING_VERSION,
    DeterministicOfflineEmbeddingProvider,
    InMemoryVectorStore,
    LexicalSemanticOfflineEmbeddingProvider,
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


def test_lexical_semantic_provider_returns_same_vector_for_same_text():
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=32)

    assert provider.embed_text("source priority policy") == provider.embed_text("source priority policy")


def test_lexical_semantic_provider_vector_length_matches_embedding_dim():
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=17)

    vector = provider.embed_text("source-grounded biological intelligence")

    assert len(vector) == 17
    assert all(-1.0 <= value <= 1.0 for value in vector)


def test_lexical_semantic_provider_rejects_invalid_embedding_dim():
    with pytest.raises(ValueError, match="embedding_dim must be positive"):
        LexicalSemanticOfflineEmbeddingProvider(embedding_dim=0)

    with pytest.raises(ValueError, match="embedding_dim must be positive"):
        LexicalSemanticOfflineEmbeddingProvider(embedding_dim=-1)


def test_lexical_semantic_provider_fallback_is_deterministic_for_featureless_text():
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=9)

    first = provider.embed_text("!!!")
    second = provider.embed_text("!!!")

    assert first == second
    assert len(first) == 9
    assert any(value != 0.0 for value in first)


def test_lexical_semantic_provider_requires_no_external_api_dependency():
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=8)

    assert provider.embedding_model == DEFAULT_LEXICAL_SEMANTIC_EMBEDDING_MODEL
    assert provider.embedding_version == DEFAULT_LEXICAL_SEMANTIC_EMBEDDING_VERSION
    assert provider.embed_text("offline local lexical semantic provider")


def test_lexical_semantic_provider_metadata_is_compatible_with_embedding_record_schema():
    source = make_source()
    chunk = make_chunk(source)
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=16)

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


def test_lexical_semantic_provider_ranks_shared_features_above_unrelated_text():
    source = make_source()
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=64)
    store = InMemoryVectorStore(embedding_dim=provider.embedding_dim)
    matching_chunk = make_chunk(source)
    unrelated_chunk = Chunk(
        **{
            **matching_chunk.to_json(),
            "chunk_id": f"{matching_chunk.chunk_id}-unrelated",
            "text": "Protein folding assays describe enzyme structure and catalytic mechanisms.",
            "section": "Protein Methods",
            "section_heading": "Protein Methods",
            "section_path": ["Biological Intelligence", "Protein Methods"],
            "heading_context": "Biological Intelligence > Protein Methods",
        }
    )
    for chunk in (unrelated_chunk, matching_chunk):
        record = build_embedding_record(
            chunk,
            source_file=source.path,
            embedding_model=provider.embedding_model,
            embedding_dim=provider.embedding_dim,
            embedding_version=provider.embedding_version,
        )
        store.add(record, provider.embed_text(f"{chunk.title} {chunk.heading_context} {chunk.text}"))

    result = store.search(provider.embed_text("source priority policy"), top_k=1)[0]

    assert result.record.chunk_id == matching_chunk.chunk_id


def make_vector_record(
    suffix: str,
    vector: list[float],
    source: SourceRecord | None = None,
    chunk: Chunk | None = None,
):
    source = source or make_source()
    chunk = chunk or make_chunk(source)
    chunk = Chunk(**{**chunk.to_json(), "chunk_id": f"{chunk.chunk_id}-{suffix}"})
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=len(vector))
    return build_embedding_record(
        chunk,
        source_file=source.path,
        embedding_model=provider.embedding_model,
        embedding_dim=provider.embedding_dim,
        embedding_version=provider.embedding_version,
    )


def test_in_memory_vector_store_adds_records():
    store = InMemoryVectorStore(embedding_dim=3)
    record = make_vector_record("one", [1.0, 0.0, 0.0])

    store.add(record, [1.0, 0.0, 0.0])

    assert len(store) == 1


def test_in_memory_vector_store_empty_search_returns_no_results():
    store = InMemoryVectorStore(embedding_dim=3)

    assert store.search([1.0, 0.0, 0.0]) == []


def test_in_memory_vector_store_search_returns_ranked_results():
    store = InMemoryVectorStore(embedding_dim=2)
    best = make_vector_record("best", [1.0, 0.0])
    middle = make_vector_record("middle", [0.5, 0.5])
    worst = make_vector_record("worst", [0.0, 1.0])

    store.add(worst, [0.0, 1.0])
    store.add(middle, [0.5, 0.5])
    store.add(best, [1.0, 0.0])

    results = store.search([1.0, 0.0], top_k=3)

    assert [result.record.chunk_id for result in results] == [best.chunk_id, middle.chunk_id, worst.chunk_id]
    assert results[0].score > results[1].score > results[2].score


def test_in_memory_vector_store_search_results_preserve_metadata():
    source = make_source()
    chunk = make_chunk(source)
    store = InMemoryVectorStore(embedding_dim=3)
    record = make_vector_record("metadata", [1.0, 0.0, 0.0], source=source, chunk=chunk)

    store.add(record, [1.0, 0.0, 0.0])
    result = store.search([1.0, 0.0, 0.0], top_k=1)[0]
    payload = result.to_json()

    assert payload["source_id"] == chunk.source_id
    assert payload["source_file"] == source.path
    assert payload["source_priority"] == chunk.source_priority
    assert payload["evidence_label"] == chunk.evidence_label
    assert payload["section"] == chunk.section
    assert payload["section_heading"] == chunk.section_heading
    assert payload["section_path"] == chunk.section_path
    assert payload["heading_context"] == chunk.heading_context
    assert payload["embedding_model"] == record.embedding_model
    assert payload["embedding_dim"] == record.embedding_dim
    assert payload["embedding_version"] == record.embedding_version
    assert payload["content_hash"] == record.content_hash
    assert payload["score"] == 1.0


def test_in_memory_vector_store_rejects_dimension_mismatch():
    store = InMemoryVectorStore(embedding_dim=3)
    record = make_vector_record("mismatch", [1.0, 0.0, 0.0])
    wrong_record = build_embedding_record(
        make_chunk(make_source()),
        source_file=make_source().path,
        embedding_model="offline-deterministic-hash",
        embedding_dim=2,
        embedding_version="mvp005-phase2-offline",
    )

    with pytest.raises(ValueError, match="vector dimension does not match"):
        store.add(record, [1.0, 0.0])

    with pytest.raises(ValueError, match="record embedding_dim does not match"):
        store.add(wrong_record, [1.0, 0.0, 0.0])

    with pytest.raises(ValueError, match="query_vector dimension does not match"):
        store.search([1.0, 0.0])

    with pytest.raises(ValueError, match="embedding_dim must be positive"):
        InMemoryVectorStore(embedding_dim=0)


def test_in_memory_vector_store_top_k_behavior_is_stable():
    store = InMemoryVectorStore(embedding_dim=2)
    first = make_vector_record("first", [1.0, 0.0])
    second = make_vector_record("second", [1.0, 0.0])
    third = make_vector_record("third", [1.0, 0.0])

    store.add(first, [1.0, 0.0])
    store.add(second, [1.0, 0.0])
    store.add(third, [1.0, 0.0])

    assert store.search([1.0, 0.0], top_k=0) == []
    assert [result.record.chunk_id for result in store.search([1.0, 0.0], top_k=2)] == [first.chunk_id, second.chunk_id]
    assert [result.record.chunk_id for result in store.search([1.0, 0.0], top_k=99)] == [first.chunk_id, second.chunk_id, third.chunk_id]


def test_embedding_record_provider_and_vector_store_are_compatible():
    source = make_source()
    chunk = make_chunk(source)
    provider = DeterministicOfflineEmbeddingProvider(embedding_dim=5)
    vector = provider.embed_text(chunk.text)
    record = build_embedding_record(
        chunk,
        source_file=source.path,
        embedding_model=provider.embedding_model,
        embedding_dim=provider.embedding_dim,
        embedding_version=provider.embedding_version,
    )
    store = InMemoryVectorStore(embedding_dim=provider.embedding_dim)

    store.add(record, vector)
    result = store.search(vector, top_k=1)[0]

    assert result.record.chunk_id == record.chunk_id
    assert result.record.source_id == record.source_id
    assert result.record.source_file == record.source_file
    assert result.record.source_priority == record.source_priority
    assert result.record.evidence_label == record.evidence_label
    assert result.record.section == record.section
    assert result.record.section_heading == record.section_heading
    assert result.record.section_path == record.section_path
    assert result.record.heading_context == record.heading_context
    assert result.record.embedding_model == provider.embedding_model
    assert result.record.embedding_dim == provider.embedding_dim
    assert result.record.embedding_version == provider.embedding_version

