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
    row = valid_question()
    row["expected_path_context"] = "P1_RND_PROJECTS"
    write_jsonl(path, [row])

    questions = module.load_questions(path)

    assert len(questions) == 1
    assert questions[0].question_id == "Q1"
    assert questions[0].expected_source_file == "AGENTS.md"
    assert questions[0].expected_path_context == "P1_RND_PROJECTS"


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
    assert summary["path_context_match"] is None
    assert summary["overall_pass_rate"] == 1.0


def test_score_results_counts_path_context_separately_from_section():
    module = load_eval_module()
    question = module.EvalQuestion(
        question_id="Q1",
        user_question="Where is the R&D projects copy stored?",
        expected_source_file="01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx",
        expected_source_priority="P1",
        expected_chunk_or_section="",
        expected_path_context="P1_RND_PROJECTS",
        expected_evidence_label="Document-Supported Fact",
        rationale="The folder path is the expected provenance signal.",
        difficulty="medium",
        category="operations",
    )
    results = {
        "Q1": [
            {
                "source_file": "01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx",
                "source_priority": "P1",
                "evidence_label": "Document-Supported Fact",
                "section": "",
                "heading_context": "",
                "title": "2026 PTMC project",
                "text": "Project body text without the folder token.",
            }
        ]
    }

    summary = module.score_results([question], results)

    assert summary["source_file_match_at_5"] == 1.0
    assert summary["section_match"] is None
    assert summary["path_context_match"] == 1.0
    assert summary["overall_pass_rate"] == 1.0


def test_path_context_does_not_satisfy_section_expectation():
    module = load_eval_module()
    question = module.EvalQuestion(
        question_id="Q1",
        user_question="Where is the R&D projects copy stored?",
        expected_source_file="01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx",
        expected_source_priority="P1",
        expected_chunk_or_section="P1_RND_PROJECTS",
        expected_evidence_label="Document-Supported Fact",
        rationale="Path context must not masquerade as section metadata.",
        difficulty="medium",
        category="operations",
    )
    results = {
        "Q1": [
            {
                "source_file": "01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx",
                "source_priority": "P1",
                "evidence_label": "Document-Supported Fact",
                "section": "",
                "heading_context": "",
                "title": "2026 PTMC project",
                "text": "Project body text without the folder token.",
            }
        ]
    }

    summary = module.score_results([question], results)

    assert summary["section_match"] == 0.0
    assert summary["path_context_match"] is None
    assert summary["overall_pass_rate"] == 0.0


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


def test_parser_accepts_hybrid_retriever_mode():
    module = load_eval_module()

    args = module.build_parser().parse_args(["--retriever", "hybrid"])

    assert args.retriever == "hybrid"


def test_parser_defaults_to_no_reranker():
    module = load_eval_module()

    args = module.build_parser().parse_args([])

    assert args.reranker == module.RERANKER_NONE


def test_parser_accepts_deterministic_test_reranker():
    module = load_eval_module()

    args = module.build_parser().parse_args(["--retriever", "mvp003", "--reranker", "deterministic-test"])

    assert args.reranker == module.RERANKER_DETERMINISTIC_TEST


def test_build_reranker_selects_explicit_modes():
    module = load_eval_module()

    assert module.build_reranker(module.RERANKER_NONE) is None
    reranker = module.build_reranker(module.RERANKER_DETERMINISTIC_TEST)

    assert reranker.reranker_name == "deterministic-test-reranker"
    assert reranker.deterministic is True


def test_run_retriever_selects_vector_mode(monkeypatch):
    module = load_eval_module()
    sentinel = {"Q1": []}

    def fake_vector_retrieval(questions, registry_path, chunks_path, limit):
        return sentinel

    monkeypatch.setattr(module, "run_vector_retrieval", fake_vector_retrieval)

    mode, results = module.run_retriever("vector", [], Path("registry.csv"), Path("chunks.jsonl"), 5)

    assert mode == module.MVP005_VECTOR_EVAL_MODE
    assert results is sentinel


def test_run_retriever_selects_hybrid_mode(monkeypatch):
    module = load_eval_module()
    sentinel = {"Q1": []}

    def fake_hybrid_retrieval(questions, registry_path, chunks_path, limit):
        return sentinel

    monkeypatch.setattr(module, "run_hybrid_retrieval", fake_hybrid_retrieval)

    mode, results = module.run_retriever("hybrid", [], Path("registry.csv"), Path("chunks.jsonl"), 5)

    assert mode == module.MVP006_HYBRID_EVAL_MODE
    assert results is sentinel


def test_run_retriever_keeps_existing_mode_paths(monkeypatch):
    module = load_eval_module()
    calls: list[str] = []

    def fake_baseline(questions, registry_path, chunks_path, limit):
        calls.append("baseline")
        return {"baseline": []}

    def fake_mvp003(questions, registry_path, chunks_path, limit):
        calls.append("mvp003")
        return {"mvp003": []}

    def fake_vector(questions, registry_path, chunks_path, limit):
        calls.append("vector")
        return {"vector": []}

    def forbidden_hybrid(questions, registry_path, chunks_path, limit):
        raise AssertionError("hybrid path should not run for existing modes")

    monkeypatch.setattr(module, "run_baseline_retrieval", fake_baseline)
    monkeypatch.setattr(module, "run_mvp003_retrieval", fake_mvp003)
    monkeypatch.setattr(module, "run_vector_retrieval", fake_vector)
    monkeypatch.setattr(module, "run_hybrid_retrieval", forbidden_hybrid)

    baseline_mode, baseline_results = module.run_retriever("baseline", [], Path("registry.csv"), Path("chunks.jsonl"), 5)
    mvp003_mode, mvp003_results = module.run_retriever("mvp003", [], Path("registry.csv"), Path("chunks.jsonl"), 5)
    vector_mode, vector_results = module.run_retriever("vector", [], Path("registry.csv"), Path("chunks.jsonl"), 5)

    assert calls == ["baseline", "mvp003", "vector"]
    assert baseline_mode == "current-tfidf-baseline"
    assert baseline_results == {"baseline": []}
    assert mvp003_mode == "mvp003-deterministic-metadata"
    assert mvp003_results == {"mvp003": []}
    assert vector_mode == module.MVP005_VECTOR_EVAL_MODE
    assert vector_results == {"vector": []}


def test_hybrid_top_results_keep_mvp003_top_k_sources_with_section_substitution():
    module = load_eval_module()
    ranked = [
        {
            "chunk_id": "vector-only",
            "source_id": "VECTOR",
            "score": 0.95,
            "vector_rank": 1,
            "score_components": {"mvp003_score": 0.0, "vector_score": 1.0, "metadata_score": 1.0},
        },
        {
            "chunk_id": "mvp003-first",
            "source_id": "A",
            "score": 0.8,
            "mvp003_rank": 1,
            "mvp003_score_raw": 100.0,
            "score_components": {"mvp003_score": 1.0, "vector_score": 0.2, "section_score": 0.5, "metadata_score": 1.0},
        },
        {
            "chunk_id": "section-first",
            "source_id": "A",
            "score": 0.78,
            "section_candidate_rank": 30,
            "mvp003_score_raw": 95.0,
            "score_components": {"mvp003_score": 0.95, "vector_score": 0.0, "section_score": 1.0, "metadata_score": 1.0},
        },
        {
            "chunk_id": "mvp003-second",
            "source_id": "B",
            "score": 0.2,
            "mvp003_rank": 2,
            "mvp003_score_raw": 20.0,
            "score_components": {"mvp003_score": 0.2, "vector_score": 0.0, "section_score": 0.5, "metadata_score": 1.0},
        },
    ]

    selected = module.select_hybrid_top_results(ranked, limit=2)

    assert {row["source_id"] for row in selected} == {"A", "B"}
    assert {row["chunk_id"] for row in selected} == {"section-first", "mvp003-second"}


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
    assert row["embedding_model"] == "offline-lexical-semantic-hash"
    assert row["embedding_dim"] == module.MVP005_VECTOR_EVAL_EMBEDDING_DIM
    assert row["embedding_version"] == "mvp005-phase5-lexical-semantic"
    assert row["content_hash"] == chunk.checksum
    assert isinstance(row["score"], float)


def test_hybrid_retrieval_preserves_metadata_and_score_components(tmp_path):
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

    results = module.run_hybrid_retrieval([question], registry_path, chunks_path, limit=5)
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
    assert row["embedding_model"] == "offline-lexical-semantic-hash"
    assert row["embedding_dim"] == module.MVP005_VECTOR_EVAL_EMBEDDING_DIM
    assert row["embedding_version"] == "mvp005-phase5-lexical-semantic"
    assert row["content_hash"] == chunk.checksum
    assert row["mvp003_rank"] == 1
    assert row["vector_rank"] == 1
    assert isinstance(row["score"], float)
    assert row["score_components"]["mvp003_score"] == 1.0
    assert row["score_components"]["vector_score"] > 0.0
    assert row["score_components"]["section_score"] == 1.0
    assert row["score_components"]["metadata_score"] == 1.0


def test_hybrid_retrieval_can_substitute_same_source_section_candidate(tmp_path):
    module = load_eval_module()
    source = make_source()
    base_chunk = make_chunk(source)
    wrong_section = Chunk(
        **{
            **base_chunk.to_json(),
            "chunk_id": f"{source.source_id}::VECTOR::chunk-wrong",
            "char_start": 0,
            "char_end": len(base_chunk.text),
            "section": "General Governance",
            "section_heading": "General Governance",
            "section_path": ["General Governance"],
            "heading_context": "General Governance",
            "checksum": "c" * 64,
        }
    )
    right_section = Chunk(
        **{
            **base_chunk.to_json(),
            "chunk_id": f"{source.source_id}::VECTOR::chunk-right",
            "char_start": 100,
            "char_end": 100 + len(base_chunk.text),
            "section": "Source Priority Policy",
            "section_heading": "Source Priority Policy",
            "section_path": ["Governance", "Source Priority Policy"],
            "heading_context": "Governance > Source Priority Policy",
            "checksum": "d" * 64,
        }
    )
    registry_path = tmp_path / "source_registry.csv"
    chunks_path = tmp_path / "chunks.jsonl"
    write_registry([source], path=registry_path)
    write_chunks([wrong_section, right_section], path=chunks_path)
    question = module.EvalQuestion(
        question_id="Q1",
        user_question="What does the source priority policy say?",
        expected_source_file=source.path,
        expected_source_priority=source.source_priority,
        expected_chunk_or_section="Source Priority Policy",
        expected_evidence_label=base_chunk.evidence_label,
        rationale="The fixture chunk contains the expected policy section.",
        difficulty="easy",
        category="source_governance",
    )

    mvp003_results = module.run_mvp003_retrieval([question], registry_path, chunks_path, limit=1)
    hybrid_results = module.run_hybrid_retrieval([question], registry_path, chunks_path, limit=1)

    assert mvp003_results["Q1"][0]["chunk_id"] == wrong_section.chunk_id
    assert hybrid_results["Q1"][0]["chunk_id"] == right_section.chunk_id
    assert hybrid_results["Q1"][0]["source_id"] == source.source_id
    assert hybrid_results["Q1"][0]["source_priority"] == source.source_priority
    assert hybrid_results["Q1"][0]["evidence_label"] == base_chunk.evidence_label
    assert hybrid_results["Q1"][0]["score_components"]["section_score"] == 1.0


def test_disabled_reranker_eval_preserves_default_order():
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
            eval_candidate("weak", rank=1, section="General Governance", text="unrelated body"),
            eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy"),
        ]
    }

    reranked = module.apply_reranker_to_results([question], results, reranker=None, limit=5)

    assert [row["chunk_id"] for row in reranked["Q1"]] == ["weak", "strong"]
    assert "reranker_metadata" not in reranked["Q1"][0]


def test_deterministic_test_reranker_eval_reorders_rows_and_preserves_original_rank():
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
            eval_candidate("weak", rank=1, section="General Governance", text="unrelated body"),
            eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy evidence hierarchy"),
        ]
    }

    reranked = module.apply_reranker_to_results(
        [question],
        results,
        reranker=module.build_reranker(module.RERANKER_DETERMINISTIC_TEST),
        limit=5,
    )
    row = reranked["Q1"][0]

    assert [row["chunk_id"] for row in reranked["Q1"]] == ["strong", "weak"]
    assert row["rank"] == 2
    assert row["score"] == results["Q1"][1]["score"]
    assert row["score_components"] == results["Q1"][1]["score_components"]
    assert row["reranker_metadata"]["input_rank"] == 2
    assert row["reranker_metadata"]["reranked_rank"] == 1


def test_deterministic_test_reranker_eval_preserves_metadata_fields():
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
            eval_candidate("weak", rank=1, section="General Governance", text="unrelated body"),
            eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy"),
        ]
    }

    reranked = module.apply_reranker_to_results(
        [question],
        results,
        reranker=module.build_reranker(module.RERANKER_DETERMINISTIC_TEST),
        limit=5,
    )
    original_by_chunk = {row["chunk_id"]: row for row in results["Q1"]}

    for row in reranked["Q1"]:
        original = original_by_chunk[row["chunk_id"]]
        for field_name in (
            "source_id",
            "source_file",
            "source_priority",
            "evidence_label",
            "section",
            "section_heading",
            "section_path",
            "heading_context",
            "embedding_model",
            "embedding_dim",
            "embedding_version",
            "content_hash",
        ):
            assert row[field_name] == original[field_name]


def test_reranker_comparison_reports_top_k_ordering_changes():
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
    base_results = {
        "Q1": [
            eval_candidate("weak", rank=1, section="General Governance", text="unrelated body"),
            eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy"),
        ]
    }
    reranked_results = {
        "Q1": [
            eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy"),
            eval_candidate("weak", rank=1, section="General Governance", text="unrelated body"),
        ]
    }
    base_summary = module.score_results([question], base_results)
    reranked_summary = module.score_results([question], reranked_results)

    comparison = module.compare_reranker_outputs(
        questions=[question],
        base_results=base_results,
        reranked_results=reranked_results,
        base_summary=base_summary,
        reranked_summary=reranked_summary,
        base_mode="mvp003-deterministic-metadata",
        reranker_name=module.RERANKER_DETERMINISTIC_TEST,
    )

    assert comparison["top1_changed_count"] == 1
    assert comparison["top3_changed_count"] == 1
    assert comparison["top5_changed_count"] == 1
    assert comparison["source_file_match_at_3_delta"] == 0.0
    assert comparison["source_file_match_at_5_delta"] == 0.0


def eval_candidate(chunk_id: str, rank: int, section: str, text: str) -> dict:
    return {
        "rank": rank,
        "chunk_id": chunk_id,
        "source_id": "ASP-P0-EVAL",
        "source_file": "AGENTS.md",
        "source_priority": "P0",
        "evidence_label": "Document-Supported Fact",
        "section": section,
        "section_heading": section,
        "section_path": ["Governance", section],
        "heading_context": f"Governance > {section}",
        "embedding_model": "offline-lexical-semantic-hash",
        "embedding_dim": 1024,
        "embedding_version": "mvp005-phase5-lexical-semantic",
        "content_hash": "a" * 64,
        "score": 0.42,
        "score_components": {"mvp003_score": 0.4, "vector_score": 0.5},
        "title": "AGENTS",
        "text": text,
    }
