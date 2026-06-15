from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from asperitas_agent.chunking import write_chunks
from asperitas_agent.registry import write_registry
from asperitas_agent.schemas import Chunk, SourceRecord


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_retrieval_eval.py"


def load_eval_module():
    spec = importlib.util.spec_from_file_location("run_retrieval_eval", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def valid_question(question_id: str = "Q1") -> dict:
    return {
        "question_id": question_id,
        "user_question": "What is the source priority policy?",
        "expected_source_file": "AGENTS.md",
        "expected_source_priority": "P0",
        "expected_chunk_or_section": "Source Priority Policy",
        "expected_evidence_label": "Document-Supported Fact",
        "rationale": "AGENTS.md defines the source policy.",
        "difficulty": "easy",
        "category": "source_governance",
    }


def valid_expected(question_id: str = "Q1") -> dict:
    return {
        "question_id": question_id,
        "expected_source_file": "AGENTS.md",
        "expected_source_priority": "P0",
        "expected_evidence_label": "Document-Supported Fact",
        "expected_section_keywords": ["Source Priority Policy"],
    }


def make_source() -> SourceRecord:
    return SourceRecord(
        source_id="ASP-P0-EVAL",
        title="Vector Eval Source",
        original_filename="vector-eval.md",
        path="01_RAW_SOURCES/P0_ACTIVE_PROMPT/vector-eval.md",
        source_priority="P0",
        source_type="prompt",
        disclosure_level="confidential",
        license_status="owned",
        verification_status="verified_internal",
        date="2026-06-15",
        author_or_owner="Asperitas",
        use_case="retrieval_eval_test",
        checksum="a" * 64,
        parse_status="parsed",
    )


def make_chunk(source: SourceRecord) -> Chunk:
    return Chunk(
        chunk_id=f"{source.source_id}::VECTOR::chunk-0001",
        source_id=source.source_id,
        title=source.title,
        text="Source Priority Policy requires P0 instructions to override lower-priority sources.",
        page_start=None,
        page_end=None,
        char_start=0,
        char_end=78,
        source_priority=source.source_priority,
        source_type=source.source_type,
        disclosure_level=source.disclosure_level,
        evidence_label="Document-Supported Fact",
        verification_status=source.verification_status,
        risk_tags=[],
        checksum="b" * 64,
        section="Source Priority Policy",
        section_heading="Source Priority Policy",
        section_path=["Governance", "Source Priority Policy"],
        section_level=2,
        parent_section="Governance",
        subsection="Source Priority Policy",
        heading_context="Governance > Source Priority Policy",
    )


def test_load_questions_validates_required_schema(tmp_path):
    module = load_eval_module()
    path = tmp_path / "questions.jsonl"
    write_jsonl(path, [valid_question()])

    questions = module.load_questions(path)

    assert len(questions) == 1
    assert questions[0].question_id == "Q1"
    assert questions[0].expected_source_file == "AGENTS.md"


def test_load_questions_rejects_invalid_category(tmp_path):
    module = load_eval_module()
    path = tmp_path / "questions.jsonl"
    row = valid_question()
    row["category"] = "vector_db"
    write_jsonl(path, [row])

    with pytest.raises(module.EvalError, match="invalid category"):
        module.load_questions(path)


def test_expected_alignment_rejects_mismatch(tmp_path):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    write_jsonl(questions_path, [valid_question()])
    expected = valid_expected()
    expected["expected_source_file"] = "README.md"
    write_jsonl(expected_path, [expected])

    questions = module.load_questions(questions_path)
    expected_rows = module.load_expected_sources(expected_path)

    with pytest.raises(module.EvalError, match="mismatch"):
        module.validate_expected_alignment(questions, expected_rows)


def test_score_results_counts_top3_top5_priority_and_section():
    module = load_eval_module()
    question = module.EvalQuestion(
        question_id="Q1",
        user_question="What is the source priority policy?",
        expected_source_file="AGENTS.md",
        expected_source_priority="P0",
        expected_chunk_or_section="Source Priority Policy",
        expected_evidence_label="Document-Supported Fact",
        rationale="AGENTS.md defines the source policy.",
        difficulty="easy",
        category="source_governance",
    )
    results = {
        "Q1": [
            {
                "source_file": "README.md",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "title": "README",
                "text": "Other text",
            },
            {
                "source_file": "AGENTS.md",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "title": "AGENTS",
                "text": "Source Priority Policy and evidence hierarchy",
            },
        ]
    }

    summary = module.score_results([question], results)

    assert summary["source_file_match_at_3"] == 1.0
    assert summary["source_file_match_at_5"] == 1.0
    assert summary["source_priority_match"] == 1.0
    assert summary["section_match"] == 1.0
    assert summary["overall_pass_rate"] == 1.0


def test_section_match_uses_normalized_section_metadata():
    module = load_eval_module()

    result = {
        "title": "AGENTS",
        "section": "1. Source-Priority Policy",
        "section_heading": "1. Source-Priority Policy",
        "section_path": ["Agent Rules", "1. Source-Priority Policy"],
        "heading_context": "Agent Rules > 1. Source-Priority Policy",
        "text": "Body without the exact label.",
    }

    assert module.contains_section(result, "source priority policy")


def test_missing_jsonl_file_returns_eval_error(tmp_path):
    module = load_eval_module()

    with pytest.raises(module.EvalError, match="Required file not found"):
        module.load_jsonl(tmp_path / "missing.jsonl")


def test_parser_accepts_vector_retriever_mode():
    module = load_eval_module()

    args = module.build_parser().parse_args(["--retriever", "vector"])

    assert args.retriever == "vector"


def test_run_retriever_selects_vector_mode(monkeypatch):
    module = load_eval_module()
    sentinel = {"Q1": []}

    def fake_vector_retrieval(questions, registry_path, chunks_path, limit):
        return sentinel

    monkeypatch.setattr(module, "run_vector_retrieval", fake_vector_retrieval)

    mode, results = module.run_retriever("vector", [], Path("registry.csv"), Path("chunks.jsonl"), 5)

    assert mode == module.MVP005_VECTOR_EVAL_MODE
    assert results is sentinel


def test_vector_retrieval_preserves_embedding_record_metadata(tmp_path):
    module = load_eval_module()
    source = make_source()
    chunk = make_chunk(source)
    registry_path = tmp_path / "source_registry.csv"
    chunks_path = tmp_path / "chunks.jsonl"
    write_registry([source], path=registry_path)
    write_chunks([chunk], path=chunks_path)
    question = module.EvalQuestion(
        question_id="Q1",
        user_question="What does the source priority policy say?",
        expected_source_file=source.path,
        expected_source_priority=source.source_priority,
        expected_chunk_or_section="Source Priority Policy",
        expected_evidence_label=chunk.evidence_label,
        rationale="The fixture chunk contains the expected policy section.",
        difficulty="easy",
        category="source_governance",
    )

    results = module.run_vector_retrieval([question], registry_path, chunks_path, limit=5)
    row = results["Q1"][0]

    assert row["rank"] == 1
    assert row["source_id"] == source.source_id
    assert row["source_file"] == source.path
    assert row["source_priority"] == source.source_priority
    assert row["evidence_label"] == chunk.evidence_label
    assert row["section"] == chunk.section
    assert row["section_heading"] == chunk.section_heading
    assert row["section_path"] == chunk.section_path
    assert row["heading_context"] == chunk.heading_context
    assert row["title"] == chunk.title
    assert row["text"] == chunk.text
    assert row["embedding_model"] == "offline-deterministic-hash"
    assert row["embedding_dim"] == module.MVP005_VECTOR_EVAL_EMBEDDING_DIM
    assert row["embedding_version"] == "mvp005-phase2-offline"
    assert row["content_hash"] == chunk.checksum
    assert isinstance(row["score"], float)
