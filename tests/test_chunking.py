from asperitas_agent.chunking import chunk_document, detect_section_heading, extract_section_markers, normalize_section_text
from asperitas_agent.schemas import LoadedDocument, SourceRecord


def make_source() -> SourceRecord:
    return SourceRecord(
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


def test_chunks_preserve_source_metadata():
    source = make_source()
    document = LoadedDocument(source=source, text="AOS source hierarchy. " * 100, parser_used="plain_text", parse_status="parsed")

    chunks = chunk_document(document, chunk_size=200, overlap=50)

    assert chunks
    assert all(chunk.source_id == source.source_id for chunk in chunks)
    assert all(chunk.source_priority == "P1" for chunk in chunks)
    assert all(chunk.disclosure_level == "confidential" for chunk in chunks)
    assert all(chunk.verification_status == "unverified" for chunk in chunks)
    assert all(hasattr(chunk, "section") for chunk in chunks)


def test_chunking_rejects_invalid_parameters():
    source = make_source()
    document = LoadedDocument(source=source, text="AOS source hierarchy.", parser_used="plain_text", parse_status="parsed")

    for chunk_size, overlap in ((0, 0), (100, -1), (100, 100)):
        try:
            chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid chunk parameters should raise ValueError")


def test_markdown_heading_detection_and_section_path_propagation():
    source = make_source()
    text = "# Source Priority Policy\nP0 evidence.\n## Evidence Hierarchy\nDocument facts.\n" + ("More evidence. " * 40)
    document = LoadedDocument(source=source, text=text, parser_used="markdown", parse_status="parsed")

    chunks = chunk_document(document, chunk_size=120, overlap=0)

    assert chunks[0].section == "Source Priority Policy"
    assert chunks[0].section_path == ["Source Priority Policy"]
    assert any(chunk.heading_context == "Source Priority Policy > Evidence Hierarchy" for chunk in chunks)
    assert any(chunk.parent_section == "Source Priority Policy" for chunk in chunks)


def test_numbered_heading_detection_tracks_level():
    markers = extract_section_markers("1. Strategy\nText\n1.1 Market Entry\nMore\n1.1.1 Korea\n")

    assert [marker.heading for marker in markers] == ["Strategy", "Market Entry", "Korea"]
    assert markers[1].path == ("Strategy", "Market Entry")
    assert markers[2].level == 3


def test_korean_heading_detection():
    detected = detect_section_heading("개요")

    assert detected == ("개요", 1)


def test_section_normalization_ignores_case_punctuation_and_numbering():
    assert normalize_section_text("1.1 Source-Priority Policy") == normalize_section_text("source priority policy")
