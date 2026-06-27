from __future__ import annotations

import json
import subprocess
from pathlib import Path

from asperitas_agent.agent_runner import ask_agent
from asperitas_agent.answer_generation import generate_grounded_answer
from asperitas_agent.evidence_pack import build_evidence_pack
from asperitas_agent.guardrails import evaluate_evidence_guardrail
from asperitas_agent.schemas import Chunk, SourceRecord


REPO_ROOT = Path(__file__).resolve().parents[1]


def record(source_id: str, path: str = "docs/V1_KNOWN_LIMITATIONS.md") -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        title=f"Asperitas Source {source_id}",
        original_filename=Path(path).name,
        path=path,
        source_priority="P1",
        source_type="internal",
        disclosure_level="internal",
        license_status="internal_use",
        verification_status="verified_internal",
        date="2026-06-27",
        author_or_owner="Asperitas",
        use_case="answer_contract_testing",
        checksum="a" * 64,
        parse_status="parsed",
    )


def chunk(source: SourceRecord, index: int, text: str) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::chunk-{index:04d}",
        source_id=source.source_id,
        title=source.title,
        text=text,
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=len(text),
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
        section="Retrieval And Answering",
        section_heading="Retrieval And Answering",
        section_path=["V1 Known Limitations", "Retrieval And Answering"],
        section_level=2,
    )


def sample_response(query: str = "Can we describe Asperitas as production deployed and biologically validated?") -> dict:
    records = [record("ASP-P1-ONE"), record("ASP-P1-TWO", "docs/V1_RELEASE_CLOSEOUT.md")]
    chunks = [
        chunk(records[0], 1, "V1 is an internal release-candidate with known limitations and no public product workflow."),
        chunk(records[1], 2, "Release closeout evidence is internal and does not establish biological validation."),
    ]
    return ask_agent(query, top_k=2, records=records, chunks=chunks).to_json()


def test_answer_contract_sections_and_citations_are_present_when_evidence_exists():
    response = sample_response()
    answer = response["answer"]

    for heading in (
        "Bottom line:",
        "Internal facts:",
        "Key evidence:",
        "Inference:",
        "Missing evidence:",
        "Limitations/truth-boundary:",
        "Next action:",
    ):
        assert heading in answer
    assert response["citations_used"] == ["[E1]", "[E2]"]
    assert "[E1]" in answer and "[E2]" in answer


def test_answer_contract_does_not_make_unsupported_status_or_approval_claims():
    answer = sample_response()["answer"].casefold()

    forbidden = (
        "production-ready",
        "production ready",
        "wet-lab validated",
        "regulatory approval granted",
        "automatically approved",
    )
    assert not any(term in answer for term in forbidden)
    assert "does not establish production deployment" in answer
    assert "biological validation" in answer


def test_answer_contract_states_uncertainty_when_evidence_is_missing():
    response = ask_agent("No evidence query", top_k=5, records=[], chunks=[]).to_json()

    assert response["status"] == "abstained"
    assert "Missing evidence: no retrieved evidence supports a source-grounded answer." in response["answer"]
    assert "cannot answer" in response["answer"]
    assert response["citations_used"] == []


def test_answer_contract_adds_compliance_gate_and_actionable_next_step():
    records = [
        record("ASP-P1-CITES", "04_AGENT_SYSTEM/guardrails/biosafety_compliance_checklist.md"),
        record("ASP-P1-NAGOYA", "04_AGENT_SYSTEM/guardrails/source_truth_rules.md"),
    ]
    chunks = [
        chunk(records[0], 1, "CITES Nagoya LMO biosafety actions require human approval and review gates."),
        chunk(records[1], 2, "Wet-lab or regulatory-sensitive requests require qualified human review before action."),
    ]
    response = ask_agent(
        "What approvals are required for CITES Nagoya LMO biosafety actions?",
        top_k=2,
        records=records,
        chunks=chunks,
    ).to_json()
    answer = response["answer"]

    assert "Compliance/biosafety/legal gate:" in answer
    assert "Human review is required" in answer
    assert "Next action:" in answer


def test_answer_contract_metadata_version_is_v1_3c():
    response = sample_response()

    assert response["metadata"]["answer_generation"]["generator_version"] == "V1.3C"


def answer_from_results(query: str, results: list[dict]) -> dict:
    pack = build_evidence_pack(query, results, top_k=len(results) or 5)
    decision = evaluate_evidence_guardrail(pack)
    return generate_grounded_answer(pack, decision).to_json()


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
        "section": "Benchmark Boundary",
        "section_heading": "Benchmark Boundary",
        "section_path": ["Benchmark Boundary"],
        "text": text,
    }


def test_p6_is_used_only_as_analogy_not_internal_fact():
    answer = answer_from_results(
        "Compare Asperitas to founder/operator benchmark doctrine.",
        [
            evidence_result(1, "ASP-P1-INTERNAL", "P1", "docs/V1_RELEASE_CLOSEOUT.md", "Asperitas status is internal RC only."),
            evidence_result(
                2,
                "ASP-P6-BENCH",
                "P6",
                "01_RAW_SOURCES/P6_BENCHMARK_OPERATING/benchmark.pdf",
                "Founder operator benchmark pattern describes workflow doctrine.",
                "Inference",
            ),
        ],
    )
    text = answer["answer_text"]

    assert "Internal facts:" in text
    assert "P6 benchmark analogy/doctrine:" in text
    assert "analogy/doctrine only" in text
    assert "cannot override P0-P4/internal evidence" in text


def test_p6_not_decisive_when_internal_source_exists():
    answer = answer_from_results(
        "What is the decisive Asperitas internal status compared with benchmark doctrine?",
        [
            evidence_result(1, "ASP-P1-INTERNAL", "P1", "docs/V1_KNOWN_LIMITATIONS.md", "Internal status remains release-candidate."),
            evidence_result(
                2,
                "ASP-P6-BENCH",
                "P6",
                "01_RAW_SOURCES/P6_BENCHMARK_OPERATING/benchmark.pdf",
                "Benchmark pattern suggests mature operating intelligence.",
                "Inference",
            ),
        ],
    )
    text = answer["answer_text"]

    assert text.index("Internal facts:") < text.index("P6 benchmark analogy/doctrine:")
    assert "No internal/P0-P4 fact evidence was retrieved" not in text
    assert "not Asperitas internal fact evidence" in text


def test_source_map_only_url_is_not_cited_as_ingested_evidence():
    answer = answer_from_results(
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
    )

    assert answer["citations_used"] == []
    assert "[E1]" not in answer["answer_text"]
    assert "Source-map-only URLs are not cited as ingested evidence" in answer["answer_text"]


def test_db_completion_overclaim_is_refused_without_logs():
    answer = answer_from_results(
        "Is external web ingestion complete with production vector DB indexed?",
        [
            evidence_result(
                1,
                "ASP-P6-BENCH",
                "P6",
                "01_RAW_SOURCES/P6_BENCHMARK_OPERATING/benchmark.pdf",
                "Offline deterministic benchmark vector artifacts are not a production vector DB.",
                "Inference",
            )
        ],
    )

    assert "DB-completion or external-ingestion claims are refused" in answer["answer_text"]
    assert "production vector DB is complete" not in answer["answer_text"].casefold()


def test_founder_operator_benchmark_comparison_discloses_status():
    answer = answer_from_results(
        "Give a founder/operator benchmark comparison for Asperitas.",
        [
            evidence_result(1, "ASP-P1-INTERNAL", "P1", "docs/ops/GSTACK_OPERATING_STACK.md", "Internal docs describe local operations."),
            evidence_result(
                2,
                "ASP-P6-BENCH",
                "P6",
                "01_RAW_SOURCES/P6_BENCHMARK_OPERATING/benchmark.pdf",
                "Founder operator workflow benchmark doctrine.",
                "Inference",
            ),
        ],
    )

    assert "Founder/operator or AI-agent benchmark comparison is analogy-only" in answer["answer_text"]
    assert "not an Asperitas internal fact" in answer["answer_text"]


def test_ai_agent_benchmark_comparison_discloses_status():
    answer = answer_from_results(
        "Give an AI-agent benchmark comparison for Asperitas.",
        [
            evidence_result(1, "ASP-P1-INTERNAL", "P1", "docs/ops/AI_DEVELOPMENT_RUNBOOK.md", "Internal docs describe AI development workflow."),
            evidence_result(
                2,
                "ASP-P6-BENCH",
                "P6",
                "01_RAW_SOURCES/P6_BENCHMARK_OPERATING/benchmark.pdf",
                "AI-agent benchmark comparison doctrine.",
                "Inference",
            ),
        ],
    )

    assert "P6 benchmark analogy/doctrine:" in answer["answer_text"]
    assert "Founder/operator or AI-agent benchmark comparison is analogy-only" in answer["answer_text"]


def test_v1_3c_check_script_passes_and_reports_no_retrieval_change():
    completed = subprocess.run(
        ["python", "scripts/check_v1_3c_answer_contract.py", "--overwrite", "--json"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    report = json.loads(completed.stdout)

    assert report["ok"]
    assert report["retrieval_scoring_changed"] is False
    assert report["source_artifacts_mutated"] is False
