from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .claim_verifier_schema import AnswerVerificationSummary
from .schemas import GroundedAnswer


INTEGRATION_NAME = "v1.5d-answer-verification-metadata-integration"
INTEGRATION_VERSION = "V1.5D"
ANSWER_VERIFICATION_METADATA_KEY = "answer_verification"
RUNTIME_DIAGNOSTIC_KEYS = (
    "runtime_verifier_enabled",
    "runtime_verification_attempted",
    "runtime_verification_skipped_reason",
    "metadata_only_fallback_used",
    "verifier_input_claim_count",
    "verifier_output_claim_count",
    "verifier_failure_modes",
    "verifier_schema_version",
    "runtime_evidence_metadata",
)


def build_answer_verification_metadata(summary: AnswerVerificationSummary) -> dict[str, Any]:
    """Return deterministic answer-level verification metadata from an aggregate summary."""
    summary.require_valid()
    summary_payload = summary.to_dict()
    metrics = dict(summary_payload.get("metrics") or {})
    payload = {
        "integration_name": INTEGRATION_NAME,
        "integration_version": INTEGRATION_VERSION,
        "deterministic": True,
        "summary_schema_version": summary.schema_version,
        "answer_id": summary.answer_id,
        "answer_faithfulness_status": summary.answer_faithfulness_status,
        "total_claims": summary.total_claims,
        "status_counts": metrics.get("status_counts", {}),
        "blocking_failures": list(summary.blocking_failures),
        "warnings": list(summary.warnings),
        "claim_ids": metrics.get("claim_ids", []),
        "citation_keys": metrics.get("citation_keys", []),
        "evidence_span_ids": metrics.get("evidence_span_ids", []),
        "source_ids": metrics.get("source_ids", []),
        "failure_modes": metrics.get("failure_modes", []),
        "compliance_tags": metrics.get("compliance_tags", []),
        "diagnostics": metrics.get("diagnostics", []),
        "claim_details": metrics.get("claim_details", []),
        "summary": summary_payload,
    }
    for key in RUNTIME_DIAGNOSTIC_KEYS:
        if key in metrics:
            payload[key] = metrics[key]
    return _json_safe(payload)


def expose_answer_verification_metadata(
    answer: GroundedAnswer | Mapping[str, Any],
    summary: AnswerVerificationSummary,
    *,
    metadata_key: str = ANSWER_VERIFICATION_METADATA_KEY,
) -> dict[str, Any]:
    """Copy an answer payload and expose verification under its existing metadata hook."""
    if not metadata_key.strip():
        raise ValueError("metadata_key must not be empty")

    payload = _answer_payload(answer)
    existing_metadata = payload.get("metadata", {})
    metadata = dict(existing_metadata) if isinstance(existing_metadata, Mapping) else {}
    metadata[metadata_key] = build_answer_verification_metadata(summary)
    payload["metadata"] = metadata
    return _json_safe(payload)


def _answer_payload(answer: GroundedAnswer | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(answer, GroundedAnswer):
        return answer.to_json()
    if isinstance(answer, Mapping):
        return _json_safe(dict(answer))
    raise TypeError("answer must be a GroundedAnswer or mapping payload")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)
