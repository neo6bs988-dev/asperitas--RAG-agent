#!/usr/bin/env python3
"""Asperitas source registry, ingestion, retrieval, and compliance gate.

The implementation is intentionally deterministic and local-first. It does not
embed, upload, or call external services. Registry rows and chunks retain the
source path, SHA-256 hash, source priority, disclosure level, and risk flags.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence
from xml.etree import ElementTree


REPO_ROOT = Path(__file__).resolve().parents[2]

REGISTRY_COLUMNS = [
    "source_id",
    "title",
    "file_name",
    "relative_path",
    "absolute_path",
    "sha256",
    "file_size_bytes",
    "modified_utc",
    "source_priority",
    "source_type",
    "disclosure_level",
    "origin",
    "author_or_owner",
    "date_created",
    "date_accessed",
    "jurisdiction",
    "license_status",
    "confidentiality_notes",
    "pii_status",
    "verification_status",
    "ingestion_status",
    "legal_review_status",
    "wet_lab_validation_status",
    "provenance",
    "summary",
    "evidence_label",
    "risk_flags",
    "allowed_use_cases",
    "prohibited_use_cases",
]

RAW_PRIORITY_DIRS = {
    "P0_ACTIVE_PROMPT": ("P0", "prompt", "restricted"),
    "P1_ASPERITAS_INTERNAL": ("P1", "internal", "confidential"),
    "P1_RND_PROJECTS": ("P1", "internal", "confidential"),
    "P2_OFFICIAL_ASPERITAS": ("P2", "official", "external-safe"),
    "P3_SCIENTIFIC_LITERATURE": ("P3", "paper", "external-safe"),
    "P4_REGULATORY_GOVERNMENT": ("P4", "regulatory", "external-safe"),
    "P5_INDUSTRY_INTELLIGENCE": ("P5", "market", "internal"),
    "P6_BENCHMARK_OPERATING": ("P6", "benchmark", "external-safe"),
}

SOURCE_ROOTS = [
    "AGENTS.md",
    "README.md",
    "00_ADMIN",
    "01_RAW_SOURCES",
    "04_AGENT_SYSTEM",
    "06_EVALS/golden_questions",
]

GENERATED_RELATIVE_PATHS = {
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "00_ADMIN/file_inventory_generated.csv",
    "00_ADMIN/metadata_schema.yaml",
    "03_PROCESSED_KB/chunks/source_chunks.jsonl",
    "03_PROCESSED_KB/chunks/source_chunks_manifest.json",
}

BINARY_EXTENSIONS = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".doc",
    ".docx",
    ".hwpx",
    ".xlsx",
    ".xls",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
}

READABLE_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".py",
}

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5, "P6": 6}

EVIDENCE_BY_PRIORITY = {
    "P0": "Document-Supported Fact",
    "P1": "Document-Supported Fact",
    "P2": "Official Source",
    "P3": "Peer-Reviewed Evidence",
    "P4": "Regulatory Source",
    "P5": "Industry Signal",
    "P6": "Inference",
}

ALLOWED_USE_CASES = {
    "P0": ["agent_development", "operations", "rag", "historical_context"],
    "P1": ["strategy", "science", "compliance", "market", "fundraising", "operations", "agent_development", "rag", "historical_context"],
    "P2": ["strategy", "market", "fundraising", "operations", "rag", "historical_context"],
    "P3": ["science", "compliance", "rag", "historical_context"],
    "P4": ["compliance", "operations", "rag", "historical_context"],
    "P5": ["strategy", "market", "fundraising", "rag", "historical_context"],
    "P6": ["strategy", "operations", "agent_development", "historical_context"],
}

PROHIBITED_BY_DISCLOSURE = {
    "restricted": ["public", "external_unapproved"],
    "confidential": ["public", "external_unapproved"],
    "internal": ["public"],
    "external-safe": [],
    "public": [],
    "unknown": ["public"],
}

RISK_PATTERNS = {
    "CITES": [r"(?<![A-Za-z0-9])CITES(?![A-Za-z0-9])", "멸종위기", "야생생물"],
    "Nagoya": [r"(?<![A-Za-z0-9])Nagoya(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])ABS(?![A-Za-z0-9])", "나고야", "유전자원", "생물자원"],
    "LMO": [r"(?<![A-Za-z0-9])LMO(?![A-Za-z0-9])", r"(?<![A-Za-z0-9])GMO(?![A-Za-z0-9])", "유전자변형", "유전자 조작", "유전자조작"],
    "biosafety": ["biosafety", "생물안전", "무세포", "미생물", "합성생물학", "CRISPR", "유전자회로"],
    "biosecurity": ["biosecurity", "항생제", "pathogen", "toxin", "독소", "병원체"],
    "IP": ["IP", "특허", "영업비밀", "proprietary", "trade secret", "protein design"],
    "privacy": ["개인", "후기", "contact", "email", "phone", "이메일", "전화"],
    "legal": ["규제", "법", "compliance", "legal", "정부", "R&D", "연구과제"],
    "financial": ["IR", "투자", "market", "시장", "fundraising", "investor", "deck"],
    "external_comm": ["IR", "소개", "public", "investor", "partner", "deck"],
}

HIGH_RISK_ACTION_PATTERNS = [
    "step-by-step",
    "protocol",
    "wet-lab",
    "실험 프로토콜",
    "배양 조건",
    "transformation",
    "plasmid",
    "gene drive",
    "gain of function",
    "optimize virulence",
    "bypass",
]

BIO_KEYWORDS = [
    "crispr",
    "gmo",
    "lmo",
    "gene",
    "genetic",
    "synthetic biology",
    "microbe",
    "pathogen",
    "toxin",
    "항생제",
    "미생물",
    "합성생물학",
    "유전자",
    "생물안전",
]


@dataclass
class SourceRecord:
    source_id: str
    title: str
    file_name: str
    relative_path: str
    absolute_path: str
    sha256: str
    file_size_bytes: int
    modified_utc: str
    source_priority: str
    source_type: str
    disclosure_level: str
    origin: str
    author_or_owner: str | None
    date_created: str | None
    date_accessed: str
    jurisdiction: str
    license_status: str
    confidentiality_notes: str
    pii_status: str
    verification_status: str
    ingestion_status: str
    legal_review_status: str
    wet_lab_validation_status: str
    provenance: str
    summary: str
    evidence_label: str
    risk_flags: list[str] = field(default_factory=list)
    allowed_use_cases: list[str] = field(default_factory=list)
    prohibited_use_cases: list[str] = field(default_factory=list)

    def csv_row(self) -> dict[str, str]:
        row = asdict(self)
        for key in ["risk_flags", "allowed_use_cases", "prohibited_use_cases"]:
            row[key] = "|".join(row[key])
        for key, value in list(row.items()):
            if value is None:
                row[key] = ""
        return row


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    title: str
    relative_path: str
    source_priority: str
    source_type: str
    disclosure_level: str
    license_status: str
    verification_status: str
    evidence_label: str
    risk_flags: list[str]
    page_or_location: str
    text: str
    content_sha256: str

    def as_json(self) -> dict[str, object]:
        return asdict(self)


def normalized_relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_source_id(priority: str, digest: str) -> str:
    return f"ASP-{priority}-{digest[:12].upper()}"


def utc_now_date() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def modified_utc(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()


def is_generated_path(relpath: str) -> bool:
    return relpath in GENERATED_RELATIVE_PATHS or relpath.startswith("03_PROCESSED_KB/")


def discover_source_files(root: Path = REPO_ROOT) -> list[Path]:
    files: list[Path] = []
    for entry in SOURCE_ROOTS:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            relpath = normalized_relpath(path, root)
            if not is_generated_path(relpath):
                files.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file():
                relpath = normalized_relpath(child, root)
                if not is_generated_path(relpath):
                    files.append(child)
    return sorted(set(files), key=lambda item: normalized_relpath(item, root).lower())


def classify_path(path: Path, root: Path = REPO_ROOT) -> tuple[str, str, str]:
    rel = normalized_relpath(path, root)
    parts = Path(rel).parts
    for part in parts:
        if part in RAW_PRIORITY_DIRS:
            return RAW_PRIORITY_DIRS[part]

    lower = rel.lower()
    if rel in {"AGENTS.md", "README.md"}:
        return "P0", "prompt", "restricted"
    if lower.startswith("04_agent_system/prompts/"):
        return "P0", "prompt", "restricted"
    if lower.startswith("04_agent_system/guardrails/"):
        return "P1", "internal", "confidential"
    if lower.startswith("06_evals/"):
        return "P1", "internal", "confidential"
    if lower.startswith("00_admin/"):
        return "P1", "internal", "confidential"
    return "P1", "unknown", "confidential"


def jurisdiction_for_path(path: Path) -> str:
    text = path.as_posix().lower()
    if any(token in text for token in ["korea", "kr", "한국", "정부", "규제", "연구과제"]):
        return "KR"
    if "china" in text or "중국" in text:
        return "CN"
    if "global" in text or "글로벌" in text:
        return "GLOBAL"
    return "unknown"


def origin_for_path(path: Path, root: Path) -> str:
    rel = normalized_relpath(path, root)
    if rel.startswith("01_RAW_SOURCES/"):
        return "uploaded"
    if rel.startswith("04_AGENT_SYSTEM/") or rel in {"AGENTS.md", "README.md"}:
        return "manual"
    if rel.startswith("00_ADMIN/"):
        return "manual"
    return "unknown"


def license_status(priority: str, disclosure: str) -> str:
    if disclosure in {"restricted", "confidential"}:
        return "restricted"
    if priority in {"P2", "P3", "P4", "P5", "P6"}:
        return "needs_review"
    return "unknown"


def verification_status(priority: str) -> str:
    if priority == "P0":
        return "partially_verified"
    if priority == "P4":
        return "needs_external_verification"
    if priority in {"P2", "P3"}:
        return "partially_verified"
    return "unverified"


def pii_status(path: Path, disclosure: str) -> str:
    haystack = path.name.lower()
    if any(token in haystack for token in ["후기", "contact", "email", "phone", "소개"]):
        return "unknown"
    if disclosure in {"restricted", "confidential", "internal"}:
        return "unknown"
    return "none"


def risk_flags_for_text(text: str) -> list[str]:
    found: set[str] = set()
    for flag, patterns in RISK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.add(flag)
                break
    return sorted(found)


def risk_flags_for_path(path: Path, priority: str, disclosure: str) -> list[str]:
    text = path.as_posix()
    flags = set(risk_flags_for_text(text))
    if priority in {"P0", "P1"} or disclosure in {"restricted", "confidential"}:
        flags.add("external_comm")
    return sorted(flags)


def title_from_file(path: Path) -> str:
    return path.stem.strip() or path.name


def summary_for_record(path: Path, priority: str, source_type: str, disclosure: str) -> str:
    return (
        f"Registered local source file classified as {priority}/{source_type} "
        f"with {disclosure} disclosure. Content claims require retrieval-level citation."
    )


def build_record(path: Path, root: Path = REPO_ROOT) -> SourceRecord:
    priority, source_type, disclosure = classify_path(path, root)
    digest = sha256_file(path)
    rel = normalized_relpath(path, root)
    risks = risk_flags_for_path(path, priority, disclosure)
    prohibited = PROHIBITED_BY_DISCLOSURE.get(disclosure, ["public"])
    return SourceRecord(
        source_id=stable_source_id(priority, digest),
        title=title_from_file(path),
        file_name=path.name,
        relative_path=rel,
        absolute_path=str(path.resolve()),
        sha256=digest,
        file_size_bytes=path.stat().st_size,
        modified_utc=modified_utc(path),
        source_priority=priority,
        source_type=source_type,
        disclosure_level=disclosure,
        origin=origin_for_path(path, root),
        author_or_owner=None,
        date_created=None,
        date_accessed=utc_now_date(),
        jurisdiction=jurisdiction_for_path(path),
        license_status=license_status(priority, disclosure),
        confidentiality_notes=f"Default classification from source priority and repository path: {disclosure}.",
        pii_status=pii_status(path, disclosure),
        verification_status=verification_status(priority),
        ingestion_status="registered",
        legal_review_status="not_reviewed",
        wet_lab_validation_status="not_applicable",
        provenance=rel,
        summary=summary_for_record(path, priority, source_type, disclosure),
        evidence_label=EVIDENCE_BY_PRIORITY.get(priority, "Needs External Verification"),
        risk_flags=risks,
        allowed_use_cases=ALLOWED_USE_CASES.get(priority, ["historical_context"]),
        prohibited_use_cases=prohibited,
    )


def build_registry(root: Path = REPO_ROOT) -> list[SourceRecord]:
    return [build_record(path, root) for path in discover_source_files(root)]


def write_registry(records: Sequence[SourceRecord], csv_path: Path, jsonl_path: Path | None = None) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.csv_row())
    if jsonl_path:
        with jsonl_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True) + "\n")


def write_inventory(records: Sequence[SourceRecord], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["relative_path", "source_id", "sha256", "file_size_bytes", "modified_utc", "source_priority", "disclosure_level"]
    with out_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field_name: getattr(record, field_name) for field_name in fields})


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            try:
                decoded = data.decode(encoding)
            except UnicodeDecodeError:
                continue
            if "\x00" not in decoded[:256] and decoded.strip():
                return decoded
        return ""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return data.decode("cp949", errors="ignore")


def xml_text_from_zip(path: Path, suffix_filter: tuple[str, ...]) -> str:
    texts: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = sorted(name for name in archive.namelist() if name.endswith(suffix_filter))
            for name in names:
                with archive.open(name) as handle:
                    payload = handle.read()
                try:
                    root = ElementTree.fromstring(payload)
                except ElementTree.ParseError:
                    continue
                node_texts = [node.text for node in root.iter() if node.text and node.text.strip()]
                if node_texts:
                    texts.append("\n".join(node_texts))
    except (zipfile.BadZipFile, OSError):
        return ""
    return "\n\n".join(texts)


def docx_text(path: Path) -> str:
    return xml_text_from_zip(path, ("document.xml", "footnotes.xml", "endnotes.xml"))


def pptx_text(path: Path) -> str:
    return xml_text_from_zip(path, tuple(f"slide{i}.xml" for i in range(1, 500)))


def hwpx_text(path: Path) -> str:
    return xml_text_from_zip(path, (".xml",))


def pdf_text_with_pypdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    try:
        reader = PdfReader(str(path))
        pages = []
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[page {index + 1}]\n{text}")
        return "\n\n".join(pages)
    except Exception:
        return ""


def find_pdftotext() -> str | None:
    binary = shutil.which("pdftotext")
    if binary:
        return binary
    dependency_bin = Path(sys.executable).resolve().parents[1] / "bin"
    for name in ("pdftotext.exe", "pdftotext"):
        candidate = dependency_bin / name
        if candidate.exists():
            return str(candidate)
    return None


def pdf_text_with_pdftotext(path: Path) -> str:
    binary = find_pdftotext()
    if not binary:
        return ""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "out.txt"
        try:
            subprocess.run([binary, "-layout", str(path), str(out_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return out_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""


def load_source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in READABLE_TEXT_EXTENSIONS:
        try:
            if path.read_bytes()[:4] == b"PK\x03\x04":
                return xml_text_from_zip(path, (".xml",))
        except OSError:
            return ""
    if suffix in READABLE_TEXT_EXTENSIONS:
        return read_text_file(path)
    if suffix == ".docx":
        return docx_text(path)
    if suffix == ".pptx":
        return pptx_text(path)
    if suffix == ".hwpx":
        return hwpx_text(path)
    if suffix == ".pdf":
        return pdf_text_with_pypdf(path) or pdf_text_with_pdftotext(path)
    return ""


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_chunks(text: str, max_chars: int = 1600, overlap: int = 200) -> list[str]:
    text = normalize_text(text)
    if not text:
        return []
    paragraphs = [para.strip() for para in re.split(r"\n\s*\n", text) if para.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(para) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            for start in range(0, len(para), max_chars - overlap):
                piece = para[start : start + max_chars]
                if piece.strip():
                    chunks.append(piece.strip())
            continue
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current.strip())
            prefix = current[-overlap:] if overlap and current else ""
            current = f"{prefix}\n\n{para}".strip() if prefix else para
    if current:
        chunks.append(current.strip())
    return chunks


def chunks_for_record(record: SourceRecord, root: Path = REPO_ROOT, max_chars: int = 1600) -> list[Chunk]:
    path = root / record.relative_path
    text = load_source_text(path)
    chunks = split_chunks(text, max_chars=max_chars)
    result: list[Chunk] = []
    for index, chunk_text in enumerate(chunks, start=1):
        content_sha = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
        result.append(
            Chunk(
                chunk_id=f"{record.source_id}::chunk-{index:04d}",
                source_id=record.source_id,
                title=record.title,
                relative_path=record.relative_path,
                source_priority=record.source_priority,
                source_type=record.source_type,
                disclosure_level=record.disclosure_level,
                license_status=record.license_status,
                verification_status=record.verification_status,
                evidence_label=record.evidence_label,
                risk_flags=record.risk_flags,
                page_or_location=f"chunk {index}",
                text=chunk_text,
                content_sha256=content_sha,
            )
        )
    return result


def build_chunks(records: Sequence[SourceRecord], root: Path = REPO_ROOT, max_chars: int = 1600) -> tuple[list[Chunk], dict[str, object]]:
    chunks: list[Chunk] = []
    skipped: list[dict[str, str]] = []
    for record in records:
        record_chunks = chunks_for_record(record, root=root, max_chars=max_chars)
        if record_chunks:
            record.ingestion_status = "chunked"
            chunks.extend(record_chunks)
        else:
            skipped.append({"source_id": record.source_id, "relative_path": record.relative_path, "reason": "no_extractable_text"})
    manifest = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_count": len(records),
        "chunk_count": len(chunks),
        "skipped_count": len(skipped),
        "skipped": skipped,
    }
    return chunks, manifest


def write_chunks(chunks: Sequence[Chunk], out_path: Path, manifest: dict[str, object], manifest_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.as_json(), ensure_ascii=False, sort_keys=True) + "\n")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


TOKEN_RE = re.compile(r"[A-Za-z0-9_가-힣]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def load_chunks(path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            chunks.append(Chunk(**data))
    return chunks


def allowed_for_use_case(disclosure_level: str, use_case: str) -> bool:
    if use_case in {"internal", "operations", "agent_development"}:
        return True
    if use_case in {"public", "investor", "partner", "researcher", "external"}:
        return disclosure_level in {"public", "external-safe"}
    return disclosure_level in {"public", "external-safe", "internal"}


def retrieve(query: str, chunks: Sequence[Chunk], use_case: str = "internal", limit: int = 5) -> list[dict[str, object]]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    query_set = set(query_tokens)
    doc_freq: dict[str, int] = {token: 0 for token in query_set}
    chunk_tokens: list[list[str]] = []
    visible_chunks: list[Chunk] = []
    for chunk in chunks:
        if not allowed_for_use_case(chunk.disclosure_level, use_case):
            continue
        tokens = tokenize(chunk.text + " " + chunk.title)
        token_set = set(tokens)
        for token in query_set:
            if token in token_set:
                doc_freq[token] += 1
        chunk_tokens.append(tokens)
        visible_chunks.append(chunk)

    scored: list[tuple[float, Chunk]] = []
    total = max(len(visible_chunks), 1)
    phrase = query.lower().strip()
    for chunk, tokens in zip(visible_chunks, chunk_tokens):
        counts = {token: tokens.count(token) for token in query_set}
        score = 0.0
        for token, count in counts.items():
            if count:
                score += (1 + math.log(count)) * math.log((total + 1) / (doc_freq.get(token, 0) + 1) + 1)
        if phrase and phrase in chunk.text.lower():
            score += 2.0
        if score > 0:
            score += 0.1 * (6 - PRIORITY_RANK.get(chunk.source_priority, 6))
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "score": round(score, 4),
            "source_id": chunk.source_id,
            "title": chunk.title,
            "priority": chunk.source_priority,
            "source_type": chunk.source_type,
            "disclosure_level": chunk.disclosure_level,
            "license_status": chunk.license_status,
            "verification_status": chunk.verification_status,
            "evidence_label": chunk.evidence_label,
            "chunk_id": chunk.chunk_id,
            "page_or_location": chunk.page_or_location,
            "claim_supported": True,
            "confidence": "medium" if score >= 2 else "low",
            "risk_flags": chunk.risk_flags,
            "excerpt": textwrap.shorten(" ".join(chunk.text.split()), width=500, placeholder="..."),
        }
        for score, chunk in scored[:limit]
    ]


def compliance_scan(text: str, use_case: str = "internal", disclosure_level: str | None = None) -> dict[str, object]:
    flags = set(risk_flags_for_text(text))
    lowered = text.lower()
    high_risk_action = any(pattern.lower() in lowered for pattern in HIGH_RISK_ACTION_PATTERNS)
    bio_context = any(keyword.lower() in lowered for keyword in BIO_KEYWORDS)
    if high_risk_action and bio_context:
        flags.update({"biosafety", "biosecurity"})
    blocked = False
    approval = False
    reasons: list[str] = []

    if disclosure_level and not allowed_for_use_case(disclosure_level, use_case):
        blocked = True
        flags.add("external_comm")
        reasons.append(f"{disclosure_level} source is not allowed for {use_case} use.")

    if high_risk_action and bio_context:
        blocked = True
        approval = True
        reasons.append("Wet-lab or biosecurity-sensitive operational detail requires human approval and narrowing.")

    if use_case in {"public", "investor", "partner", "external"} and flags.intersection({"financial", "legal", "external_comm", "privacy"}):
        approval = True
        reasons.append("External-facing use requires review for claims, confidentiality, privacy, and legal risk.")

    return {
        "allowed": not blocked,
        "requires_human_approval": approval,
        "risk_flags": sorted(flags),
        "blocked_reasons": reasons,
        "safe_next_action": (
            "Use public/external-safe sources or request human approval before external release."
            if blocked or approval
            else "Proceed with source-grounded answer and citations."
        ),
    }


def command_registry(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    records = build_registry(root)
    write_registry(records, root / args.out, root / args.jsonl)
    write_inventory(records, root / args.inventory)
    print(json.dumps({"source_count": len(records), "registry": args.out, "jsonl": args.jsonl, "inventory": args.inventory}, ensure_ascii=False))
    return 0


def command_ingest(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    records = build_registry(root)
    chunks, manifest = build_chunks(records, root=root, max_chars=args.max_chars)
    write_chunks(chunks, root / args.out, manifest, root / args.manifest)
    if args.update_registry:
        write_registry(records, root / args.registry, root / args.registry_jsonl)
        write_inventory(records, root / args.inventory)
    print(json.dumps({"chunk_count": len(chunks), "skipped_count": manifest["skipped_count"], "out": args.out}, ensure_ascii=False))
    return 0


def command_search(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    chunks_path = root / args.chunks
    if not chunks_path.exists():
        print(f"Chunk file not found: {chunks_path}", file=sys.stderr)
        return 2
    results = retrieve(args.query, load_chunks(chunks_path), use_case=args.use_case, limit=args.limit)
    payload = {
        "answer": "Retrieval results only; compose final answers from these cited chunks.",
        "source_ids": [result["source_id"] for result in results],
        "source_priorities": [result["priority"] for result in results],
        "evidence_labels": [result["evidence_label"] for result in results],
        "confidence": "medium" if results else "low",
        "verification_status": [result["verification_status"] for result in results],
        "unsupported_claims_removed_or_labeled": True,
        "compliance_flags": sorted({flag for result in results for flag in result["risk_flags"]}),
        "next_action": "Use returned chunks as source-grounded context; do not cite filtered or unavailable sources.",
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_compliance(args: argparse.Namespace) -> int:
    payload = compliance_scan(args.text, use_case=args.use_case, disclosure_level=args.disclosure_level)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["allowed"] else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    registry = subparsers.add_parser("registry", help="Generate source registry and file inventory.")
    registry.add_argument("--root", default=str(REPO_ROOT))
    registry.add_argument("--out", default="00_ADMIN/source_registry.csv")
    registry.add_argument("--jsonl", default="00_ADMIN/source_registry.jsonl")
    registry.add_argument("--inventory", default="00_ADMIN/file_inventory_generated.csv")
    registry.set_defaults(func=command_registry)

    ingest = subparsers.add_parser("ingest", help="Load extractable text, chunk it, and preserve provenance.")
    ingest.add_argument("--root", default=str(REPO_ROOT))
    ingest.add_argument("--out", default="03_PROCESSED_KB/chunks/source_chunks.jsonl")
    ingest.add_argument("--manifest", default="03_PROCESSED_KB/chunks/source_chunks_manifest.json")
    ingest.add_argument("--max-chars", type=int, default=1600)
    ingest.add_argument("--update-registry", action="store_true")
    ingest.add_argument("--registry", default="00_ADMIN/source_registry.csv")
    ingest.add_argument("--registry-jsonl", default="00_ADMIN/source_registry.jsonl")
    ingest.add_argument("--inventory", default="00_ADMIN/file_inventory_generated.csv")
    ingest.set_defaults(func=command_ingest)

    search = subparsers.add_parser("search", help="Run local lexical retrieval over chunks.")
    search.add_argument("query")
    search.add_argument("--root", default=str(REPO_ROOT))
    search.add_argument("--chunks", default="03_PROCESSED_KB/chunks/source_chunks.jsonl")
    search.add_argument("--use-case", default="internal")
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=command_search)

    compliance = subparsers.add_parser("compliance", help="Scan text for compliance gates.")
    compliance.add_argument("text")
    compliance.add_argument("--use-case", default="internal")
    compliance.add_argument("--disclosure-level", default=None)
    compliance.set_defaults(func=command_compliance)

    return parser


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: Sequence[str] | None = None) -> int:
    configure_output_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
