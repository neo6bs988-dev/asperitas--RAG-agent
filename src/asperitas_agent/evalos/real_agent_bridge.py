from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
from time import perf_counter_ns
from typing import Any, Callable


def _normalizable(value: Any) -> Any:
    if hasattr(value, "to_json") and callable(value.to_json):
        return _normalizable(value.to_json())
    if is_dataclass(value):
        return _normalizable(asdict(value))
    if isinstance(value, dict):
        return {
            str(key): _normalizable(raw)
            for key, raw in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalizable(item) for item in value]
    if isinstance(value, set):
        return sorted(_normalizable(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        _normalizable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def response_payload(value: Any) -> dict[str, Any]:
    normalized = _normalizable(value)
    if not isinstance(normalized, dict):
        raise TypeError("agent response must normalize to a dictionary")
    required = {
        "query",
        "top_k",
        "status",
        "answer",
        "citations_used",
        "evidence_count",
        "evidence",
        "guardrail",
        "metadata",
    }
    missing = sorted(required - set(normalized))
    if missing:
        raise ValueError(
            "agent response missing fields: " + ",".join(missing)
        )
    return normalized


def invoke_no_effect_agent(
    ask_agent_callable: Callable[..., Any],
    *,
    query: str,
    top_k: int,
    records: list[Any],
    chunks: list[Any],
    call_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    kwargs = dict(call_kwargs or {})
    records_before = canonical_sha256(records)
    chunks_before = canonical_sha256(chunks)

    started_ns = perf_counter_ns()
    raw_response = ask_agent_callable(
        query,
        top_k=top_k,
        records=records,
        chunks=chunks,
        **kwargs,
    )
    ended_ns = perf_counter_ns()

    records_after = canonical_sha256(records)
    chunks_after = canonical_sha256(chunks)
    response = response_payload(raw_response)

    return {
        "response": response,
        "latency_ms": (ended_ns - started_ns) / 1_000_000,
        "input_mutation": {
            "records_mutated": records_before != records_after,
            "chunks_mutated": chunks_before != chunks_after,
            "records_before_sha256": records_before,
            "records_after_sha256": records_after,
            "chunks_before_sha256": chunks_before,
            "chunks_after_sha256": chunks_after,
        },
        "external_effect_count": 0,
        "network_egress_count": 0,
        "provider_export_count": 0,
    }
