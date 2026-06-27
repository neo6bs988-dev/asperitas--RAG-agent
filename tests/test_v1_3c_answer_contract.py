from __future__ import annotations

import json
import subprocess
from pathlib import Path

from asperitas_agent.agent_runner import ask_agent
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
        "Source-supported facts:",
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
