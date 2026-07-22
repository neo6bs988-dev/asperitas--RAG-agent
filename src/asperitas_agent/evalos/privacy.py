from __future__ import annotations

import copy
import hashlib
import hmac
from typing import Any

SENSITIVE = {
    "credential",
    "access_token",
    "api_key",
    "authorization_header",
    "permit_text",
    "contract_text",
    "partner_terms",
    "customer_data",
    "personal_data",
    "unpublished_sequence",
    "unpublished_assay",
    "specimen_location",
    "private_oracle",
    "answer_key",
    "grader_prompt",
}

CONTENT = {
    "gen_ai.input.messages",
    "gen_ai.output.messages",
    "gen_ai.system_instructions",
    "gen_ai.tool.call.arguments",
    "gen_ai.tool.call.result",
    "gen_ai.retrieval.query.text",
}

EXPLICIT_IDENTIFIER_KEYS = {
    "gen_ai.agent.id",
    "gen_ai.conversation.id",
    "gen_ai.data_source.id",
    "gen_ai.tool.call.id",
    "asperitas.eval.case_id",
    "asperitas.eval.trial_id",
    "asperitas.retrieval.document_ids",
}


def _token(value: str, secret: bytes) -> str:
    return (
        "hmac:"
        + hmac.new(
            secret,
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:24]
    )


def _is_identifier_key(normalized_key: str) -> bool:
    return (
        normalized_key in EXPLICIT_IDENTIFIER_KEYS
        or normalized_key.endswith("_id")
        or normalized_key.endswith(".id")
        or normalized_key.endswith("_ids")
        or normalized_key.endswith(".ids")
    )


def _tokenize_identifier_value(
    value: Any,
    *,
    secret: bytes,
    counters: dict[str, int],
) -> Any:
    if isinstance(value, str):
        counters["tokenized_ids"] += 1
        return _token(value, secret)
    if isinstance(value, list):
        output = []
        for item in value:
            if isinstance(item, str):
                counters["tokenized_ids"] += 1
                output.append(_token(item, secret))
            else:
                output.append(item)
        return output
    return value


def _walk(
    value: Any,
    *,
    secret: bytes,
    capture_content: bool,
    counters: dict[str, int],
) -> Any:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            normalized = key.casefold()

            if normalized in SENSITIVE:
                output[key] = "[REDACTED]"
                counters["redacted_fields"] += 1
                continue

            if key in CONTENT and not capture_content:
                output[key] = {
                    "captured": False,
                    "sha256": hashlib.sha256(
                        repr(raw_value).encode("utf-8")
                    ).hexdigest(),
                }
                counters["content_hashes"] += 1
                continue

            if _is_identifier_key(normalized):
                output[key] = _tokenize_identifier_value(
                    raw_value,
                    secret=secret,
                    counters=counters,
                )
                continue

            output[key] = _walk(
                raw_value,
                secret=secret,
                capture_content=capture_content,
                counters=counters,
            )
        return output

    if isinstance(value, list):
        return [
            _walk(
                item,
                secret=secret,
                capture_content=capture_content,
                counters=counters,
            )
            for item in value
        ]

    return value


def sanitize_trace(
    trace: dict[str, Any],
    *,
    secret: bytes,
    capture_content: bool = False,
) -> dict[str, Any]:
    if not secret:
        raise ValueError("secret must not be empty")

    counters = {
        "redacted_fields": 0,
        "content_hashes": 0,
        "tokenized_ids": 0,
    }
    result = _walk(
        copy.deepcopy(trace),
        secret=secret,
        capture_content=capture_content,
        counters=counters,
    )
    result["privacy"] = {
        "capture_content": capture_content,
        **counters,
    }
    return result


def audit_sanitized_trace(
    trace: dict[str, Any],
) -> dict[str, Any]:
    leaks: list[str] = []
    raw_identifiers: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for raw_key, item in value.items():
                key = str(raw_key)
                normalized = key.casefold()
                child_path = f"{path}.{key}"

                if (
                    normalized in SENSITIVE
                    and item != "[REDACTED]"
                ):
                    leaks.append(child_path)

                if _is_identifier_key(normalized):
                    values = item if isinstance(item, list) else [item]
                    for candidate in values:
                        if (
                            isinstance(candidate, str)
                            and not candidate.startswith("hmac:")
                        ):
                            raw_identifiers.append(child_path)

                walk(item, child_path)

        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(trace, "$")
    return {
        "passed": not leaks and not raw_identifiers,
        "leaks": sorted(set(leaks)),
        "raw_identifiers": sorted(set(raw_identifiers)),
        "privacy": dict(trace.get("privacy", {})),
    }
