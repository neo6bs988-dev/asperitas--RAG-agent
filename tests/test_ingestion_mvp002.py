from pathlib import Path
import io
import zipfile

from asperitas_agent.chunking import chunk_document, write_chunks
from asperitas_agent.ingestion_log import write_ingestion_log
from asperitas_agent.inventory import build_inventory
from asperitas_agent.loaders import load_documents
from asperitas_agent.registry import validate_registry, write_registry
from asperitas_agent.schemas import IngestionLogEntry
from asperitas_agent.verification import verify_artifacts


def _pptx_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", f"<sld><t>{text}</t></sld>")
    return buffer.getvalue()


def test_mixed_ingestion_preserves_registry_and_chunk_provenance(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    (raw / "source.txt").write_text("AOS source hierarchy", encoding="utf-8")
    (raw / "deck.pptx").write_bytes(_pptx_bytes("PPTX source hierarchy"))
    with zipfile.ZipFile(raw / "bundle.zip", "w") as archive:
        archive.writestr("inner.txt", "ZIP CITES compliance source")
        archive.writestr("unsupported.bin", b"\x00\x01")

    records = build_inventory(tmp_path)
    chunks = []
    entries = []
    for record in records:
        bundle = load_documents(record, tmp_path)
        record.parse_status = bundle.source_parse_status
        for document in bundle.documents:
            document_chunks = chunk_document(document)
            chunks.extend(document_chunks)
            for entry in bundle.entries:
                if entry.path == document.source.path:
                    entry.extracted_chunk_count = len(document_chunks)
        entries.extend(bundle.entries)

    registry_path = write_registry(records, tmp_path)
    write_chunks(chunks, tmp_path)
    log_path = write_ingestion_log(entries, tmp_path)
    ok, errors = validate_registry(registry_path)
    verification = verify_artifacts(tmp_path)

    assert ok, errors
    assert verification["ok"], verification["errors"]
    assert chunks
    assert all(chunk.source_id in {record.source_id for record in records} for chunk in chunks)
    assert "unsupported.bin" in log_path.read_text(encoding="utf-8")


def test_ingestion_log_default_path_is_run_logs(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "01_RAW_SOURCES").mkdir()
    entry = IngestionLogEntry(
        source_id="ASP-P0-1",
        path="AGENTS.md",
        filename="AGENTS.md",
        extension=".md",
        ingestion_status="success",
        reason="plain_text",
        extracted_chunk_count=1,
        source_priority="P0",
        disclosure_level="confidential",
        compliance_flags=[],
    )

    path = write_ingestion_log([entry], tmp_path)

    assert path == tmp_path / "09_LOGS" / "run_logs" / "source_ingestion_log.md"
