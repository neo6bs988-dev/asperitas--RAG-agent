from __future__ import annotations

import hashlib
import json
import re
import string
import unicodedata
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

from .compliance import detect_risk_tags
from .inventory import repo_root
from .loaders import normalize_text
from .schemas import Chunk, EVIDENCE_LABELS, LoadedDocument


EVIDENCE_BY_PRIORITY = {
    "P0": "Document-Supported Fact",
    "P1": "Document-Supported Fact",
    "P2": "Official Source",
    "P3": "Peer-Reviewed Evidence",
    "P4": "Regulatory Source",
    "P5": "Industry Signal",
    "P6": "Inference",
}

ENGLISH_SECTION_HEADINGS = {
    "abstract",
    "introduction",
    "background",
    "methods",
    "method",
    "materials and methods",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "references",
}

KOREAN_SECTION_HEADINGS = {
    "개요",
    "배경",
    "방법",
    "결과",
    "논의",
    "결론",
    "참고문헌",
    "목적",
    "실험 방법",
    "실험 결과",
    "요약",
    # Mojibake variants found in some extracted Korean PDFs.
    "媛쒖슂",
    "諛곌꼍",
    "諛⑸쾿",
    "寃곌낵",
    "?쇱쓽",
    "寃곕줎",
    "李멸퀬臾명뿄",
    "紐⑹쟻",
    "?ㅽ뿕 諛⑸쾿",
    "?ㅽ뿕 寃곌낵",
    "?붿빟",
}

_MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_NUMBERED_HEADING_RE = re.compile(r"^\s*((?:\d+\.){0,4}\d+)[.)]?\s+(.{2,160})\s*$")
_DECORATION_RE = re.compile(r"^[\s\-=_*#]{3,}$")
_MULTISPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class SectionMarker:
    start: int
    heading: str
    level: int
    path: tuple[str, ...]


def evidence_label_for_priority(priority: str) -> str:
    return EVIDENCE_BY_PRIORITY.get(priority, EVIDENCE_LABELS[-1])


def normalize_section_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").casefold()
    normalized = re.sub(r"^\s*(?:section|chapter|part)\s+", "", normalized)
    normalized = re.sub(r"^\s*\d+(?:\.\d+)*[.)]?\s+", "", normalized)
    translation = str.maketrans({char: " " for char in string.punctuation})
    normalized = normalized.translate(translation)
    normalized = _MULTISPACE_RE.sub(" ", normalized).strip()
    return normalized


def _strip_heading_tail(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+\.{2,}\s*\d+\s*$", "", value)
    value = re.sub(r"\s+\d+\s*/\s*\d+\s*$", "", value)
    return value.strip(" \t-:：")


def _looks_like_heading_text(value: str) -> bool:
    stripped = _strip_heading_tail(value)
    if not stripped or _DECORATION_RE.match(stripped):
        return False
    if len(stripped) > 160:
        return False
    if stripped.endswith((".", ",", ";")):
        return False
    return True


def detect_section_heading(line: str) -> tuple[str, int] | None:
    stripped = line.strip()
    if not _looks_like_heading_text(stripped):
        return None

    markdown = _MARKDOWN_HEADING_RE.match(stripped)
    if markdown:
        heading = _strip_heading_tail(markdown.group(2))
        return (heading, len(markdown.group(1))) if _looks_like_heading_text(heading) else None

    numbered = _NUMBERED_HEADING_RE.match(stripped)
    if numbered:
        number, heading = numbered.groups()
        heading = _strip_heading_tail(heading)
        level = max(number.count(".") + 1, 1)
        return (heading, min(level, 6)) if _looks_like_heading_text(heading) else None

    normalized = normalize_section_text(stripped)
    english = {normalize_section_text(item) for item in ENGLISH_SECTION_HEADINGS}
    korean = {normalize_section_text(item) for item in KOREAN_SECTION_HEADINGS}
    if normalized in english or normalized in korean:
        return _strip_heading_tail(stripped), 1
    for prefix in ("chapter", "part", "section"):
        if normalized.startswith(prefix + " ") and len(normalized.split()) <= 12:
            return _strip_heading_tail(stripped), 1
    return None


def extract_section_markers(text: str) -> list[SectionMarker]:
    markers: list[SectionMarker] = []
    stack: list[tuple[int, str]] = []
    offset = 0
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        detected = detect_section_heading(line)
        if detected:
            heading, level = detected
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, heading))
            markers.append(SectionMarker(start=offset, heading=heading, level=level, path=tuple(item[1] for item in stack)))
        offset += len(raw_line)
    return markers


def _marker_for_chunk(markers: list[SectionMarker], start: int, end: int) -> SectionMarker | None:
    if not markers:
        return None
    starts = [marker.start for marker in markers]
    index = bisect_right(starts, start) - 1
    if index >= 0:
        return markers[index]
    for marker in markers:
        if start <= marker.start < end:
            return marker
    return None


def _section_metadata(marker: SectionMarker | None) -> dict[str, object]:
    if marker is None:
        return {
            "section": "",
            "section_heading": "",
            "section_path": [],
            "section_level": None,
            "parent_section": "",
            "subsection": "",
            "heading_context": "",
        }
    section_path = list(marker.path)
    return {
        "section": marker.heading,
        "section_heading": marker.heading,
        "section_path": section_path,
        "section_level": marker.level,
        "parent_section": section_path[-2] if len(section_path) >= 2 else "",
        "subsection": marker.heading if marker.level > 1 else "",
        "heading_context": " > ".join(section_path),
    }


def chunk_document(document: LoadedDocument, chunk_size: int = 1000, overlap: int = 125) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    text = normalize_text(document.text)
    if document.parse_status != "parsed" or not text:
        return []
    chunks: list[Chunk] = []
    step = max(chunk_size - overlap, 1)
    namespace = hashlib.sha256(document.source.path.encode("utf-8")).hexdigest()[:8].upper()
    section_markers = extract_section_markers(text)
    for index, start in enumerate(range(0, len(text), step), start=1):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()
        if not chunk_text:
            continue
        checksum = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
        source = document.source
        section_metadata = _section_metadata(_marker_for_chunk(section_markers, start, end))
        chunks.append(
            Chunk(
                chunk_id=f"{source.source_id}::{namespace}::chunk-{index:04d}",
                source_id=source.source_id,
                title=source.title,
                text=chunk_text,
                page_start=None,
                page_end=None,
                char_start=start,
                char_end=end,
                source_priority=source.source_priority,
                source_type=source.source_type,
                disclosure_level=source.disclosure_level,
                evidence_label=evidence_label_for_priority(source.source_priority),
                verification_status=source.verification_status,
                risk_tags=detect_risk_tags(chunk_text + " " + source.title),
                checksum=checksum,
                **section_metadata,
            )
        )
        if end == len(text):
            break
    return chunks


def write_chunks(chunks: list[Chunk], root: Path | None = None, path: Path | None = None) -> Path:
    root = repo_root(root)
    output = path or root / "data" / "chunks.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk.to_json(), ensure_ascii=False, sort_keys=True) + "\n")
    return output


def read_chunks(path: Path) -> list[Chunk]:
    if not path.exists():
        return []
    chunks: list[Chunk] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            chunks.append(Chunk(**json.loads(line)))
    return chunks
