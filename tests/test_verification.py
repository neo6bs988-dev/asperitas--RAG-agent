from pathlib import Path

from asperitas_agent.chunking import write_chunks
from asperitas_agent.registry import write_registry
from asperitas_agent.schemas import Chunk, SourceRecord
from asperitas_agent.verification import verify_artifacts


def make_source(root: Path) -> SourceRecord:
    (root / "AGENTS.md").write_text("agents", encoding="utf-8")
    (root / "01_RAW_SOURCES").mkdir()
    return SourceRecord(
        source_id="ASP-P0-ABCDEF123456",
        title="AOS",
        original_filename="AGENTS.md",
        path="AGENTS.md",
        source_priority="P0",
        source_type="prompt",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-12",
        author_or_owner="unknown",
        use_case="agent_development",
        checksum="a" * 64,
        parse_status="parsed",
    )


def make_chunk(source: SourceRecord) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::chunk-0001",
        source_id=source.source_id,
        title=source.title,
        text="AOS source hierarchy",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=20,
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
    )


def test_verify_artifacts_passes_for_consistent_registry_and_chunks(tmp_path: Path):
    source = make_source(tmp_path)
    write_registry([source], tmp_path)
    write_chunks([make_chunk(source)], tmp_path)

    result = verify_artifacts(tmp_path)

    assert result["ok"]
    assert result["registry_records"] == 1
    assert result["chunk_count"] == 1


def test_verify_artifacts_catches_unknown_chunk_source(tmp_path: Path):
    source = make_source(tmp_path)
    chunk = make_chunk(source)
    chunk.source_id = "ASP-P0-MISSING"
    write_registry([source], tmp_path)
    write_chunks([chunk], tmp_path)

    result = verify_artifacts(tmp_path)

    assert not result["ok"]
    assert any("unknown source_id" in error for error in result["errors"])


def test_verify_artifacts_reports_missing_registry_without_crashing(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "01_RAW_SOURCES").mkdir()

    result = verify_artifacts(tmp_path)

    assert not result["ok"]
    assert result["registry_records"] == 0
    assert any("Registry not found" in error for error in result["errors"])


def test_verify_artifacts_reports_corrupt_chunks_without_crashing(tmp_path: Path):
    source = make_source(tmp_path)
    write_registry([source], tmp_path)
    chunk_path = tmp_path / "data" / "chunks.jsonl"
    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_path.write_text("{not json}\n", encoding="utf-8")

    result = verify_artifacts(tmp_path)

    assert not result["ok"]
    assert any("Could not read chunks" in error for error in result["errors"])
