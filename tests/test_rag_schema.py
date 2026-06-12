from asperitas_agent.rag import build_answer
from asperitas_agent.schemas import Chunk


def make_chunk(text: str) -> Chunk:
    return Chunk(
        chunk_id="c1",
        source_id="ASP-P0-1",
        title="AOS",
        text=text,
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=len(text),
        source_priority="P0",
        source_type="prompt",
        disclosure_level="confidential",
        evidence_label="Document-Supported Fact",
        verification_status="verified_internal",
        risk_tags=[],
        checksum="abc",
    )


def test_rag_answer_includes_required_fields():
    answer = build_answer("AOS source hierarchy", [make_chunk("AOS source hierarchy defines P0 through P6.")])
    data = answer.to_json()

    assert data["evidence_labels_used"]
    assert data["limitations"]
    assert data["next_action"]


def test_high_risk_answer_requires_human_approval():
    answer = build_answer("CITES export permit for protected species", [make_chunk("CITES requires careful compliance review.")])

    assert answer.compliance_flag
    assert answer.human_approval_required


def test_strategy_answer_is_not_blocked_by_cautionary_retrieved_context():
    answer = build_answer(
        "Asperitas AI agent development priority",
        [make_chunk("The agent roadmap says autonomous wet-lab execution is not part of the MVP.")],
    )

    assert answer.compliance_flag
    assert not answer.human_approval_required
    assert "Retrieved evidence summary" in answer.answer
