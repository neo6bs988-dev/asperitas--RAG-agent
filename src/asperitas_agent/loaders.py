from __future__ import annotations

import copy
import io
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from .inventory import repo_root
from .schemas import IngestionLogEntry, LoadedDocument, SourceRecord


SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".hwpx", ".pptx", ".zip"}
ZIP_INNER_SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".hwpx", ".pptx"}
SUSPICIOUS_INNER_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".com",
    ".dll",
    ".dmg",
    ".exe",
    ".jar",
    ".js",
    ".msi",
    ".ps1",
    ".scr",
    ".sh",
    ".vbs",
}
SUSPICIOUS_MAGIC = (b"MZ", b"\x7fELF", b"\xfe\xed\xfa", b"\xca\xfe\xba\xbe")
MAX_ZIP_MEMBER_BYTES = 25 * 1024 * 1024


@dataclass
class LoadedSourceBundle:
    documents: list[LoadedDocument]
    entries: list[IngestionLogEntry]
    source_parse_status: str


def _decode_text(data: bytes) -> str:
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _safe_source_path(root: Path, source_path: str) -> Path:
    root_resolved = root.resolve()
    path = (root_resolved / source_path).resolve()
    try:
        path.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("Source path escapes repository root.") from exc
    return path


def _entry(
    source: SourceRecord,
    path: str,
    filename: str,
    extension: str,
    status: str,
    reason: str,
) -> IngestionLogEntry:
    return IngestionLogEntry(
        source_id=source.source_id,
        path=path,
        filename=filename,
        extension=extension or "<none>",
        ingestion_status=status,
        reason=reason,
        extracted_chunk_count=0,
        source_priority=source.source_priority,
        disclosure_level=source.disclosure_level,
        compliance_flags=[],
    )


def _xml_text_from_zip_bytes(data: bytes, suffixes: tuple[str, ...], prefixes: tuple[str, ...] = ()) -> str:
    chunks: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in sorted(archive.namelist()):
                normalized = name.replace("\\", "/")
                if prefixes and not normalized.startswith(prefixes):
                    continue
                if not normalized.endswith(suffixes):
                    continue
                try:
                    root = ElementTree.fromstring(archive.read(name))
                except (ElementTree.ParseError, KeyError):
                    continue
                text = "\n".join(t.strip() for t in root.itertext() if t and t.strip())
                if text:
                    chunks.append(text)
    except (OSError, zipfile.BadZipFile):
        return ""
    return "\n\n".join(chunks)


def _xml_text_from_zip(path: Path, suffixes: tuple[str, ...], prefixes: tuple[str, ...] = ()) -> str:
    try:
        return _xml_text_from_zip_bytes(path.read_bytes(), suffixes, prefixes)
    except OSError:
        return ""


def _load_pdf_bytes(data: bytes) -> tuple[str, str, list[str], list[tuple[int | None, str]]]:
    warnings: list[str] = []
    page_texts: list[tuple[int | None, str]] = []
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(data))
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                page_texts.append((index, text))
        if page_texts:
            return "\n\n".join(text for _, text in page_texts), "pypdf", warnings, page_texts
    except Exception as exc:
        warnings.append(f"pypdf unavailable_or_failed: {exc.__class__.__name__}")
    return "", "pdf_unparsed", warnings or ["No PDF parser available or no extractable text."], page_texts


def _load_pdf(path: Path) -> tuple[str, str, list[str], list[tuple[int | None, str]]]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        return "", "pdf_unreadable", [f"Could not read PDF: {exc.__class__.__name__}"], []

    text, parser, warnings, pages = _load_pdf_bytes(data)
    if text.strip():
        return text, parser, warnings, pages

    binary = shutil.which("pdftotext")
    if binary:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "out.txt"
                subprocess.run([binary, "-layout", str(path), str(output)], check=True, capture_output=True)
                text = output.read_text(encoding="utf-8", errors="replace")
                if text.strip():
                    return text, "pdftotext", warnings, [(None, text)]
        except Exception as exc:
            warnings.append(f"pdftotext_failed: {exc.__class__.__name__}")
    return "", parser, warnings or ["No PDF parser available or no extractable text."], pages


def _load_text_bytes(data: bytes) -> tuple[str, str, str, list[str]]:
    if data.startswith(b"PK\x03\x04"):
        text = _xml_text_from_zip_bytes(data, (".xml",))
        return text, "zip_xml_text", "parsed" if text.strip() else "failed", [] if text.strip() else ["No extractable XML text."]
    if b"\x00" in data[:128] and not (data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff")):
        return "", "text", "failed", ["NUL bytes detected in text file."]
    text = _decode_text(data)
    return text, "plain_text", "parsed" if text.strip() else "failed", [] if text.strip() else ["No extractable text."]


def _load_docx_bytes(data: bytes) -> tuple[str, str, str, list[str]]:
    text = _xml_text_from_zip_bytes(data, ("document.xml", "footnotes.xml", "endnotes.xml"))
    return text, "docx_zip_xml", "parsed" if text.strip() else "failed", [] if text.strip() else ["No extractable DOCX text."]


def _load_pptx_bytes(data: bytes) -> tuple[str, str, str, list[str]]:
    text = _xml_text_from_zip_bytes(data, (".xml",), ("ppt/slides/", "ppt/notesSlides/"))
    return text, "pptx_zip_xml", "parsed" if text.strip() else "failed", [] if text.strip() else ["No extractable PPTX slide text."]


def _load_hwpx_bytes(data: bytes) -> tuple[str, str, str, list[str]]:
    if not data.startswith(b"PK\x03\x04"):
        return "", "hwpx_zip_xml", "unsupported", ["HWPX is not a ZIP/XML payload or cannot be parsed by the MVP-002 fallback."]
    text = _xml_text_from_zip_bytes(data, (".xml",))
    return text, "hwpx_zip_xml", "parsed" if text.strip() else "unsupported", [] if text.strip() else ["No extractable HWPX XML text with MVP-002 fallback."]


def _document_from_bytes(source: SourceRecord, data: bytes, suffix: str) -> LoadedDocument:
    suffix = suffix.lower()
    if suffix in {".md", ".txt"}:
        text, parser, status, warnings = _load_text_bytes(data)
        return LoadedDocument(source, text, parser, status, warnings)
    if suffix == ".docx":
        text, parser, status, warnings = _load_docx_bytes(data)
        return LoadedDocument(source, text, parser, status, warnings)
    if suffix == ".pptx":
        text, parser, status, warnings = _load_pptx_bytes(data)
        return LoadedDocument(source, text, parser, status, warnings)
    if suffix == ".hwpx":
        text, parser, status, warnings = _load_hwpx_bytes(data)
        return LoadedDocument(source, text, parser, status, warnings)
    if suffix == ".pdf":
        text, parser, warnings, pages = _load_pdf_bytes(data)
        status = "parsed" if text.strip() else "failed"
        return LoadedDocument(source, text, parser, status, warnings, pages)
    return LoadedDocument(source, "", "unsupported", "unsupported", [f"Unsupported file type: {suffix or '<none>'}"])


def _inner_source(source: SourceRecord, inner_path: str) -> SourceRecord:
    clone = copy.copy(source)
    clone.title = f"{source.title}::{inner_path}"
    clone.original_filename = PurePosixPath(inner_path).name
    clone.path = f"{source.path}::{inner_path}"
    return clone


def _safe_zip_member_name(name: str) -> tuple[bool, str]:
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return False, "absolute path"
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return False, "path traversal"
    return True, normalized


def _member_looks_suspicious(filename: str, data_head: bytes) -> bool:
    suffix = PurePosixPath(filename).suffix.lower()
    return suffix in SUSPICIOUS_INNER_EXTENSIONS or data_head.startswith(SUSPICIOUS_MAGIC)


def _is_zip_metadata_member(normalized: str) -> bool:
    path = PurePosixPath(normalized)
    return "__MACOSX" in path.parts or path.name.startswith("._") or path.name == ".DS_Store"


def _load_zip(source: SourceRecord, path: Path) -> LoadedSourceBundle:
    documents: list[LoadedDocument] = []
    entries: list[IngestionLogEntry] = []
    any_success = False
    any_issue = False

    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        entry = _entry(source, source.path, source.original_filename, ".zip", "failed", f"Could not open ZIP: {exc.__class__.__name__}")
        return LoadedSourceBundle([], [entry], "failed")

    with archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename.lower()):
            if info.is_dir():
                continue
            is_safe, normalized = _safe_zip_member_name(info.filename)
            if not is_safe:
                any_issue = True
                entries.append(_entry(source, f"{source.path}::{info.filename}", PurePosixPath(info.filename).name, PurePosixPath(info.filename).suffix.lower(), "failed", f"Rejected ZIP member with unsafe path: {normalized}"))
                continue

            filename = PurePosixPath(normalized).name
            suffix = PurePosixPath(normalized).suffix.lower()
            entry_path = f"{source.path}::{normalized}"

            if _is_zip_metadata_member(normalized):
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "unsupported", "Ignored ZIP metadata/resource fork file."))
                continue

            if suffix in SUSPICIOUS_INNER_EXTENSIONS:
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "failed", "Rejected suspicious binary/executable ZIP inner file."))
                continue

            if suffix not in ZIP_INNER_SUPPORTED_EXTENSIONS:
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "unsupported", f"Unsupported ZIP inner file type: {suffix or '<none>'}"))
                continue

            if info.file_size > MAX_ZIP_MEMBER_BYTES:
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "failed", f"ZIP inner file exceeds size limit: {info.file_size} bytes"))
                continue

            try:
                with archive.open(info, "r") as handle:
                    data = handle.read()
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "failed", f"Could not read ZIP inner file: {exc.__class__.__name__}"))
                continue

            if _member_looks_suspicious(filename, data[:16]):
                any_issue = True
                entries.append(_entry(source, entry_path, filename, suffix, "failed", "Rejected suspicious binary/executable ZIP inner file."))
                continue

            document = _document_from_bytes(_inner_source(source, normalized), data, suffix)
            documents.append(document)
            if document.parse_status == "parsed":
                any_success = True
                status = "success"
            elif document.parse_status == "unsupported":
                any_issue = True
                status = "unsupported"
            else:
                any_issue = True
                status = "failed"
            entries.append(_entry(source, entry_path, filename, suffix, status, "; ".join(document.parse_warnings) or document.parser_used))

    if any_success and any_issue:
        source_status = "partial"
    elif any_success:
        source_status = "parsed"
    elif entries:
        source_status = "unsupported" if all(entry.ingestion_status == "unsupported" for entry in entries) else "failed"
    else:
        source_status = "unsupported"
        entries.append(_entry(source, source.path, source.original_filename, ".zip", "unsupported", "ZIP archive contains no files."))
    return LoadedSourceBundle(documents, entries, source_status)


def _load_single(source: SourceRecord, path: Path) -> LoadedSourceBundle:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        entry = _entry(source, source.path, source.original_filename, suffix, "unsupported", f"Unsupported file type: {suffix or '<none>'}")
        document = LoadedDocument(source, "", "unsupported", "unsupported", [entry.reason])
        return LoadedSourceBundle([document], [entry], "unsupported")

    if suffix == ".zip":
        return _load_zip(source, path)

    try:
        if suffix == ".pdf":
            text, parser, warnings, pages = _load_pdf(path)
            status = "parsed" if text.strip() else "failed"
            document = LoadedDocument(source, text, parser, status, warnings, pages)
        else:
            document = _document_from_bytes(source, path.read_bytes(), suffix)
    except Exception as exc:
        document = LoadedDocument(source, "", suffix.lstrip(".") or "unknown", "failed", [f"Loader failed: {exc.__class__.__name__}"])

    if document.parse_status == "parsed":
        entry_status = "success"
    elif document.parse_status == "unsupported":
        entry_status = "unsupported"
    else:
        entry_status = "failed"
    entry = _entry(source, source.path, source.original_filename, suffix, entry_status, "; ".join(document.parse_warnings) or document.parser_used)
    return LoadedSourceBundle([document], [entry], document.parse_status)


def load_documents(source: SourceRecord, root: Path | None = None) -> LoadedSourceBundle:
    root = repo_root(root)
    try:
        path = _safe_source_path(root, source.path)
    except ValueError as exc:
        entry = _entry(source, source.path, source.original_filename, Path(source.path).suffix.lower(), "failed", str(exc))
        document = LoadedDocument(source, "", "path_guard", "failed", [str(exc)])
        return LoadedSourceBundle([document], [entry], "failed")
    return _load_single(source, path)


def load_document(source: SourceRecord, root: Path | None = None) -> LoadedDocument:
    bundle = load_documents(source, root)
    parsed = [document for document in bundle.documents if document.parse_status == "parsed"]
    if len(parsed) == 1:
        return parsed[0]
    if parsed:
        text = "\n\n".join(f"[{document.source.path}]\n{document.text}" for document in parsed)
        warnings = [entry.reason for entry in bundle.entries if entry.ingestion_status != "success"]
        return LoadedDocument(source, text, "bundle", "parsed", warnings)
    if bundle.documents:
        return bundle.documents[0]
    warnings = [entry.reason for entry in bundle.entries]
    return LoadedDocument(source, "", "unsupported", bundle.source_parse_status, warnings)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
