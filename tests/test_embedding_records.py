import pytest

from asperitas_agent.embedding_records import EmbeddingRecord, content_hash_for_text
from asperitas_agent.schemas import Chunk


def make_chunk() -> Chunk:
    return Chunk(
        chunk_id="ASP-P1-EMBED::TEST::chunk-0001",
        source_id="ASP-P1-EMBED",
        title="Embedding Source",
        text="Stable text used for deterministic embedding record hashes.",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=58,
        source_priority="P1",
        source_type="internal",
        disclosure_level="confidential",
        evidence_label="Document-Supported Fact",
        verification_status="verified_internal",
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


def make_record(chunk: Chunk | None = None) -> EmbeddingRecord:
    return EmbeddingRecord.from_chunk(
        chunk=chunk or make_chunk(),
        source_file="01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/embedding-source.md",
        embedding_model="offline-test-embedding",
        embedding_dim=384,
        embedding_version="mvp005-phase1",
    )


def test_embedding_record_schema_contains_required_fields():
    payload = make_record().to_json()

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


def test_embedding_record_preserves_chunk_metadata():
    chunk = make_chunk()
    record = make_record(chunk)

    assert record.chunk_id == chunk.chunk_id
    assert record.source_id == chunk.source_id
    assert record.source_priority == chunk.source_priority
    assert record.evidence_label == chunk.evidence_label
    assert record.section == chunk.section
    assert record.section_heading == chunk.section_heading
    assert record.section_path == chunk.section_path
    assert record.heading_context == chunk.heading_context


def test_embedding_record_preserves_source_file_and_embedding_metadata():
    record = make_record()

    assert record.source_file == "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/embedding-source.md"
    assert record.embedding_model == "offline-test-embedding"
    assert record.embedding_dim == 384
    assert record.embedding_version == "mvp005-phase1"


def test_content_hash_is_stable_and_derived_from_chunk_text():
    chunk = make_chunk()
    first = make_record(chunk)
    second = make_record(chunk)

    assert first.content_hash == second.content_hash
    assert first.content_hash == content_hash_for_text(chunk.text)
    assert first.content_hash != chunk.checksum


def test_section_path_is_copied_not_shared():
    chunk = make_chunk()
    record = make_record(chunk)

    record.section_path.append("Mutated")

    assert chunk.section_path == ["Biological Intelligence", "Methods"]


@pytest.mark.parametrize(
    ("embedding_model", "embedding_dim", "expected_error"),
    [
        ("", 384, "embedding_model must be non-empty"),
        ("   ", 384, "embedding_model must be non-empty"),
        ("offline-test-embedding", 0, "embedding_dim must be positive"),
        ("offline-test-embedding", -1, "embedding_dim must be positive"),
    ],
)
def test_embedding_record_validation_rejects_invalid_model_or_dim(
    embedding_model: str,
    embedding_dim: int,
    expected_error: str,
):
    with pytest.raises(ValueError, match=expected_error):
        EmbeddingRecord.from_chunk(
            chunk=make_chunk(),
            source_file="01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/embedding-source.md",
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            embedding_version="mvp005-phase1",
        )

