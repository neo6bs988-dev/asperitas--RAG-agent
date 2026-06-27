from __future__ import annotations

from dataclasses import dataclass, field

from .answer_contract import (
    asks_db_completion_claim,
    is_p6_benchmark,
    is_source_map_only,
    requires_compliance_gate,
)
from .schemas import EvidencePack, GroundedAnswer, GuardrailDecision


ROUTER_NAME = "v1.3d-truth-compliance-router"
ROUTER_VERSION = "V1.3D"

INTERNAL_PRIORITIES = {"P0", "P1", "P2", "P3", "P4"}
UNVERIFIED_LABELS = {"Needs External Verification", "Speculation"}
OVERCLAIM_TERMS = (
    "production-ready",
    "production ready",
    "production deployed",
    "deployed in production",
    "wet-lab validated",
    "biologically validated",
    "has legal clearance",
    "has regulatory clearance",
    "legal clearance granted",
    "regulatory clearance granted",
    "regulatory approval granted",
    "full external ingestion",
    "external ingestion is complete",
    "production vector db is complete",
    "foundation-model complete",
    "foundation model complete",
)
P6_FACT_CLAIM_TERMS = (
    "p6 proves",
    "benchmark proves",
    "benchmark evidence establishes",
    "as an asperitas fact",
)
HUMAN_REVIEW_LINE = "Human review is required before public, investor, legal, regulatory, biosafety, or wet-lab-sensitive use."


@dataclass(frozen=True)
class RouterFinding:
    rule_id: str
    severity: str
    message: str

    def to_json(self) -> dict[str, str]:
        return {"rule_id": self.rule_id, "severity": self.severity, "message": self.message}


@dataclass(frozen=True)
class RouterResult:
    router_name: str = ROUTER_NAME
    router_version: str = ROUTER_VERSION
    blocked: bool = False
    human_review_required: bool = False
    findings: list[RouterFinding] = field(default_factory=list)
    removed_citations: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, object]:
        return {
            "router_name": self.router_name,
            "router_version": self.router_version,
            "blocked": self.blocked,
            "human_review_required": self.human_review_required,
            "removed_citations": list(self.removed_citations),
            "findings": [finding.to_json() for finding in self.findings],
        }


def route_grounded_answer(pack: EvidencePack, decision: GuardrailDecision, answer: GroundedAnswer) -> tuple[GroundedAnswer, RouterResult]:
    findings = _findings(pack, decision, answer)
    removed = _source_map_citations(pack, answer)
    if removed:
        findings.append(
            RouterFinding(
                "source_map_only_citation_block",
                "block",
                "Source-map-only URLs cannot be cited as ingested evidence.",
            )
        )
    human_review_required = requires_compliance_gate(pack.query, list(pack.evidence_items), decision)
    blocked = any(finding.severity == "block" for finding in findings)
    routed_text = _append_router_block(answer.answer_text, findings, human_review_required)
    answer.answer_text = routed_text
    answer.citations_used = [citation for citation in answer.citations_used if citation not in set(removed)]
    answer.citation_coverage.cited_evidence_count = len(set(answer.citations_used))
    answer.citation_coverage.uncited_evidence_count = max(
        answer.citation_coverage.evidence_item_count - answer.citation_coverage.cited_evidence_count,
        0,
    )
    if blocked and answer.answer_status == "answered":
        answer.answer_status = "caution"
    result = RouterResult(blocked=blocked, human_review_required=human_review_required, findings=findings, removed_citations=removed)
    return answer, result


def _findings(pack: EvidencePack, decision: GuardrailDecision, answer: GroundedAnswer) -> list[RouterFinding]:
    text = answer.answer_text.casefold()
    query = pack.query.casefold()
    items = list(pack.evidence_items)
    findings: list[RouterFinding] = []
    internal_items = [item for item in items if item.source_priority in INTERNAL_PRIORITIES and not is_source_map_only(item)]
    p6_items = [item for item in items if is_p6_benchmark(item) and not is_source_map_only(item)]
    source_map_items = [item for item in items if is_source_map_only(item)]
    has_overclaim = _has_unsafe_overclaim(answer.answer_text)
    if decision.should_abstain and has_overclaim:
        findings.append(RouterFinding("missing_evidence_overclaim_block", "block", "Missing-evidence answers cannot contain production, validation, legal, regulatory, or completion claims."))
    if has_overclaim:
        findings.append(RouterFinding("overclaim_risk_block", "block", "Unsafe production, wet-lab, legal, regulatory, ingestion, vector-DB, or model-completion overclaim detected."))
    if p6_items and internal_items and any(term in text for term in P6_FACT_CLAIM_TERMS):
        findings.append(RouterFinding("p6_internal_override_block", "block", "P6 benchmark material is analogy/doctrine only and cannot override P0-P4/internal evidence."))
    if source_map_items and ("cited as ingested evidence" in text or "ingested evidence citation" in text) and "cannot" not in text:
        findings.append(RouterFinding("source_map_evidence_block", "block", "Source-map-only URLs cannot be treated as ingested evidence."))
    if _has_unverified_p1(items) and _claims_verified_p1_fact(text):
        findings.append(RouterFinding("unverified_p1_fact_block", "block", "Unverified P1 evidence cannot be stated as verified fact."))
    if asks_db_completion_claim(pack.query) and not _has_completion_logs(items):
        findings.append(RouterFinding("completion_claim_evidence_block", "block", "Production, deployment, vector-DB, and full-external-ingestion claims require explicit completion logs."))
    if ("foundation" in query or "foundation" in text) and "complete" in text and not _has_completion_logs(items):
        findings.append(RouterFinding("foundation_model_completion_block", "block", "Foundation-model completion claims require explicit evidence."))
    return list(dict.fromkeys(findings))


def _source_map_citations(pack: EvidencePack, answer: GroundedAnswer) -> list[str]:
    source_map_keys = {item.citation_key for item in pack.evidence_items if is_source_map_only(item)}
    return sorted(set(answer.citations_used) & source_map_keys)


def _has_unsafe_overclaim(answer_text: str) -> bool:
    safe_boundary_markers = (
        "never say",
        "does not establish",
        "not establish",
        "not a production",
        "not production",
        "cannot claim",
        "cannot support",
        "claims are refused",
        "refused unless",
        "without evidence",
    )
    for line in answer_text.casefold().splitlines():
        if any(marker in line for marker in safe_boundary_markers):
            continue
        if any(term in line for term in OVERCLAIM_TERMS):
            return True
    return False


def _has_unverified_p1(items: list) -> bool:
    return any(
        item.source_priority == "P1"
        and (item.evidence_label in UNVERIFIED_LABELS or "unverified" in item.text_excerpt.casefold() or "needs review" in item.text_excerpt.casefold())
        for item in items
    )


def _claims_verified_p1_fact(text: str) -> bool:
    return ("verified fact" in text or "verified internal fact" in text) and ("p1" in text or "internal" in text)


def _has_completion_logs(items: list) -> bool:
    haystack = " ".join(" ".join([item.source_path, item.source_title, item.text_excerpt]) for item in items).casefold()
    return all(term in haystack for term in ("acquisition", "license", "chunk", "embed", "index", "eval"))


def _append_router_block(answer_text: str, findings: list[RouterFinding], human_review_required: bool) -> str:
    lines = [answer_text.rstrip()]
    if findings:
        lines.extend(["", "Truth/compliance router:"])
        lines.extend(f"- Blocked unsafe overclaim: {finding.message}" for finding in findings if finding.severity == "block")
    if human_review_required and HUMAN_REVIEW_LINE not in answer_text:
        if "Truth/compliance router:" not in lines:
            lines.extend(["", "Truth/compliance router:"])
        lines.append(f"- Compliance/biosafety/legal gate: {HUMAN_REVIEW_LINE}")
    return "\n".join(lines)
