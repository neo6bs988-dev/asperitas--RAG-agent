from __future__ import annotations

from pathlib import Path

from asperitas_agent.chunking import read_chunks
from asperitas_agent.evidence_pack import build_evidence_pack
from asperitas_agent.guardrails import evaluate_evidence_guardrail
from asperitas_agent.registry import read_registry
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003


REPO_ROOT = Path(__file__).resolve().parents[1]


def item(rank: int, source_id: str, priority: str = "P1", label: str = "Document-Supported Fact", section: str = "Methods") -> dict:
    return {
        "chunk_id": f"{source_id}::chunk-{rank:04d}",
        "score": 10.0 - rank,
        "source_id": source_id,
        "source_title": f"Source {source_id}",
        "source_file": f"source/{source_id}.md",
        "source_priority": priority,
        "evidence_label": label,
        "section": section,
        "section_heading": section,
        "section_path": [section] if section else [],
        "section_level": 1 if section else None,
        "text": "Evidence text.",
    }


def decision_for(results: list[dict]):
    pack = build_evidence_pack("query", results, top_k=len(results) or 5)
    return evaluate_evidence_guardrail(pack).to_json()


def test_no_evidence_produces_abstain():
    decision = decision_for([])

    assert decision["decision"] == "abstain"
    assert decision["should_abstain"]
    assert decision["confidence_level"] == "none"
    assert "No evidence found." in decision["reasons"]


def test_sufficient_evidence_produces_proceed():
    decision = decision_for([item(1, "s1"), item(2, "s2")])

    assert decision["decision"] == "proceed"
    assert not decision["should_abstain"]
    assert decision["confidence_level"] == "high"
    assert decision["recommended_next_action"] == "answer_allowed"


def test_mixed_evidence_produces_caution():
    decision = decision_for([item(1, "s1", section=""), item(2, "s2")])

    assert decision["decision"] == "caution"
    assert not decision["should_abstain"]
    assert decision["confidence_level"] == "medium"


def test_low_source_diversity_creates_warning():
    decision = decision_for([item(1, "same"), item(2, "same")])

    assert decision["decision"] == "caution"
    assert "Low source diversity." in decision["warnings"]


def test_missing_source_priority_creates_warning():
    decision = decision_for([item(1, "s1", priority=""), item(2, "s2")])

    assert decision["decision"] == "caution"
    assert any("source priority" in warning for warning in decision["warnings"])


def test_missing_evidence_label_creates_warning():
    decision = decision_for([item(1, "s1", label=""), item(2, "s2")])

    assert decision["decision"] == "caution"
    assert any("evidence label" in warning for warning in decision["warnings"])


def test_missing_section_metadata_warns_without_abstention_when_otherwise_sufficient():
    decision = decision_for([item(1, "s1", section=""), item(2, "s2")])

    assert decision["decision"] == "caution"
    assert not decision["should_abstain"]
    assert any("section metadata" in warning for warning in decision["warnings"])


def test_confidence_level_is_deterministic():
    results = [item(1, "s1", section=""), item(2, "s2")]

    assert decision_for(results)["confidence_level"] == decision_for(results)["confidence_level"]


def test_integration_guardrail_works_with_mvp003_and_evidence_pack():
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    retrieved = search_chunks_mvp003("What is Asperitas?", chunks, records, limit=5, include_explanations=True)
    pack = build_evidence_pack("What is Asperitas?", retrieved, top_k=5)
    decision = evaluate_evidence_guardrail(pack).to_json()

    assert decision["decision"] in {"proceed", "caution"}
    assert decision["recommended_next_action"] in {"answer_allowed", "answer_with_citations_and_caveats"}
    assert not decision["should_abstain"]


def test_retrieval_code_does_not_reference_benchmark_answer_files():
    files = [
        "src/asperitas_agent/guardrails.py",
        "src/asperitas_agent/evidence_pack.py",
        "src/asperitas_agent/retrieval_mvp003.py",
    ]
    forbidden = ("expected_sources", "retrieval_questions", "gold", "ground_truth", "ground-truth")

    for file_name in files:
        text = Path(file_name).read_text(encoding="utf-8").casefold()
        assert not any(pattern in text for pattern in forbidden)
