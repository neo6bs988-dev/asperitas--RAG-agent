from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from .claim_extractor import extract_atomic_claims
from .claim_verification_report_aggregator import aggregate_claim_verification_reports
from .claim_verifier_schema import (
    AnswerVerificationSummary,
    EvidenceSpan,
    SCHEMA_VERSION,
    COMPLIANCE_TRUTH_BOUNDARY_TAGS,
)
from .schemas import EvidenceItem, GroundedAnswer
from .support_status_classifier import classify_answer_claim_support


RUNTIME_VERIFIER_NAME = "v1.6a-runtime-verifier-metadata-hook"
RUNTIME_VERIFIER_VERSION = "V1.6A"
RUNTIME_FALLBACK_DIAGNOSTIC = "metadata_only_runtime_integration_fallback"
RUNTIME_NOT_COMPLETED_WARNING = "runtime_verifier_not_completed"
DEFAULT_RUNTIME_ANSWER_ID = "runtime-answer"

RUNTIME_DIAGNOSTIC_FIELDS = (
    "runtime_verifier_enabled",
    "runtime_verification_attempted",
    "runtime_verification_skipped_reason",
    "metadata_only_fallback_used",
    "verifier_input_claim_count",
    "verifier_output_claim_count",
    "verifier_failure_modes",
    "verifier_schema_version",
)

_ALLOWED_COMPLIANCE_TAGS = set(COMPLIANCE_TRUTH_BOUNDARY_TAGS)


def build_runtime_answer_verification_summary(
    *,
    question: str | None,
    answer: GroundedAnswer | str | object,
    evidence_items: Sequence[EvidenceItem] | Sequence[object] | None,
    answer_id: str | None = None,
    enabled: bool = False,
    caller_supplied_summary: AnswerVerificationSummary | None = None,
) -> AnswerVerificationSummary | None:
    """Build a passive runtime verification summary without changing answer behavior."""
    if not enabled:
        return caller_supplied_summary

    resolved_question = _resolve_question(question, answer)
    resolved_answer_id = _resolve_answer_id(answer_id, answer)

    if caller_supplied_summary is not None:
        try:
            caller_supplied_summary.require_valid()
        except ValueError as exc:
            return _fallback_summary(
                answer_id=resolved_answer_id,
                question=resolved_question,
                skipped_reason="caller_supplied_summary_schema_invalid",
                diagnostics=("caller_supplied_summary_schema_invalid",),
                failure_modes=("verifier_not_applicable",),
                exception=exc,
            )
        return caller_supplied_summary

    answer_text = _answer_text(answer)
    if not answer_text:
        return _fallback_summary(
            answer_id=resolved_answer_id,
            question=resolved_question,
            skipped_reason="missing_answer",
            diagnostics=("missing_answer",),
            failure_modes=("verifier_not_applicable",),
        )

    claims = extract_atomic_claims(answer_text, answer_id=resolved_answer_id)
    if not claims:
        return _fallback_summary(
            answer_id=resolved_answer_id,
            question=resolved_question,
            skipped_reason="no_runtime_claims",
            diagnostics=("no_runtime_claims",),
            verifier_input_claim_count=0,
        )

    spans, span_diagnostics, runtime_evidence_metadata = _evidence_spans(evidence_items)
    if not evidence_items:
        return _fallback_summary(
            answer_id=resolved_answer_id,
            question=resolved_question,
            skipped_reason="no_runtime_evidence_items",
            diagnostics=span_diagnostics or ("no_runtime_evidence_items",),
            claim_ids=tuple(claim.claim_id for claim in claims),
            citation_keys=tuple(key for claim in claims for key in claim.citation_keys),
            verifier_input_claim_count=len(claims),
            runtime_evidence_metadata=runtime_evidence_metadata,
        )
    if not spans:
        return _fallback_summary(
            answer_id=resolved_answer_id,
            question=resolved_question,
            skipped_reason="no_valid_runtime_evidence_spans",
            diagnostics=span_diagnostics or ("no_valid_runtime_evidence_spans",),
            claim_ids=tuple(claim.claim_id for claim in claims),
            citation_keys=tuple(key for claim in claims for key in claim.citation_keys),
            verifier_input_claim_count=len(claims),
            runtime_evidence_metadata=runtime_evidence_metadata,
        )

    try:
        evidence_by_claim_id = {claim.claim_id: spans for claim in claims}
        reports = classify_answer_claim_support(claims, evidence_by_claim_id)
        summary = aggregate_claim_verification_reports(
            reports,
            answer_id=resolved_answer_id,
            question=resolved_question,
        )
        return _with_runtime_metrics(
            summary,
            enabled=True,
            attempted=True,
            skipped_reason="",
            fallback_used=False,
            input_claim_count=len(claims),
            output_claim_count=len(reports),
            diagnostics=span_diagnostics,
            runtime_evidence_metadata=runtime_evidence_metadata,
        )
    except (TypeError, ValueError, AttributeError) as exc:
        return _fallback_summary(
            answer_id=resolved_answer_id,
            question=resolved_question,
            skipped_reason="runtime_verifier_exception",
            diagnostics=("runtime_verifier_exception", *span_diagnostics),
            failure_modes=("verifier_not_applicable",),
            claim_ids=tuple(claim.claim_id for claim in claims),
            citation_keys=tuple(key for claim in claims for key in claim.citation_keys),
            verifier_input_claim_count=len(claims),
            runtime_evidence_metadata=runtime_evidence_metadata,
            exception=exc,
        )


def _resolve_question(question: str | None, answer: GroundedAnswer | str | object) -> str:
    if question and question.strip():
        return question.strip()
    if isinstance(answer, GroundedAnswer) and answer.query.strip():
        return answer.query.strip()
    if isinstance(answer, Mapping):
        value = answer.get("query") or answer.get("question")
        if str(value or "").strip():
            return str(value).strip()
    value = getattr(answer, "query", None) or getattr(answer, "question", None)
    if str(value or "").strip():
        return str(value).strip()
    return "question_not_provided"


def _resolve_answer_id(answer_id: str | None, answer: GroundedAnswer | str | object) -> str:
    if answer_id and answer_id.strip():
        return answer_id.strip()
    if isinstance(answer, Mapping):
        value = answer.get("answer_id") or answer.get("id")
        if str(value or "").strip():
            return str(value).strip()
    value = getattr(answer, "answer_id", None) or getattr(answer, "id", None)
    if str(value or "").strip():
        return str(value).strip()
    return DEFAULT_RUNTIME_ANSWER_ID


def _answer_text(answer: GroundedAnswer | str | object) -> str:
    if isinstance(answer, GroundedAnswer):
        return answer.answer_text.strip()
    if isinstance(answer, str):
        return answer.strip()
    if isinstance(answer, Mapping):
        for key in ("answer_text", "answer", "text"):
            value = answer.get(key)
            if str(value or "").strip():
                return str(value).strip()
        return ""
    for key in ("answer_text", "answer", "text"):
        value = getattr(answer, key, None)
        if str(value or "").strip():
            return str(value).strip()
    return ""


def _evidence_spans(
    evidence_items: Sequence[EvidenceItem] | Sequence[object] | None,
) -> tuple[tuple[EvidenceSpan, ...], tuple[str, ...], tuple[dict[str, Any], ...]]:
    if not evidence_items:
        return (), ("no_runtime_evidence_items",), ()

    spans: list[EvidenceSpan] = []
    diagnostics: list[str] = []
    metadata_rows: list[dict[str, Any]] = []
    for index, item in enumerate(evidence_items, start=1):
        payload = _evidence_payload(item)
        metadata_rows.append(_runtime_evidence_metadata(payload, index))
        span = _span_from_payload(payload, index)
        if span is None:
            diagnostics.append(f"runtime_evidence_span_invalid:{index}")
            continue
        errors = span.validate()
        if errors:
            diagnostics.append(f"runtime_evidence_span_invalid:{index}")
            continue
        spans.append(span)
    if not spans:
        diagnostics.append("no_valid_runtime_evidence_spans")
    return tuple(spans), tuple(dict.fromkeys(diagnostics)), tuple(metadata_rows)


def _evidence_payload(item: EvidenceItem | object) -> dict[str, Any]:
    if isinstance(item, EvidenceItem):
        return item.to_json()
    if isinstance(item, Mapping):
        return dict(item)
    if hasattr(item, "to_json"):
        payload = item.to_json()
        if isinstance(payload, Mapping):
            return dict(payload)
    return {
        key: getattr(item, key)
        for key in (
            "rank",
            "chunk_id",
            "source_id",
            "source_title",
            "source_path",
            "source_priority",
            "evidence_label",
            "section",
            "section_heading",
            "section_path",
            "section_level",
            "parent_section",
            "subsection",
            "text_excerpt",
            "citation_key",
            "score",
            "compliance_tags",
        )
        if hasattr(item, key)
    }


def _span_from_payload(payload: Mapping[str, Any], index: int) -> EvidenceSpan | None:
    source_id = str(payload.get("source_id") or "").strip()
    text_excerpt = str(payload.get("text_excerpt") or payload.get("evidence_text_hash_or_excerpt") or "").strip()
    if not source_id or not text_excerpt:
        return None

    citation_key = str(payload.get("citation_key") or f"[E{index}]").strip()
    span_id = str(payload.get("span_id") or payload.get("chunk_id") or f"runtime-span-{index}").strip()
    section_path_value = payload.get("section_path", ())
    if isinstance(section_path_value, (list, tuple)):
        section_path = tuple(str(item) for item in section_path_value if str(item).strip())
    elif section_path_value:
        section_path = (str(section_path_value),)
    else:
        section_path = ()

    metadata = _runtime_evidence_metadata(payload, index)
    if not payload.get("chunk_id"):
        metadata["runtime_generated_span_id"] = True

    return EvidenceSpan(
        source_id=source_id,
        span_id=span_id,
        document_title=str(payload.get("source_title") or payload.get("title") or ""),
        section=str(payload.get("section") or ""),
        locator=str(payload.get("locator") or payload.get("chunk_id") or citation_key),
        evidence_text_hash_or_excerpt=text_excerpt,
        metadata=metadata,
        compliance_tags=_safe_compliance_tags(payload.get("compliance_tags", ())),
        retrieval_rank=_positive_int(payload.get("rank")),
        retrieval_score=_non_negative_float(payload.get("score")),
        citation_key=citation_key,
        chunk_id=str(payload.get("chunk_id") or ""),
        source_path=str(payload.get("source_path") or ""),
        section_heading=str(payload.get("section_heading") or ""),
        section_path=section_path,
    )


def _runtime_evidence_metadata(payload: Mapping[str, Any], index: int) -> dict[str, Any]:
    return {
        "runtime_evidence_index": index,
        "citation_key": str(payload.get("citation_key") or f"[E{index}]"),
        "chunk_id": str(payload.get("chunk_id") or ""),
        "source_id": str(payload.get("source_id") or ""),
        "source_title": str(payload.get("source_title") or payload.get("title") or ""),
        "source_path": str(payload.get("source_path") or ""),
        "source_priority": str(payload.get("source_priority") or ""),
        "evidence_label": str(payload.get("evidence_label") or ""),
        "section": str(payload.get("section") or ""),
        "section_heading": str(payload.get("section_heading") or ""),
        "section_path": _json_list(payload.get("section_path", ())),
    }


def _safe_compliance_tags(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        raw_values = (value,)
    elif isinstance(value, Sequence):
        raw_values = tuple(str(item) for item in value)
    else:
        raw_values = ()
    return tuple(dict.fromkeys(tag for tag in raw_values if tag in _ALLOWED_COMPLIANCE_TAGS))


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 1:
        return value
    return None


def _non_negative_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    return None


def _json_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    if str(value or "").strip():
        return [str(value).strip()]
    return []


def _fallback_summary(
    *,
    answer_id: str,
    question: str,
    skipped_reason: str,
    diagnostics: Sequence[str],
    failure_modes: Sequence[str] = (),
    claim_ids: Sequence[str] = (),
    citation_keys: Sequence[str] = (),
    verifier_input_claim_count: int = 0,
    runtime_evidence_metadata: Sequence[dict[str, Any]] = (),
    exception: Exception | None = None,
) -> AnswerVerificationSummary:
    metrics = _runtime_metrics(
        enabled=True,
        attempted=True,
        skipped_reason=skipped_reason,
        fallback_used=True,
        input_claim_count=verifier_input_claim_count,
        output_claim_count=0,
        failure_modes=failure_modes,
        diagnostics=(RUNTIME_FALLBACK_DIAGNOSTIC, *diagnostics),
        claim_ids=claim_ids,
        citation_keys=citation_keys,
        runtime_evidence_metadata=runtime_evidence_metadata,
    )
    if exception is not None:
        metrics["runtime_verifier_error_type"] = type(exception).__name__
    summary = AnswerVerificationSummary(
        answer_id=answer_id or DEFAULT_RUNTIME_ANSWER_ID,
        question=question or "question_not_provided",
        total_claims=0,
        supported_claims=0,
        partially_supported_claims=0,
        unsupported_claims=0,
        contradicted_claims=0,
        citation_missing_claims=0,
        citation_mismatch_claims=0,
        compliance_blocked_claims=0,
        ambiguous_claims=0,
        not_verifiable_from_context_claims=0,
        answer_faithfulness_status="not_scored",
        blocking_failures=(),
        warnings=(RUNTIME_NOT_COMPLETED_WARNING, f"runtime_verifier_skipped:{skipped_reason}"),
        metrics=metrics,
    )
    summary.require_valid()
    return summary


def _with_runtime_metrics(
    summary: AnswerVerificationSummary,
    *,
    enabled: bool,
    attempted: bool,
    skipped_reason: str,
    fallback_used: bool,
    input_claim_count: int,
    output_claim_count: int,
    diagnostics: Sequence[str],
    runtime_evidence_metadata: Sequence[dict[str, Any]],
) -> AnswerVerificationSummary:
    existing_metrics = dict(summary.metrics)
    existing_diagnostics = tuple(str(item) for item in existing_metrics.get("diagnostics", ()) if str(item).strip())
    merged_diagnostics = tuple(dict.fromkeys((*existing_diagnostics, "runtime_verification_completed", *diagnostics)))
    metrics = {
        **existing_metrics,
        **_runtime_metrics(
            enabled=enabled,
            attempted=attempted,
            skipped_reason=skipped_reason,
            fallback_used=fallback_used,
            input_claim_count=input_claim_count,
            output_claim_count=output_claim_count,
            failure_modes=existing_metrics.get("failure_modes", ()),
            diagnostics=merged_diagnostics,
            claim_ids=existing_metrics.get("claim_ids", ()),
            citation_keys=existing_metrics.get("citation_keys", ()),
            evidence_span_ids=existing_metrics.get("evidence_span_ids", ()),
            source_ids=existing_metrics.get("source_ids", ()),
            compliance_tags=existing_metrics.get("compliance_tags", ()),
            runtime_evidence_metadata=runtime_evidence_metadata,
        ),
    }
    enriched = replace(summary, metrics=metrics)
    enriched.require_valid()
    return enriched


def _runtime_metrics(
    *,
    enabled: bool,
    attempted: bool,
    skipped_reason: str,
    fallback_used: bool,
    input_claim_count: int,
    output_claim_count: int,
    failure_modes: Sequence[str],
    diagnostics: Sequence[str],
    claim_ids: Sequence[str] = (),
    citation_keys: Sequence[str] = (),
    evidence_span_ids: Sequence[str] = (),
    source_ids: Sequence[str] = (),
    compliance_tags: Sequence[str] = (),
    runtime_evidence_metadata: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    normalized_failure_modes = _sorted_unique(failure_modes)
    return {
        "runtime_verifier_name": RUNTIME_VERIFIER_NAME,
        "runtime_verifier_version": RUNTIME_VERIFIER_VERSION,
        "runtime_verifier_enabled": enabled,
        "runtime_verification_attempted": attempted,
        "runtime_verification_skipped_reason": skipped_reason,
        "metadata_only_fallback_used": fallback_used,
        "verifier_input_claim_count": input_claim_count,
        "verifier_output_claim_count": output_claim_count,
        "verifier_failure_modes": list(normalized_failure_modes),
        "verifier_schema_version": SCHEMA_VERSION,
        "claim_ids": list(_sorted_unique(claim_ids)),
        "citation_keys": list(_sorted_unique(citation_keys)),
        "evidence_span_ids": list(_sorted_unique(evidence_span_ids)),
        "source_ids": list(_sorted_unique(source_ids)),
        "failure_modes": list(normalized_failure_modes),
        "compliance_tags": list(_sorted_unique(compliance_tags)),
        "diagnostics": list(_sorted_unique(diagnostics)),
        "runtime_evidence_metadata": [_json_safe_dict(row) for row in runtime_evidence_metadata],
    }


def _sorted_unique(values: Sequence[str] | Any) -> tuple[str, ...]:
    if isinstance(values, str):
        raw_values = (values,)
    elif isinstance(values, Sequence):
        raw_values = tuple(str(value) for value in values)
    else:
        raw_values = ()
    return tuple(sorted(dict.fromkeys(value for value in raw_values if value.strip())))


def _json_safe_dict(row: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _json_safe(value) for key, value in sorted(row.items(), key=lambda item: str(item[0]))}


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return _json_safe_dict(value)
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)
