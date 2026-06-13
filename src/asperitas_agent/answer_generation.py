from __future__ import annotations

import re

from .schemas import (
    CitationCoverage,
    EvidenceItem,
    EvidencePack,
    GroundedAnswer,
    GroundedAnswerMetadata,
    GroundedEvidenceUsed,
    GuardrailDecision,
    GuardrailDecisionSummary,
)


GENERATOR_NAME = "deterministic-grounded-answer-composer"
GENERATOR_VERSION = "MVP-007"
MAX_BULLET_CHARS = 260


def _compact(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _cited_excerpt(item: EvidenceItem) -> str:
    excerpt = _compact(item.text_excerpt)
    if not excerpt:
        excerpt = "No excerpt text was available"
    if len(excerpt) > MAX_BULLET_CHARS:
        excerpt = excerpt[: MAX_BULLET_CHARS - 3].rstrip() + "..."
    return f"{excerpt} {item.citation_key}"


def _section_label(item: EvidenceItem) -> str:
    return item.section or item.section_heading or (" > ".join(item.section_path) if item.section_path else "")


def _evidence_used(items: list[EvidenceItem]) -> list[GroundedEvidenceUsed]:
    return [
        GroundedEvidenceUsed(
            citation_key=item.citation_key,
            source_path=item.source_path,
            source_title=item.source_title,
            source_priority=item.source_priority,
            evidence_label=item.evidence_label,
            section=_section_label(item),
        )
        for item in items
    ]


def _guardrail_summary(decision: GuardrailDecision) -> GuardrailDecisionSummary:
    return GuardrailDecisionSummary(
        decision=decision.decision,
        should_abstain=decision.should_abstain,
        confidence_level=decision.confidence_level,
        recommended_next_action=decision.recommended_next_action,
        warnings=list(decision.warnings),
        reasons=list(decision.reasons),
    )


def _limitations(decision: GuardrailDecision) -> list[str]:
    return list(dict.fromkeys([*decision.reasons, *decision.warnings]))


def _coverage(pack: EvidencePack, citations: list[str], all_claims_cited: bool) -> CitationCoverage:
    evidence_count = len(pack.evidence_items)
    cited_count = len(set(citations))
    return CitationCoverage(
        evidence_item_count=evidence_count,
        cited_evidence_count=cited_count,
        uncited_evidence_count=max(evidence_count - cited_count, 0),
        all_claims_cited=all_claims_cited,
    )


def generate_grounded_answer(pack: EvidencePack, decision: GuardrailDecision) -> GroundedAnswer:
    if decision.should_abstain:
        limitations = _limitations(decision) or ["Retrieved evidence was insufficient for a grounded answer."]
        text = (
            "The system cannot answer this query from the retrieved evidence because the guardrail decision requires abstention. "
            f"Recommended next action: {decision.recommended_next_action}."
        )
        return GroundedAnswer(
            query=pack.query,
            answer_status="abstained",
            answer_text=text,
            citations_used=[],
            citation_coverage=_coverage(pack, [], all_claims_cited=True),
            guardrail_decision_summary=_guardrail_summary(decision),
            evidence_used=[],
            limitations=limitations,
            metadata=GroundedAnswerMetadata(generator_name=GENERATOR_NAME, generator_version=GENERATOR_VERSION),
        )

    items = list(pack.evidence_items)
    citations = [item.citation_key for item in items if item.citation_key]
    status = "caution" if decision.decision == "caution" else "answered"
    caveat = (
        "Caution: this draft is based only on the retrieved evidence and should be used with the listed limitations."
        if status == "caution"
        else "This draft is limited to the retrieved cited evidence."
    )
    first_citation = citations[0] if citations else ""
    lines = [f"{caveat} {first_citation}".strip(), "", "Key evidence:"]
    lines.extend(f"- {_cited_excerpt(item)}" for item in items)
    limitations = _limitations(decision)
    if limitations:
        lines.extend(["", "Limitations:"])
        lines.extend(f"- {limitation}" for limitation in limitations)
    return GroundedAnswer(
        query=pack.query,
        answer_status=status,
        answer_text="\n".join(lines),
        citations_used=citations,
        citation_coverage=_coverage(pack, citations, all_claims_cited=True),
        guardrail_decision_summary=_guardrail_summary(decision),
        evidence_used=_evidence_used(items),
        limitations=limitations,
        metadata=GroundedAnswerMetadata(generator_name=GENERATOR_NAME, generator_version=GENERATOR_VERSION),
    )
