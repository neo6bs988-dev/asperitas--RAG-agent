from __future__ import annotations

import hashlib
import textwrap

from .compliance import scan_compliance
from .retrieval_tfidf import search_chunks
from .schemas import Chunk, RagAnswer


def build_answer(question: str, chunks: list[Chunk], limit: int = 5) -> RagAnswer:
    results = search_chunks(question, chunks, limit=limit)
    retrieved_text = "\n".join(result.chunk.text for result in results)
    compliance = scan_compliance(question, retrieved_text)
    retrieved_sources = [result.to_json() for result in results]
    evidence_labels = sorted({result.chunk.evidence_label for result in results})
    verification_statuses = sorted({result.chunk.verification_status for result in results}) or ["needs_review"]
    snippets = [
        f"- {result.chunk.title} ({result.chunk.source_id}, {result.chunk.evidence_label}): "
        f"{textwrap.shorten(' '.join(result.chunk.text.split()), width=260, placeholder='...')}"
        for result in results
    ]
    if compliance.human_approval_required:
        answer = (
            "Compliance review required before producing an operational or external-facing answer.\n"
            + "\n".join(compliance.rationale)
        )
    elif snippets:
        answer = "Retrieved evidence summary:\n" + "\n".join(snippets)
    else:
        answer = "No source-grounded evidence was retrieved for this question."
    limitations = [
        "MVP-001 uses local lexical retrieval, not production vector search.",
        "No legal, regulatory, compliance, wet-lab, or external communication approval is implied.",
    ]
    if not results:
        limitations.append("No matching chunks were found; missing evidence must be labeled before acting.")
    return RagAnswer(
        answer_id="ANS-" + hashlib.sha256(question.encode("utf-8")).hexdigest()[:12].upper(),
        question=question,
        answer=answer,
        retrieved_sources=retrieved_sources,
        evidence_labels_used=evidence_labels,
        confidence="medium" if results and not compliance.human_approval_required else "low",
        verification_status=";".join(verification_statuses),
        compliance_flag=compliance.compliance_flag,
        human_approval_required=compliance.human_approval_required,
        risk_tags=compliance.risk_tags,
        limitations=limitations,
        next_action=compliance.safe_next_action if compliance.compliance_flag else "Use cited sources only; label unsupported claims.",
    )
