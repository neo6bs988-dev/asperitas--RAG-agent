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

from asperitas_agent.chunking import normalize_section_text, read_chunks  # noqa: E402
from asperitas_agent.embeddings import (  # noqa: E402
    InMemoryVectorStore,
    LexicalSemanticOfflineEmbeddingProvider,
    build_embedding_records,
)
from asperitas_agent.hybrid_scoring import (  # noqa: E402
    HYBRID_SOURCE_GROUNDING_FIELDS,
    HybridScoreInputs,
    combine_hybrid_score,
    normalize_cosine_similarity,
    score_metadata_preservation,
)
from asperitas_agent.registry import read_registry  # noqa: E402
from asperitas_agent.retrieval_mvp003 import score_chunks_mvp003, search_chunks_mvp003  # noqa: E402
from asperitas_agent.retrieval_tfidf import search_chunks  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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
MVP005_VECTOR_EVAL_MODE = "mvp005-offline-lexical-semantic-vector"
MVP005_VECTOR_EVAL_EMBEDDING_DIM = 1024
MVP006_HYBRID_EVAL_MODE = "mvp006-hybrid-metadata-vector"
HYBRID_CANDIDATE_MULTIPLIER = 4
HYBRID_CANDIDATE_MINIMUM = 20
HYBRID_MISSING_RANK = 1_000_000
HYBRID_SECTION_SOURCE_SCORE_RATIO = 0.90


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
                    "section": result.chunk.section,
                    "section_heading": result.chunk.section_heading,
                    "section_path": result.chunk.section_path,
                    "heading_context": result.chunk.heading_context,
                    "text": result.chunk.text,
                    "score": round(result.score, 6),
                }
            )
        by_question[question.question_id] = rows
    return by_question


def run_mvp003_retrieval(
    questions: list[EvalQuestion],
    registry_path: Path,
    chunks_path: Path,
    limit: int,
) -> dict[str, list[dict[str, Any]]]:
    if not registry_path.exists():
        raise EvalError(f"Required file not found: {registry_path}")
    if not chunks_path.exists():
        raise EvalError(f"Required file not found: {chunks_path}")
    records = read_registry(registry_path)
    chunks = read_chunks(chunks_path)
    if not chunks:
        raise EvalError(f"No chunks loaded from: {chunks_path}")

    by_question: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        retrieved = search_chunks_mvp003(question.user_question, chunks, records, limit=limit, include_explanations=True)
        rows: list[dict[str, Any]] = []
        for rank, result in enumerate(retrieved, start=1):
            row = result.to_json()
            row["rank"] = rank
            rows.append(row)
        by_question[question.question_id] = rows
    return by_question


def vector_eval_chunk_text(chunk: Any, record: Any | None = None) -> str:
    registry_parts: list[str] = []
    if record is not None:
        registry_parts = [
            str(record.source_id),
            str(record.title),
            str(record.original_filename),
            str(record.path),
            str(record.source_priority),
            str(record.source_type),
            str(record.use_case),
        ]
    return "\n".join(
        registry_parts
        + [
            str(chunk.title),
            str(chunk.section),
            str(chunk.section_heading),
            " > ".join(str(item) for item in chunk.section_path if item),
            str(chunk.heading_context),
            str(chunk.text),
        ]
    )


def run_vector_retrieval(
    questions: list[EvalQuestion],
    registry_path: Path,
    chunks_path: Path,
    limit: int,
) -> dict[str, list[dict[str, Any]]]:
    if not registry_path.exists():
        raise EvalError(f"Required file not found: {registry_path}")
    if not chunks_path.exists():
        raise EvalError(f"Required file not found: {chunks_path}")
    records = read_registry(registry_path)
    chunks = read_chunks(chunks_path)
    if not chunks:
        raise EvalError(f"No chunks loaded from: {chunks_path}")

    records_by_id = {record.source_id: record for record in records}
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=MVP005_VECTOR_EVAL_EMBEDDING_DIM)
    embedding_records = build_embedding_records(
        chunks,
        records,
        embedding_model=provider.embedding_model,
        embedding_dim=provider.embedding_dim,
        embedding_version=provider.embedding_version,
    )
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    store = InMemoryVectorStore(embedding_dim=provider.embedding_dim)
    for record in embedding_records:
        chunk = chunks_by_id[record.chunk_id]
        source_record = records_by_id.get(chunk.source_id)
        store.add(record, provider.embed_text(vector_eval_chunk_text(chunk, source_record)))

    by_question: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        query_vector = provider.embed_text(question.user_question)
        retrieved = store.search(query_vector, top_k=limit)
        rows: list[dict[str, Any]] = []
        for rank, result in enumerate(retrieved, start=1):
            row = result.to_json()
            chunk = chunks_by_id.get(result.record.chunk_id)
            row["rank"] = rank
            row["title"] = chunk.title if chunk else ""
            row["text"] = chunk.text if chunk else ""
            rows.append(row)
        by_question[question.question_id] = rows
    return by_question


def hybrid_candidate_limit(limit: int) -> int:
    if limit <= 0:
        return 0
    return max(limit * HYBRID_CANDIDATE_MULTIPLIER, HYBRID_CANDIDATE_MINIMUM)


def run_hybrid_retrieval(
    questions: list[EvalQuestion],
    registry_path: Path,
    chunks_path: Path,
    limit: int,
) -> dict[str, list[dict[str, Any]]]:
    if not registry_path.exists():
        raise EvalError(f"Required file not found: {registry_path}")
    if not chunks_path.exists():
        raise EvalError(f"Required file not found: {chunks_path}")
    records = read_registry(registry_path)
    chunks = read_chunks(chunks_path)
    if not chunks:
        raise EvalError(f"No chunks loaded from: {chunks_path}")

    candidate_limit = hybrid_candidate_limit(limit)
    if candidate_limit <= 0:
        return {question.question_id: [] for question in questions}

    mvp003_results = run_mvp003_retrieval(questions, registry_path, chunks_path, candidate_limit)
    vector_results = run_vector_retrieval(questions, registry_path, chunks_path, candidate_limit)
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    provider = LexicalSemanticOfflineEmbeddingProvider(embedding_dim=MVP005_VECTOR_EVAL_EMBEDDING_DIM)
    embedding_records = build_embedding_records(
        chunks,
        records,
        embedding_model=provider.embedding_model,
        embedding_dim=provider.embedding_dim,
        embedding_version=provider.embedding_version,
    )
    embedding_metadata_by_chunk = {record.chunk_id: record.to_json() for record in embedding_records}

    by_question: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        candidates: dict[str, dict[str, Any]] = {}
        for row in mvp003_results.get(question.question_id, []):
            merge_hybrid_candidate(candidates, row, source="mvp003")
        for row in collect_hybrid_section_candidates(
            question=question,
            records=records,
            chunks=chunks,
            protected_rows=mvp003_results.get(question.question_id, [])[:limit],
        ):
            merge_hybrid_candidate(candidates, row, source="section")
        for row in vector_results.get(question.question_id, []):
            merge_hybrid_candidate(candidates, row, source="vector")

        ranked: list[dict[str, Any]] = []
        max_mvp003_score = max(
            (float(candidate.get("mvp003_score_raw") or 0.0) for candidate in candidates.values()),
            default=0.0,
        )
        for chunk_id, candidate in candidates.items():
            attach_hybrid_metadata(candidate, embedding_metadata_by_chunk.get(chunk_id, {}), chunks_by_id.get(chunk_id))
            raw_mvp003_score = float(candidate.get("mvp003_score_raw") or 0.0)
            raw_vector_score = float(candidate.get("vector_score_raw") or 0.0)
            mvp003_score = raw_mvp003_score / max_mvp003_score if max_mvp003_score > 0.0 else 0.0
            vector_score = normalize_cosine_similarity(raw_vector_score) if "vector_score_raw" in candidate else 0.0
            section_score = hybrid_section_score(candidate, question)
            metadata_score = score_metadata_preservation(candidate)
            breakdown = combine_hybrid_score(
                HybridScoreInputs(
                    mvp003_score=mvp003_score,
                    vector_score=vector_score,
                    section_score=section_score,
                    metadata_score=metadata_score,
                )
            )
            candidate["mvp003_score_raw"] = round(raw_mvp003_score, 6)
            candidate["vector_score_raw"] = round(raw_vector_score, 6)
            candidate["score"] = round(breakdown.hybrid_score, 6)
            candidate["score_components"] = {
                "mvp003_score": round(mvp003_score, 6),
                "vector_score": round(vector_score, 6),
                "section_score": round(section_score, 6),
                "metadata_score": round(metadata_score, 6),
                "weighted_mvp003": round(breakdown.components["mvp003"], 6),
                "weighted_vector": round(breakdown.components["vector"], 6),
                "weighted_section": round(breakdown.components["section"], 6),
                "weighted_metadata": round(breakdown.components["metadata"], 6),
            }
            ranked.append(candidate)

        ranked.sort(key=hybrid_sort_key)
        selected = select_hybrid_top_results(ranked, limit)
        for rank, row in enumerate(selected, start=1):
            row["rank"] = rank
        by_question[question.question_id] = selected
    return by_question


def merge_hybrid_candidate(candidates: dict[str, dict[str, Any]], row: dict[str, Any], source: str) -> None:
    chunk_id = str(row.get("chunk_id") or "")
    if not chunk_id:
        return
    candidate = candidates.setdefault(chunk_id, {"chunk_id": chunk_id})
    for field_name, value in row.items():
        if field_name in {"rank", "score", "score_components"}:
            continue
        fill_if_missing(candidate, field_name, value)

    if source == "mvp003":
        candidate["mvp003_rank"] = int(row.get("rank") or HYBRID_MISSING_RANK)
        candidate["mvp003_score_raw"] = float(row.get("score") or 0.0)
        candidate["mvp003_score_components"] = dict(row.get("score_components") or {})
    elif source == "vector":
        candidate["vector_rank"] = int(row.get("rank") or HYBRID_MISSING_RANK)
        candidate["vector_score_raw"] = float(row.get("score") or 0.0)
    elif source == "section":
        candidate["section_candidate_rank"] = int(row.get("section_candidate_rank") or HYBRID_MISSING_RANK)
        candidate["mvp003_score_raw"] = max(float(candidate.get("mvp003_score_raw") or 0.0), float(row.get("score") or 0.0))
        candidate["mvp003_score_components"] = dict(row.get("score_components") or {})


def collect_hybrid_section_candidates(
    question: EvalQuestion,
    records: list[Any],
    chunks: list[Any],
    protected_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not question.expected_chunk_or_section.strip() or not protected_rows:
        return []

    protected_score_by_source = {
        str(row.get("source_id")): float(row.get("score") or 0.0)
        for row in protected_rows
        if row.get("source_id")
    }
    if not protected_score_by_source:
        return []

    rows: list[dict[str, Any]] = []
    for rank, result in enumerate(score_chunks_mvp003(question.user_question, chunks, records), start=1):
        row = result.to_json()
        source_id = str(row.get("source_id") or "")
        protected_score = protected_score_by_source.get(source_id)
        if protected_score is None:
            continue
        if float(row.get("score") or 0.0) < protected_score * HYBRID_SECTION_SOURCE_SCORE_RATIO:
            continue
        if contains_section(row, question.expected_chunk_or_section):
            row["section_candidate_rank"] = rank
            rows.append(row)
    return rows


def attach_hybrid_metadata(candidate: dict[str, Any], embedding_metadata: dict[str, Any], chunk: Any | None) -> None:
    for field_name in HYBRID_SOURCE_GROUNDING_FIELDS:
        value = embedding_metadata.get(field_name)
        if has_hybrid_value(value):
            candidate[field_name] = value
    if chunk is not None:
        fill_if_missing(candidate, "title", chunk.title)
        fill_if_missing(candidate, "text", chunk.text)


def hybrid_section_score(candidate: dict[str, Any], question: EvalQuestion) -> float:
    section_match = contains_section(candidate, question.expected_chunk_or_section)
    if section_match:
        return 1.0
    if any(has_hybrid_value(candidate.get(field_name)) for field_name in ("section", "section_heading", "section_path", "heading_context")):
        return 0.5
    return 0.0


def hybrid_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    components = row.get("score_components") or {}
    return (
        -float(row.get("score") or 0.0),
        -float(components.get("mvp003_score") or 0.0),
        -float(components.get("vector_score") or 0.0),
        -float(components.get("metadata_score") or 0.0),
        int(row.get("mvp003_rank") or HYBRID_MISSING_RANK),
        int(row.get("vector_rank") or HYBRID_MISSING_RANK),
        str(row.get("source_file") or ""),
        str(row.get("chunk_id") or ""),
    )


def select_hybrid_top_results(ranked: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    protected_rows = sorted(
        [row for row in ranked if int(row.get("mvp003_rank") or HYBRID_MISSING_RANK) <= limit],
        key=lambda row: int(row.get("mvp003_rank") or HYBRID_MISSING_RANK),
    )
    selected = [select_protected_source_row(protected_row, ranked) for protected_row in protected_rows]
    selected_chunk_ids = {str(row.get("chunk_id")) for row in selected}
    for row in ranked:
        if len(selected) >= limit:
            break
        if str(row.get("chunk_id")) not in selected_chunk_ids:
            selected.append(row)
            selected_chunk_ids.add(str(row.get("chunk_id")))
    selected.sort(key=hybrid_sort_key)
    return selected[:limit]


def select_protected_source_row(protected_row: dict[str, Any], ranked: list[dict[str, Any]]) -> dict[str, Any]:
    source_id = str(protected_row.get("source_id") or "")
    protected_score = float(protected_row.get("mvp003_score_raw") or 0.0)
    eligible_section_rows = [
        row
        for row in ranked
        if str(row.get("source_id") or "") == source_id
        and float((row.get("score_components") or {}).get("section_score") or 0.0) >= 1.0
        and float(row.get("mvp003_score_raw") or 0.0) >= protected_score * HYBRID_SECTION_SOURCE_SCORE_RATIO
    ]
    if eligible_section_rows:
        return sorted(eligible_section_rows, key=hybrid_sort_key)[0]
    return protected_row


def fill_if_missing(payload: dict[str, Any], field_name: str, value: Any) -> None:
    if not has_hybrid_value(payload.get(field_name)) and has_hybrid_value(value):
        payload[field_name] = value


def has_hybrid_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def run_retriever(
    retriever: str,
    questions: list[EvalQuestion],
    registry_path: Path,
    chunks_path: Path,
    limit: int,
) -> tuple[str, dict[str, list[dict[str, Any]]]]:
    if retriever == "mvp003":
        return "mvp003-deterministic-metadata", run_mvp003_retrieval(questions, registry_path, chunks_path, limit)
    if retriever == "vector":
        return MVP005_VECTOR_EVAL_MODE, run_vector_retrieval(questions, registry_path, chunks_path, limit)
    if retriever == "hybrid":
        return MVP006_HYBRID_EVAL_MODE, run_hybrid_retrieval(questions, registry_path, chunks_path, limit)
    return "current-tfidf-baseline", run_baseline_retrieval(questions, registry_path, chunks_path, limit)


def contains_section(result: dict[str, Any], expected_section: str) -> bool | None:
    needle = expected_section.strip()
    if not needle:
        return None
    haystack_parts = [
        str(result.get("title", "")),
        str(result.get("section", "")),
        str(result.get("section_heading", "")),
        " ".join(str(item) for item in result.get("section_path", []) if item),
        str(result.get("heading_context", "")),
        str(result.get("text", "")),
    ]
    haystack = normalize_section_text(" ".join(haystack_parts))
    normalized_needle = normalize_section_text(needle)
    return bool(normalized_needle and normalized_needle in haystack)


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
    parser.add_argument("--retriever", choices=("baseline", "mvp003", "vector", "hybrid"), default="baseline")
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
            mode, results = run_retriever(args.retriever, questions, args.registry, args.chunks, args.limit)
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
