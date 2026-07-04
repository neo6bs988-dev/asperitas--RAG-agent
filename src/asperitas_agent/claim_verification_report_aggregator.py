from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .claim_verifier_schema import AnswerVerificationSummary, ClaimVerificationReport


AGGREGATOR_NAME = "v1.5c-deterministic-claim-verification-report-aggregator"
AGGREGATOR_VERSION = "V1.5C-step5"

_COUNTED_STATUSES = (
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "citation_missing",
    "citation_mismatch",
    "ambiguous",
    "not_verifiable_from_context",
    "compliance_blocked",
)

_STATUS_COUNT_FIELDS = {
    "supported": "supported_claims",
    "partially_supported": "partially_supported_claims",
    "unsupported": "unsupported_claims",
    "contradicted": "contradicted_claims",
    "citation_missing": "citation_missing_claims",
    "citation_mismatch": "citation_mismatch_claims",
    "ambiguous": "ambiguous_claims",
    "not_verifiable_from_context": "not_verifiable_from_context_claims",
    "compliance_blocked": "compliance_blocked_claims",
}

_WARNING_STATUSES = {
    "partially_supported",
    "unsupported",
    "citation_missing",
    "citation_mismatch",
    "ambiguous",
    "not_verifiable_from_context",
    "compliance_blocked",
}


@dataclass(frozen=True)
class ClaimVerificationReportAggregationConfig:
    answer_id: str = ""
    question: str = ""
    include_report_metadata: bool = True


def aggregate_claim_verification_reports(
    reports: Sequence[ClaimVerificationReport],
    *,
    answer_id: str | None = None,
    question: str | None = None,
    config: ClaimVerificationReportAggregationConfig | None = None,
) -> AnswerVerificationSummary:
    active_config = config or ClaimVerificationReportAggregationConfig()
    resolved_answer_id = answer_id or active_config.answer_id or _infer_answer_id(reports)
    resolved_question = question or active_config.question or "question_not_provided"
    counts = {status: 0 for status in _COUNTED_STATUSES}
    claim_details: list[dict[str, Any]] = []
    blocking_failures: list[str] = []
    warnings: list[str] = []
    aggregate_failure_modes: list[str] = []
    aggregate_compliance_tags: list[str] = []
    aggregate_citation_keys: list[str] = []
    aggregate_claim_ids: list[str] = []
    aggregate_span_ids: list[str] = []
    aggregate_source_ids: list[str] = []
    aggregate_diagnostics: list[str] = []

    if not reports:
        counts["not_verifiable_from_context"] = 0
        warnings.append("not_verifiable_from_context:no_claims")

    for index, report in enumerate(reports):
        report.require_valid()
        claim = report.claim
        status = report.support_status
        if status in counts:
            counts[status] += 1

        citation_keys = list(claim.citation_keys)
        span_ids = _unique_preserve_order((*claim.cited_span_ids, *(span.span_id for span in report.candidate_evidence_spans)))
        source_ids = _unique_preserve_order((*claim.cited_source_ids, *(span.source_id for span in report.candidate_evidence_spans)))
        compliance_tags = list(claim.compliance_tags)
        failure_mode = report.failure_mode or claim.failure_mode
        report_diagnostics = _report_diagnostics(report)

        aggregate_claim_ids.append(claim.claim_id)
        aggregate_citation_keys.extend(citation_keys)
        aggregate_span_ids.extend(span_ids)
        aggregate_source_ids.extend(source_ids)
        aggregate_compliance_tags.extend(compliance_tags)
        aggregate_diagnostics.extend(report_diagnostics)
        if failure_mode:
            aggregate_failure_modes.append(failure_mode)

        if status == "contradicted":
            blocking_failures.append(_claim_signal(claim.claim_id, status, failure_mode))
        if status in _WARNING_STATUSES or report.warnings or compliance_tags:
            warnings.append(_claim_signal(claim.claim_id, status, failure_mode))
        for tag in compliance_tags:
            warnings.append(f"compliance_flag:{tag}")
        warnings.extend(report.warnings)

        detail: dict[str, Any] = {
            "claim_id": claim.claim_id,
            "claim_index": index,
            "support_status": status,
            "citation_keys": citation_keys,
            "evidence_span_ids": list(span_ids),
            "source_ids": list(source_ids),
            "failure_mode": failure_mode,
            "blocking": report.blocking,
            "compliance_tags": compliance_tags,
            "diagnostics": report_diagnostics,
            "warnings": list(report.warnings),
        }
        if active_config.include_report_metadata:
            detail["report_metadata"] = _json_safe(report.metadata)
            detail["claim_metadata"] = _json_safe(claim.metadata)
        claim_details.append(detail)

    total_claims = len(reports)
    summary = AnswerVerificationSummary(
        answer_id=resolved_answer_id,
        question=resolved_question,
        total_claims=total_claims,
        supported_claims=counts["supported"],
        partially_supported_claims=counts["partially_supported"],
        unsupported_claims=counts["unsupported"],
        contradicted_claims=counts["contradicted"],
        citation_missing_claims=counts["citation_missing"],
        citation_mismatch_claims=counts["citation_mismatch"],
        compliance_blocked_claims=counts["compliance_blocked"],
        ambiguous_claims=counts["ambiguous"],
        not_verifiable_from_context_claims=counts["not_verifiable_from_context"],
        answer_faithfulness_status=_answer_faithfulness_status(counts, total_claims),
        blocking_failures=_sorted_unique(blocking_failures),
        warnings=_sorted_unique(warnings),
        metrics={
            "aggregator_name": AGGREGATOR_NAME,
            "aggregator_version": AGGREGATOR_VERSION,
            "deterministic": True,
            "claim_ids": list(_sorted_unique(aggregate_claim_ids)),
            "citation_keys": list(_sorted_unique(aggregate_citation_keys)),
            "evidence_span_ids": list(_sorted_unique(aggregate_span_ids)),
            "source_ids": list(_sorted_unique(aggregate_source_ids)),
            "failure_modes": list(_sorted_unique(aggregate_failure_modes)),
            "compliance_tags": list(_sorted_unique(aggregate_compliance_tags)),
            "diagnostics": list(_sorted_unique(aggregate_diagnostics)),
            "claim_details": claim_details,
            "status_counts": {status: counts[status] for status in _COUNTED_STATUSES},
        },
    )
    summary.require_valid()
    return summary


def _infer_answer_id(reports: Sequence[ClaimVerificationReport]) -> str:
    for report in reports:
        if report.claim.answer_id:
            return report.claim.answer_id
    return "answer_not_provided"


def _answer_faithfulness_status(counts: dict[str, int], total_claims: int) -> str:
    if total_claims == 0:
        return "not_scored"
    if counts["contradicted"] or counts["unsupported"] or counts["citation_missing"] or counts["citation_mismatch"] or counts["compliance_blocked"]:
        return "fail"
    if counts["partially_supported"] or counts["ambiguous"] or counts["not_verifiable_from_context"]:
        return "caution"
    return "pass"


def _claim_signal(claim_id: str, status: str, failure_mode: str | None) -> str:
    if failure_mode:
        return f"{status}:{claim_id}:{failure_mode}"
    return f"{status}:{claim_id}"


def _report_diagnostics(report: ClaimVerificationReport) -> list[str]:
    diagnostics: list[str] = []
    raw_diagnostics = report.metadata.get("matcher_diagnostics", ())
    if isinstance(raw_diagnostics, str):
        diagnostics.append(raw_diagnostics)
    elif isinstance(raw_diagnostics, Sequence):
        diagnostics.extend(str(item) for item in raw_diagnostics)
    for signal in report.metadata.get("span_signals", ()):
        if isinstance(signal, dict):
            if signal.get("contradiction"):
                diagnostics.append("span_signal:contradiction")
            if signal.get("numeric_conflict"):
                diagnostics.append("span_signal:numeric_conflict")
            if signal.get("not_verifiable"):
                diagnostics.append("span_signal:not_verifiable")
    return list(_sorted_unique(diagnostics))


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


def _unique_preserve_order(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value) for value in values if str(value).strip()))


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(str(value) for value in values if str(value).strip())))
