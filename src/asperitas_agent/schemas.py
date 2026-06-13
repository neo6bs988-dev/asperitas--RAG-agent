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
