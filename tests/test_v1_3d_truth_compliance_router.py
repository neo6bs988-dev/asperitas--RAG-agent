from __future__ import annotations

from pathlib import Path

from asperitas_agent.answer_generation import generate_grounded_answer
from asperitas_agent.evidence_pack import build_evidence_pack
from asperitas_agent.guardrails import evaluate_evidence_guardrail
from asperitas_agent.schemas import CitationCoverage, GroundedAnswer, GroundedAnswerMetadata
from asperitas_agent.truth_compliance_router import route_grounded_answer


def evidence_result(
    rank: int,
    source_id: str,
    priority: str,
    path: str,
    text: str,
    label: str = "Document-Supported Fact",
) -> dict:
    return {
        "chunk_id": f"{source_id}::chunk-{rank:04d}",
        "score": 100 - rank,
        "source_id": source_id,
        "source_title": Path(path).name,
        "source_path": path,
        "source_priority": priority,
        "evidence_label": label,
        "section": "Truth Router",
        "section_heading": "Truth Router",
        "section_path": ["Truth Router"],
        "text": text,
    }


def draft_answer(query: str, results: list[dict], answer_text: str, citations: list[str] | None = None):
    pack = build_evidence_pack(query, results, top_k=len(results) or 5)
    decision = evaluate_evidence_guardrail(pack)
    answer = GroundedAnswer(
        query=query,
        answer_status="answered",
        answer_text=answer_text,
        citations_used=citations or [],
        citation_coverage=CitationCoverage(
            evidence_item_count=len(pack.evidence_items),
            cited_evidence_count=len(citations or []),
            uncited_evidence_count=max(len(pack.evidence_items) - len(citations or []), 0),
            all_claims_cited=True,
        ),
        guardrail_decision_summary=generate_grounded_answer(pack, decision).guardrail_decision_summary,
        evidence_used=[],
        limitations=[],
        metadata=GroundedAnswerMetadata("test-draft", "test"),
    )
    routed, result = route_grounded_answer(pack, decision, answer)
    return routed, result


def test_router_blocks_overclaim_risk_in_drafted_answer():
    routed, result = draft_answer(
        "Is Asperitas production deployed and biologically validated?",
        [evidence_result(1, "ASP-P1", "P1", "docs/V1_KNOWN_LIMITATIONS.md", "Internal RC status only.")],
        "Asperitas is production deployed and biologically validated. [E1]",
        ["[E1]"],
    )

    assert result.blocked
    assert routed.answer_status == "caution"
    assert "Truth/compliance router:" in routed.answer_text
    assert "Unsafe production" in routed.answer_text


def test_router_blocks_p6_override_of_internal_sources():
    routed, result = draft_answer(
        "Can P6 benchmark doctrine override internal status?",
        [
            evidence_result(1, "ASP-P1", "P1", "docs/V1_KNOWN_LIMITATIONS.md", "Internal status remains release-candidate."),
            evidence_result(2, "ASP-P6", "P6", "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/bench.md", "Benchmark doctrine only.", "Inference"),
        ],
        "Benchmark proves the mature status as an Asperitas fact. [E2]",
        ["[E2]"],
    )

    assert result.blocked
    assert "P6 benchmark material is analogy/doctrine only" in routed.answer_text


def test_router_removes_source_map_only_citations():
    routed, result = draft_answer(
        "Can this source-map-only URL be cited as ingested evidence?",
        [
            evidence_result(
                1,
                "ASP-P6-URL",
                "P6",
                "https://example.com/source-map-only",
                "source_mapped_not_ingested external URL metadata",
                "Needs External Verification",
            )
        ],
        "This URL is cited as ingested evidence. [E1]",
        ["[E1]"],
    )

    assert result.blocked
    assert result.removed_citations == ["[E1]"]
    assert routed.citations_used == []


def test_router_blocks_unverified_p1_verified_fact_claim():
    routed, result = draft_answer(
        "Is this unverified P1 note verified?",
        [evidence_result(1, "ASP-P1", "P1", "docs/internal_note.md", "unverified internal note", "Needs External Verification")],
        "This P1 internal source is a verified fact. [E1]",
        ["[E1]"],
    )

    assert result.blocked
    assert "Unverified P1 evidence cannot be stated as verified fact" in routed.answer_text


def test_router_adds_human_review_gate_for_compliance_query():
    routed, result = draft_answer(
        "What legal approvals are required for CITES Nagoya LMO biosafety actions?",
        [evidence_result(1, "ASP-P1", "P1", "04_AGENT_SYSTEM/guardrails/biosafety_compliance_checklist.md", "Human review is required.")],
        "Use the cited internal checklist only. [E1]",
        ["[E1]"],
    )

    assert result.human_review_required
    assert "Compliance/biosafety/legal gate:" in routed.answer_text
    assert "Human review is required" in routed.answer_text


def test_generated_answer_keeps_v1_3c_contract_and_adds_v1_3d_router_when_needed():
    pack = build_evidence_pack(
        "Is external web ingestion complete with production vector DB indexed?",
        [
            evidence_result(
                1,
                "ASP-P6",
                "P6",
                "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/bench.md",
                "Offline deterministic benchmark vector artifacts are not a production vector DB.",
                "Inference",
            )
        ],
        top_k=1,
    )
    answer = generate_grounded_answer(pack, evaluate_evidence_guardrail(pack))

    assert answer.metadata.generator_version == "V1.3C"
    assert "DB-completion or external-ingestion claims are refused" in answer.answer_text
    assert "Truth/compliance router:" in answer.answer_text
    assert "Production, deployment, vector-DB" in answer.answer_text
