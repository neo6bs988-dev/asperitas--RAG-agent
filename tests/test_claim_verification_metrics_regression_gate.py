from __future__ import annotations

import copy
import json
import sys

from asperitas_agent.claim_verification_metrics import build_claim_verification_regression_metrics
from asperitas_agent.claim_verification_report_aggregator import aggregate_claim_verification_reports
from asperitas_agent.claim_verifier_schema import AtomicClaim, EvidenceSpan
from asperitas_agent.support_status_classifier import classify_answer_claim_support, classify_claim_support
from fixtures.claim_verification_biology_compliance_golden_set import (
    ANSWER_ID,
    EXPECTED_COMPLIANCE_TAGS,
    EXPECTED_SUMMARY_COUNTS,
    QUESTION,
    golden_set_claims,
    golden_set_evidence_by_claim_id,
)


FORBIDDEN_RUNTIME_MODULES = {
    "asperitas_agent.answer_generation",
    "asperitas_agent.hybrid_scoring",
    "asperitas_agent.rag",
    "asperitas_agent.reranking",
    "asperitas_agent.retrieval_mvp003",
    "asperitas_agent.retrieval_tfidf",
}


def _golden_reports():
    return classify_answer_claim_support(golden_set_claims(), golden_set_evidence_by_claim_id())


def _golden_summary(reports=None):
    return aggregate_claim_verification_reports(reports or _golden_reports(), answer_id=ANSWER_ID, question=QUESTION)


def _claim(**overrides) -> AtomicClaim:
    kwargs = {
        "claim_id": "A1",
        "answer_id": "ADV-A1",
        "claim_text": "The answer contract includes citation keys [E1].",
        "claim_type": "sourced_fact",
        "source_sentence": "The answer contract includes citation keys [E1].",
        "sentence_index": 0,
        "cited_source_ids": (),
        "cited_span_ids": (),
        "citation_keys": ("[E1]",),
        "required_evidence_type": "deterministic_fixture_only",
        "detected_entities": (),
        "compliance_tags": (),
        "support_status": "not_verifiable_from_context",
        "confidence": None,
        "verifier_notes": "Adversarial fixture awaiting deterministic support classification.",
        "failure_mode": "verifier_not_applicable",
        "blocking": False,
        "metadata": {"fixture": "v1_5g_adversarial_metrics_gate"},
    }
    return AtomicClaim(**{**kwargs, **overrides})


def _span(**overrides) -> EvidenceSpan:
    kwargs = {
        "source_id": "ADV-SRC-1",
        "span_id": "E1",
        "document_title": "V1.5G adversarial verifier fixture",
        "section": "Verifier metrics",
        "locator": "fixture:E1",
        "evidence_text_hash_or_excerpt": "The answer contract includes citation keys.",
        "metadata": {"source_priority": "P3", "fixture_source_rights": "synthetic_fixture_text"},
        "license_tags": ("fixture_public",),
        "compliance_tags": (),
        "retrieval_rank": 1,
        "retrieval_score": 1.0,
        "citation_key": "[E1]",
        "chunk_id": "adv-chunk-1",
        "source_path": "tests/test_claim_verification_metrics_regression_gate.py::fixture",
        "section_heading": "Verifier metrics",
        "section_path": ("Verifier metrics",),
    }
    return EvidenceSpan(**{**kwargs, **overrides})


def test_biology_compliance_golden_set_metrics_regression_gate():
    reports = _golden_reports()
    summary = _golden_summary(reports)
    metrics = build_claim_verification_regression_metrics(summary, reports)

    expected_status_counts = {
        "supported": EXPECTED_SUMMARY_COUNTS["supported_claims"],
        "partially_supported": EXPECTED_SUMMARY_COUNTS["partially_supported_claims"],
        "unsupported": EXPECTED_SUMMARY_COUNTS["unsupported_claims"],
        "contradicted": EXPECTED_SUMMARY_COUNTS["contradicted_claims"],
        "citation_missing": EXPECTED_SUMMARY_COUNTS["citation_missing_claims"],
        "citation_mismatch": EXPECTED_SUMMARY_COUNTS["citation_mismatch_claims"],
        "ambiguous": EXPECTED_SUMMARY_COUNTS["ambiguous_claims"],
        "not_verifiable_from_context": EXPECTED_SUMMARY_COUNTS["not_verifiable_from_context_claims"],
        "compliance_blocked": EXPECTED_SUMMARY_COUNTS["compliance_blocked_claims"],
    }

    assert metrics.total_claims == 9
    assert metrics.status_counts == expected_status_counts
    assert metrics.contradiction_count == 1
    assert metrics.citation_missing_count == 0
    assert metrics.citation_mismatch_count == 1
    assert metrics.unsupported_count == 1
    assert metrics.not_verifiable_count == 1
    assert metrics.ambiguous_count == 0
    assert metrics.compliance_tag_counts == {
        "biosafety": 1,
        "cites": 1,
        "export_or_security_sensitive_biology": 1,
        "ip_license": 1,
        "nagoya_abs": 1,
    }
    assert metrics.license_tag_counts == {
        "fixture_only": 1,
        "fixture_public": 7,
        "fixture_source_permission": 1,
        "source_permission_required": 2,
    }
    assert metrics.provenance_coverage_count == 10
    assert metrics.metadata_json_safe is True
    assert metrics.deterministic_ordering is True
    assert summary.metrics["compliance_tags"] == list(EXPECTED_COMPLIANCE_TAGS)
    assert "legal_regulatory_approval_claim" not in metrics.compliance_tag_counts
    assert "legal_regulatory_approval_claim" not in json.dumps(metrics.to_dict(), sort_keys=True)


def test_adversarial_security_metrics_cover_blockers_and_warnings():
    reports = [
        classify_claim_support(
            _claim(claim_id="A1", claim_text="Treatment increases pathway activity [E1]."),
            [_span(evidence_text_hash_or_excerpt="Treatment decreases pathway activity.")],
        ),
        classify_claim_support(
            _claim(claim_id="A2", claim_text="The source registry preserves source priority [E2].", citation_keys=("[E2]",)),
            [_span(span_id="E2", citation_key="[E2]", evidence_text_hash_or_excerpt="The answer contract includes citation keys.")],
        ),
        classify_claim_support(
            _claim(claim_id="A3", claim_text="The verifier preserves malformed citation input [E1].", citation_keys=("[E1]; DROP TABLE evidence",)),
            [_span(span_id="E1", citation_key="[E1]")],
        ),
        classify_claim_support(
            _claim(claim_id="A4", claim_text="The answer contract includes citation keys [E1]."),
            [_span(evidence_text_hash_or_excerpt="N/A")],
        ),
    ]
    summary = aggregate_claim_verification_reports(reports, answer_id="ADV-A1", question="What fails safely?")
    metrics = build_claim_verification_regression_metrics(summary, reports)

    assert metrics.status_counts["contradicted"] == 1
    assert metrics.status_counts["unsupported"] == 1
    assert metrics.status_counts["citation_mismatch"] == 1
    assert metrics.status_counts["not_verifiable_from_context"] == 1
    assert metrics.blocking_diagnostic_count == 4
    assert metrics.warning_diagnostic_count >= 4
    assert "matcher_diagnostic:malformed_citation_key" in summary.warnings
    assert "span_signal:contradiction" in summary.metrics["diagnostics"]
    assert "span_signal:not_verifiable" in summary.metrics["diagnostics"]
    assert metrics.metadata_json_safe is True
    assert metrics.deterministic_ordering is True


def test_metrics_gate_is_json_safe_deterministic_non_mutating_and_runtime_bounded():
    claims = golden_set_claims()
    evidence_by_claim_id = golden_set_evidence_by_claim_id()
    before_claims = copy.deepcopy([claim.to_dict() for claim in claims])
    before_evidence = copy.deepcopy(
        {claim_id: [span.to_dict() for span in spans] for claim_id, spans in evidence_by_claim_id.items()}
    )
    before_modules = set(sys.modules)

    first_reports = classify_answer_claim_support(claims, evidence_by_claim_id)
    first_summary = aggregate_claim_verification_reports(first_reports, answer_id=ANSWER_ID, question=QUESTION)
    first_metrics = build_claim_verification_regression_metrics(first_summary, first_reports)
    second_reports = classify_answer_claim_support(claims, evidence_by_claim_id)
    second_summary = aggregate_claim_verification_reports(second_reports, answer_id=ANSWER_ID, question=QUESTION)
    second_metrics = build_claim_verification_regression_metrics(second_summary, second_reports)

    assert [claim.to_dict() for claim in claims] == before_claims
    assert {claim_id: [span.to_dict() for span in spans] for claim_id, spans in evidence_by_claim_id.items()} == before_evidence
    assert first_metrics.to_dict() == second_metrics.to_dict()
    encoded = json.dumps(first_metrics.to_dict(), sort_keys=True, separators=(",", ":"))
    assert json.loads(encoded) == first_metrics.to_dict()
    assert first_metrics.metadata_json_safe is True
    assert first_metrics.deterministic_ordering is True
    assert not (set(sys.modules) - before_modules) & FORBIDDEN_RUNTIME_MODULES
