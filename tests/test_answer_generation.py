from __future__ import annotations

from pathlib import Path

from asperitas_agent.answer_generation import generate_grounded_answer
from asperitas_agent.chunking import read_chunks
from asperitas_agent.evidence_pack import build_evidence_pack
from asperitas_agent.guardrails import evaluate_evidence_guardrail
from asperitas_agent.registry import read_registry
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003


REPO_ROOT = Path(__file__).resolve().parents[1]


def item(rank: int, source_id: str, section: str = "Methods") -> dict:
    return {
        "chunk_id": f"{source_id}::chunk-{rank:04d}",
        "score": 10.0 - rank,
        "source_id": source_id,
        "source_title": f"Source {source_id}",
        "source_file": f"source/{source_id}.md",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": section,
        "section_heading": section,
        "section_path": [section] if section else [],
        "section_level": 1 if section else None,
        "text": f"Evidence statement {rank} about Asperitas.",
    }


def answer_for(results: list[dict]):
    pack = build_evidence_pack("What is Asperitas?", results, top_k=len(results) or 5)
    decision = evaluate_evidence_guardrail(pack)
    return generate_grounded_answer(pack, decision).to_json()


def test_abstain_guardrail_produces_abstained_answer():
    answer = answer_for([])

    assert answer["answer_status"] == "abstained"
    assert "cannot answer" in answer["answer_text"]
    assert answer["citations_used"] == []
    assert answer["limitations"]


def test_caution_guardrail_produces_caution_answer_with_warnings():
    answer = answer_for([item(1, "s1", section=""), item(2, "s2")])

    assert answer["answer_status"] == "caution"
    assert "Caution:" in answer["answer_text"]
    assert answer["guardrail_decision_summary"]["warnings"]
    assert answer["limitations"]


def test_proceed_guardrail_produces_answered_answer():
    answer = answer_for([item(1, "s1"), item(2, "s2")])

    assert answer["answer_status"] == "answered"
    assert answer["guardrail_decision_summary"]["decision"] == "proceed"
    assert answer["metadata"]["deterministic"]


def test_answer_text_includes_citation_markers_when_evidence_exists():
    answer = answer_for([item(1, "s1"), item(2, "s2")])

    assert "[E1]" in answer["answer_text"]
    assert "[E2]" in answer["answer_text"]


def test_citations_used_are_subset_of_evidence_pack_keys():
    answer = answer_for([item(1, "s1"), item(2, "s2")])
    evidence_keys = {evidence["citation_key"] for evidence in answer["evidence_used"]}

    assert set(answer["citations_used"]) <= evidence_keys


def test_no_fabricated_citation_keys():
    answer = answer_for([item(1, "s1"), item(2, "s2")])

    assert "[E3]" not in answer["answer_text"]
    assert "[E3]" not in answer["citations_used"]


def test_citation_coverage_is_deterministic():
    first = answer_for([item(1, "s1"), item(2, "s2")])["citation_coverage"]
    second = answer_for([item(1, "s1"), item(2, "s2")])["citation_coverage"]

    assert first == second
    assert first["all_claims_cited"]


def test_limitations_include_guardrail_warnings_or_reasons():
    answer = answer_for([item(1, "s1", section=""), item(2, "s2")])

    assert answer["limitations"] == answer["guardrail_decision_summary"]["warnings"]


def test_factual_evidence_bullets_include_citation_markers():
    answer = answer_for([item(1, "s1"), item(2, "s2")])
    bullets = [line for line in answer["answer_text"].splitlines() if line.startswith("- Evidence statement")]

    assert bullets
    assert all("[E" in bullet for bullet in bullets)


def test_integration_full_pipeline_generates_grounded_answer():
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    query = "What is Asperitas?"
    results = search_chunks_mvp003(query, chunks, records, limit=5, include_explanations=True)
    pack = build_evidence_pack(query, results, top_k=5)
    decision = evaluate_evidence_guardrail(pack)
    answer = generate_grounded_answer(pack, decision).to_json()

    assert answer["answer_status"] in {"answered", "caution"}
    assert answer["citations_used"]
    assert answer["metadata"]["generator_version"] == "V1.3C"


def test_answer_generation_code_does_not_reference_benchmark_answer_files():
    files = [
        "src/asperitas_agent/answer_generation.py",
        "scripts/generate_grounded_answer.py",
    ]
    forbidden = ("expected_sources", "retrieval_questions", "gold", "ground_truth", "ground-truth")

    for file_name in files:
        text = Path(file_name).read_text(encoding="utf-8").casefold()
        assert not any(pattern in text for pattern in forbidden)
