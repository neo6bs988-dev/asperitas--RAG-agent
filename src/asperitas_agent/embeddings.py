from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from .schemas import Chunk, EmbeddingRecord, SourceRecord


DEFAULT_EMBEDDING_MODEL = "offline-placeholder"
DEFAULT_EMBEDDING_VERSION = "mvp005-phase1-schema"
DEFAULT_OFFLINE_EMBEDDING_MODEL = "offline-deterministic-hash"
DEFAULT_OFFLINE_EMBEDDING_VERSION = "mvp005-phase2-offline"


class EmbeddingProvider(Protocol):
    embedding_model: str
    embedding_dim: int
    embedding_version: str

    def embed_text(self, text: str) -> list[float]:
        ...


@dataclass(frozen=True)
class DeterministicOfflineEmbeddingProvider:
    embedding_dim: int
    embedding_model: str = DEFAULT_OFFLINE_EMBEDDING_MODEL
    embedding_version: str = DEFAULT_OFFLINE_EMBEDDING_VERSION

    def __post_init__(self) -> None:
        if self.embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive")
        if not self.embedding_model.strip():
            raise ValueError("embedding_model must be non-empty")
        if not self.embedding_version.strip():
            raise ValueError("embedding_version must be non-empty")

    def embed_text(self, text: str) -> list[float]:
        seed = "\x00".join([self.embedding_model, self.embedding_version, str(self.embedding_dim), text])
        return [_stable_unit_float(seed, index) for index in range(self.embedding_dim)]


def build_source_file_lookup(records: list[SourceRecord]) -> dict[str, str]:
    return {record.source_id: record.path for record in records}


def build_embedding_record(
    chunk: Chunk,
    source_file: str,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dim: int = 0,
    embedding_version: str = DEFAULT_EMBEDDING_VERSION,
) -> EmbeddingRecord:
    if not source_file:
        raise ValueError("source_file is required to preserve source-grounding metadata")
    if embedding_dim < 0:
        raise ValueError("embedding_dim must be non-negative")
    return EmbeddingRecord(
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
        content_hash=chunk.checksum,
    )


def build_embedding_records(
    chunks: list[Chunk],
    records: list[SourceRecord],
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dim: int = 0,
    embedding_version: str = DEFAULT_EMBEDDING_VERSION,
) -> list[EmbeddingRecord]:
    source_files = build_source_file_lookup(records)
    missing = sorted({chunk.source_id for chunk in chunks if chunk.source_id not in source_files})
    if missing:
        raise ValueError(f"Missing source registry records for source_id: {', '.join(missing)}")
    return [
        build_embedding_record(
            chunk=chunk,
            source_file=source_files[chunk.source_id],
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            embedding_version=embedding_version,
        )
        for chunk in chunks
    ]


def _stable_unit_float(seed: str, index: int) -> float:
    digest = hashlib.sha256(f"{seed}\x00{index}".encode("utf-8")).digest()
    integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return (integer / ((1 << 64) - 1)) * 2.0 - 1.0

