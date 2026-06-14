from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from .schemas import Chunk


@dataclass
class EmbeddingRecord:
    chunk_id: str
    source_id: str
    source_file: str
    source_priority: str
    evidence_label: str
    section: str
    section_heading: str
    section_path: list[str]
    heading_context: str
    embedding_model: str
    embedding_dim: int
    embedding_version: str
    content_hash: str

    @classmethod
    def from_chunk(
        cls,
        chunk: Chunk,
        source_file: str,
        embedding_model: str,
        embedding_dim: int,
        embedding_version: str,
    ) -> "EmbeddingRecord":
        embedding_model = embedding_model.strip()
        embedding_version = embedding_version.strip()
        if not source_file.strip():
            raise ValueError("source_file is required")
        if not embedding_model:
            raise ValueError("embedding_model must be non-empty")
        if embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive")
        if not embedding_version:
            raise ValueError("embedding_version must be non-empty")
        return cls(
            chunk_id=chunk.chunk_id,
            source_id=chunk.source_id,
            source_file=source_file,
            source_priority=chunk.source_priority,
            evidence_label=chunk.evidence_label,
            section=chunk.section,
            section_heading=chunk.section_heading,
            section_path=list(chunk.section_path),
            heading_context=chunk.heading_context,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            embedding_version=embedding_version,
            content_hash=content_hash_for_text(chunk.text),
        )

    def to_json(self) -> dict[str, object]:
        return asdict(self)


def content_hash_for_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

