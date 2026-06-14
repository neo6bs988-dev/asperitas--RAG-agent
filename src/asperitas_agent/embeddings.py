from __future__ import annotations

import hashlib
import math
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


class VectorStore(Protocol):
    embedding_dim: int

    def add(self, record: EmbeddingRecord, vector: list[float]) -> None:
        ...

    def search(self, query_vector: list[float], top_k: int = 5) -> list["VectorSearchResult"]:
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


@dataclass(frozen=True)
class VectorSearchResult:
    record: EmbeddingRecord
    score: float

    def to_json(self) -> dict[str, object]:
        payload = self.record.to_json()
        payload["score"] = round(self.score, 6)
        return payload


@dataclass(frozen=True)
class _VectorEntry:
    record: EmbeddingRecord
    vector: tuple[float, ...]
    insertion_index: int


class InMemoryVectorStore:
    def __init__(self, embedding_dim: int) -> None:
        if embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive")
        self.embedding_dim = embedding_dim
        self._entries: list[_VectorEntry] = []

    def __len__(self) -> int:
        return len(self._entries)

    def add(self, record: EmbeddingRecord, vector: list[float]) -> None:
        self._validate_record(record)
        vector_tuple = self._validate_vector(vector, label="vector")
        self._entries.append(
            _VectorEntry(
                record=_copy_embedding_record(record),
                vector=vector_tuple,
                insertion_index=len(self._entries),
            )
        )

    def search(self, query_vector: list[float], top_k: int = 5) -> list[VectorSearchResult]:
        query_tuple = self._validate_vector(query_vector, label="query_vector")
        if top_k <= 0 or not self._entries:
            return []
        ranked = [
            (
                VectorSearchResult(record=entry.record, score=_cosine_similarity(query_tuple, entry.vector)),
                entry.insertion_index,
            )
            for entry in self._entries
        ]
        ranked.sort(key=lambda item: (-item[0].score, item[1]))
        return [result for result, _ in ranked[:top_k]]

    def _validate_record(self, record: EmbeddingRecord) -> None:
        if record.embedding_dim != self.embedding_dim:
            raise ValueError("record embedding_dim does not match vector store dimension")

    def _validate_vector(self, vector: list[float], label: str) -> tuple[float, ...]:
        if len(vector) != self.embedding_dim:
            raise ValueError(f"{label} dimension does not match vector store dimension")
        return tuple(float(value) for value in vector)


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


def _cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return dot_product / (left_norm * right_norm)


def _copy_embedding_record(record: EmbeddingRecord) -> EmbeddingRecord:
    return EmbeddingRecord(
        chunk_id=record.chunk_id,
        source_id=record.source_id,
        source_file=record.source_file,
        source_priority=record.source_priority,
        evidence_label=record.evidence_label,
        section=record.section,
        section_heading=record.section_heading,
        section_path=list(record.section_path),
        heading_context=record.heading_context,
        embedding_model=record.embedding_model,
        embedding_dim=record.embedding_dim,
        embedding_version=record.embedding_version,
        content_hash=record.content_hash,
    )

