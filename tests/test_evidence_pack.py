from __future__ import annotations

from pathlib import Path

from asperitas_agent.chunking import read_chunks
from asperitas_agent.evidence_pack import build_evidence_pack
from asperitas_agent.registry import read_registry
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003


REPO_ROOT = Path(__file__).resolve().parents[1]


def mock_result(rank: int = 1, source_id: str = "ASP-P1-ONE", section: str = "Methods") -> dict:
    return {
        "rank": rank,
        "chunk_id": f"{source_id}::chunk-{rank:04d}",
        "score": 12.3456789,
        "source_id": source_id,
        "source_title": "Synthetic Biology Review",
        "source_file": f"01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/{source_id}.pdf",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": section,
        "section_heading": section,
        "section_path": ["Review", section] if section else [],
        "section_level": 2 if section else None,
        "parent_section": "Review" if section else "",
        "subsection": section if section else "",
        "text": f"{section or 'Unsectioned'} evidence text for Asperitas retrieval.",
    }


def test_evidence_pack_can_be_built_from_mock_results():
    pack = build_evidence_pack("What is Asperitas?", [mock_result()], top_k=1)
    payload = pack.to_json()

    assert payload["query"] == "What is Asperitas?"
    assert payload["retriever"]["retriever_name"] == "mvp003-deterministic-metadata"
    assert payload["evidence_items"][0]["citation_key"] == "[E1]"
    assert payload["source_coverage_summary"]["unique_source_count"] == 1
    assert not payload["risk_flags"]["no_evidence_found"]


def test_citation_keys_are_deterministic():
    results = [mock_result(1, "ASP-P1-ONE"), mock_result(2, "ASP-P1-TWO")]

    first = build_evidence_pack("query", results, top_k=2).to_json()
    second = build_evidence_pack("query", results, top_k=2).to_json()

    assert [item["citation_key"] for item in first["evidence_items"]] == ["[E1]", "[E2]"]
    assert first == second


def test_no_evidence_sets_no_evidence_and_abstention():
    pack = build_evidence_pack("empty query", [], top_k=5).to_json()

    assert pack["risk_flags"]["no_evidence_found"]
    assert pack["abstention"]["should_abstain"]
    assert "No retrieved evidence was available." in pack["abstention"]["reasons"]
    assert pack["context_block"] == ""


def test_missing_section_metadata_triggers_flag():
    pack = build_evidence_pack("query", [mock_result(section="")], top_k=1).to_json()

    assert pack["source_coverage_summary"]["missing_section_metadata_count"] == 1
    assert pack["risk_flags"]["missing_section_metadata"]
    assert pack["risk_flags"]["weak_section_coverage"]


def test_low_source_diversity_triggers_flag():
    results = [mock_result(1, "ASP-P1-SAME"), mock_result(2, "ASP-P1-SAME")]
    pack = build_evidence_pack("query", results, top_k=2).to_json()

    assert pack["source_coverage_summary"]["unique_source_count"] == 1
    assert pack["risk_flags"]["low_source_diversity"]


def test_context_block_includes_citation_markers_and_traceability():
    pack = build_evidence_pack("query", [mock_result()], top_k=1).to_json()
    context = pack["context_block"]

    assert "[E1] Source:" in context
    assert "[E1] Path:" in context
    assert "[E1] Section:" in context
    assert "[E1] Excerpt:" in context


def test_integration_builds_pack_from_existing_mvp003_retriever():
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    retrieved = search_chunks_mvp003("What is Asperitas?", chunks, records, limit=3, include_explanations=True)

    pack = build_evidence_pack("What is Asperitas?", retrieved, top_k=3).to_json()

    assert pack["evidence_items"]
    assert pack["retriever"]["top_k"] == 3
    assert pack["context_block"].count("[E") >= len(pack["evidence_items"])


def test_building_evidence_pack_does_not_change_retrieval_order():
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    query = "Which source should answer questions about the 2026 PTMC project?"

    before = search_chunks_mvp003(query, chunks, records, limit=5, include_explanations=True)
    _pack = build_evidence_pack(query, before, top_k=5)
    after = search_chunks_mvp003(query, chunks, records, limit=5, include_explanations=True)

    assert [item.source_file for item in before] == [item.source_file for item in after]
    assert [round(item.score, 6) for item in before] == [round(item.score, 6) for item in after]
