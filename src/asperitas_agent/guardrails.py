from __future__ import annotations

from dataclasses import dataclass

from .schemas import EvidencePack, GuardrailDecision, GuardrailEvidenceSummary


@dataclass(frozen=True)
class GuardrailConfig:
    min_evidence_count: int = 2
    min_unique_sources: int = 2
    min_section_coverage: float = 0.5


def _evidence_summary(pack: EvidencePack) -> GuardrailEvidenceSummary:
    summary = pack.source_coverage_summary
    evidence_count = len(pack.evidence_items)
    section_coverage = 0.0 if evidence_count == 0 else (evidence_count - summary.missing_section_metadata_count) / evidence_count
    return GuardrailEvidenceSummary(
        evidence_count=evidence_count,
        unique_source_count=summary.unique_source_count,
        source_priorities_present=list(summary.source_priorities_present),
        evidence_labels_present=list(summary.evidence_labels_present),
        section_metadata_coverage=round(section_coverage, 6),
        missing_section_metadata_count=summary.missing_section_metadata_count,
        missing_source_priority_count=summary.missing_source_priority_count,
        missing_evidence_label_count=summary.missing_evidence_label_count,
    )


def evaluate_evidence_guardrail(pack: EvidencePack, config: GuardrailConfig | None = None) -> GuardrailDecision:
    config = config or GuardrailConfig()
    summary = _evidence_summary(pack)
    reasons: list[str] = []
    warnings: list[str] = []
    failed_rules: list[str] = []
    passed_rules: list[str] = []

    if summary.evidence_count == 0:
        reasons.append("No evidence found.")
        failed_rules.append("no_evidence")
        return GuardrailDecision(
            decision="abstain",
            should_abstain=True,
            confidence_level="none",
            reasons=reasons,
            warnings=warnings,
            failed_rules=failed_rules,
            passed_rules=passed_rules,
            evidence_summary=summary,
            recommended_next_action="abstain_due_to_insufficient_evidence",
        )
    passed_rules.append("evidence_present")

    if summary.evidence_count < config.min_evidence_count:
        warnings.append(f"Evidence count below minimum threshold: {summary.evidence_count} < {config.min_evidence_count}.")
        failed_rules.append("minimum_evidence_count")
    else:
        passed_rules.append("minimum_evidence_count")

    if summary.unique_source_count < config.min_unique_sources:
        warnings.append("Low source diversity.")
        failed_rules.append("source_diversity")
    else:
        passed_rules.append("source_diversity")

    if summary.missing_source_priority_count:
        warnings.append("One or more evidence items are missing source priority.")
        failed_rules.append("source_priority_present")
    else:
        passed_rules.append("source_priority_present")

    if summary.missing_evidence_label_count:
        warnings.append("One or more evidence items are missing evidence label.")
        failed_rules.append("evidence_label_present")
    else:
        passed_rules.append("evidence_label_present")

    if summary.missing_section_metadata_count:
        warnings.append("One or more evidence items are missing section metadata.")
        failed_rules.append("section_metadata_present")
    else:
        passed_rules.append("section_metadata_present")

    if summary.section_metadata_coverage < config.min_section_coverage:
        warnings.append("Section metadata coverage is weak.")
        failed_rules.append("section_coverage")
    else:
        passed_rules.append("section_coverage")

    all_missing_priority = summary.missing_source_priority_count == summary.evidence_count
    all_missing_labels = summary.missing_evidence_label_count == summary.evidence_count
    sparse_and_weak_sections = summary.evidence_count < config.min_evidence_count and summary.section_metadata_coverage < config.min_section_coverage

    if all_missing_priority:
        reasons.append("All evidence items are missing source priority.")
    if all_missing_labels:
        reasons.append("All evidence items are missing evidence labels.")
    if sparse_and_weak_sections:
        reasons.append("Evidence is sparse and section coverage is weak.")

    if reasons:
        return GuardrailDecision(
            decision="abstain",
            should_abstain=True,
            confidence_level="low",
            reasons=reasons,
            warnings=warnings,
            failed_rules=failed_rules,
            passed_rules=passed_rules,
            evidence_summary=summary,
            recommended_next_action="abstain_due_to_insufficient_evidence",
        )

    if warnings:
        confidence = "low" if summary.evidence_count < config.min_evidence_count else "medium"
        return GuardrailDecision(
            decision="caution",
            should_abstain=False,
            confidence_level=confidence,
            reasons=[],
            warnings=warnings,
            failed_rules=failed_rules,
            passed_rules=passed_rules,
            evidence_summary=summary,
            recommended_next_action="answer_with_citations_and_caveats",
        )

    return GuardrailDecision(
        decision="proceed",
        should_abstain=False,
        confidence_level="high",
        reasons=[],
        warnings=[],
        failed_rules=failed_rules,
        passed_rules=passed_rules,
        evidence_summary=summary,
        recommended_next_action="answer_allowed",
    )
