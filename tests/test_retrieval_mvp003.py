from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003
from asperitas_agent.schemas import Chunk, SourceRecord


def make_source(source_id: str, title: str, filename: str, path: str, priority: str = "P1") -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        title=title,
        original_filename=filename,
        path=path,
        source_priority=priority,
        source_type="internal",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-12",
        author_or_owner="unknown",
        use_case="retrieval_test",
        checksum="a" * 64,
        parse_status="parsed",
    )


def make_chunk(source: SourceRecord, text: str) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::chunk-0001",
        source_id=source.source_id,
        title=source.title,
        text=text,
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=len(text),
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Industry Signal" if source.source_priority == "P5" else "Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
    )


def test_mvp003_metadata_filename_beats_generic_body_match():
    target = make_source("ASP-P1-TARGET", "Asperitas IR", "Asperitas Inc. IR deck.pdf", "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/Asperitas Inc. IR deck.pdf")
    distractor = make_source("ASP-P1-DISTRACTOR", "README", "README.md", "README.md", priority="P0")
    chunks = [
        make_chunk(target, "Company facts."),
        make_chunk(distractor, "investor investor investor narrative company positioning"),
    ]

    results = search_chunks_mvp003("Where should retrieval look for Asperitas IR deck investor narrative?", chunks, [target, distractor], limit=2)

    assert results[0].source_file.endswith("Asperitas Inc. IR deck.pdf")
    assert results[0].score_components["filename_match"] > 0


def test_mvp003_duplicate_folder_context_prefers_industry_seed():
    internal = make_source("ASP-P1-SEED", "SEED 후기", "SEED 후기.pdf", "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/SEED 후기.pdf")
    industry = make_source("ASP-P5-SEED", "SEED 후기", "SEED 후기.pdf", "01_RAW_SOURCES/P5_INDUSTRY_INTELLIGENCE/SEED 후기.pdf", priority="P5")
    chunks = [
        make_chunk(internal, "SEED conference notes"),
        make_chunk(industry, "SEED conference notes"),
    ]

    results = search_chunks_mvp003("Which source should ground SEED conference from the industry intelligence folder?", chunks, [internal, industry], limit=2)

    assert results[0].source_file.startswith("01_RAW_SOURCES/P5_INDUSTRY_INTELLIGENCE")
    assert results[0].score_components["duplicate_context_bonus"] > 0


def test_mvp003_returns_unique_sources_for_top_k():
    source = make_source("ASP-P1-ONE", "Protein Design", "protein design.pdf", "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/protein design.pdf")
    chunks = [
        make_chunk(source, "protein design first chunk"),
        Chunk(**{**make_chunk(source, "protein design second chunk").to_json(), "chunk_id": "ASP-P1-ONE::chunk-0002", "char_start": 100}),
    ]

    results = search_chunks_mvp003("protein design", chunks, [source], limit=5)

    assert len(results) == 1
    assert results[0].chunk.source_id == source.source_id
