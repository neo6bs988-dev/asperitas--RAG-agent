from pathlib import Path
import io
import zipfile

from asperitas_agent.inventory import build_inventory
from asperitas_agent.loaders import load_document, load_documents
from asperitas_agent.schemas import SourceRecord


def _source_for(root: Path, relative: str):
    return next(record for record in build_inventory(root) if record.path == relative)


def test_md_and_txt_load(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    (raw / "a.md").write_text("markdown source", encoding="utf-8")
    (raw / "b.txt").write_text("text source", encoding="utf-8")

    assert load_document(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/a.md"), tmp_path).parse_status == "parsed"
    assert load_document(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/b.txt"), tmp_path).parse_status == "parsed"


def test_pdf_loader_does_not_crash(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P3_SCIENTIFIC_LITERATURE"
    raw.mkdir(parents=True)
    (raw / "paper.pdf").write_bytes(b"%PDF-1.4\n% minimal invalid pdf")

    doc = load_document(_source_for(tmp_path, "01_RAW_SOURCES/P3_SCIENTIFIC_LITERATURE/paper.pdf"), tmp_path)

    assert doc.parse_status in {"parsed", "failed"}


def test_docx_loader_does_not_crash(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "doc.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", "<document><body><p>docx text</p></body></document>")

    doc = load_document(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/doc.docx"), tmp_path)

    assert doc.parse_status == "parsed"
    assert "docx text" in doc.text


def test_hwpx_loader_fails_safely_or_parses(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P4_REGULATORY_GOVERNMENT"
    raw.mkdir(parents=True)
    (raw / "reg.hwpx").write_bytes(b"not a zip")

    doc = load_document(_source_for(tmp_path, "01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/reg.hwpx"), tmp_path)

    assert doc.parse_status in {"parsed", "failed", "unsupported"}
    assert doc.parse_warnings


def test_loader_rejects_paths_outside_repo(tmp_path: Path):
    source = SourceRecord(
        source_id="ASP-P1-ESCAPE",
        title="Escape",
        original_filename="outside.txt",
        path="../outside.txt",
        source_priority="P1",
        source_type="internal",
        disclosure_level="confidential",
        license_status="internal_use",
        verification_status="unverified",
        date="2026-06-12",
        author_or_owner="unknown",
        use_case="strategy",
        checksum="abc",
        parse_status="not_attempted",
    )

    doc = load_document(source, tmp_path)

    assert doc.parse_status == "failed"
    assert doc.parser_used == "path_guard"


def _pptx_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", f"<sld><t>{text}</t></sld>")
    return buffer.getvalue()


def test_pptx_loader_extracts_slide_text(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    (raw / "deck.pptx").write_bytes(_pptx_bytes("PPTX slide source truth"))

    doc = load_document(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/deck.pptx"), tmp_path)

    assert doc.parse_status == "parsed"
    assert "PPTX slide source truth" in doc.text


def test_zip_safe_extraction_loads_supported_inner_files(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "bundle.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("notes/readme.txt", "zip text source")
        archive.writestr("slides/deck.pptx", _pptx_bytes("zip pptx source"))

    bundle = load_documents(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/bundle.zip"), tmp_path)

    assert bundle.source_parse_status == "parsed"
    assert len([doc for doc in bundle.documents if doc.parse_status == "parsed"]) == 2
    assert any("zip text source" in doc.text for doc in bundle.documents)
    assert any("zip pptx source" in doc.text for doc in bundle.documents)
    assert all("::" in doc.source.path for doc in bundle.documents)


def test_zip_path_traversal_member_is_rejected(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../evil.txt", "do not read")

    bundle = load_documents(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/unsafe.zip"), tmp_path)

    assert bundle.source_parse_status == "failed"
    assert not bundle.documents
    assert any(entry.ingestion_status == "failed" and "unsafe path" in entry.reason for entry in bundle.entries)


def test_zip_suspicious_binary_member_is_rejected_and_logged(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "suspicious.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("safe.txt", "safe text")
        archive.writestr("payload.exe", b"MZ executable")

    bundle = load_documents(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/suspicious.zip"), tmp_path)

    assert bundle.source_parse_status == "partial"
    assert any(entry.ingestion_status == "failed" and "suspicious" in entry.reason for entry in bundle.entries)
    assert any(doc.parse_status == "parsed" and "safe text" in doc.text for doc in bundle.documents)


def test_zip_unsupported_inner_file_is_logged(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "mixed.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("image.png", b"\x89PNG\r\n")

    bundle = load_documents(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/mixed.zip"), tmp_path)

    assert bundle.source_parse_status == "unsupported"
    assert any(entry.ingestion_status == "unsupported" and entry.filename == "image.png" for entry in bundle.entries)


def test_zip_macos_metadata_file_is_logged_without_parsing(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    path = raw / "macos.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("__MACOSX/._doc.pdf", b"not really a pdf")

    bundle = load_documents(_source_for(tmp_path, "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/macos.zip"), tmp_path)

    assert bundle.source_parse_status == "unsupported"
    assert any(entry.ingestion_status == "unsupported" and "metadata" in entry.reason for entry in bundle.entries)
