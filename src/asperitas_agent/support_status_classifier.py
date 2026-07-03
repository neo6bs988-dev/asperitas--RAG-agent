from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from .claim_verifier_schema import (
    AtomicClaim,
    ClaimVerificationReport,
    EvidenceSpan,
    evidence_span_from_dict,
)
from .evidence_span_matcher import resolve_claim_citations


CLASSIFIER_NAME = "v1.5c-deterministic-support-status-classifier"
CLASSIFIER_VERSION = "V1.5C-step4"

_CITATION_RE = re.compile(r"\[(?:[A-Za-z]+)?\d+(?:[-,]\s*(?:[A-Za-z]+)?\d+)*\]")
_SPACE_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*|\d+(?:\.\d+)?")
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}

_INCREASE_TERMS = {"increase", "increases", "increased", "increasing", "higher", "raises", "raised", "upregulated"}
_DECREASE_TERMS = {"decrease", "decreases", "decreased", "decreasing", "lower", "lowers", "reduced", "reduces", "downregulated"}
_PRESENT_TERMS = {"present", "detected", "detects", "contains", "included", "includes", "expressed", "expresses"}
_ABSENT_TERMS = {"absent", "undetected", "lacks", "missing"}
_NEGATED_PRESENT_PATTERNS = (
    re.compile(r"\bnot\s+(?:present|detected|expressed|included)\b"),
    re.compile(r"\bno\s+(?:detectable\s+)?(?:signal|expression|evidence|presence)\b"),
    re.compile(r"\bdoes\s+not\s+(?:contain|include|express|detect)\b"),
)


@dataclass(frozen=True)
class SupportStatusClassifierConfig:
    min_evidence_text_chars: int = 12
    strong_support_token_coverage: float = 0.72
    partial_support_token_coverage: float = 0.35
    min_supporting_tokens: int = 3
    numeric_conflict_min_overlap: float = 0.45


@dataclass(frozen=True)
class _SpanSignal:
    span: EvidenceSpan
    token_coverage: float
    shared_tokens: tuple[str, ...]
    contradiction: bool
    numeric_conflict: bool
    not_verifiable: bool


def classify_claim_support(
    claim: AtomicClaim,
    evidence_spans: Sequence[EvidenceSpan | Mapping[str, Any]],
    *,
    config: SupportStatusClassifierConfig | None = None,
) -> ClaimVerificationReport:
    active_config = config or SupportStatusClassifierConfig()
    valid_spans, span_warnings = _coerce_valid_spans(evidence_spans)
    resolution = resolve_claim_citations(claim, evidence_spans)
    candidate_spans = valid_spans

    if not claim.citation_keys:
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="citation_missing",
            confidence=0.99,
            rationale="Claim has no citation keys, so support cannot be attributed to a cited evidence span.",
            failure_mode="no_citation",
            blocking=True,
            warnings=tuple(dict.fromkeys((*span_warnings, *resolution.warnings))),
            metadata={"matcher_diagnostics": list(resolution.diagnostics)},
        )

    mismatch_diagnostics = {"unresolved", "malformed_citation_key", "ambiguous", "duplicate_key", "evidence_span_invalid"}
    if any(diagnostic in mismatch_diagnostics for diagnostic in resolution.diagnostics):
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="citation_mismatch",
            confidence=0.97,
            rationale="Citation resolution produced blocking diagnostics before support classification.",
            failure_mode="citation_points_to_wrong_source",
            blocking=True,
            warnings=tuple(
                dict.fromkeys(
                    (
                        *span_warnings,
                        *resolution.warnings,
                        *[f"matcher_diagnostic:{diagnostic}" for diagnostic in resolution.diagnostics],
                    )
                )
            ),
            metadata={
                "matcher_diagnostics": list(resolution.diagnostics),
                "unresolved_keys": list(resolution.unresolved_keys),
                "ambiguous_keys": list(resolution.ambiguous_keys),
            },
        )

    if not candidate_spans:
        return _build_report(
            claim=claim,
            candidate_spans=(),
            status="citation_missing",
            confidence=0.98,
            rationale="Claim cites evidence, but no matched evidence span was available.",
            failure_mode="evidence_span_missing",
            blocking=True,
            warnings=tuple(dict.fromkeys(span_warnings)),
            metadata={"matcher_diagnostics": list(resolution.diagnostics)},
        )

    signals = tuple(_span_signal(claim.claim_text, span, active_config) for span in candidate_spans)
    if all(signal.not_verifiable for signal in signals):
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="not_verifiable_from_context",
            confidence=0.9,
            rationale="Matched evidence text is missing, invalid, too short, or insufficient for deterministic comparison.",
            failure_mode="evidence_span_missing",
            blocking=True,
            warnings=tuple(dict.fromkeys((*span_warnings, "evidence_text_not_verifiable"))),
            metadata=_signal_metadata(resolution.diagnostics, signals),
        )

    contradictory = tuple(signal for signal in signals if signal.contradiction or signal.numeric_conflict)
    strong = tuple(signal for signal in signals if _is_strong_support(signal, active_config))
    partial = tuple(signal for signal in signals if _is_partial_support(signal, active_config))

    if contradictory and (strong or len(contradictory) < len(signals)):
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="ambiguous",
            confidence=0.64,
            rationale="Candidate spans produced both support and contradiction signals without a deterministic winner.",
            failure_mode="verifier_not_applicable",
            blocking=True,
            warnings=tuple(dict.fromkeys((*span_warnings, "conflicting_support_signals"))),
            metadata=_signal_metadata(resolution.diagnostics, signals),
        )

    if contradictory:
        failure_mode = "numeric_or_unit_mismatch" if any(signal.numeric_conflict for signal in contradictory) else "claim_contradicts_cited_span"
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="contradicted",
            confidence=0.88,
            rationale="Deterministic contradiction markers or numeric mismatch were found near overlapping claim content.",
            failure_mode=failure_mode,
            blocking=True,
            warnings=tuple(dict.fromkeys(span_warnings)),
            metadata=_signal_metadata(resolution.diagnostics, signals),
        )

    if strong:
        best = max(strong, key=lambda signal: signal.token_coverage)
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="supported",
            confidence=min(0.95, 0.72 + (best.token_coverage * 0.25)),
            rationale="Claim tokens strongly overlap with cited evidence and no deterministic contradiction was detected.",
            failure_mode=None,
            blocking=False,
            warnings=tuple(dict.fromkeys(span_warnings)),
            metadata=_signal_metadata(resolution.diagnostics, signals),
        )

    if partial:
        best = max(partial, key=lambda signal: signal.token_coverage)
        return _build_report(
            claim=claim,
            candidate_spans=candidate_spans,
            status="partially_supported",
            confidence=min(0.82, 0.45 + (best.token_coverage * 0.45)),
            rationale="Some important claim content appears in cited evidence, but overlap is not strong enough for full support.",
            failure_mode="overgeneralization",
            blocking=False,
            warnings=tuple(dict.fromkeys((*span_warnings, "partial_overlap_only"))),
            metadata=_signal_metadata(resolution.diagnostics, signals),
        )

    return _build_report(
        claim=claim,
        candidate_spans=candidate_spans,
        status="unsupported",
        confidence=0.82,
        rationale="Evidence exists, but deterministic token overlap is too weak to support the claim.",
        failure_mode="cited_span_does_not_support_claim",
        blocking=True,
        warnings=tuple(dict.fromkeys(span_warnings)),
        metadata=_signal_metadata(resolution.diagnostics, signals),
    )


def classify_answer_claim_support(
    claims: Sequence[AtomicClaim],
    evidence_by_claim_id: Mapping[str, Sequence[EvidenceSpan | Mapping[str, Any]]],
    *,
    config: SupportStatusClassifierConfig | None = None,
) -> list[ClaimVerificationReport]:
    return [
        classify_claim_support(
            claim,
            evidence_by_claim_id.get(claim.claim_id, ()),
            config=config,
        )
        for claim in claims
    ]


def _build_report(
    *,
    claim: AtomicClaim,
    candidate_spans: tuple[EvidenceSpan, ...],
    status: str,
    confidence: float,
    rationale: str,
    failure_mode: str | None,
    blocking: bool,
    warnings: tuple[str, ...],
    metadata: dict[str, Any],
) -> ClaimVerificationReport:
    source_ids = _unique((*claim.cited_source_ids, *(span.source_id for span in candidate_spans)))
    span_ids = _unique((*claim.cited_span_ids, *(span.span_id for span in candidate_spans)))
    updated_claim = replace(
        claim,
        cited_source_ids=source_ids,
        cited_span_ids=span_ids,
        support_status=status,
        confidence=confidence,
        verifier_notes=rationale,
        failure_mode=failure_mode,
        blocking=blocking,
        metadata={
            **claim.metadata,
            "support_classifier_name": CLASSIFIER_NAME,
            "support_classifier_version": CLASSIFIER_VERSION,
        },
    )
    report = ClaimVerificationReport(
        claim=updated_claim,
        candidate_evidence_spans=candidate_spans,
        support_status=status,
        confidence=confidence,
        support_rationale=rationale,
        failure_mode=failure_mode,
        blocking=blocking,
        warnings=warnings,
        metadata={
            "classifier_name": CLASSIFIER_NAME,
            "classifier_version": CLASSIFIER_VERSION,
            "deterministic": True,
            **metadata,
        },
    )
    report.require_valid()
    return report


def _coerce_valid_spans(records: Sequence[EvidenceSpan | Mapping[str, Any]]) -> tuple[tuple[EvidenceSpan, ...], tuple[str, ...]]:
    spans: list[EvidenceSpan] = []
    warnings: list[str] = []
    for index, record in enumerate(records, start=1):
        span = _coerce_span(record)
        if span is None:
            warnings.append(f"evidence span {index} is not an EvidenceSpan or mapping")
            continue
        errors = span.validate()
        if errors:
            warnings.append(f"evidence span {index} invalid: {'; '.join(errors)}")
            continue
        spans.append(span)
    return tuple(spans), tuple(warnings)


def _coerce_span(record: EvidenceSpan | Mapping[str, Any]) -> EvidenceSpan | None:
    if isinstance(record, EvidenceSpan):
        return record
    if not isinstance(record, Mapping):
        return None
    payload = dict(record.get("evidence_span") if isinstance(record.get("evidence_span"), Mapping) else record)
    metadata = dict(payload.get("metadata") or {})
    for field_name in ("citation_label", "evidence_label", "evidence_key", "source_priority"):
        if field_name in payload and field_name not in metadata:
            metadata[field_name] = payload[field_name]

    citation_key = str(payload.get("citation_key") or payload.get("citation_label") or payload.get("evidence_label") or "")
    source_id = str(payload.get("source_id") or payload.get("source") or payload.get("source_path") or "")
    span_id = str(payload.get("span_id") or payload.get("chunk_id") or citation_key.strip("[]") or "")
    excerpt = str(
        payload.get("evidence_text_hash_or_excerpt")
        or payload.get("text_excerpt")
        or payload.get("excerpt")
        or payload.get("text")
        or ""
    )
    return evidence_span_from_dict(
        {
            **payload,
            "source_id": source_id,
            "span_id": span_id,
            "evidence_text_hash_or_excerpt": excerpt,
            "metadata": metadata,
            "citation_key": citation_key,
        }
    )


def _span_signal(claim_text: str, span: EvidenceSpan, config: SupportStatusClassifierConfig) -> _SpanSignal:
    evidence_text = _clean_text(span.evidence_text_hash_or_excerpt)
    if len(evidence_text) < config.min_evidence_text_chars:
        return _SpanSignal(span=span, token_coverage=0.0, shared_tokens=(), contradiction=False, numeric_conflict=False, not_verifiable=True)

    claim_tokens = _important_tokens(claim_text)
    evidence_tokens = _important_tokens(evidence_text)
    if not claim_tokens or not evidence_tokens:
        return _SpanSignal(span=span, token_coverage=0.0, shared_tokens=(), contradiction=False, numeric_conflict=False, not_verifiable=True)

    shared = tuple(token for token in claim_tokens if token in set(evidence_tokens))
    coverage = len(shared) / len(claim_tokens)
    numeric_conflict = _numeric_conflict(claim_text, evidence_text) and coverage >= config.numeric_conflict_min_overlap
    contradiction = _directional_conflict(claim_text, evidence_text) or _present_absent_conflict(claim_text, evidence_text)
    return _SpanSignal(
        span=span,
        token_coverage=coverage,
        shared_tokens=shared,
        contradiction=contradiction,
        numeric_conflict=numeric_conflict,
        not_verifiable=False,
    )


def _is_strong_support(signal: _SpanSignal, config: SupportStatusClassifierConfig) -> bool:
    return (
        not signal.not_verifiable
        and not signal.contradiction
        and not signal.numeric_conflict
        and signal.token_coverage >= config.strong_support_token_coverage
        and len(signal.shared_tokens) >= config.min_supporting_tokens
    )


def _is_partial_support(signal: _SpanSignal, config: SupportStatusClassifierConfig) -> bool:
    return (
        not signal.not_verifiable
        and not signal.contradiction
        and not signal.numeric_conflict
        and signal.token_coverage >= config.partial_support_token_coverage
        and len(signal.shared_tokens) >= 2
    )


def _clean_text(text: str) -> str:
    return _SPACE_RE.sub(" ", _CITATION_RE.sub("", text or "")).strip()


def _important_tokens(text: str) -> tuple[str, ...]:
    tokens = []
    for token in _TOKEN_RE.findall(_clean_text(text).casefold()):
        if token in _STOPWORDS:
            continue
        if len(token) <= 2 and not token.isdigit():
            continue
        tokens.append(token)
    return tuple(dict.fromkeys(tokens))


def _numeric_conflict(claim_text: str, evidence_text: str) -> bool:
    claim_numbers = tuple(_NUMBER_RE.findall(_clean_text(claim_text)))
    evidence_numbers = tuple(_NUMBER_RE.findall(_clean_text(evidence_text)))
    return bool(claim_numbers and evidence_numbers and set(claim_numbers) != set(evidence_numbers))


def _directional_conflict(claim_text: str, evidence_text: str) -> bool:
    claim_tokens = set(_important_tokens(claim_text))
    evidence_tokens = set(_important_tokens(evidence_text))
    return bool(
        (claim_tokens & _INCREASE_TERMS and evidence_tokens & _DECREASE_TERMS)
        or (claim_tokens & _DECREASE_TERMS and evidence_tokens & _INCREASE_TERMS)
    )


def _present_absent_conflict(claim_text: str, evidence_text: str) -> bool:
    claim_clean = _clean_text(claim_text).casefold()
    evidence_clean = _clean_text(evidence_text).casefold()
    claim_tokens = set(_important_tokens(claim_clean))
    evidence_tokens = set(_important_tokens(evidence_clean))
    claim_negated_present = any(pattern.search(claim_clean) for pattern in _NEGATED_PRESENT_PATTERNS)
    evidence_negated_present = any(pattern.search(evidence_clean) for pattern in _NEGATED_PRESENT_PATTERNS)
    return bool(
        (claim_tokens & _PRESENT_TERMS and (evidence_tokens & _ABSENT_TERMS or evidence_negated_present))
        or (evidence_tokens & _PRESENT_TERMS and (claim_tokens & _ABSENT_TERMS or claim_negated_present))
    )


def _signal_metadata(matcher_diagnostics: tuple[str, ...], signals: tuple[_SpanSignal, ...]) -> dict[str, Any]:
    return {
        "matcher_diagnostics": list(matcher_diagnostics),
        "span_signals": [
            {
                "span_id": signal.span.span_id,
                "source_id": signal.span.source_id,
                "token_coverage": round(signal.token_coverage, 4),
                "shared_tokens": list(signal.shared_tokens),
                "contradiction": signal.contradiction,
                "numeric_conflict": signal.numeric_conflict,
                "not_verifiable": signal.not_verifiable,
            }
            for signal in signals
        ],
    }


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))
