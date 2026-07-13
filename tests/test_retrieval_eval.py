from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from asperitas_agent.chunking import write_chunks
from asperitas_agent.registry import write_registry
from asperitas_agent.schemas import Chunk, SourceRecord


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_retrieval_eval.py"
REPO_ROOT = SCRIPT_PATH.parents[1]
TARGET_RISK_QUESTION_IDS = ("MVP0025-Q001", "MVP0025-Q004", "MVP0025-Q010")


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


def test_merge_expected_oracle_fields_adds_optional_relaxed_metadata():
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
    expected = {
        "Q1": {
            "question_id": "Q1",
            "expected_source_file": "AGENTS.md",
            "expected_source_priority": "P0",
            "expected_evidence_label": "Document-Supported Fact",
            "expected_source_id": "ASP-P0-AGENTS",
            "accepted_sources": ["README.md"],
            "accepted_aliases": ["source policy mirror"],
            "accepted_source_ids": ["ASP-P0-README"],
            "multi_valid_source": True,
            "oracle_notes": "AGENTS and README both describe source policy.",
        }
    }

    merged = module.merge_expected_oracle_fields([question], expected)[0]

    assert merged.expected_source_id == "ASP-P0-AGENTS"
    assert merged.accepted_sources == ("README.md",)
    assert merged.accepted_aliases == ("source policy mirror",)
    assert merged.accepted_source_ids == ("ASP-P0-README",)
    assert merged.multi_valid_source is True
    assert merged.oracle_notes == "AGENTS and README both describe source policy."


def test_relaxed_accepted_sources_do_not_replace_strict_metrics():
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
        accepted_sources=("README.md",),
        multi_valid_source=True,
    )
    results = {
        "Q1": [
            {
                "source_file": "README.md",
                "source_id": "ASP-P0-README",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "section": "Source Priority Policy",
                "title": "README",
                "text": "Source Priority Policy and evidence hierarchy",
            }
        ]
    }

    summary = module.score_results([question], results)
    row = summary["per_question"][0]

    assert summary["source_file_match_at_5"] == 0.0
    assert summary["overall_pass_rate"] == 0.0
    assert summary["relaxed_source_match_at_5"] == 1.0
    assert summary["relaxed_overall_pass_rate"] == 1.0
    assert row["relaxed_match_basis"] == "accepted_sources"
    assert row["multi_valid_source"] is True


def test_relaxed_metrics_preserve_strict_pass_when_accepted_source_ranks_first():
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
        accepted_sources=("README.md",),
        multi_valid_source=True,
    )
    results = {
        "Q1": [
            {
                "source_file": "README.md",
                "source_id": "ASP-P0-README",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "section": "General Governance",
                "title": "README",
                "text": "General governance mirror.",
            },
            {
                "source_file": "AGENTS.md",
                "source_id": "ASP-P0-AGENTS",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "section": "Source Priority Policy",
                "title": "AGENTS",
                "text": "Source Priority Policy and evidence hierarchy",
            },
        ]
    }

    summary = module.score_results([question], results)
    row = summary["per_question"][0]

    assert summary["overall_pass_rate"] == 1.0
    assert summary["relaxed_overall_pass_rate"] == 1.0
    assert row["relaxed_match_basis"] == "expected_source_file"
    assert row["relaxed_section_match"] is True


def test_relaxed_source_id_and_alias_matching_are_additive():
    module = load_eval_module()
    source_id_question = module.EvalQuestion(
        question_id="Q1",
        user_question="What is the source priority policy?",
        expected_source_file="AGENTS.md",
        expected_source_priority="P0",
        expected_chunk_or_section="Source Priority Policy",
        expected_evidence_label="Document-Supported Fact",
        rationale="AGENTS.md defines the source policy.",
        difficulty="easy",
        category="source_governance",
        accepted_source_ids=("ASP-P0-README",),
    )
    alias_question = module.EvalQuestion(
        question_id="Q2",
        user_question="What is the source priority policy?",
        expected_source_file="AGENTS.md",
        expected_source_priority="P0",
        expected_chunk_or_section="Source Priority Policy",
        expected_evidence_label="Document-Supported Fact",
        rationale="AGENTS.md defines the source policy.",
        difficulty="easy",
        category="source_governance",
        accepted_aliases=("source policy mirror",),
    )
    results = {
        "Q1": [
            {
                "source_file": "README.md",
                "source_id": "ASP-P0-README",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "section": "Source Priority Policy",
                "title": "README",
                "text": "Source Priority Policy",
            }
        ],
        "Q2": [
            {
                "source_file": "docs/source-policy-mirror.md",
                "source_id": "ASP-P0-MIRROR",
                "source_priority": "P0",
                "evidence_label": "Document-Supported Fact",
                "section": "Source Priority Policy",
                "title": "Source Policy Mirror",
                "text": "Source Priority Policy",
            }
        ],
    }

    first = module.score_question(source_id_question, results["Q1"])
    second = module.score_question(alias_question, results["Q2"])

    assert first["source_file_match_top5"] is False
    assert first["relaxed_source_match_top5"] is True
    assert first["relaxed_match_basis"] == "accepted_source_ids"
    assert second["source_file_match_top5"] is False
    assert second["relaxed_source_match_top5"] is True
    assert second["relaxed_match_basis"] == "accepted_aliases"


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


def test_parser_defaults_to_direct_reranker_policy():
    module = load_eval_module()

    args = module.build_parser().parse_args([])

    assert args.reranker_policy == module.RERANKER_POLICY_DIRECT


def test_parser_accepts_fail_closed_reranker_policy():
    module = load_eval_module()

    args = module.build_parser().parse_args(
        ["--retriever", "mvp003", "--reranker", "deterministic-test", "--reranker-policy", "fail-closed"]
    )

    assert args.reranker_policy == module.RERANKER_POLICY_FAIL_CLOSED


def test_parser_defaults_to_thresholds_disabled():
    module = load_eval_module()

    args = module.build_parser().parse_args([])

    assert args.enforce_thresholds is False


def test_parser_accepts_threshold_enforcement():
    module = load_eval_module()

    args = module.build_parser().parse_args(["--retriever", "mvp003", "--enforce-thresholds"])

    assert args.enforce_thresholds is True


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


def test_mvp003_rows_from_scored_results_preserves_source_dedup_sorting():
    module = load_eval_module()
    rows = module.mvp003_rows_from_scored_results(
        [
            fake_mvp003_result(eval_candidate("source-a-low", rank=1, section="General", text="source priority"), score=4.0),
            fake_mvp003_result(eval_candidate("source-b", rank=2, section="General", text="source priority"), source_id="SOURCE-B", score=7.0),
            fake_mvp003_result(eval_candidate("source-a-high", rank=3, section="General", text="source priority"), score=9.0),
        ],
        limit=2,
    )

    assert [row["chunk_id"] for row in rows] == ["source-a-high", "source-b"]
    assert [row["rank"] for row in rows] == [1, 2]


def test_collect_hybrid_section_candidates_can_reuse_precomputed_scores(monkeypatch):
    module = load_eval_module()
    question = eval_question()
    row = eval_candidate("section-match", rank=2, section="Source Priority Policy", text="source priority policy")
    row["score"] = 9.5
    protected_row = eval_candidate("protected", rank=1, section="General", text="source priority")
    protected_row["score"] = 10.0

    def fail_if_called(*args, **kwargs):
        raise AssertionError("section candidate collection should reuse precomputed scores")

    monkeypatch.setattr(module, "score_chunks_mvp003", fail_if_called)

    rows = module.collect_hybrid_section_candidates(
        question=question,
        records=[],
        chunks=[],
        protected_rows=[protected_row],
        scored_results=[fake_mvp003_result(row, score=9.5)],
    )

    assert [candidate["chunk_id"] for candidate in rows] == ["section-match"]
    assert rows[0]["section_candidate_rank"] == 1


def test_disabled_reranker_eval_preserves_default_order():
    module = load_eval_module()
    question = eval_question()
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
    question = eval_question()
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


def test_fail_closed_policy_falls_back_and_reports_diagnostics():
    module = load_eval_module()
    question = eval_question()
    base_rows = source_at3_regression_fixture_rows()
    results = {"Q1": base_rows}

    application = module.apply_reranker_to_results_with_diagnostics(
        [question],
        results,
        reranker=module.build_reranker(module.RERANKER_DETERMINISTIC_TEST),
        limit=5,
        reranker_policy=module.RERANKER_POLICY_FAIL_CLOSED,
    )

    assert [row["chunk_id"] for row in application.results_by_question["Q1"]] == [row["chunk_id"] for row in base_rows]
    assert application.fallback_diagnostics == {"Q1": ("top3_source_identity_lost",)}


def test_direct_policy_keeps_deterministic_test_behavior_unchanged():
    module = load_eval_module()
    question = eval_question()
    base_rows = source_at3_regression_fixture_rows()

    reranked = module.apply_reranker_to_results(
        [question],
        {"Q1": base_rows},
        reranker=module.build_reranker(module.RERANKER_DETERMINISTIC_TEST),
        limit=5,
    )

    assert [row["chunk_id"] for row in reranked["Q1"]][:3] != [row["chunk_id"] for row in base_rows][:3]


def test_target_risk_question_fixture_contract_remains_locked():
    module = load_eval_module()
    questions = {question.question_id: question for question in module.load_questions(REPO_ROOT / "eval" / "retrieval_questions.jsonl")}
    expected = module.load_expected_sources(REPO_ROOT / "eval" / "expected_sources.jsonl")

    assert set(TARGET_RISK_QUESTION_IDS).issubset(questions)
    assert {
        question_id: (
            questions[question_id].expected_source_file,
            questions[question_id].expected_chunk_or_section,
            questions[question_id].expected_path_context,
            expected[question_id]["expected_source_priority"],
            expected[question_id]["expected_evidence_label"],
        )
        for question_id in TARGET_RISK_QUESTION_IDS
    } == {
        "MVP0025-Q001": ("00_ADMIN/source_priority_policy.md", "Core Source Philosophy", "", "P0", "Document-Supported Fact"),
        "MVP0025-Q004": (
            "01_RAW_SOURCES/P0_ACTIVE_PROMPT/P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf",
            "SINGLE SOURCE OF TRUTH",
            "",
            "P0",
            "Document-Supported Fact",
        ),
        "MVP0025-Q010": (
            "01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx",
            "",
            "P1_RND_PROJECTS",
            "P1",
            "Document-Supported Fact",
        ),
    }


@pytest.mark.parametrize("base_mode", ["mvp003-deterministic-metadata", "mvp006-hybrid-metadata-vector"])
def test_fail_closed_policy_prevents_target_risk_source_at3_regression(base_mode):
    module = load_eval_module()
    questions = load_target_risk_questions(module)
    base_results = target_risk_source_at3_regression_results(questions)
    base_summary = module.score_results(questions, base_results)
    reranker = module.build_reranker(module.RERANKER_DETERMINISTIC_TEST)

    direct_results = module.apply_reranker_to_results(
        questions,
        base_results,
        reranker=reranker,
        limit=5,
    )
    direct_summary = module.score_results(questions, direct_results)
    direct_comparison = module.compare_reranker_outputs(
        questions=questions,
        base_results=base_results,
        reranked_results=direct_results,
        base_summary=base_summary,
        reranked_summary=direct_summary,
        base_mode=base_mode,
        reranker_name=module.RERANKER_DETERMINISTIC_TEST,
    )

    assert direct_comparison["source_file_match_at_3_delta"] < 0.0
    assert direct_comparison["source_file_match_at_5_delta"] == 0.0
    assert direct_comparison["would_fail_closed_count"] == len(TARGET_RISK_QUESTION_IDS)
    assert direct_comparison["would_fail_closed_reasons"]["source_at3_regression"] == len(TARGET_RISK_QUESTION_IDS)
    assert direct_comparison["would_fail_closed_reasons"]["top3_source_identity_lost"] == len(TARGET_RISK_QUESTION_IDS)

    application = module.apply_reranker_to_results_with_diagnostics(
        questions,
        base_results,
        reranker=reranker,
        limit=5,
        reranker_policy=module.RERANKER_POLICY_FAIL_CLOSED,
    )
    fail_closed_summary = module.score_results(questions, application.results_by_question)
    fail_closed_comparison = module.compare_reranker_outputs(
        questions=questions,
        base_results=base_results,
        reranked_results=application.results_by_question,
        base_summary=base_summary,
        reranked_summary=fail_closed_summary,
        base_mode=base_mode,
        reranker_name=module.RERANKER_DETERMINISTIC_TEST,
        reranker_policy=module.RERANKER_POLICY_FAIL_CLOSED,
        fallback_diagnostics=application.fallback_diagnostics,
    )

    for metric in (
        "source_file_match_at_3",
        "source_file_match_at_5",
        "source_priority_match",
        "evidence_label_match",
        "section_match",
        "path_context_match",
        "overall_pass_rate",
    ):
        assert fail_closed_summary[metric] == base_summary[metric]
    for delta in (
        "source_file_match_at_3_delta",
        "source_file_match_at_5_delta",
        "source_priority_match_delta",
        "evidence_label_match_delta",
        "section_match_delta",
        "path_context_match_delta",
        "overall_pass_rate_delta",
    ):
        assert fail_closed_comparison[delta] == 0.0
    assert fail_closed_comparison["fallback_count"] == len(TARGET_RISK_QUESTION_IDS)
    assert fail_closed_comparison["fallback_reasons"] == {"top3_source_identity_lost": len(TARGET_RISK_QUESTION_IDS)}


def test_deterministic_test_reranker_eval_preserves_metadata_fields():
    module = load_eval_module()
    question = eval_question()
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
            "rank",
            "score",
            "score_components",
        ):
            assert row[field_name] == original[field_name]


def test_reranker_comparison_reports_top_k_ordering_changes():
    module = load_eval_module()
    question = eval_question()
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
    assert comparison["top3_changed_question_ids"] == ["Q1"]
    assert comparison["top5_changed_question_ids"] == ["Q1"]
    assert comparison["source_file_match_at_3_delta"] == 0.0
    assert comparison["source_file_match_at_5_delta"] == 0.0
    assert comparison["source_priority_match_delta"] == 0.0
    assert comparison["evidence_label_match_delta"] == 0.0
    assert comparison["section_match_delta"] == 1.0
    assert comparison["path_context_match_delta"] is None
    assert comparison["top3_source_identity_preserved_count"] == 1
    assert comparison["top5_source_coverage_preserved_count"] == 1
    assert comparison["candidate_dropped_count"] == 0
    assert comparison["candidate_duplicated_count"] == 0
    assert comparison["candidate_introduced_count"] == 0
    assert comparison["metadata_preservation_violation_count"] == 0
    assert comparison["would_fail_closed_count"] == 0
    assert comparison["would_fail_closed_reasons"] == {}


def test_candidate_identity_prefers_stable_composite_fields():
    module = load_eval_module()
    row = eval_candidate("chunk-a", rank=1, section="General", text="body")

    assert module.candidate_identity(row) == "ASP-P0-EVAL|AGENTS.md|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa|chunk-a"
    assert module.candidate_identity({"source_file": "AGENTS.md"}) == "AGENTS.md"


def test_candidate_preservation_delta_reports_dropped_duplicated_and_introduced_candidates():
    module = load_eval_module()
    base_rows = [
        eval_candidate("chunk-a", rank=1, section="General", text="a"),
        eval_candidate("chunk-b", rank=2, section="General", text="b"),
    ]
    reranked_rows = [
        eval_candidate("chunk-a", rank=1, section="General", text="a"),
        eval_candidate("chunk-a", rank=1, section="General", text="a"),
        eval_candidate("chunk-c", rank=3, section="General", text="c"),
    ]

    delta = module.candidate_preservation_delta(base_rows, reranked_rows)

    assert delta == {"dropped": 1, "duplicated": 1, "introduced": 1}


def test_source_identity_preservation_counts_top3_and_top5_coverage():
    module = load_eval_module()
    question = eval_question()
    base_results = {"Q1": [eval_candidate_for_source(f"base-{index}", source_id=f"SRC-{index}") for index in range(1, 6)]}
    reranked_results = {
        "Q1": [
            eval_candidate_for_source("base-3", source_id="SRC-3"),
            eval_candidate_for_source("base-2", source_id="SRC-2"),
            eval_candidate_for_source("base-1", source_id="SRC-1"),
            eval_candidate_for_source("base-5", source_id="SRC-5"),
            eval_candidate_for_source("base-4", source_id="SRC-4"),
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

    assert comparison["top3_source_identity_preserved_count"] == 1
    assert comparison["top5_source_coverage_preserved_count"] == 1
    assert comparison["would_fail_closed_count"] == 0


def test_grounding_metadata_mutation_is_reported_without_changing_eval_semantics():
    module = load_eval_module()
    question = eval_question()
    base_row = eval_candidate("chunk-a", rank=1, section="Source Priority Policy", text="source priority policy")
    mutated_row = {**base_row, "source_priority": "P5"}
    base_results = {"Q1": [base_row]}
    reranked_results = {"Q1": [mutated_row]}
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

    assert comparison["metadata_preservation_violation_count"] == 1
    assert comparison["would_fail_closed_count"] == 1
    assert comparison["would_fail_closed_reasons"]["grounding_metadata_mutated"] == 1
    assert comparison["would_fail_closed_reasons"]["priority_regression"] == 1

    content_hash_mutation_count = module.grounding_metadata_violation_count(
        [base_row],
        [{**base_row, "content_hash": "b" * 64}],
    )
    assert content_hash_mutation_count == 1


def test_would_fail_closed_reason_aggregation_reports_source_at3_regression():
    module = load_eval_module()
    question = eval_question()
    base_results = {
        "Q1": [
            eval_candidate_for_source("expected", source_id="EXPECTED", source_file="AGENTS.md"),
            eval_candidate_for_source("other-1", source_id="OTHER-1", source_file="README.md"),
            eval_candidate_for_source("other-2", source_id="OTHER-2", source_file="README.md"),
            eval_candidate_for_source("other-3", source_id="OTHER-3", source_file="README.md"),
        ]
    }
    reranked_results = {
        "Q1": [
            eval_candidate_for_source("other-1", source_id="OTHER-1", source_file="README.md"),
            eval_candidate_for_source("other-2", source_id="OTHER-2", source_file="README.md"),
            eval_candidate_for_source("other-3", source_id="OTHER-3", source_file="README.md"),
            eval_candidate_for_source("expected", source_id="EXPECTED", source_file="AGENTS.md"),
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

    assert comparison["source_file_match_at_3_delta"] == -1.0
    assert comparison["source_file_match_at_5_delta"] == 0.0
    assert comparison["would_fail_closed_count"] == 1
    assert comparison["would_fail_closed_reasons"]["source_at3_regression"] == 1
    assert comparison["would_fail_closed_reasons"]["top3_source_identity_lost"] == 1


def test_json_summary_is_backward_compatible_and_additive_for_reranker(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(
        results_path,
        [
            {
                "question_id": "Q1",
                "results": [
                    eval_candidate("weak", rank=1, section="General", text="unrelated"),
                    eval_candidate("strong", rank=2, section="Source Priority Policy", text="source priority policy"),
                ],
            }
        ],
    )

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--reranker",
            module.RERANKER_DETERMINISTIC_TEST,
            "--limit",
            "5",
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    comparison = payload["reranker_comparison"]
    assert comparison["top1_changed_count"] == 1
    assert comparison["source_file_match_at_3_delta"] == 0.0
    assert comparison["top3_source_identity_preserved_count"] == 1
    assert comparison["candidate_dropped_count"] == 0
    assert comparison["would_fail_closed_reasons"] == {}
    assert "fallback_count" not in comparison
    assert "reranker_policy" not in comparison


def test_fail_closed_json_summary_adds_fallback_diagnostics_only_when_enabled(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(results_path, [{"question_id": "Q1", "results": source_at3_regression_fixture_rows()}])

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--reranker",
            module.RERANKER_DETERMINISTIC_TEST,
            "--reranker-policy",
            module.RERANKER_POLICY_FAIL_CLOSED,
            "--limit",
            "5",
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    comparison = payload["reranker_comparison"]
    assert payload["source_file_match_at_3"] == 1.0
    assert comparison["reranker_policy"] == module.RERANKER_POLICY_FAIL_CLOSED
    assert comparison["fallback_count"] == 1
    assert comparison["fallback_reasons"] == {"top3_source_identity_lost": 1}
    assert comparison["fallback_by_question"] == [
        {"question_id": "Q1", "fallback_reasons": ["top3_source_identity_lost"]}
    ]
    assert comparison["source_file_match_at_3_delta"] == 0.0


def test_fail_closed_stdout_summary_is_additive_only_when_enabled(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(results_path, [{"question_id": "Q1", "results": source_at3_regression_fixture_rows()}])

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--reranker",
            module.RERANKER_DETERMINISTIC_TEST,
            "--reranker-policy",
            module.RERANKER_POLICY_FAIL_CLOSED,
            "--limit",
            "5",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Candidate preservation:" in output
    assert "Fail-closed fallback:" in output
    assert "Fallback count: 1/1" in output


def test_json_summary_without_reranker_keeps_existing_shape(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(
        results_path,
        [{"question_id": "Q1", "results": [eval_candidate("weak", rank=1, section="Source Priority Policy", text="source priority policy")]}],
    )

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "reranker_comparison" not in payload


def test_stdout_without_reranker_keeps_existing_shape(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(
        results_path,
        [{"question_id": "Q1", "results": [eval_candidate("weak", rank=1, section="Source Priority Policy", text="source priority policy")]}],
    )

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Candidate preservation:" not in output
    assert "Fail-closed fallback:" not in output


def test_threshold_report_passes_when_profile_minimums_are_met():
    module = load_eval_module()
    summary = {
        "source_file_match_at_5": 1.0,
        "source_priority_match": 1.0,
        "evidence_label_match": 1.0,
        "section_match": 0.95,
        "path_context_match": 1.0,
        "overall_pass_rate": 0.95,
    }

    report = module.evaluate_thresholds(summary, "mvp003")

    assert report["profile"] == "mvp003"
    assert report["passed"] is True
    assert report["failures"] == []


def test_threshold_report_fails_when_required_metric_regresses():
    module = load_eval_module()
    summary = {
        "source_file_match_at_5": 1.0,
        "source_priority_match": 1.0,
        "evidence_label_match": 1.0,
        "section_match": 0.75,
        "path_context_match": 1.0,
        "overall_pass_rate": 0.89,
    }

    report = module.evaluate_thresholds(summary, "mvp003")

    assert report["passed"] is False
    assert [failure["metric"] for failure in report["failures"]] == ["section_match", "overall_pass_rate"]


def test_threshold_report_treats_unavailable_metric_as_not_applicable():
    module = load_eval_module()
    summary = {
        "source_file_match_at_5": 1.0,
        "source_priority_match": 1.0,
        "evidence_label_match": 1.0,
        "section_match": 1.0,
        "path_context_match": None,
        "overall_pass_rate": 1.0,
    }

    report = module.evaluate_thresholds(summary, "hybrid")

    assert report["passed"] is True
    path_context_metric = next(metric for metric in report["metrics"] if metric["metric"] == "path_context_match")
    assert path_context_metric["not_applicable"] is True
    assert path_context_metric["passed"] is True


def test_threshold_enforcement_returns_nonzero_on_failure(tmp_path):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(
        results_path,
        [
            {
                "question_id": "Q1",
                "results": [
                    {
                        "source_file": "README.md",
                        "source_priority": "P1",
                        "evidence_label": "Inference",
                        "section": "Other",
                        "title": "README",
                        "text": "Other text",
                    }
                ],
            }
        ],
    )

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--retriever",
            "mvp003",
            "--enforce-thresholds",
            "--json",
        ]
    )

    assert exit_code == 1


def test_progress_logging_uses_stderr_and_preserves_json_stdout(tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    results_path = tmp_path / "results.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])
    write_jsonl(
        results_path,
        [
            {
                "question_id": "Q1",
                "results": [
                    {
                        "source_file": "AGENTS.md",
                        "source_priority": "P0",
                        "evidence_label": "Document-Supported Fact",
                        "section": "Source Priority Policy",
                        "title": "AGENTS",
                        "text": "Source Priority Policy and evidence hierarchy",
                    }
                ],
            }
        ],
    )

    exit_code = module.main(
        [
            "--questions",
            str(questions_path),
            "--expected",
            str(expected_path),
            "--results-jsonl",
            str(results_path),
            "--retriever",
            "baseline",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out)["overall_pass_rate"] == 1.0
    assert "[retrieval-eval] loading questions" in captured.err
    assert "[retrieval-eval] aggregating retrieval metrics" in captured.err


def test_emit_line_flushes_output_stream():
    module = load_eval_module()
    stream = FlushTrackingStream()

    module.emit_line("reranker summary", stream=stream)

    assert stream.contents == "reranker summary\n"
    assert stream.flush_count == 1


class FlushTrackingStream:
    def __init__(self) -> None:
        self.contents = ""
        self.flush_count = 0

    def write(self, value: str) -> int:
        self.contents += value
        return len(value)

    def flush(self) -> None:
        self.flush_count += 1


def v112b_result(source_file: str, *, score: float = 1.0) -> dict:
    return {
        "source_file": source_file,
        "source_id": f"source::{source_file}",
        "source_priority": "P0",
        "evidence_label": "Document-Supported Fact",
        "section": "Source Priority Policy",
        "title": source_file,
        "text": "Source Priority Policy",
        "score": score,
    }


@pytest.mark.parametrize(
    ("results", "expected_rank", "expected_mrr"),
    [
        ([v112b_result("AGENTS.md")], 1, 1.0),
        ([v112b_result("README.md"), v112b_result("AGENTS.md")], 2, 0.5),
        (
            [v112b_result(name) for name in ("A.md", "B.md", "C.md", "D.md", "AGENTS.md")],
            5,
            0.2,
        ),
        ([v112b_result(name) for name in ("A.md", "B.md", "C.md", "D.md", "E.md", "AGENTS.md")], None, 0.0),
    ],
)
def test_v112b_strict_source_rank_and_mrr_are_source_level(results, expected_rank, expected_mrr):
    module = load_eval_module()
    summary = module.score_results([eval_question()], {"Q1": results})

    assert summary["per_question"][0]["strict_source_rank_at_5"] == expected_rank
    assert summary["mean_reciprocal_rank_at_5"] == expected_mrr
    assert summary["source_file_match_at_1"] == (1.0 if expected_rank == 1 else 0.0)


def test_v112b_strict_metrics_do_not_use_relaxed_aliases_or_accepted_sources():
    module = load_eval_module()
    question = module.EvalQuestion(**{**eval_question().__dict__, "accepted_sources": ("README.md",), "multi_valid_source": True})
    summary = module.score_results([question], {"Q1": [v112b_result("README.md")]})

    assert summary["source_file_match_at_1"] == 0.0
    assert summary["mean_reciprocal_rank_at_5"] == 0.0
    assert summary["source_level_ndcg_at_5"] == 0.0


def test_v112b_duplicate_chunks_do_not_distort_source_rank_or_ndcg():
    module = load_eval_module()
    results = [v112b_result("README.md"), v112b_result("README.md"), v112b_result("AGENTS.md")]
    summary = module.score_results([eval_question()], {"Q1": results})

    assert summary["per_question"][0]["strict_source_rank_at_5"] == 2
    assert summary["mean_reciprocal_rank_at_5"] == 0.5
    assert summary["source_level_ndcg_at_5"] == pytest.approx(1.0 / __import__("math").log2(3))


def test_v112b_metric_outputs_are_finite_bounded_and_serialized():
    module = load_eval_module()
    summary = module.score_results([eval_question()], {"Q1": []})

    assert summary["per_question"][0]["strict_source_rank_at_5"] is None
    for name in ("source_file_match_at_1", "mean_reciprocal_rank_at_5", "source_level_ndcg_at_5"):
        assert 0.0 <= summary[name] <= 1.0
    assert json.loads(json.dumps(summary))["per_question"][0]["strict_source_rank_at_5"] is None


def test_v112b_missing_source_identity_fails_closed():
    module = load_eval_module()

    with pytest.raises(module.EvalError, match="source_file identity"):
        module.score_results([eval_question()], {"Q1": [{"source_file": ""}]})


def test_v112b_percentile_and_latency_summary_are_deterministic():
    module = load_eval_module()

    assert module.deterministic_percentile([10.0], 50.0) == 10.0
    assert module.deterministic_percentile([10.0, 30.0], 50.0) == 20.0
    assert module.deterministic_percentile([40.0, 10.0, 30.0, 20.0], 95.0) == 38.5
    assert module.summarize_latency_ms([10.0, 30.0]) == {
        "count": 2, "min": 10.0, "mean": 20.0, "p50": 20.0, "p95": 29.0, "max": 30.0, "total": 40.0,
    }


@pytest.mark.parametrize("samples", [[], [-1.0], [float("inf")]])
def test_v112b_latency_rejects_empty_negative_and_nonfinite_samples(samples):
    module = load_eval_module()

    with pytest.raises(module.EvalError):
        module.summarize_latency_ms(samples)


@pytest.mark.parametrize("retriever", ["baseline", "mvp003", "vector"])
def test_v112b_oracle_free_retrievers_receive_safe_projection(monkeypatch, retriever):
    module = load_eval_module()
    received = []

    def fake_retrieval(questions, registry_path, chunks_path, limit):
        received.extend(questions)
        return {"Q1": []}

    monkeypatch.setattr(module, {"baseline": "run_baseline_retrieval", "mvp003": "run_mvp003_retrieval", "vector": "run_vector_retrieval"}[retriever], fake_retrieval)
    module.run_retriever(retriever, [eval_question()], Path("registry.csv"), Path("chunks.jsonl"), 5)

    assert received and type(received[0]) is module.RetrievalQuestion
    assert received[0].question_id == "Q1"
    assert not hasattr(received[0], "expected_source_file")
    assert not hasattr(received[0], "accepted_sources")


def test_v112b_reranked_diagnostics_preserve_retrieval_latency(monkeypatch, tmp_path, capsys):
    module = load_eval_module()
    questions_path = tmp_path / "questions.jsonl"
    expected_path = tmp_path / "expected.jsonl"
    write_jsonl(questions_path, [valid_question()])
    write_jsonl(expected_path, [valid_expected()])

    monkeypatch.setattr(
        module,
        "run_retriever_with_diagnostics",
        lambda *args: (
            "mvp006-hybrid-metadata-vector",
            {"Q1": [v112b_result("AGENTS.md")]},
            {"per_question": [{"question_id": "Q1", "retrieval_latency_ms": 1.0}], "retrieval_latency_ms": {"count": 1}, "end_to_end_ms": 1.0},
        ),
    )

    assert module.main([
        "--questions", str(questions_path), "--expected", str(expected_path), "--retriever", "hybrid",
        "--reranker", module.RERANKER_DETERMINISTIC_TEST, "--measure-diagnostics", "--json",
    ]) == 0
    assert json.loads(capsys.readouterr().out)["diagnostics"]["retrieval_latency_ms"] == {"count": 1}


def eval_question():
    module = load_eval_module()
    return module.EvalQuestion(
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


def eval_candidate_for_source(
    chunk_id: str,
    source_id: str,
    source_file: str = "AGENTS.md",
    rank: int = 1,
) -> dict:
    row = eval_candidate(chunk_id, rank=rank, section="Source Priority Policy", text="source priority policy")
    row["source_id"] = source_id
    row["source_file"] = source_file
    row["content_hash"] = f"{chunk_id:0<64}"[:64]
    return row


def source_at3_regression_fixture_rows() -> list[dict]:
    expected = eval_candidate_for_source("expected", source_id="EXPECTED", source_file="AGENTS.md", rank=1)
    expected["text"] = "unrelated"
    expected["section"] = "General"
    expected["section_heading"] = "General"
    expected["section_path"] = ["Governance", "General"]
    expected["heading_context"] = "Governance > General"
    return [
        expected,
        eval_candidate_for_source("other-1", source_id="OTHER-1", source_file="README-1.md", rank=2),
        eval_candidate_for_source("other-2", source_id="OTHER-2", source_file="README-2.md", rank=3),
        eval_candidate_for_source("other-3", source_id="OTHER-3", source_file="README-3.md", rank=4),
        eval_candidate_for_source("other-4", source_id="OTHER-4", source_file="README-4.md", rank=5),
    ]


def load_target_risk_questions(module):
    questions = module.load_questions(REPO_ROOT / "eval" / "retrieval_questions.jsonl")
    by_id = {question.question_id: question for question in questions}
    return [by_id[question_id] for question_id in TARGET_RISK_QUESTION_IDS]


def target_risk_source_at3_regression_results(questions) -> dict[str, list[dict]]:
    return {question.question_id: source_at3_regression_rows_for_question(question) for question in questions}


def source_at3_regression_rows_for_question(question) -> list[dict]:
    expected = eval_candidate_for_source(
        f"{question.question_id}-expected",
        source_id=f"{question.question_id}-EXPECTED",
        source_file=question.expected_source_file,
        rank=1,
    )
    expected["source_priority"] = question.expected_source_priority
    expected["evidence_label"] = question.expected_evidence_label
    expected["section"] = question.expected_chunk_or_section or "Registered Source Location"
    expected["section_heading"] = expected["section"]
    expected["section_path"] = ["Target Risk", expected["section"]]
    expected["heading_context"] = f"Target Risk > {expected['section']}"
    expected["title"] = f"{question.question_id} expected source"
    expected["text"] = "registered source placeholder"

    rows = [expected]
    for index in range(1, 5):
        distractor = eval_candidate_for_source(
            f"{question.question_id}-distractor-{index}",
            source_id=f"{question.question_id}-DISTRACTOR-{index}",
            source_file=f"unrelated/{question.question_id}/distractor-{index}.md",
            rank=index + 1,
        )
        distractor["title"] = f"{question.question_id} high lexical overlap {index}"
        distractor["section"] = f"High Overlap {index}"
        distractor["section_heading"] = distractor["section"]
        distractor["section_path"] = ["Target Risk", distractor["section"]]
        distractor["heading_context"] = f"Target Risk > {distractor['section']}"
        distractor["text"] = f"{question.user_question} {question.user_question}"
        rows.append(distractor)
    return rows


def fake_mvp003_result(row: dict, source_id: str = "ASP-P0-EVAL", score: float = 1.0):
    payload = {**row, "source_id": source_id, "score": score}
    chunk = SimpleNamespace(
        chunk_id=payload["chunk_id"],
        source_id=payload["source_id"],
        source_priority=payload["source_priority"],
        char_start=payload.get("char_start", 0),
    )
    return SimpleNamespace(
        chunk=chunk,
        score=score,
        source_file=payload["source_file"],
        score_components=payload.get("score_components", {}),
        to_json=lambda: dict(payload),
    )
