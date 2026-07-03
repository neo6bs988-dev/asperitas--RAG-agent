from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .claim_verifier_schema import AtomicClaim, EvidenceSpan, evidence_span_from_dict


MATCHER_NAME = "v1.5c-deterministic-evidence-span-matcher"
MATCHER_VERSION = "V1.5C-step3"

_SPACE_RE = re.compile(r"\s+")
_VALID_CITATION_KEY_RE = re.compile(r"^(?:[A-Z][A-Z0-9_-]*\d|\d+)$")
_VALID_CASE_SENSITIVE_CITATION_KEY_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9_-]*\d|\d+)$")
_METADATA_MATCH_KEYS = (
    "citation_key",
    "citation_label",
    "evidence_label",
    "evidence_key",
    "span_id",
    "source_id",
)


@dataclass(frozen=True)
class EvidenceSpanMatcherConfig:
    allow_metadata_key_match: bool = True
    allow_source_id_match: bool = True
    allow_span_id_match: bool = True
    case_sensitive: bool = False
    max_matches_per_key: int | None = None


@dataclass(frozen=True)
class CitationMatch:
    citation_key: str
    normalized_key: str
    span_id: str
    source_id: str
    match_fields: tuple[str, ...]
    evidence_span: EvidenceSpan
    rank: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "citation_key": self.citation_key,
            "normalized_key": self.normalized_key,
            "span_id": self.span_id,
            "source_id": self.source_id,
            "match_fields": list(self.match_fields),
            "evidence_span": self.evidence_span.to_dict(),
            "rank": self.rank,
        }


@dataclass(frozen=True)
class ClaimCitationResolution:
    claim_id: str
    citation_keys: tuple[str, ...]
    matched_spans: tuple[CitationMatch, ...]
    unresolved_keys: tuple[str, ...]
    ambiguous_keys: tuple[str, ...]
    diagnostics: tuple[str, ...]
    blocking: bool
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "citation_keys": list(self.citation_keys),
            "matched_spans": [match.to_dict() for match in self.matched_spans],
            "unresolved_keys": list(self.unresolved_keys),
            "ambiguous_keys": list(self.ambiguous_keys),
            "diagnostics": list(self.diagnostics),
            "blocking": self.blocking,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class IndexedEvidenceSpan:
    rank: int
    evidence_span: EvidenceSpan
    normalized_keys: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class EvidenceSpanIndex:
    entries: tuple[IndexedEvidenceSpan, ...]
    invalid_spans: tuple[str, ...] = ()


def normalize_citation_key(key: str) -> str:
    return _normalize_citation_key(key, case_sensitive=False)


def build_evidence_span_index(spans: Sequence[EvidenceSpan | Mapping[str, Any]]) -> EvidenceSpanIndex:
    return _build_evidence_span_index(spans, EvidenceSpanMatcherConfig())


def resolve_claim_citations(
    claim: AtomicClaim,
    evidence_spans: Sequence[EvidenceSpan | Mapping[str, Any]],
    *,
    config: EvidenceSpanMatcherConfig | None = None,
) -> ClaimCitationResolution:
    active_config = config or EvidenceSpanMatcherConfig()
    index = _build_evidence_span_index(evidence_spans, active_config)
    matches_by_key = _matches_by_key(index)

    diagnostics: list[str] = []
    warnings: list[str] = []
    matched_spans: list[CitationMatch] = []
    unresolved_keys: list[str] = []
    ambiguous_keys: list[str] = []

    if index.invalid_spans:
        _append_unique(diagnostics, "evidence_span_invalid")
        warnings.extend(index.invalid_spans)

    if not claim.citation_keys:
        _append_unique(diagnostics, "missing_citation_keys")
        warnings.append(f"claim {claim.claim_id} has no citation keys")
        return ClaimCitationResolution(
            claim_id=claim.claim_id,
            citation_keys=(),
            matched_spans=(),
            unresolved_keys=(),
            ambiguous_keys=(),
            diagnostics=tuple(diagnostics),
            blocking=True,
            warnings=tuple(warnings),
        )

    for citation_key in claim.citation_keys:
        normalized_key = _normalize_citation_key(citation_key, case_sensitive=active_config.case_sensitive)
        if not normalized_key or not _is_well_formed_citation_key(normalized_key, active_config):
            _append_unique(diagnostics, "malformed_citation_key")
            unresolved_keys.append(citation_key)
            warnings.append(f"claim {claim.claim_id} has malformed citation key: {citation_key}")
            continue

        indexed_matches = matches_by_key.get(normalized_key, ())
        if not indexed_matches:
            _append_unique(diagnostics, "unresolved")
            unresolved_keys.append(citation_key)
            continue

        limited_matches = indexed_matches
        if active_config.max_matches_per_key is not None:
            limited_matches = indexed_matches[: max(active_config.max_matches_per_key, 0)]

        if len(indexed_matches) > 1:
            _append_unique(diagnostics, "ambiguous")
            _append_unique(diagnostics, "duplicate_key")
            ambiguous_keys.append(citation_key)
        else:
            _append_unique(diagnostics, "resolved")

        for indexed_span in limited_matches:
            match_fields = indexed_span.normalized_keys.get(normalized_key, ())
            matched_spans.append(
                CitationMatch(
                    citation_key=citation_key,
                    normalized_key=normalized_key,
                    span_id=indexed_span.evidence_span.span_id,
                    source_id=indexed_span.evidence_span.source_id,
                    match_fields=match_fields,
                    evidence_span=indexed_span.evidence_span,
                    rank=indexed_span.rank,
                )
            )

    blocking = bool(unresolved_keys or ambiguous_keys or "missing_citation_keys" in diagnostics or "malformed_citation_key" in diagnostics)
    return ClaimCitationResolution(
        claim_id=claim.claim_id,
        citation_keys=tuple(claim.citation_keys),
        matched_spans=tuple(matched_spans),
        unresolved_keys=tuple(unresolved_keys),
        ambiguous_keys=tuple(ambiguous_keys),
        diagnostics=tuple(diagnostics),
        blocking=blocking,
        warnings=tuple(warnings),
    )


def resolve_answer_claim_citations(
    claims: Sequence[AtomicClaim],
    evidence_spans: Sequence[EvidenceSpan | Mapping[str, Any]],
    *,
    config: EvidenceSpanMatcherConfig | None = None,
) -> list[ClaimCitationResolution]:
    return [resolve_claim_citations(claim, evidence_spans, config=config) for claim in claims]


def _build_evidence_span_index(
    spans: Sequence[EvidenceSpan | Mapping[str, Any]],
    config: EvidenceSpanMatcherConfig,
) -> EvidenceSpanIndex:
    entries: list[IndexedEvidenceSpan] = []
    invalid_spans: list[str] = []
    for index, record in enumerate(spans, start=1):
        span = _coerce_evidence_span(record, index)
        if span is None:
            invalid_spans.append(f"evidence span {index} is not an EvidenceSpan or mapping")
            continue
        errors = span.validate()
        if errors:
            invalid_spans.append(f"evidence span {index} invalid: {'; '.join(errors)}")
            continue
        entries.append(
            IndexedEvidenceSpan(
                rank=index,
                evidence_span=span,
                normalized_keys=_normalized_span_keys(span, config),
            )
        )
    return EvidenceSpanIndex(entries=tuple(entries), invalid_spans=tuple(invalid_spans))


def _coerce_evidence_span(record: EvidenceSpan | Mapping[str, Any], index: int) -> EvidenceSpan | None:
    if isinstance(record, EvidenceSpan):
        return record
    if not isinstance(record, Mapping):
        return None

    payload = dict(record)
    metadata = dict(payload.get("metadata") or {})
    for field_name in ("citation_label", "evidence_label", "evidence_key", "source_priority"):
        if field_name in payload and field_name not in metadata:
            metadata[field_name] = payload[field_name]

    citation_key = str(payload.get("citation_key") or payload.get("citation_label") or payload.get("evidence_label") or "")
    source_id = str(payload.get("source_id") or payload.get("source") or payload.get("source_path") or "")
    span_id = str(
        payload.get("span_id")
        or payload.get("chunk_id")
        or normalize_citation_key(citation_key)
        or (f"span-{index}" if source_id else "")
    )
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


def _normalized_span_keys(span: EvidenceSpan, config: EvidenceSpanMatcherConfig) -> Mapping[str, tuple[str, ...]]:
    fields_by_key: dict[str, list[str]] = {}
    _add_key(fields_by_key, span.citation_key, "citation_key", config)
    if config.allow_span_id_match:
        _add_key(fields_by_key, span.span_id, "span_id", config)
        _add_key(fields_by_key, span.chunk_id, "chunk_id", config)
    if config.allow_source_id_match:
        _add_key(fields_by_key, span.source_id, "source_id", config)
    if config.allow_metadata_key_match:
        for metadata_key, metadata_value in sorted(span.metadata.items(), key=lambda item: str(item[0])):
            key_name = str(metadata_key)
            if key_name in _METADATA_MATCH_KEYS:
                _add_key(fields_by_key, key_name, f"metadata_key:{key_name}", config)
            if key_name in _METADATA_MATCH_KEYS or key_name.endswith("_key") or key_name.endswith("_label") or key_name.endswith("_id"):
                _add_key(fields_by_key, str(metadata_value), f"metadata:{key_name}", config)
    return {key: tuple(fields) for key, fields in fields_by_key.items()}


def _add_key(
    fields_by_key: dict[str, list[str]],
    raw_key: str,
    field_name: str,
    config: EvidenceSpanMatcherConfig,
) -> None:
    normalized_key = _normalize_citation_key(raw_key, case_sensitive=config.case_sensitive)
    if not normalized_key or not _is_well_formed_citation_key(normalized_key, config):
        return
    fields = fields_by_key.setdefault(normalized_key, [])
    if field_name not in fields:
        fields.append(field_name)


def _matches_by_key(index: EvidenceSpanIndex) -> Mapping[str, tuple[IndexedEvidenceSpan, ...]]:
    matches: dict[str, list[IndexedEvidenceSpan]] = {}
    for entry in index.entries:
        for normalized_key in entry.normalized_keys:
            matches.setdefault(normalized_key, []).append(entry)
    return {key: tuple(entries) for key, entries in matches.items()}


def _normalize_citation_key(key: str, *, case_sensitive: bool) -> str:
    compact = _SPACE_RE.sub("", str(key or "").strip())
    if len(compact) >= 2 and compact.startswith("[") and compact.endswith("]"):
        compact = compact[1:-1]
    compact = compact.strip()
    return compact if case_sensitive else compact.upper()


def _is_well_formed_citation_key(normalized_key: str, config: EvidenceSpanMatcherConfig) -> bool:
    if config.case_sensitive:
        return bool(_VALID_CASE_SENSITIVE_CITATION_KEY_RE.fullmatch(normalized_key))
    return bool(_VALID_CITATION_KEY_RE.fullmatch(normalized_key.upper()))


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)
