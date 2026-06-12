from __future__ import annotations

import hashlib
import json
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


def evidence_label_for_priority(priority: str) -> str:
    return EVIDENCE_BY_PRIORITY.get(priority, EVIDENCE_LABELS[-1])


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
    for index, start in enumerate(range(0, len(text), step), start=1):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()
        if not chunk_text:
            continue
        checksum = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
        source = document.source
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
