from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.chunking import read_chunks  # noqa: E402
from asperitas_agent.registry import read_registry  # noqa: E402
from asperitas_agent.retrieval_tfidf import search_chunks  # noqa: E402


DIFFICULTIES = {"easy", "medium", "hard"}
CATEGORIES = {
    "company_strategy",
    "compliance",
    "synthetic_biology",
    "ai_agent",
    "operations",
    "market",
    "source_governance",
}
QUESTION_REQUIRED = {
    "question_id",
    "user_question",
    "expected_source_file",
    "expected_source_priority",
    "expected_chunk_or_section",
    "expected_evidence_label",
    "rationale",
    "difficulty",
    "category",
}
EXPECTED_REQUIRED = {
    "question_id",
    "expected_source_file",
    "expected_source_priority",
    "expected_evidence_label",
}


class EvalError(Exception):
    pass


@dataclass(frozen=True)
class EvalQuestion:
    question_id: str
    user_question: str
    expected_source_file: str
    expected_source_priority: str
    expected_chunk_or_section: str
    expected_evidence_label: str
    rationale: str
    difficulty: str
    category: str


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().casefold()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise EvalError(f"Required file not found: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvalError(f"{path}:{line_number} invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise EvalError(f"{path}:{line_number} must contain a JSON object")
            rows.append(payload)
    if not rows:
        raise EvalError(f"Required file is empty: {path}")
    return rows


def load_questions(path: Path) -> list[EvalQuestion]:
    rows = load_jsonl(path)
    questions: list[EvalQuestion] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        missing = sorted(QUESTION_REQUIRED - row.keys())
        if missing:
            raise EvalError(f"{path}:{index} missing required fields: {', '.join(missing)}")
        if row["difficulty"] not in DIFFICULTIES:
            raise EvalError(f"{path}:{index} invalid difficulty: {row['difficulty']}")
        if row["category"] not in CATEGORIES:
            raise EvalError(f"{path}:{index} invalid category: {row['category']}")
        question_id = str(row["question_id"])
        if question_id in seen_ids:
            raise EvalError(f"{path}:{index} duplicate question_id: {question_id}")
        seen_ids.add(question_id)
        questions.append(
            EvalQuestion(
                question_id=question_id,
                user_question=str(row["user_question"]),
                expected_source_file=str(row["expected_source_file"]),
                expected_source_priority=str(row["expected_source_priority"]),
                expected_chunk_or_section=str(row.get("expected_chunk_or_section") or ""),
                expected_evidence_label=str(row["expected_evidence_label"]),
                rationale=str(row["rationale"]),
                difficulty=str(row["difficulty"]),
                category=str(row["category"]),
            )
        )
    return questions


def load_expected_sources(path: Path) -> dict[str, dict[str, Any]]:
    rows = load_jsonl(path)
    expected: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows, start=1):
        missing = sorted(EXPECTED_REQUIRED - row.keys())
        if missing:
            raise EvalError(f"{path}:{index} missing required fields: {', '.join(missing)}")
        question_id = str(row["question_id"])
        if question_id in expected:
            raise EvalError(f"{path}:{index} duplicate question_id: {question_id}")
        expected[question_id] = row
    return expected


def validate_expected_alignment(questions: list[EvalQuestion], expected: dict[str, dict[str, Any]]) -> None:
    question_ids = {question.question_id for question in questions}
    expected_ids = set(expected)
    missing = sorted(question_ids - expected_ids)
    extra = sorted(expected_ids - question_ids)
    if missing:
        raise EvalError(f"Expected source rows missing for question_id: {', '.join(missing)}")
    if extra:
        raise EvalError(f"Expected source rows without matching question: {', '.join(extra)}")
    for question in questions:
        row = expected[question.question_id]
        for field in ("expected_source_file", "expected_source_priority", "expected_evidence_label"):
            if str(row[field]) != getattr(question, field):
                raise EvalError(f"{question.question_id} mismatch between questions and expected_sources for {field}")


def load_simulated_results(path: Path) -> dict[str, list[dict[str, Any]]]:
    rows = load_jsonl(path)
    results: dict[str, list[dict[str, Any]]] = {}
    for index, row in enumerate(rows, start=1):
        question_id = row.get("question_id")
        payload = row.get("results")
        if not question_id or not isinstance(payload, list):
            raise EvalError(f"{path}:{index} must include question_id and results list")
        results[str(question_id)] = [dict(result) for result in payload if isinstance(result, dict)]
    return results


def run_baseline_retrieval(
    questions: list[EvalQuestion],
    registry_path: Path,
    chunks_path: Path,
    limit: int,
) -> dict[str, list[dict[str, Any]]]:
    if not registry_path.exists():
        raise EvalError(f"Required file not found: {registry_path}")
    if not chunks_path.exists():
        raise EvalError(f"Required file not found: {chunks_path}")
    records = {record.source_id: record for record in read_registry(registry_path)}
    chunks = read_chunks(chunks_path)
    if not chunks:
        raise EvalError(f"No chunks loaded from: {chunks_path}")

    by_question: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        retrieved = search_chunks(question.user_question, chunks, limit=limit)
        rows: list[dict[str, Any]] = []
        for rank, result in enumerate(retrieved, start=1):
            record = records.get(result.chunk.source_id)
            rows.append(
                {
                    "rank": rank,
                    "source_id": result.chunk.source_id,
                    "source_file": record.path if record else "",
                    "source_priority": result.chunk.source_priority,
                    "evidence_label": result.chunk.evidence_label,
                    "title": result.chunk.title,
                    "text": result.chunk.text,
                    "score": round(result.score, 6),
                }
            )
        by_question[question.question_id] = rows
    return by_question


def contains_section(result: dict[str, Any], expected_section: str) -> bool | None:
    needle = expected_section.strip()
    if not needle:
        return None
    haystack = f"{result.get('title', '')} {result.get('text', '')}".casefold()
    return needle.casefold() in haystack


def score_question(question: EvalQuestion, results: list[dict[str, Any]]) -> dict[str, Any]:
    expected_file = normalize_path(question.expected_source_file)
    top3 = results[:3]
    top5 = results[:5]
    matched = next((result for result in top5 if normalize_path(str(result.get("source_file", ""))) == expected_file), None)
    section_match = contains_section(matched, question.expected_chunk_or_section) if matched else (None if not question.expected_chunk_or_section else False)
    source_file_match_top3 = any(normalize_path(str(result.get("source_file", ""))) == expected_file for result in top3)
    source_file_match_top5 = matched is not None
    source_priority_match = bool(matched and str(matched.get("source_priority")) == question.expected_source_priority)
    evidence_label_match = bool(matched and str(matched.get("evidence_label", question.expected_evidence_label)) == question.expected_evidence_label)
    overall_pass = bool(source_file_match_top5 and source_priority_match and evidence_label_match and section_match is not False)
    return {
        "question_id": question.question_id,
        "source_file_match_top3": source_file_match_top3,
        "source_file_match_top5": source_file_match_top5,
        "source_priority_match": source_priority_match,
        "evidence_label_match": evidence_label_match,
        "section_match": section_match,
        "overall_pass": overall_pass,
        "top_result_source_file": str(results[0].get("source_file", "")) if results else "",
    }


def score_results(questions: list[EvalQuestion], results_by_question: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    per_question = [score_question(question, results_by_question.get(question.question_id, [])) for question in questions]
    total = len(per_question)
    if total == 0:
        raise EvalError("No questions to score")

    def rate(field: str) -> float:
        return sum(1 for row in per_question if row[field]) / total

    section_rows = [row for row in per_question if row["section_match"] is not None]
    section_rate = None
    if section_rows:
        section_rate = sum(1 for row in section_rows if row["section_match"]) / len(section_rows)
    return {
        "total_questions": total,
        "source_file_match_at_3": rate("source_file_match_top3"),
        "source_file_match_at_5": rate("source_file_match_top5"),
        "source_priority_match": rate("source_priority_match"),
        "evidence_label_match": rate("evidence_label_match"),
        "section_match": section_rate,
        "overall_pass_rate": rate("overall_pass"),
        "per_question": per_question,
    }


def format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def print_summary(summary: dict[str, Any], mode: str) -> None:
    print("MVP-002.5 Retrieval Evaluation")
    print(f"Mode: {mode}")
    print(f"Questions: {summary['total_questions']}")
    print(f"Source file match @3: {format_percent(summary['source_file_match_at_3'])}")
    print(f"Source file match @5: {format_percent(summary['source_file_match_at_5'])}")
    print(f"Source priority match: {format_percent(summary['source_priority_match'])}")
    print(f"Evidence label match: {format_percent(summary['evidence_label_match'])}")
    print(f"Section match: {format_percent(summary['section_match'])}")
    print(f"Overall pass rate: {format_percent(summary['overall_pass_rate'])}")
    failed = [row for row in summary["per_question"] if not row["overall_pass"]]
    if failed:
        print("Failed question_ids:")
        for row in failed[:20]:
            print(f"- {row['question_id']} top_result={row['top_result_source_file']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic MVP-002.5 retrieval evaluation.")
    parser.add_argument("--questions", type=Path, default=REPO_ROOT / "eval" / "retrieval_questions.jsonl")
    parser.add_argument("--expected", type=Path, default=REPO_ROOT / "eval" / "expected_sources.jsonl")
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "data" / "source_registry.csv")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "data" / "chunks.jsonl")
    parser.add_argument("--results-jsonl", type=Path, default=None, help="Optional external retrieval results to score.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        questions = load_questions(args.questions)
        expected = load_expected_sources(args.expected)
        validate_expected_alignment(questions, expected)
        if args.results_jsonl:
            mode = "external-results"
            results = load_simulated_results(args.results_jsonl)
        else:
            mode = "current-tfidf-baseline"
            results = run_baseline_retrieval(questions, args.registry, args.chunks, args.limit)
        summary = score_results(questions, results)
    except EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_summary(summary, mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
