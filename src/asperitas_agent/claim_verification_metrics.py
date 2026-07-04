from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .claim_verifier_schema import AnswerVerificationSummary, ClaimVerificationReport, SUPPORT_STATUSES


METRICS_NAME = "v1.5g-deterministic-claim-verification-regression-metrics"
METRICS_VERSION = "V1.5G"

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


@dataclass(frozen=True)
class ClaimVerificationRegressionMetrics:
    total_claims: int
    status_counts: dict[str, int]
    blocking_diagnostic_count: int
    warning_diagnostic_count: int
    contradiction_count: int
    citation_missing_count: int
    citation_mismatch_count: int
    unsupported_count: int
    not_verifiable_count: int
    ambiguous_count: int
    compliance_tag_counts: dict[str, int]
    license_tag_counts: dict[str, int]
    provenance_coverage_count: int
    metadata_json_safe: bool
    deterministic_ordering: bool
    metrics_name: str = METRICS_NAME
    metrics_version: str = METRICS_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_name": self.metrics_name,
            "metrics_version": self.metrics_version,
            "total_claims": self.total_claims,
            "status_counts": dict(self.status_counts),
            "blocking_diagnostic_count": self.blocking_diagnostic_count,
            "warning_diagnostic_count": self.warning_diagnostic_count,
            "contradiction_count": self.contradiction_count,
            "citation_missing_count": self.citation_missing_count,
            "citation_mismatch_count": self.citation_mismatch_count,
            "unsupported_count": self.unsupported_count,
            "not_verifiable_count": self.not_verifiable_count,
            "ambiguous_count": self.ambiguous_count,
            "compliance_tag_counts": dict(self.compliance_tag_counts),
            "license_tag_counts": dict(self.license_tag_counts),
            "provenance_coverage_count": self.provenance_coverage_count,
            "metadata_json_safe": self.metadata_json_safe,
            "deterministic_ordering": self.deterministic_ordering,
        }


def build_claim_verification_regression_metrics(
    summary: AnswerVerificationSummary,
    reports: Sequence[ClaimVerificationReport],
) -> ClaimVerificationRegressionMetrics:
    """Project existing verifier outputs into deterministic regression-gate metrics."""
    summary.require_valid()
    for report in reports:
        report.require_valid()

    status_counts = {
        status: int(getattr(summary, _STATUS_COUNT_FIELDS[status]))
        for status in SUPPORT_STATUSES
    }
    compliance_tag_counts = _sorted_counts(
        tag
        for report in reports
        for tag in report.claim.compliance_tags
    )
    license_tag_counts = _sorted_counts(
        tag
        for report in reports
        for span in report.candidate_evidence_spans
        for tag in span.license_tags
    )

    return ClaimVerificationRegressionMetrics(
        total_claims=summary.total_claims,
        status_counts=status_counts,
        blocking_diagnostic_count=len(summary.blocking_failures),
        warning_diagnostic_count=len(summary.warnings),
        contradiction_count=summary.contradicted_claims,
        citation_missing_count=summary.citation_missing_claims,
        citation_mismatch_count=summary.citation_mismatch_claims,
        unsupported_count=summary.unsupported_claims,
        not_verifiable_count=summary.not_verifiable_from_context_claims,
        ambiguous_count=summary.ambiguous_claims,
        compliance_tag_counts=compliance_tag_counts,
        license_tag_counts=license_tag_counts,
        provenance_coverage_count=_provenance_coverage_count(reports),
        metadata_json_safe=_is_json_safe(summary.to_dict()),
        deterministic_ordering=_has_deterministic_ordering(summary, reports),
    )


def _sorted_counts(values: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if not str(value).strip():
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def _provenance_coverage_count(reports: Sequence[ClaimVerificationReport]) -> int:
    covered: set[tuple[str, str, str, str]] = set()
    for report in reports:
        for span in report.candidate_evidence_spans:
            if span.source_id and span.span_id and span.source_path and span.chunk_id:
                covered.add((span.source_id, span.span_id, span.source_path, span.chunk_id))
    return len(covered)


def _is_json_safe(payload: Mapping[str, Any]) -> bool:
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        return False
    return json.loads(encoded) == payload


def _has_deterministic_ordering(
    summary: AnswerVerificationSummary,
    reports: Sequence[ClaimVerificationReport],
) -> bool:
    metrics = summary.metrics
    if metrics.get("deterministic") is not True:
        return False
    claim_details = metrics.get("claim_details", [])
    if not isinstance(claim_details, list):
        return False
    report_claim_ids = [report.claim.claim_id for report in reports]
    detail_claim_ids = [str(detail.get("claim_id")) for detail in claim_details if isinstance(detail, Mapping)]
    if detail_claim_ids != report_claim_ids:
        return False
    for key in ("claim_ids", "citation_keys", "evidence_span_ids", "source_ids", "failure_modes", "compliance_tags", "diagnostics"):
        values = metrics.get(key, [])
        if not isinstance(values, list) or values != sorted(values):
            return False
    return _is_json_safe(summary.to_dict())
