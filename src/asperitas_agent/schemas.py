from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SOURCE_PRIORITIES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
DISCLOSURE_LEVELS = ("confidential", "internal", "external_safe", "public", "unknown")
VERIFICATION_STATUSES = ("verified_internal", "verified_official", "externally_verified", "unverified", "needs_review")
LICENSE_STATUSES = ("owned", "internal_use", "public", "restricted", "unknown", "needs_review")
EVIDENCE_LABELS = (
    "Document-Supported Fact",
    "Official Source",
    "Peer-Reviewed Evidence",
    "Regulatory Source",
    "Industry Signal",
    "Inference",
    "Speculation",
    "Needs External Verification",
)
PARSE_STATUSES = ("not_attempted", "parsed", "partial", "failed", "unsupported")
INGESTION_STATUSES = ("success", "partial", "unsupported", "failed")

REGISTRY_COLUMNS = (
    "source_id",
    "title",
    "original_filename",
    "path",
    "source_priority",
    "source_type",
    "disclosure_level",
    "license_status",
    "verification_status",
    "date",
    "author_or_owner",
    "use_case",
    "checksum",
    "parse_status",
    "notes",
)


@dataclass
class SourceRecord:
    source_id: str
    title: str
    original_filename: str
    path: str
    source_priority: str
    source_type: str
    disclosure_level: str
    license_status: str
    verification_status: str
    date: str
    author_or_owner: str
    use_case: str
    checksum: str
    parse_status: str = "not_attempted"
    notes: str = ""

    def to_row(self) -> dict[str, str]:
        return {key: str(getattr(self, key)) for key in REGISTRY_COLUMNS}


@dataclass
class LoadedDocument:
    source: SourceRecord
    text: str
    parser_used: str
    parse_status: str
    parse_warnings: list[str] = field(default_factory=list)
    page_texts: list[tuple[int | None, str]] = field(default_factory=list)


@dataclass
class IngestionLogEntry:
    source_id: str
    path: str
    filename: str
    extension: str
    ingestion_status: str
    reason: str
    extracted_chunk_count: int
    source_priority: str
    disclosure_level: str
    compliance_flags: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    title: str
    text: str
    page_start: int | None
    page_end: int | None
    char_start: int
    char_end: int
    source_priority: str
    source_type: str
    disclosure_level: str
    evidence_label: str
    verification_status: str
    risk_tags: list[str]
    checksum: str
    section: str = ""
    section_heading: str = ""
    section_path: list[str] = field(default_factory=list)
    section_level: int | None = None
    parent_section: str = ""
    subsection: str = ""
    heading_context: str = ""

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalResult:
    query: str
    chunk: Chunk
    score: float

    def to_json(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "chunk_id": self.chunk.chunk_id,
            "source_id": self.chunk.source_id,
            "title": self.chunk.title,
            "source_priority": self.chunk.source_priority,
            "disclosure_level": self.chunk.disclosure_level,
            "evidence_label": self.chunk.evidence_label,
            "verification_status": self.chunk.verification_status,
            "score": round(self.score, 6),
            "risk_tags": self.chunk.risk_tags,
            "text": self.chunk.text,
        }


@dataclass
class RetrieverMetadata:
    retriever_name: str
    retriever_version: str
    top_k: int

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceItem:
    rank: int
    chunk_id: str
    score: float
    source_id: str = ""
    source_title: str = ""
    source_path: str = ""
    source_priority: str = ""
    evidence_label: str = ""
    section: str = ""
    section_heading: str = ""
    section_path: list[str] = field(default_factory=list)
    section_level: int | None = None
    parent_section: str = ""
    subsection: str = ""
    text_excerpt: str = ""
    citation_key: str = ""

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceCoverageSummary:
    unique_source_count: int
    source_priorities_present: list[str]
    evidence_labels_present: list[str]
    section_paths_present: list[str]
    missing_section_metadata_count: int
    missing_source_priority_count: int
    missing_evidence_label_count: int

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceRiskFlags:
    no_evidence_found: bool
    low_source_diversity: bool
    missing_source_priority: bool
    missing_evidence_label: bool
    missing_section_metadata: bool
    weak_section_coverage: bool

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AbstentionDecision:
    should_abstain: bool
    reasons: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidencePack:
    query: str
    retriever: RetrieverMetadata
    evidence_items: list[EvidenceItem]
    source_coverage_summary: SourceCoverageSummary
    risk_flags: EvidenceRiskFlags
    abstention: AbstentionDecision
    context_block: str

    def to_json(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "retriever": self.retriever.to_json(),
            "evidence_items": [item.to_json() for item in self.evidence_items],
            "source_coverage_summary": self.source_coverage_summary.to_json(),
            "risk_flags": self.risk_flags.to_json(),
            "abstention": self.abstention.to_json(),
            "context_block": self.context_block,
        }


@dataclass
class GuardrailEvidenceSummary:
    evidence_count: int
    unique_source_count: int
    source_priorities_present: list[str]
    evidence_labels_present: list[str]
    section_metadata_coverage: float
    missing_section_metadata_count: int
    missing_source_priority_count: int
    missing_evidence_label_count: int

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardrailDecision:
    decision: str
    should_abstain: bool
    confidence_level: str
    reasons: list[str]
    warnings: list[str]
    failed_rules: list[str]
    passed_rules: list[str]
    evidence_summary: GuardrailEvidenceSummary
    recommended_next_action: str

    def to_json(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "should_abstain": self.should_abstain,
            "confidence_level": self.confidence_level,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "failed_rules": self.failed_rules,
            "passed_rules": self.passed_rules,
            "evidence_summary": self.evidence_summary.to_json(),
            "recommended_next_action": self.recommended_next_action,
        }


@dataclass
class CitationCoverage:
    evidence_item_count: int
    cited_evidence_count: int
    uncited_evidence_count: int
    all_claims_cited: bool

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardrailDecisionSummary:
    decision: str
    should_abstain: bool
    confidence_level: str
    recommended_next_action: str
    warnings: list[str]
    reasons: list[str]

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroundedEvidenceUsed:
    citation_key: str
    source_path: str
    source_title: str
    source_priority: str
    evidence_label: str
    section: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroundedAnswerMetadata:
    generator_name: str
    generator_version: str
    deterministic: bool = True

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroundedAnswer:
    query: str
    answer_status: str
    answer_text: str
    citations_used: list[str]
    citation_coverage: CitationCoverage
    guardrail_decision_summary: GuardrailDecisionSummary
    evidence_used: list[GroundedEvidenceUsed]
    limitations: list[str]
    metadata: GroundedAnswerMetadata

    def to_json(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "answer_status": self.answer_status,
            "answer_text": self.answer_text,
            "citations_used": self.citations_used,
            "citation_coverage": self.citation_coverage.to_json(),
            "guardrail_decision_summary": self.guardrail_decision_summary.to_json(),
            "evidence_used": [item.to_json() for item in self.evidence_used],
            "limitations": self.limitations,
            "metadata": self.metadata.to_json(),
        }


@dataclass
class ComplianceResult:
    compliance_flag: bool
    human_approval_required: bool
    risk_tags: list[str]
    rationale: list[str]
    safe_next_action: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RagAnswer:
    answer_id: str
    question: str
    answer: str
    retrieved_sources: list[dict[str, Any]]
    evidence_labels_used: list[str]
    confidence: str
    verification_status: str
    compliance_flag: bool
    human_approval_required: bool
    risk_tags: list[str]
    limitations: list[str]
    next_action: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)
