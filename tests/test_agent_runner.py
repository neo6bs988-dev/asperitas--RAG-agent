from __future__ import annotations

import copy
import json

import pytest

from asperitas_agent.agent_runner import _response_metadata, ask_agent
from asperitas_agent.answer_verification_integration import ANSWER_VERIFICATION_METADATA_KEY
from asperitas_agent.claim_verifier_schema import AnswerVerificationSummary
from asperitas_agent.schemas import (
    Chunk,
    CitationCoverage,
    GroundedAnswer,
    GroundedAnswerMetadata,
    GuardrailDecisionSummary,
    SourceRecord,
)


def record(source_id: str) -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        title=f"Asperitas Source {source_id}",
        original_filename=f"{source_id}.md",
        path=f"01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/{source_id}.md",
        source_priority="P1",
        source_type="internal",
        disclosure_level="internal",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-14",
        author_or_owner="Asperitas",
        use_case="agent_testing",
        checksum="a" * 64,
        parse_status="parsed",
    )


def chunk(source: SourceRecord, index: int) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::chunk-{index:04d}",
        source_id=source.source_id,
        title=source.title,
        text="Asperitas is described through source-grounded evidence and deterministic agent testing.",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=88,
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
        section="Overview",
        section_heading="Overview",
        section_path=["Overview"],
        section_level=1,
    )


def sample_inputs() -> tuple[list[SourceRecord], list[Chunk]]:
    records = [record("ASP-P1-ONE"), record("ASP-P1-TWO")]
    chunks = [chunk(records[0], 1), chunk(records[1], 2)]
    return records, chunks


def verifier_summary() -> AnswerVerificationSummary:
    return AnswerVerificationSummary(
        answer_id="A-runtime",
        question="What is Asperitas?",
        total_claims=4,
        supported_claims=0,
        partially_supported_claims=0,
        unsupported_claims=1,
        contradicted_claims=1,
        citation_missing_claims=0,
        citation_mismatch_claims=1,
        compliance_blocked_claims=1,
        ambiguous_claims=0,
        not_verifiable_from_context_claims=0,
        answer_faithfulness_status="fail",
        blocking_failures=(
            "contradicted:C2:claim_contradicts_cited_span",
            "compliance_blocked:C4:compliance_sensitive_unverified_claim",
        ),
        warnings=(
            "unsupported:C1:cited_span_does_not_support_claim",
            "citation_mismatch:C3:citation_points_to_wrong_source",
            "compliance_flag:biosafety",
        ),
        metrics={
            "deterministic": True,
            "status_counts": {
                "supported": 0,
                "partially_supported": 0,
                "unsupported": 1,
                "contradicted": 1,
                "citation_missing": 0,
                "citation_mismatch": 1,
                "ambiguous": 0,
                "not_verifiable_from_context": 0,
                "compliance_blocked": 1,
            },
            "claim_ids": ["C1", "C2", "C3", "C4"],
            "citation_keys": ["[E1]", "[E2]", "[E3]", "[E4]"],
            "evidence_span_ids": ["SPAN-1", "SPAN-2"],
            "source_ids": ["SRC-1", "SRC-2"],
            "failure_modes": [
                "citation_points_to_wrong_source",
                "cited_span_does_not_support_claim",
                "claim_contradicts_cited_span",
                "compliance_sensitive_unverified_claim",
            ],
            "compliance_tags": ["biosafety"],
            "diagnostics": ["span_signal:contradiction"],
            "claim_details": [
                {"claim_id": "C1", "support_status": "unsupported", "compliance_tags": []},
                {"claim_id": "C2", "support_status": "contradicted", "compliance_tags": []},
                {"claim_id": "C3", "support_status": "citation_mismatch", "compliance_tags": []},
                {"claim_id": "C4", "support_status": "compliance_blocked", "compliance_tags": ["biosafety"]},
            ],
        },
    )


def empty_verifier_summary() -> AnswerVerificationSummary:
    return AnswerVerificationSummary(
        answer_id="A-empty-runtime",
        question="What is Asperitas?",
        total_claims=0,
        supported_claims=0,
        partially_supported_claims=0,
        unsupported_claims=0,
        contradicted_claims=0,
        citation_missing_claims=0,
        citation_mismatch_claims=0,
        compliance_blocked_claims=0,
        ambiguous_claims=0,
        not_verifiable_from_context_claims=0,
        answer_faithfulness_status="not_scored",
        metrics={"deterministic": True, "status_counts": {}},
    )


def grounded_answer_fixture() -> GroundedAnswer:
    return GroundedAnswer(
        query="What is Asperitas?",
        answer_status="answered",
        answer_text="Runtime answer text remains unchanged [E1].",
        citations_used=["[E1]"],
        citation_coverage=CitationCoverage(
            evidence_item_count=1,
            cited_evidence_count=1,
            uncited_evidence_count=0,
            all_claims_cited=True,
        ),
        guardrail_decision_summary=GuardrailDecisionSummary(
            decision="proceed",
            should_abstain=False,
            confidence_level="high",
            recommended_next_action="Use cited evidence only.",
            warnings=[],
            reasons=[],
        ),
        evidence_used=[],
        limitations=["fixture limitation"],
        metadata=GroundedAnswerMetadata("fixture-generator", "test"),
    )


def test_ask_agent_returns_valid_agent_response_structure():
    records, chunks = sample_inputs()

    response = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()

    assert response["query"] == "What is Asperitas?"
    assert response["top_k"] == 2
    assert response["status"] in {"answered", "caution", "abstained"}
    assert response["answer"]
    assert response["evidence_count"] == 2
    assert response["evidence"]
    assert response["guardrail"]["decision"] in {"proceed", "caution", "abstain"}
    assert response["metadata"]["runner_version"] == "MVP-008"
    assert ANSWER_VERIFICATION_METADATA_KEY not in response["metadata"]


def test_citations_used_are_subset_of_evidence_keys():
    records, chunks = sample_inputs()
    response = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    evidence_keys = {item["citation_key"] for item in response["evidence"]}

    assert set(response["citations_used"]) <= evidence_keys
    assert response["metadata"]["citation_integrity"]["citations_subset_of_evidence"]


def test_ask_agent_output_is_deterministic_for_same_inputs():
    records, chunks = sample_inputs()

    first = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    second = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()

    assert first == second


def test_runtime_answer_verification_metadata_is_passively_attached_when_summary_exists():
    records, chunks = sample_inputs()

    baseline = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    enriched = ask_agent(
        "What is Asperitas?",
        top_k=2,
        records=records,
        chunks=chunks,
        answer_verification_summary=verifier_summary(),
    ).to_json()

    assert enriched["answer"] == baseline["answer"]
    assert enriched["status"] == baseline["status"]
    assert enriched["citations_used"] == baseline["citations_used"]
    assert enriched["evidence"] == baseline["evidence"]
    assert enriched["guardrail"] == baseline["guardrail"]

    enriched_metadata = dict(enriched["metadata"])
    verification = enriched_metadata.pop(ANSWER_VERIFICATION_METADATA_KEY)
    assert enriched_metadata == baseline["metadata"]
    assert verification["answer_faithfulness_status"] == "fail"
    assert verification["status_counts"]["unsupported"] == 1
    assert verification["status_counts"]["contradicted"] == 1
    assert verification["status_counts"]["citation_mismatch"] == 1
    assert verification["status_counts"]["compliance_blocked"] == 1
    assert verification["compliance_tags"] == ["biosafety"]
    assert "compliance_flag:biosafety" in verification["warnings"]


def test_runtime_verifier_metadata_absent_when_summary_absent_and_empty_summary_is_safe():
    records, chunks = sample_inputs()

    absent = ask_agent("What is Asperitas?", top_k=2, records=records, chunks=chunks).to_json()
    empty = ask_agent(
        "What is Asperitas?",
        top_k=2,
        records=records,
        chunks=chunks,
        answer_verification_summary=empty_verifier_summary(),
    ).to_json()

    assert ANSWER_VERIFICATION_METADATA_KEY not in absent["metadata"]
    assert empty["answer"] == absent["answer"]
    assert empty["metadata"][ANSWER_VERIFICATION_METADATA_KEY]["answer_faithfulness_status"] == "not_scored"
    assert json.loads(json.dumps(empty, sort_keys=True, separators=(",", ":"))) == empty


def test_runtime_metadata_attachment_does_not_mutate_inputs_or_call_runtime_pipeline(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("runtime pipeline function should not be called by metadata attachment")

    monkeypatch.setattr("asperitas_agent.agent_runner.search_chunks_mvp003", fail_if_called)
    monkeypatch.setattr("asperitas_agent.agent_runner.build_evidence_pack", fail_if_called)
    monkeypatch.setattr("asperitas_agent.agent_runner.evaluate_evidence_guardrail", fail_if_called)
    monkeypatch.setattr("asperitas_agent.agent_runner.generate_grounded_answer", fail_if_called)

    answer = grounded_answer_fixture()
    summary = verifier_summary()
    before_answer = copy.deepcopy(answer.to_json())
    before_summary = copy.deepcopy(summary.to_dict())
    base_metadata = {
        "runner_name": "local-deterministic-agent-runner",
        "runner_version": "MVP-008",
        "deterministic": True,
    }

    metadata = _response_metadata(
        answer=answer,
        citation_subset_ok=True,
        evidence_keys={"[E1]"},
        retriever_metadata={"retriever_name": "fixture", "retriever_version": "test", "top_k": 1},
        answer_verification_summary=summary,
    )

    assert answer.to_json() == before_answer
    assert summary.to_dict() == before_summary
    assert base_metadata == {
        "runner_name": "local-deterministic-agent-runner",
        "runner_version": "MVP-008",
        "deterministic": True,
    }
    assert metadata[ANSWER_VERIFICATION_METADATA_KEY]["diagnostics"] == ["span_signal:contradiction"]
    assert metadata["answer_generation"] == {"generator_name": "fixture-generator", "generator_version": "test", "deterministic": True}


def test_abstention_path_does_not_produce_unsupported_answer():
    response = ask_agent("No evidence query", top_k=5, records=[], chunks=[]).to_json()

    assert response["status"] == "abstained"
    assert response["evidence_count"] == 0
    assert response["citations_used"] == []
    assert "cannot answer" in response["answer"]
    assert response["guardrail"]["should_abstain"]


def test_invalid_empty_query_fails_cleanly():
    with pytest.raises(ValueError, match="query must not be empty"):
        ask_agent("   ", top_k=5, records=[], chunks=[])


def test_invalid_top_k_fails_cleanly():
    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        ask_agent("What is Asperitas?", top_k=0, records=[], chunks=[])
