from __future__ import annotations

from .answer_contract import build_contract_answer, citation_eligible_items, section_label
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
GENERATOR_VERSION = "V1.3C"


def _evidence_used(items: list[EvidenceItem]) -> list[GroundedEvidenceUsed]:
    return [
        GroundedEvidenceUsed(
            citation_key=item.citation_key,
            source_path=item.source_path,
            source_title=item.source_title,
            source_priority=item.source_priority,
            evidence_label=item.evidence_label,
            section=section_label(item),
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
        return GroundedAnswer(
            query=pack.query,
            answer_status="abstained",
            answer_text=build_contract_answer(pack, decision),
            citations_used=[],
            citation_coverage=_coverage(pack, [], all_claims_cited=True),
            guardrail_decision_summary=_guardrail_summary(decision),
            evidence_used=[],
            limitations=limitations,
            metadata=GroundedAnswerMetadata(generator_name=GENERATOR_NAME, generator_version=GENERATOR_VERSION),
        )

    items = list(pack.evidence_items)
    citations = [item.citation_key for item in citation_eligible_items(items)]
    status = "caution" if decision.decision == "caution" else "answered"
    limitations = _limitations(decision)
    return GroundedAnswer(
        query=pack.query,
        answer_status=status,
        answer_text=build_contract_answer(pack, decision),
        citations_used=citations,
        citation_coverage=_coverage(pack, citations, all_claims_cited=True),
        guardrail_decision_summary=_guardrail_summary(decision),
        evidence_used=_evidence_used(items),
        limitations=limitations,
        metadata=GroundedAnswerMetadata(generator_name=GENERATOR_NAME, generator_version=GENERATOR_VERSION),
    )
