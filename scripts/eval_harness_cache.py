from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Callable, TypeVar

from asperitas_agent.chunking import read_chunks
from asperitas_agent.evidence_pack import EvidencePack, build_evidence_pack
from asperitas_agent.registry import read_registry
from asperitas_agent.schemas import Chunk, SourceRecord


T = TypeVar("T")

_FILE_CACHE: dict[tuple[str, int, int, int], Any] = {}
_EVIDENCE_PACK_CACHE: dict[tuple[Any, ...], EvidencePack] = {}
_STATS: dict[str, int] = {
    "file_cache_hits": 0,
    "file_cache_misses": 0,
    "evidence_pack_cache_hits": 0,
    "evidence_pack_cache_misses": 0,
}


def cache_enabled() -> bool:
    return os.environ.get("ASPERITAS_EVAL_CACHE", "1").strip().casefold() not in {"0", "false", "no", "off"}


def clear_eval_harness_cache() -> None:
    _FILE_CACHE.clear()
    _EVIDENCE_PACK_CACHE.clear()
    for key in _STATS:
        _STATS[key] = 0


def cache_stats() -> dict[str, int]:
    return dict(_STATS)


def file_cache_key(path: Path) -> tuple[str, int, int, int]:
    resolved = path.resolve()
    stat = resolved.stat()
    return str(resolved), stat.st_mtime_ns, stat.st_size, stat.st_ctime_ns


def _copy_cached(value: T) -> T:
    return copy.deepcopy(value)


def cached_file_load(path: Path, loader: Callable[[Path], T]) -> T:
    if not cache_enabled():
        return loader(path)
    key = file_cache_key(path)
    if key in _FILE_CACHE:
        _STATS["file_cache_hits"] += 1
        return _copy_cached(_FILE_CACHE[key])
    _STATS["file_cache_misses"] += 1
    value = loader(path)
    _FILE_CACHE[key] = _copy_cached(value)
    return value


def read_registry_cached(path: Path) -> list[SourceRecord]:
    return cached_file_load(path, read_registry)


def read_chunks_cached(path: Path) -> list[Chunk]:
    return cached_file_load(path, read_chunks)


def load_jsonl_cached(path: Path) -> list[dict[str, Any]]:
    def load(path_to_read: Path) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with path_to_read.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    payload = json.loads(line)
                    if isinstance(payload, dict):
                        rows.append(payload)
                    else:
                        rows.append({"__non_object__": payload})
        return rows

    return cached_file_load(path, load)


def _result_fingerprint(result: Any) -> tuple[Any, ...]:
    if isinstance(result, dict):
        payload = result
    elif hasattr(result, "to_json"):
        payload = result.to_json()
    else:
        payload = getattr(result, "chunk", result)
    if isinstance(payload, dict):
        return (
            payload.get("chunk_id"),
            payload.get("source_id"),
            payload.get("source_file") or payload.get("source_path"),
            payload.get("score"),
            payload.get("text"),
        )
    return (repr(payload),)


def build_evidence_pack_cached(query: str, retrieval_results: Any, **kwargs: Any) -> EvidencePack:
    results = list(retrieval_results)
    if not cache_enabled():
        return build_evidence_pack(query, results, **kwargs)
    key = (
        query,
        kwargs.get("top_k", 5),
        kwargs.get("retriever_name"),
        kwargs.get("retriever_version"),
        kwargs.get("snippet_chars"),
        tuple(_result_fingerprint(result) for result in results),
    )
    if key in _EVIDENCE_PACK_CACHE:
        _STATS["evidence_pack_cache_hits"] += 1
        return _copy_cached(_EVIDENCE_PACK_CACHE[key])
    _STATS["evidence_pack_cache_misses"] += 1
    pack = build_evidence_pack(query, results, **kwargs)
    _EVIDENCE_PACK_CACHE[key] = _copy_cached(pack)
    return pack
