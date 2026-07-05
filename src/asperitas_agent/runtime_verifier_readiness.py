from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


READINESS_CLASSIFICATIONS = (
    "verified_metadata_present",
    "metadata_only_fallback",
    "not_scored",
    "insufficient_evidence",
    "unsupported_claims_present",
    "verifier_error",
    "human_review_recommended",
)

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

_UNSUPPORTED_STATUS_KEYS = (
    "unsupported",
    "contradicted",
    "citation_missing",
    "citation_mismatch",
    "compliance_blocked",
)

_HUMAN_REVIEW_STATUS_KEYS = (
    "partially_supported",
    "ambiguous",
    "not_verifiable_from_context",
)

_ERROR_SKIPPED_REASONS = {
    "caller_supplied_summary_schema_invalid",
    "runtime_verifier_exception",
}

_INSUFFICIENT_EVIDENCE_SKIPPED_REASONS = {
    "no_runtime_evidence_items",
    "no_valid_runtime_evidence_spans",
}

_NEXT_ACTIONS = {
    "verified_metadata_present": "Use the runtime metadata as a readiness signal only; do not claim production verification.",
    "metadata_only_fallback": "Treat the answer as not runtime-verified and inspect fallback diagnostics before relying on it.",
    "not_scored": "Do not infer readiness from verification metadata; run the opt-in runtime verifier when appropriate.",
    "insufficient_evidence": "Collect valid runtime evidence metadata before interpreting answer verification readiness.",
    "unsupported_claims_present": "Review unsupported or citation-failure claim diagnostics before relying on the answer.",
    "verifier_error": "Inspect verifier error diagnostics and rerun after fixing the metadata or runtime verifier input.",
    "human_review_recommended": "Route the answer verification metadata to human review before relying on the answer.",
}


def interpret_runtime_verifier_readiness(answer_verification: Mapping[str, Any] | None) -> dict[str, Any]:
    """Interpret V1.6A answer-verification metadata without changing runtime behavior."""
    if answer_verification is None:
        return _result("not_scored", ("answer_verification_metadata_missing",))
    if not isinstance(answer_verification, Mapping):
        return _result("not_scored", ("answer_verification_metadata_invalid",))

    metadata = dict(answer_verification)
    reason_codes: list[str] = []
    runtime_diagnostics_present = any(key in metadata for key in RUNTIME_DIAGNOSTIC_KEYS)
    if not runtime_diagnostics_present:
        return _result("not_scored", ("runtime_diagnostics_missing",))

    skipped_reason = _string(metadata.get("runtime_verification_skipped_reason"))
    diagnostics = _string_list(metadata.get("diagnostics"))
    warnings = _string_list(metadata.get("warnings"))
    failure_modes = _string_list(metadata.get("failure_modes"))
    verifier_failure_modes = _string_list(metadata.get("verifier_failure_modes"))
    status_counts = _mapping(metadata.get("status_counts"))
    answer_status = _string(metadata.get("answer_faithfulness_status"))
    total_claims = _non_negative_int(metadata.get("total_claims"))
    verifier_input_count = _non_negative_int(metadata.get("verifier_input_claim_count"))
    verifier_output_count = _non_negative_int(metadata.get("verifier_output_claim_count"))

    if metadata.get("runtime_verifier_error_type") or skipped_reason in _ERROR_SKIPPED_REASONS:
        reason_codes.append("runtime_verifier_error")
        if skipped_reason:
            reason_codes.append(f"runtime_verification_skipped:{skipped_reason}")
        return _result("verifier_error", reason_codes)

    if skipped_reason in _INSUFFICIENT_EVIDENCE_SKIPPED_REASONS or _has_any(
        diagnostics,
        ("no_runtime_evidence_items", "no_valid_runtime_evidence_spans"),
    ):
        reason_codes.append("runtime_evidence_insufficient")
        if skipped_reason:
            reason_codes.append(f"runtime_verification_skipped:{skipped_reason}")
        return _result("insufficient_evidence", reason_codes)

    if metadata.get("metadata_only_fallback_used") is True:
        reason_codes.append("metadata_only_fallback_used")
        if skipped_reason:
            reason_codes.append(f"runtime_verification_skipped:{skipped_reason}")
        return _result("metadata_only_fallback", reason_codes)

    if metadata.get("runtime_verifier_enabled") is not True:
        return _result("not_scored", ("runtime_verifier_not_enabled",))
    if metadata.get("runtime_verification_attempted") is not True:
        reason_codes.append("runtime_verification_not_attempted")
        if skipped_reason:
            reason_codes.append(f"runtime_verification_skipped:{skipped_reason}")
        return _result("not_scored", reason_codes)
    if answer_status == "not_scored" or total_claims == 0 or verifier_output_count == 0:
        reason_codes.append("runtime_verification_not_scored")
        if total_claims == 0:
            reason_codes.append("no_claims_scored")
        if verifier_input_count > 0 and verifier_output_count == 0:
            reason_codes.append("runtime_claims_not_scored")
        return _result("not_scored", reason_codes)

    unsupported_reasons = _positive_status_reasons(status_counts, _UNSUPPORTED_STATUS_KEYS)
    if unsupported_reasons:
        return _result("unsupported_claims_present", unsupported_reasons)

    human_review_reasons = _human_review_reasons(
        metadata=metadata,
        status_counts=status_counts,
        warnings=warnings,
        diagnostics=diagnostics,
        failure_modes=(*failure_modes, *verifier_failure_modes),
        answer_status=answer_status,
    )
    if human_review_reasons:
        return _result("human_review_recommended", human_review_reasons)

    return _result("verified_metadata_present", ("runtime_verification_completed",))


def _result(classification: str, reason_codes: Sequence[str]) -> dict[str, Any]:
    return {
        "readiness_classification": classification,
        "reason_codes": list(dict.fromkeys(str(code) for code in reason_codes if str(code).strip())),
        "recommended_next_action": _NEXT_ACTIONS[classification],
        "production_verification_claim": False,
        "metadata_interpretation_only": True,
    }


def _human_review_reasons(
    *,
    metadata: Mapping[str, Any],
    status_counts: Mapping[str, Any],
    warnings: Sequence[str],
    diagnostics: Sequence[str],
    failure_modes: Sequence[str],
    answer_status: str,
) -> list[str]:
    reasons: list[str] = []
    reasons.extend(_positive_status_reasons(status_counts, _HUMAN_REVIEW_STATUS_KEYS))
    if answer_status == "caution":
        reasons.append("answer_faithfulness_status:caution")
    if _string_list(metadata.get("blocking_failures")):
        reasons.append("blocking_failures_present")
    if _string_list(metadata.get("compliance_tags")):
        reasons.append("compliance_tags_present")
    if _has_any(warnings, ("human_review", "compliance_flag:", "ambiguous", "not_verifiable")):
        reasons.append("warning_signal_present")
    if _has_any(diagnostics, ("span_signal:not_verifiable", "span_signal:numeric_conflict")):
        reasons.append("diagnostic_review_signal_present")
    if _has_any(failure_modes, ("verifier_not_applicable", "source_metadata_missing", "evidence_span_missing")):
        reasons.append("failure_mode_review_signal_present")
    return reasons


def _positive_status_reasons(status_counts: Mapping[str, Any], status_keys: Sequence[str]) -> list[str]:
    reasons: list[str] = []
    for status in status_keys:
        if _non_negative_int(status_counts.get(status)) > 0:
            reasons.append(f"status_count:{status}")
    return reasons


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _string(value: Any) -> str:
    return str(value or "").strip()


def _string_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        raw_values = (value,)
    elif isinstance(value, Sequence):
        raw_values = tuple(str(item) for item in value)
    else:
        raw_values = ()
    return tuple(item for item in (_string(value) for value in raw_values) if item)


def _has_any(values: Sequence[str], needles: Sequence[str]) -> bool:
    normalized_values = tuple(value.casefold() for value in values)
    normalized_needles = tuple(needle.casefold() for needle in needles)
    return any(needle in value for value in normalized_values for needle in normalized_needles)


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value >= 0:
        return value
    return 0
