from asperitas_agent.chunking import chunk_document
from asperitas_agent.schemas import LoadedDocument, SourceRecord


def test_chunks_preserve_source_metadata():
    source = SourceRecord(
        source_id="ASP-P1-ABC",
        title="Internal",
        original_filename="internal.md",
        path="01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/internal.md",
        source_priority="P1",
        source_type="internal",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="unverified",
        date="2026-06-12",
        author_or_owner="unknown",
        use_case="strategy",
        checksum="abc",
        parse_status="parsed",
    )
    document = LoadedDocument(source=source, text="AOS source hierarchy. " * 100, parser_used="plain_text", parse_status="parsed")

    chunks = chunk_document(document, chunk_size=200, overlap=50)

    assert chunks
    assert all(chunk.source_id == source.source_id for chunk in chunks)
    assert all(chunk.source_priority == "P1" for chunk in chunks)
    assert all(chunk.disclosure_level == "confidential" for chunk in chunks)
    assert all(chunk.verification_status == "unverified" for chunk in chunks)


def test_chunking_rejects_invalid_parameters():
    source = SourceRecord(
        source_id="ASP-P1-ABC",
        title="Internal",
        original_filename="internal.md",
        path="01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/internal.md",
        source_priority="P1",
        source_type="internal",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="unverified",
        date="2026-06-12",
        author_or_owner="unknown",
        use_case="strategy",
        checksum="abc",
        parse_status="parsed",
    )
    document = LoadedDocument(source=source, text="AOS source hierarchy.", parser_used="plain_text", parse_status="parsed")

    for chunk_size, overlap in ((0, 0), (100, -1), (100, 100)):
        try:
            chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid chunk parameters should raise ValueError")
