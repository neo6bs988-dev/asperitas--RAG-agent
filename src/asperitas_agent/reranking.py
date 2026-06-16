from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Protocol

from .retrieval_normalization import normalized_token_set


RERANK_SOURCE_GROUNDING_FIELDS = (
    "source_id",
    "source_file",
    "source_priority",
    "evidence_label",
    "section",
    "section_heading",
    "section_path",
    "heading_context",
    "embedding_model",
    "embedding_dim",
    "embedding_version",
    "content_hash",
)
RERANK_TEXT_FIELDS = (
    "title",
    "source_file",
    "section",
    "section_heading",
    "section_path",
    "heading_context",
    "text",
)


class Reranker(Protocol):
    reranker_name: str
    reranker_version: str
    deterministic: bool

    def rerank(
        self,
        query: str,
        candidates: Sequence[Mapping[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        ...


def rerank_candidates(
    query: str,
    candidates: Sequence[Mapping[str, Any]],
    reranker: Reranker | None = None,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    if top_k is not None and top_k < 0:
        raise ValueError("top_k must be non-negative")
    if top_k == 0:
        return []
    if reranker is None:
        rows = _copy_candidate_rows(candidates)
        return rows[:top_k] if top_k is not None else rows

    reranked = reranker.rerank(query=query, candidates=candidates, top_k=top_k)
    assert_rerank_metadata_preserved(candidates, reranked)
    return _copy_candidate_rows(reranked)


@dataclass(frozen=True)
class DeterministicTestReranker:
    reranker_name: str = "deterministic-test-reranker"
    reranker_version: str = "mvp007-phase1"
    deterministic: bool = True

    def rerank(
        self,
        query: str,
        candidates: Sequence[Mapping[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if top_k is not None and top_k < 0:
            raise ValueError("top_k must be non-negative")
        if top_k == 0:
            return []

        query_tokens = normalized_token_set(query)
        scored_rows: list[tuple[float, int, int, dict[str, Any]]] = []
        for input_index, candidate in enumerate(candidates):
            row = deepcopy(dict(candidate))
            reranker_score = _lexical_overlap_score(query_tokens, row)
            row["reranker_metadata"] = {
                **dict(row.get("reranker_metadata") or {}),
                "reranker_name": self.reranker_name,
                "reranker_version": self.reranker_version,
                "deterministic": self.deterministic,
                "input_index": input_index,
                "input_rank": row.get("rank"),
                "reranked_rank": 0,
                "reranker_score": round(reranker_score, 6),
            }
            scored_rows.append((reranker_score, _input_rank_sort_value(row, input_index), input_index, row))

        scored_rows.sort(key=lambda item: (-item[0], item[1], item[2], str(item[3].get("chunk_id") or "")))
        rows = [row for _, _, _, row in scored_rows]
        if top_k is not None:
            rows = rows[:top_k]
        for reranked_rank, row in enumerate(rows, start=1):
            metadata = dict(row.get("reranker_metadata") or {})
            metadata["reranked_rank"] = reranked_rank
            row["reranker_metadata"] = metadata
        assert_rerank_metadata_preserved(candidates, rows)
        return rows


def assert_rerank_metadata_preserved(
    original_candidates: Sequence[Mapping[str, Any]],
    reranked_candidates: Sequence[Mapping[str, Any]],
    required_fields: tuple[str, ...] = RERANK_SOURCE_GROUNDING_FIELDS,
    identity_field: str = "chunk_id",
) -> None:
    original_by_id = _candidate_lookup(original_candidates, identity_field=identity_field)
    for reranked in reranked_candidates:
        candidate_id = reranked.get(identity_field)
        if not candidate_id:
            continue
        original = original_by_id.get(str(candidate_id))
        if original is None:
            raise ValueError(f"reranker returned unknown candidate {identity_field}: {candidate_id}")
        for field_name in required_fields:
            if field_name in original and reranked.get(field_name) != original.get(field_name):
                raise ValueError(f"reranker changed metadata field {field_name} for {candidate_id}")


def _candidate_lookup(candidates: Sequence[Mapping[str, Any]], identity_field: str) -> dict[str, Mapping[str, Any]]:
    lookup: dict[str, Mapping[str, Any]] = {}
    for candidate in candidates:
        candidate_id = candidate.get(identity_field)
        if candidate_id:
            lookup[str(candidate_id)] = candidate
    return lookup


def _copy_candidate_rows(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(dict(candidate)) for candidate in candidates]


def _lexical_overlap_score(query_tokens: set[str], candidate: Mapping[str, Any]) -> float:
    if not query_tokens:
        return 0.0
    candidate_tokens = normalized_token_set(*[_stringify_candidate_value(candidate.get(field_name)) for field_name in RERANK_TEXT_FIELDS])
    if not candidate_tokens:
        return 0.0
    return len(query_tokens & candidate_tokens) / len(query_tokens)


def _stringify_candidate_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_stringify_candidate_value(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return " ".join(_stringify_candidate_value(item) for item in value)
    return str(value)


def _input_rank_sort_value(row: Mapping[str, Any], input_index: int) -> int:
    try:
        return int(row.get("rank") or input_index + 1)
    except (TypeError, ValueError):
        return input_index + 1
