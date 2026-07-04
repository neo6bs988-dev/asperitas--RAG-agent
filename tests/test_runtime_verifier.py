from __future__ import annotations

import json

from asperitas_agent.answer_verification_integration import build_answer_verification_metadata
from asperitas_agent.claim_verifier_schema import AnswerVerificationSummary, SCHEMA_VERSION
from asperitas_agent.runtime_verifier import (
    RUNTIME_DIAGNOSTIC_FIELDS,
    RUNTIME_FALLBACK_DIAGNOSTIC,
    RUNTIME_NOT_COMPLETED_WARNING,
    build_runtime_answer_verification_summary,
)
from asperitas_agent.schemas import EvidenceItem


def runtime_evidence_item(**overrides) -> EvidenceItem:
    kwargs = {
        "rank": 1,
        "chunk_id": "CHUNK-1",
        "score": 0.99,
        "source_id": "SRC-1",
        "source_title": "Runtime Source",
        "source_path": "data/runtime-source.md",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": "Overview",
        "section_heading": "Overview",
        "section_path": ["Overview"],
        "section_level": 1,
        "parent_section": "",
        "subsection": "",
        "text_excerpt": "The source registry preserves source IDs.",
        "citation_key": "[E1]",
    }
    return EvidenceItem(**{**kwargs, **overrides})


def valid_caller_summary() -> AnswerVerificationSummary:
    return AnswerVerificationSummary(
        answer_id="caller-summary",
        question="What is verified?",
        total_claims=0,
        supported_claims=0,
        partially_supported_claims=0,
        unsupported_claims=0,
        contradicted_claims=0,
        citation_missing_claims=0,
        citation_mismatch_claims=0,
        compliance_blocked_claims=0,
        answer_faithfulness_status="not_scored",
        metrics={"deterministic": True},
    )


def invalid_caller_summary() -> AnswerVerificationSummary:
    return AnswerVerificationSummary(
        answer_id="",
        question="What is invalid?",
        total_claims=0,
        supported_claims=0,
        partially_supported_claims=0,
        unsupported_claims=0,
        contradicted_claims=0,
        citation_missing_claims=0,
        citation_mismatch_claims=0,
        compliance_blocked_claims=0,
        answer_faithfulness_status="not_scored",
    )


def test_disabled_runtime_verifier_preserves_absence_or_caller_summary():
    caller_summary = valid_caller_summary()

    assert (
        build_runtime_answer_verification_summary(
            question="What is verified?",
            answer="The source registry preserves source IDs [E1].",
            evidence_items=[runtime_evidence_item()],
            enabled=False,
        )
        is None
    )
    assert (
        build_runtime_answer_verification_summary(
            question="What is verified?",
            answer="The source registry preserves source IDs [E1].",
            evidence_items=[runtime_evidence_item()],
            enabled=False,
            caller_supplied_summary=caller_summary,
        )
        is caller_summary
    )


def test_enabled_runtime_verifier_builds_valid_summary_and_preserves_provenance():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=[runtime_evidence_item()],
        answer_id="A-runtime",
        enabled=True,
    )

    assert summary is not None
    assert summary.validate() == ()
    assert summary.total_claims == 1
    assert summary.supported_claims == 1
    assert summary.answer_faithfulness_status == "pass"

    metrics = summary.metrics
    for key in RUNTIME_DIAGNOSTIC_FIELDS:
        assert key in metrics
    assert metrics["runtime_verifier_enabled"] is True
    assert metrics["runtime_verification_attempted"] is True
    assert metrics["runtime_verification_skipped_reason"] == ""
    assert metrics["metadata_only_fallback_used"] is False
    assert metrics["verifier_input_claim_count"] == 1
    assert metrics["verifier_output_claim_count"] == 1
    assert metrics["verifier_schema_version"] == SCHEMA_VERSION
    assert metrics["claim_ids"] == ["A-runtime-C1"]
    assert metrics["citation_keys"] == ["[E1]"]
    assert metrics["evidence_span_ids"] == ["CHUNK-1"]
    assert metrics["source_ids"] == ["SRC-1"]

    runtime_metadata = metrics["runtime_evidence_metadata"][0]
    assert runtime_metadata["source_priority"] == "P1"
    assert runtime_metadata["evidence_label"] == "Document-Supported Fact"
    assert runtime_metadata["source_path"] == "data/runtime-source.md"
    assert runtime_metadata["chunk_id"] == "CHUNK-1"
    assert runtime_metadata["section_heading"] == "Overview"

    payload = summary.to_dict()
    assert json.loads(json.dumps(payload, sort_keys=True, separators=(",", ":"))) == payload


def test_enabled_runtime_verifier_surfaces_runtime_diagnostics_in_metadata_payload():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=[runtime_evidence_item()],
        answer_id="A-runtime",
        enabled=True,
    )

    metadata = build_answer_verification_metadata(summary)

    for key in RUNTIME_DIAGNOSTIC_FIELDS:
        assert key in metadata
    assert metadata["runtime_verifier_enabled"] is True
    assert metadata["runtime_evidence_metadata"][0]["source_id"] == "SRC-1"
    assert metadata["summary"]["metrics"]["runtime_evidence_metadata"][0]["section"] == "Overview"


def test_missing_runtime_evidence_produces_not_scored_fallback_with_diagnostics():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=None,
        answer_id="A-runtime",
        enabled=True,
    )

    assert summary is not None
    assert summary.validate() == ()
    assert summary.answer_faithfulness_status == "not_scored"
    assert summary.total_claims == 0
    assert RUNTIME_NOT_COMPLETED_WARNING in summary.warnings

    metrics = summary.metrics
    assert metrics["metadata_only_fallback_used"] is True
    assert metrics["runtime_verification_skipped_reason"] == "no_runtime_evidence_items"
    assert metrics["verifier_input_claim_count"] == 1
    assert metrics["verifier_output_claim_count"] == 0
    assert RUNTIME_FALLBACK_DIAGNOSTIC in metrics["diagnostics"]
    assert metrics["claim_ids"] == ["A-runtime-C1"]
    assert metrics["citation_keys"] == ["[E1]"]


def test_incompatible_runtime_evidence_does_not_crash():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=[object()],
        answer_id="A-runtime",
        enabled=True,
    )

    assert summary is not None
    assert summary.answer_faithfulness_status == "not_scored"
    assert summary.metrics["metadata_only_fallback_used"] is True
    assert summary.metrics["runtime_verification_skipped_reason"] == "no_valid_runtime_evidence_spans"
    assert "no_valid_runtime_evidence_spans" in summary.metrics["diagnostics"]


def test_missing_runtime_answer_does_not_crash():
    summary = build_runtime_answer_verification_summary(
        question=None,
        answer=object(),
        evidence_items=[runtime_evidence_item()],
        enabled=True,
    )

    assert summary is not None
    assert summary.answer_faithfulness_status == "not_scored"
    assert summary.question == "question_not_provided"
    assert summary.metrics["runtime_verification_skipped_reason"] == "missing_answer"


def test_invalid_caller_summary_with_enabled_runtime_verifier_falls_back():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=[runtime_evidence_item()],
        enabled=True,
        caller_supplied_summary=invalid_caller_summary(),
    )

    assert summary is not None
    assert summary.answer_faithfulness_status == "not_scored"
    assert summary.metrics["runtime_verification_skipped_reason"] == "caller_supplied_summary_schema_invalid"
    assert summary.metrics["runtime_verifier_error_type"] == "ValueError"


def test_valid_caller_summary_with_enabled_runtime_verifier_gets_runtime_diagnostics():
    summary = build_runtime_answer_verification_summary(
        question="What does the runtime verify?",
        answer="The source registry preserves source IDs [E1].",
        evidence_items=[runtime_evidence_item()],
        enabled=True,
        caller_supplied_summary=valid_caller_summary(),
    )

    assert summary is not None
    assert summary.answer_id == "caller-summary"
    assert summary.answer_faithfulness_status == "not_scored"
    for key in RUNTIME_DIAGNOSTIC_FIELDS:
        assert key in summary.metrics
    assert summary.metrics["runtime_verifier_enabled"] is True
    assert summary.metrics["runtime_verification_attempted"] is False
    assert summary.metrics["runtime_verification_skipped_reason"] == "caller_supplied_summary_preferred"
    assert summary.metrics["metadata_only_fallback_used"] is False
    assert summary.metrics["verifier_input_claim_count"] == 0
    assert summary.metrics["verifier_output_claim_count"] == 0
    assert "caller_supplied_summary_preferred" in summary.metrics["diagnostics"]
