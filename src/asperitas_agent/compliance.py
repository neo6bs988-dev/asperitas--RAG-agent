from __future__ import annotations

import re

from .schemas import ComplianceResult


RISK_PATTERNS: dict[str, list[str]] = {
    "CITES": [r"\bCITES\b", "endangered species", "protected species", "멸종", "보호종"],
    "Nagoya": [r"\bNagoya\b", r"\bCBD\b", r"\bABS\b", "나고야", "생물다양성협약", "유전자원"],
    "LMO_GMO": [r"\bLMO\b", r"\bGMO\b", "유전자변형", "유전자 조작", "genetic engineering"],
    "biosafety": ["biosafety", "생물안전", "quarantine", "검역", "environmental release", "field release"],
    "biosecurity": ["biosecurity", "pathogen", "toxin", "venom", "병원체", "독소"],
    "wet_lab": ["wet-lab", "protocol", "transformation", "plasmid", "cloning", "배양", "실험 프로토콜"],
    "permits_trade": ["import", "export", "customs", "permit", "수입", "수출", "허가"],
    "human_animal": ["human", "animal", "IRB", "인체", "동물"],
    "legal_ip": ["legal", "patent", "contract", "법률", "특허", "계약"],
    "financial_investor": ["investor", "fundraising", "IR", "투자", "펀딩"],
    "external_comm": ["external communication", "press release", "customer contract", "public", "보도자료"],
}

HIGH_RISK_TAGS = {
    "CITES",
    "Nagoya",
    "LMO_GMO",
    "biosafety",
    "biosecurity",
    "wet_lab",
    "permits_trade",
    "human_animal",
    "legal_ip",
    "financial_investor",
    "external_comm",
}


def detect_risk_tags(text: str) -> list[str]:
    found: set[str] = set()
    for tag, patterns in RISK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.add(tag)
                break
    return sorted(found)


def scan_compliance(query: str, retrieved_text: str = "") -> ComplianceResult:
    query_tags = detect_risk_tags(query)
    evidence_tags = detect_risk_tags(retrieved_text)
    tags = sorted(set(query_tags) | set(evidence_tags))
    high_risk_context = bool(set(tags) & HIGH_RISK_TAGS)
    high_risk_request = bool(set(query_tags) & HIGH_RISK_TAGS)
    rationale: list[str] = []
    if high_risk_context:
        rationale.append("Query or retrieved evidence touches regulated, confidential, wet-lab, legal, financial, or external-communication risk domains.")
    if high_risk_request:
        rationale.append("The user request itself touches a high-risk domain and requires qualified human review before operational action.")
    elif evidence_tags:
        rationale.append("Risk terms appeared in retrieved evidence; keep the answer high-level and do not convert it into operational instructions.")
    if "wet_lab" in query_tags or "biosecurity" in query_tags or "LMO_GMO" in query_tags:
        rationale.append("Operational biological requests require qualified human review and must not be autonomously executed.")
    if not rationale:
        rationale.append("No configured high-risk compliance trigger was detected.")
    return ComplianceResult(
        compliance_flag=high_risk_context,
        human_approval_required=high_risk_request,
        risk_tags=tags,
        rationale=rationale,
        safe_next_action=(
            "Escalate to qualified human review; provide only high-level, source-grounded analysis until approved."
            if high_risk_request
            else "Proceed with source-grounded answer; keep risk-bearing evidence contextual and non-operational."
            if high_risk_context
            else "Proceed with source-grounded answer and keep unsupported claims labeled."
        ),
    )
