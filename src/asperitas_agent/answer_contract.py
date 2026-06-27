from __future__ import annotations

import re

from .schemas import EvidenceItem, EvidencePack, GuardrailDecision


CONTRACT_NAME = "v1.3c-internal-answer-contract"
CONTRACT_VERSION = "V1.3C"
MAX_BULLET_CHARS = 260

COMPLIANCE_TERMS = {
    "approval",
    "approvals",
    "biosafety",
    "biosecurity",
    "cites",
    "compliance",
    "gmo",
    "human approval",
    "legal",
    "lmo",
    "nagoya",
    "regulatory",
    "wet-lab",
    "wet lab",
}
STATUS_TERMS = {
    "biological",
    "biologically",
    "deployed",
    "deployment",
    "legal approval",
    "production",
    "regulatory approval",
    "validated",
    "validation",
    "wet-lab validated",
}
UNSUPPORTED_CLAIM_TERMS = {
    "production-ready",
    "production ready",
    "regulatory approval granted",
    "wet-lab validated",
}


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def cited_excerpt(item: EvidenceItem) -> str:
    excerpt = compact_text(item.text_excerpt) or "No excerpt text was available"
    if len(excerpt) > MAX_BULLET_CHARS:
        excerpt = excerpt[: MAX_BULLET_CHARS - 3].rstrip() + "..."
    return f"{excerpt} {item.citation_key}"


def section_label(item: EvidenceItem) -> str:
    return item.section or item.section_heading or (" > ".join(item.section_path) if item.section_path else "n/a")


def requires_compliance_gate(query: str, items: list[EvidenceItem], decision: GuardrailDecision) -> bool:
    haystack = " ".join(
        [
            query,
            *decision.warnings,
            *decision.reasons,
            *(item.source_path for item in items),
            *(item.text_excerpt for item in items[:2]),
        ]
    ).casefold()
    return any(term in haystack for term in COMPLIANCE_TERMS)


def asks_status_claim(query: str) -> bool:
    lowered = query.casefold()
    return any(term in lowered for term in STATUS_TERMS)


def missing_evidence_line(pack: EvidencePack, decision: GuardrailDecision) -> str:
    if decision.should_abstain:
        return "Missing evidence: no retrieved evidence supports a source-grounded answer."
    missing: list[str] = []
    summary = pack.source_coverage_summary
    if summary.missing_section_metadata_count:
        missing.append("some retrieved evidence lacks section metadata")
    if summary.missing_source_priority_count:
        missing.append("some retrieved evidence lacks source priority")
    if summary.missing_evidence_label_count:
        missing.append("some retrieved evidence lacks evidence labels")
    if not missing:
        return "Missing evidence: no additional missing evidence was detected by this deterministic contract check."
    return "Missing evidence: " + "; ".join(missing) + "."


def bottom_line(pack: EvidencePack, decision: GuardrailDecision) -> str:
    citation = pack.evidence_items[0].citation_key if pack.evidence_items else ""
    if decision.should_abstain:
        return (
            "Bottom line: The system cannot answer from the retrieved evidence because the guardrail decision "
            f"requires abstention. Recommended next action: {decision.recommended_next_action}."
        )
    if asks_status_claim(pack.query):
        return (
            "Bottom line: The retrieved evidence supports only an internal, source-grounded status answer; "
            "it does not establish production deployment, biological validation, legal clearance, or regulatory clearance. "
            f"{citation}".strip()
        )
    if decision.decision == "caution":
        return (
            "Bottom line: Answer with caution from the retrieved cited evidence only; use the limitations and any "
            f"human-review gate before acting. {citation}".strip()
        )
    return f"Bottom line: Answer from the retrieved cited evidence only. {citation}".strip()


def build_contract_answer(pack: EvidencePack, decision: GuardrailDecision) -> str:
    items = list(pack.evidence_items)
    if decision.should_abstain:
        return "\n".join(
            [
                bottom_line(pack, decision),
                missing_evidence_line(pack, decision),
                "Limitations/truth-boundary:",
                "- No source-grounded evidence was retrieved, so no factual, production, validation, legal, or regulatory claim is supported.",
                f"Next action: {decision.recommended_next_action}.",
            ]
        )

    citations = [item.citation_key for item in items if item.citation_key]
    first_citation = citations[0] if citations else ""
    status = "caution" if decision.decision == "caution" else "answered"
    caveat = (
        "Caution: this draft is based only on the retrieved evidence and should be used with the listed limitations."
        if status == "caution"
        else "This draft is limited to the retrieved cited evidence."
    )
    lines = [
        bottom_line(pack, decision),
        f"{caveat} {first_citation}".strip(),
        "",
        "Source-supported facts:",
    ]
    lines.extend(f"- {_source_fact(item)}" for item in items)
    lines.extend(["", "Key evidence:"])
    lines.extend(f"- {cited_excerpt(item)}" for item in items)
    lines.extend(["", "Inference:"])
    lines.append("- Any synthesis above is a bounded inference from the cited retrieved evidence, not a new source claim.")
    lines.extend(["", missing_evidence_line(pack, decision)])
    limitations = list(dict.fromkeys([*decision.reasons, *decision.warnings]))
    lines.extend(["", "Limitations/truth-boundary:"])
    if limitations:
        lines.extend(f"- {limitation}" for limitation in limitations)
    lines.append(
        "- This answer does not establish production deployment, wet-lab capability, biological validation, legal clearance, or regulatory clearance."
    )
    if requires_compliance_gate(pack.query, items, decision):
        lines.extend(["", "Compliance/biosafety/legal gate:"])
        lines.append("- Human review is required before public, investor, legal, regulatory, biosafety, or wet-lab-sensitive use.")
    lines.extend(["", f"Next action: {decision.recommended_next_action}."])
    return "\n".join(lines)


def _source_fact(item: EvidenceItem) -> str:
    source = item.source_path or item.source_title or item.source_id or "unknown source"
    label = item.evidence_label or "unlabeled evidence"
    priority = item.source_priority or "unknown priority"
    section = section_label(item)
    return f"{source} ({priority}, {label}, section: {section}) supports this evidence item. {item.citation_key}"
