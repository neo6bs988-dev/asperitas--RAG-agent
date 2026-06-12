from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


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


def test_missing_jsonl_file_returns_eval_error(tmp_path):
    module = load_eval_module()

    with pytest.raises(module.EvalError, match="Required file not found"):
        module.load_jsonl(tmp_path / "missing.jsonl")
