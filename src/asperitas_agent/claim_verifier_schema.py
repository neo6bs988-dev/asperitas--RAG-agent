from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "V1.5C-schema-taxonomy"

SUPPORT_STATUSES = (
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

CLAIM_TYPES = (
    "sourced_fact",
    "bounded_inference",
    "biology_relation",
    "measurement",
    "method",
    "status",
    "compliance_sensitive",
    "limitation",
    "non_material",
)

BIOLOGY_ENTITY_TYPES = (
    "species",
    "gene",
    "protein",
    "compound",
    "pathway",
    "assay",
    "phenotype",
    "tissue_or_cell_type",
    "disease_or_condition",
    "organism_or_source_material",
    "experimental_method",
    "measurement_value_unit",
    "biological_relation_type",
)

COMPLIANCE_TRUTH_BOUNDARY_TAGS = (
    "cites",
    "nagoya_abs",
    "lmo_gmo",
    "biosafety",
    "ip_license",
    "human_clinical_sensitivity",
    "export_or_security_sensitive_biology",
    "production_db_claim",
    "production_kg_claim",
    "production_vector_db_claim",
    "wet_lab_validation_claim",
    "legal_regulatory_approval_claim",
    "autonomous_lab_claim",
    "foundation_model_completion_claim",
)

FAILURE_MODES = (
    "no_citation",
    "citation_points_to_wrong_source",
    "cited_span_does_not_support_claim",
    "claim_contradicts_cited_span",
    "answer_uses_parametric_memory_over_context",
    "entity_mismatch",
    "numeric_or_unit_mismatch",
    "overgeneralization",
    "compliance_sensitive_unverified_claim",
    "source_metadata_missing",
    "evidence_span_missing",
    "verifier_not_applicable",
)

ANSWER_FAITHFULNESS_STATUSES = ("pass", "caution", "fail", "not_scored")


@dataclass(frozen=True)
class BiologyEntity:
    entity_text: str
    entity_type: str
    normalized_label: str = ""
    source_span_ids: tuple[str, ...] = ()
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        _require_non_empty(errors, "entity_text", self.entity_text)
        _require_choice(errors, "entity_type", self.entity_type, BIOLOGY_ENTITY_TYPES)
        _require_string_tuple(errors, "source_span_ids", self.source_span_ids)
        _require_confidence(errors, "confidence", self.confidence)
        _require_mapping(errors, "metadata", self.metadata)
        return tuple(errors)

    def require_valid(self) -> None:
        _raise_if_errors(self.validate())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_span_ids"] = list(self.source_span_ids)
        return data


@dataclass(frozen=True)
class AtomicClaim:
    claim_id: str
    claim_text: str
    claim_type: str
    cited_source_ids: tuple[str, ...]
    cited_span_ids: tuple[str, ...]
    required_evidence_type: str
    detected_entities: tuple[BiologyEntity, ...] = ()
    compliance_tags: tuple[str, ...] = ()
    support_status: str = "not_verifiable_from_context"
    confidence: float | None = None
    verifier_notes: str = ""
    failure_mode: str | None = None
    answer_id: str = ""
    source_sentence: str = ""
    sentence_index: int | None = None
    citation_keys: tuple[str, ...] = ()
    blocking: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        _require_non_empty(errors, "claim_id", self.claim_id)
        _require_non_empty(errors, "claim_text", self.claim_text)
        _require_choice(errors, "claim_type", self.claim_type, CLAIM_TYPES)
        _require_string_tuple(errors, "cited_source_ids", self.cited_source_ids)
        _require_string_tuple(errors, "cited_span_ids", self.cited_span_ids)
        _require_non_empty(errors, "required_evidence_type", self.required_evidence_type)
        _require_choice(errors, "support_status", self.support_status, SUPPORT_STATUSES)
        _require_confidence(errors, "confidence", self.confidence)
        _require_optional_choice(errors, "failure_mode", self.failure_mode, FAILURE_MODES)
        _require_string_tuple(errors, "citation_keys", self.citation_keys)
        _require_string_tuple(errors, "compliance_tags", self.compliance_tags)
        _require_choices(errors, "compliance_tags", self.compliance_tags, COMPLIANCE_TRUTH_BOUNDARY_TAGS)
        _require_mapping(errors, "metadata", self.metadata)
        _require_optional_non_negative_int(errors, "sentence_index", self.sentence_index)
        for index, entity in enumerate(self.detected_entities):
            if not isinstance(entity, BiologyEntity):
                errors.append(f"detected_entities[{index}] must be BiologyEntity")
            else:
                errors.extend(f"detected_entities[{index}].{error}" for error in entity.validate())
        if self.support_status != "supported" and not self.failure_mode:
            errors.append("failure_mode is required when support_status is not supported")
        return tuple(errors)

    def require_valid(self) -> None:
        _raise_if_errors(self.validate())

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "answer_id": self.answer_id,
            "claim_text": self.claim_text,
            "claim_type": self.claim_type,
            "source_sentence": self.source_sentence,
            "sentence_index": self.sentence_index,
            "cited_source_ids": list(self.cited_source_ids),
            "cited_span_ids": list(self.cited_span_ids),
            "citation_keys": list(self.citation_keys),
            "required_evidence_type": self.required_evidence_type,
            "detected_entities": [entity.to_dict() for entity in self.detected_entities],
            "compliance_tags": list(self.compliance_tags),
            "support_status": self.support_status,
            "confidence": self.confidence,
            "verifier_notes": self.verifier_notes,
            "failure_mode": self.failure_mode,
            "blocking": self.blocking,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class EvidenceSpan:
    source_id: str
    span_id: str
    document_title: str = ""
    section: str = ""
    locator: str = ""
    evidence_text_hash_or_excerpt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    license_tags: tuple[str, ...] = ()
    compliance_tags: tuple[str, ...] = ()
    retrieval_rank: int | None = None
    retrieval_score: float | None = None
    citation_key: str = ""
    chunk_id: str = ""
    source_path: str = ""
    section_heading: str = ""
    section_path: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        _require_non_empty(errors, "source_id", self.source_id)
        _require_non_empty(errors, "span_id", self.span_id)
        _require_non_empty(errors, "evidence_text_hash_or_excerpt", self.evidence_text_hash_or_excerpt)
        _require_mapping(errors, "metadata", self.metadata)
        _require_string_tuple(errors, "license_tags", self.license_tags)
        _require_string_tuple(errors, "compliance_tags", self.compliance_tags)
        _require_choices(errors, "compliance_tags", self.compliance_tags, COMPLIANCE_TRUTH_BOUNDARY_TAGS)
        _require_string_tuple(errors, "section_path", self.section_path)
        if self.retrieval_rank is not None and not isinstance(self.retrieval_rank, int):
            errors.append("retrieval_rank must be an integer")
        elif self.retrieval_rank is not None and self.retrieval_rank < 1:
            errors.append("retrieval_rank must be >= 1")
        if self.retrieval_score is not None and not isinstance(self.retrieval_score, (int, float)):
            errors.append("retrieval_score must be numeric")
        elif self.retrieval_score is not None and self.retrieval_score < 0:
            errors.append("retrieval_score must be non-negative")
        return tuple(errors)

    def require_valid(self) -> None:
        _raise_if_errors(self.validate())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["license_tags"] = list(self.license_tags)
        data["compliance_tags"] = list(self.compliance_tags)
        data["section_path"] = list(self.section_path)
        return data


@dataclass(frozen=True)
class ClaimVerificationReport:
    claim: AtomicClaim
    candidate_evidence_spans: tuple[EvidenceSpan, ...]
    support_status: str
    confidence: float | None
    support_rationale: str
    failure_mode: str | None = None
    blocking: bool = False
    warnings: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        _require_choice(errors, "support_status", self.support_status, SUPPORT_STATUSES)
        _require_confidence(errors, "confidence", self.confidence)
        _require_optional_choice(errors, "failure_mode", self.failure_mode, FAILURE_MODES)
        _require_non_empty(errors, "support_rationale", self.support_rationale)
        _require_string_tuple(errors, "warnings", self.warnings)
        _require_mapping(errors, "metadata", self.metadata)
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        errors.extend(f"claim.{error}" for error in self.claim.validate())
        if self.claim.support_status != self.support_status:
            errors.append("support_status must match claim.support_status")
        for index, span in enumerate(self.candidate_evidence_spans):
            if not isinstance(span, EvidenceSpan):
                errors.append(f"candidate_evidence_spans[{index}] must be EvidenceSpan")
            else:
                errors.extend(f"candidate_evidence_spans[{index}].{error}" for error in span.validate())
        if self.support_status != "supported" and not self.failure_mode:
            errors.append("failure_mode is required when support_status is not supported")
        return tuple(errors)

    def require_valid(self) -> None:
        _raise_if_errors(self.validate())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "claim": self.claim.to_dict(),
            "candidate_evidence_spans": [span.to_dict() for span in self.candidate_evidence_spans],
            "support_status": self.support_status,
            "confidence": self.confidence,
            "support_rationale": self.support_rationale,
            "failure_mode": self.failure_mode,
            "blocking": self.blocking,
            "warnings": list(self.warnings),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class AnswerVerificationSummary:
    answer_id: str
    question: str
    total_claims: int
    supported_claims: int
    partially_supported_claims: int
    unsupported_claims: int
    contradicted_claims: int
    citation_missing_claims: int
    citation_mismatch_claims: int
    compliance_blocked_claims: int
    answer_faithfulness_status: str
    blocking_failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metrics: dict[str, Any] = field(default_factory=dict)
    ambiguous_claims: int = 0
    not_verifiable_from_context_claims: int = 0
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        _require_non_empty(errors, "answer_id", self.answer_id)
        _require_non_empty(errors, "question", self.question)
        _require_choice(errors, "answer_faithfulness_status", self.answer_faithfulness_status, ANSWER_FAITHFULNESS_STATUSES)
        _require_string_tuple(errors, "blocking_failures", self.blocking_failures)
        _require_string_tuple(errors, "warnings", self.warnings)
        _require_mapping(errors, "metrics", self.metrics)
        if not self.schema_version.strip():
            errors.append("schema_version is required")
        count_fields = (
            "total_claims",
            "supported_claims",
            "partially_supported_claims",
            "unsupported_claims",
            "contradicted_claims",
            "citation_missing_claims",
            "citation_mismatch_claims",
            "compliance_blocked_claims",
            "ambiguous_claims",
            "not_verifiable_from_context_claims",
        )
        for field_name in count_fields:
            value = getattr(self, field_name)
            _require_non_negative_int(errors, field_name, value)
        if all(_is_non_negative_int(getattr(self, field_name)) for field_name in count_fields):
            subtotal = (
                self.supported_claims
                + self.partially_supported_claims
                + self.unsupported_claims
                + self.contradicted_claims
                + self.citation_missing_claims
                + self.citation_mismatch_claims
                + self.compliance_blocked_claims
                + self.ambiguous_claims
                + self.not_verifiable_from_context_claims
            )
            if subtotal > self.total_claims:
                errors.append("status claim counts cannot exceed total_claims")
        return tuple(errors)

    def require_valid(self) -> None:
        _raise_if_errors(self.validate())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["blocking_failures"] = list(self.blocking_failures)
        data["warnings"] = list(self.warnings)
        return data


def biology_entity_from_dict(data: dict[str, Any]) -> BiologyEntity:
    return BiologyEntity(
        entity_text=str(data.get("entity_text", "")),
        entity_type=str(data.get("entity_type", "")),
        normalized_label=str(data.get("normalized_label", "")),
        source_span_ids=_as_string_tuple(data.get("source_span_ids", ())),
        confidence=data.get("confidence"),
        metadata=dict(data.get("metadata") or {}),
    )


def atomic_claim_from_dict(data: dict[str, Any]) -> AtomicClaim:
    return AtomicClaim(
        claim_id=str(data.get("claim_id", "")),
        answer_id=str(data.get("answer_id", "")),
        claim_text=str(data.get("claim_text", "")),
        claim_type=str(data.get("claim_type", "")),
        source_sentence=str(data.get("source_sentence", "")),
        sentence_index=data.get("sentence_index"),
        cited_source_ids=_as_string_tuple(data.get("cited_source_ids", ())),
        cited_span_ids=_as_string_tuple(data.get("cited_span_ids", ())),
        citation_keys=_as_string_tuple(data.get("citation_keys", ())),
        required_evidence_type=str(data.get("required_evidence_type", "")),
        detected_entities=tuple(biology_entity_from_dict(item) for item in data.get("detected_entities", ())),
        compliance_tags=_as_string_tuple(data.get("compliance_tags", ())),
        support_status=str(data.get("support_status", "not_verifiable_from_context")),
        confidence=data.get("confidence"),
        verifier_notes=str(data.get("verifier_notes", "")),
        failure_mode=data.get("failure_mode"),
        blocking=bool(data.get("blocking", False)),
        metadata=dict(data.get("metadata") or {}),
    )


def evidence_span_from_dict(data: dict[str, Any]) -> EvidenceSpan:
    return EvidenceSpan(
        source_id=str(data.get("source_id", "")),
        span_id=str(data.get("span_id", "")),
        document_title=str(data.get("document_title", "")),
        section=str(data.get("section", "")),
        locator=str(data.get("locator", "")),
        evidence_text_hash_or_excerpt=str(data.get("evidence_text_hash_or_excerpt", "")),
        metadata=dict(data.get("metadata") or {}),
        license_tags=_as_string_tuple(data.get("license_tags", ())),
        compliance_tags=_as_string_tuple(data.get("compliance_tags", ())),
        retrieval_rank=data.get("retrieval_rank"),
        retrieval_score=data.get("retrieval_score"),
        citation_key=str(data.get("citation_key", "")),
        chunk_id=str(data.get("chunk_id", "")),
        source_path=str(data.get("source_path", "")),
        section_heading=str(data.get("section_heading", "")),
        section_path=_as_string_tuple(data.get("section_path", ())),
    )


def claim_verification_report_from_dict(data: dict[str, Any]) -> ClaimVerificationReport:
    return ClaimVerificationReport(
        schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        claim=atomic_claim_from_dict(data.get("claim", {})),
        candidate_evidence_spans=tuple(evidence_span_from_dict(item) for item in data.get("candidate_evidence_spans", ())),
        support_status=str(data.get("support_status", "")),
        confidence=data.get("confidence"),
        support_rationale=str(data.get("support_rationale", "")),
        failure_mode=data.get("failure_mode"),
        blocking=bool(data.get("blocking", False)),
        warnings=_as_string_tuple(data.get("warnings", ())),
        metadata=dict(data.get("metadata") or {}),
    )


def answer_verification_summary_from_dict(data: dict[str, Any]) -> AnswerVerificationSummary:
    return AnswerVerificationSummary(
        schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        answer_id=str(data.get("answer_id", "")),
        question=str(data.get("question", "")),
        total_claims=int(data.get("total_claims", 0)),
        supported_claims=int(data.get("supported_claims", 0)),
        partially_supported_claims=int(data.get("partially_supported_claims", 0)),
        unsupported_claims=int(data.get("unsupported_claims", 0)),
        contradicted_claims=int(data.get("contradicted_claims", 0)),
        citation_missing_claims=int(data.get("citation_missing_claims", 0)),
        citation_mismatch_claims=int(data.get("citation_mismatch_claims", 0)),
        compliance_blocked_claims=int(data.get("compliance_blocked_claims", 0)),
        ambiguous_claims=int(data.get("ambiguous_claims", 0)),
        not_verifiable_from_context_claims=int(data.get("not_verifiable_from_context_claims", 0)),
        answer_faithfulness_status=str(data.get("answer_faithfulness_status", "")),
        blocking_failures=_as_string_tuple(data.get("blocking_failures", ())),
        warnings=_as_string_tuple(data.get("warnings", ())),
        metrics=dict(data.get("metrics") or {}),
    )


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _require_non_empty(errors: list[str], field_name: str, value: str) -> None:
    if not str(value).strip():
        errors.append(f"{field_name} is required")


def _require_choice(errors: list[str], field_name: str, value: str, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        errors.append(f"invalid {field_name}: {value}")


def _require_optional_choice(errors: list[str], field_name: str, value: str | None, allowed: tuple[str, ...]) -> None:
    if value is not None and value not in allowed:
        errors.append(f"invalid {field_name}: {value}")


def _require_choices(errors: list[str], field_name: str, values: tuple[str, ...], allowed: tuple[str, ...]) -> None:
    for value in values:
        if value not in allowed:
            errors.append(f"invalid {field_name}: {value}")


def _require_string_tuple(errors: list[str], field_name: str, value: tuple[str, ...]) -> None:
    if not isinstance(value, tuple):
        errors.append(f"{field_name} must be a tuple")
        return
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{field_name} must contain non-empty strings")


def _require_mapping(errors: list[str], field_name: str, value: dict[str, Any]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{field_name} must be a dict")


def _require_confidence(errors: list[str], field_name: str, value: float | None) -> None:
    if value is None:
        return
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 or value > 1:
        errors.append(f"{field_name} must be between 0 and 1")


def _require_non_negative_int(errors: list[str], field_name: str, value: Any) -> None:
    if not _is_non_negative_int(value):
        errors.append(f"{field_name} must be a non-negative integer")


def _require_optional_non_negative_int(errors: list[str], field_name: str, value: Any) -> None:
    if value is None:
        return
    _require_non_negative_int(errors, field_name, value)


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _raise_if_errors(errors: tuple[str, ...]) -> None:
    if errors:
        raise ValueError("; ".join(errors))
