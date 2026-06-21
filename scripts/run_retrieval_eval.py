from __future__ import annotations

import argparse
import faulthandler
import gc
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
from asperitas_agent.reranking import (  # noqa: E402
    RERANK_SOURCE_GROUNDING_FIELDS,
    DeterministicTestReranker,
    Reranker,
    rerank_candidates,
    rerank_candidates_fail_closed,
)
from asperitas_agent.retrieval_mvp003 import score_chunks_mvp003, search_chunks_mvp003  # noqa: E402
from asperitas_agent.retrieval_tfidf import search_chunks  # noqa: E402


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True, write_through=True)


def emit_line(message: str = "", *, stream: Any | None = None) -> None:
    print(message, file=stream or sys.stdout, flush=True)


configure_output_streams()


def enable_fault_diagnostics() -> None:
    try:
        faulthandler.enable(file=sys.stderr, all_threads=True)
    except (AttributeError, OSError, RuntimeError):
        return


enable_fault_diagnostics()


def emit_progress(message: str) -> None:
    emit_line(f"[retrieval-eval] {message}", stream=sys.stderr)


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
RERANKER_NONE = "none"
RERANKER_DETERMINISTIC_TEST = "deterministic-test"
RERANKER_POLICY_DIRECT = "direct"
RERANKER_POLICY_FAIL_CLOSED = "fail-closed"
HYBRID_CANDIDATE_MULTIPLIER = 4
HYBRID_CANDIDATE_MINIMUM = 20
HYBRID_MISSING_RANK = 1_000_000
HYBRID_SECTION_SOURCE_SCORE_RATIO = 0.90
THRESHOLD_METRIC_LABELS = {
    "source_file_match_at_3": "Source file match @3",
    "source_file_match_at_5": "Source file match @5",
    "source_priority_match": "Source priority match",
    "evidence_label_match": "Evidence label match",
    "section_match": "Section match",
    "path_context_match": "Path context match",
    "overall_pass_rate": "Overall pass rate",
}
RETRIEVAL_EVAL_THRESHOLDS = {
    "baseline": {
        "source_file_match_at_5": 0.30,
        "source_priority_match": 0.30,
        "evidence_label_match": 0.30,
        "overall_pass_rate": 0.30,
    },
    "mvp003": {
        "source_file_match_at_5": 1.00,
        "source_priority_match": 1.00,
        "evidence_label_match": 1.00,
        "section_match": 0.90,
        "path_context_match": 1.00,
        "overall_pass_rate": 0.90,
    },
    "vector": {
        "source_file_match_at_5": 0.50,
        "source_priority_match": 0.50,
        "evidence_label_match": 0.50,
        "path_context_match": 1.00,
        "overall_pass_rate": 0.50,
    },
    "hybrid": {
        "source_file_match_at_5": 1.00,
        "source_priority_match": 1.00,
        "evidence_label_match": 1.00,
        "section_match": 1.00,
        "path_context_match": 1.00,
        "overall_pass_rate": 0.95,
    },
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
    expected_path_context: str = ""


@dataclass(frozen=True)
class RerankerApplication:
    results_by_question: dict[str, list[dict[str, Any]]]
    fallback_diagnostics: dict[str, tuple[str, ...]]


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
                expected_path_context=str(row.get("expected_path_context") or ""),
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
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        emit_progress(f"baseline question {index}/{total_questions}: {question.question_id}")
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
        gc.collect()
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
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        emit_progress(f"mvp003 question {index}/{total_questions}: {question.question_id}")
        retrieved = search_chunks_mvp003(question.user_question, chunks, records, limit=limit, include_explanations=True)
        emit_progress(f"mvp003 question {index}/{total_questions}: {question.question_id} retrieved={len(retrieved)}")
        rows: list[dict[str, Any]] = []
        for rank, result in enumerate(retrieved, start=1):
            row = result.to_json()
            row["rank"] = rank
            rows.append(row)
        by_question[question.question_id] = rows
        gc.collect()
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
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        emit_progress(f"vector question {index}/{total_questions}: {question.question_id}")
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
        gc.collect()
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
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        emit_progress(f"hybrid question {index}/{total_questions}: {question.question_id}")
        emit_progress(f"hybrid question {index}/{total_questions}: scoring mvp003 candidates")
        scored_results = score_chunks_mvp003(question.user_question, chunks, records)
        emit_progress(f"hybrid question {index}/{total_questions}: mvp003 candidates={len(scored_results)}")
        mvp003_rows = mvp003_rows_from_scored_results(scored_results, candidate_limit)
        emit_progress(f"hybrid question {index}/{total_questions}: protected rows={len(mvp003_rows)}")
        candidates: dict[str, dict[str, Any]] = {}
        for row in mvp003_rows:
            merge_hybrid_candidate(candidates, row, source="mvp003")
        section_rows = collect_hybrid_section_candidates(
            question=question,
            records=records,
            chunks=chunks,
            protected_rows=mvp003_rows[:limit],
            scored_results=scored_results,
        )
        emit_progress(f"hybrid question {index}/{total_questions}: section candidates={len(section_rows)}")
        for row in section_rows:
            merge_hybrid_candidate(candidates, row, source="section")
        for row in vector_results.get(question.question_id, []):
            merge_hybrid_candidate(candidates, row, source="vector")
        emit_progress(f"hybrid question {index}/{total_questions}: merged candidates={len(candidates)}")

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
        emit_progress(f"hybrid question {index}/{total_questions}: selected={len(selected)}")
        gc.collect()
    return by_question


def mvp003_rows_from_scored_results(scored_results: list[Any], limit: int) -> list[dict[str, Any]]:
    best_by_source: dict[str, Any] = {}
    for result in scored_results:
        chunk = result.chunk
        current = best_by_source.get(chunk.source_id)
        if current is None or (result.score, -chunk.char_start, chunk.chunk_id) > (
            current.score,
            -current.chunk.char_start,
            current.chunk.chunk_id,
        ):
            best_by_source[chunk.source_id] = result

    ranked = sorted(best_by_source.values(), key=mvp003_result_sort_key, reverse=True)
    rows: list[dict[str, Any]] = []
    for rank, result in enumerate(ranked[:limit], start=1):
        row = result.to_json()
        row["rank"] = rank
        rows.append(row)
    return rows


def mvp003_result_sort_key(item: Any) -> tuple[float, float, float, float, str, str]:
    return (
        item.score,
        item.score_components.get("exact_filename_phrase", 0.0),
        item.score_components.get("alias_phrase", 0.0),
        item.score_components.get("filename_match", 0.0),
        item.chunk.source_priority,
        item.source_file,
    )


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
    scored_results: list[Any] | None = None,
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
    ranked_results = scored_results if scored_results is not None else score_chunks_mvp003(question.user_question, chunks, records)
    for rank, result in enumerate(ranked_results, start=1):
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


def build_reranker(reranker_name: str) -> Reranker | None:
    if reranker_name == RERANKER_NONE:
        return None
    if reranker_name == RERANKER_DETERMINISTIC_TEST:
        return DeterministicTestReranker()
    raise EvalError(f"Unsupported reranker: {reranker_name}")


def apply_reranker_to_results(
    questions: list[EvalQuestion],
    results_by_question: dict[str, list[dict[str, Any]]],
    reranker: Reranker | None,
    limit: int,
    reranker_policy: str = RERANKER_POLICY_DIRECT,
) -> dict[str, list[dict[str, Any]]]:
    return apply_reranker_to_results_with_diagnostics(
        questions=questions,
        results_by_question=results_by_question,
        reranker=reranker,
        limit=limit,
        reranker_policy=reranker_policy,
    ).results_by_question


def apply_reranker_to_results_with_diagnostics(
    questions: list[EvalQuestion],
    results_by_question: dict[str, list[dict[str, Any]]],
    reranker: Reranker | None,
    limit: int,
    reranker_policy: str = RERANKER_POLICY_DIRECT,
) -> RerankerApplication:
    if reranker is None:
        return RerankerApplication(
            results_by_question={
                question.question_id: [dict(row) for row in results_by_question.get(question.question_id, [])]
                for question in questions
            },
            fallback_diagnostics={},
        )

    reranked: dict[str, list[dict[str, Any]]] = {}
    fallback_diagnostics: dict[str, tuple[str, ...]] = {}
    for question in questions:
        try:
            if reranker_policy == RERANKER_POLICY_FAIL_CLOSED:
                result = rerank_candidates_fail_closed(
                    query=question.user_question,
                    candidates=results_by_question.get(question.question_id, []),
                    reranker=reranker,
                    top_k=limit,
                )
                reranked[question.question_id] = result.candidates
                if result.fell_back:
                    fallback_diagnostics[question.question_id] = result.fallback_reasons
            else:
                reranked[question.question_id] = rerank_candidates(
                    query=question.user_question,
                    candidates=results_by_question.get(question.question_id, []),
                    reranker=reranker,
                    top_k=limit,
                )
        except ValueError as exc:
            raise EvalError(f"{question.question_id} reranker metadata preservation failed: {exc}") from exc
    return RerankerApplication(results_by_question=reranked, fallback_diagnostics=fallback_diagnostics)


def compare_reranker_outputs(
    questions: list[EvalQuestion],
    base_results: dict[str, list[dict[str, Any]]],
    reranked_results: dict[str, list[dict[str, Any]]],
    base_summary: dict[str, Any],
    reranked_summary: dict[str, Any],
    base_mode: str,
    reranker_name: str,
    reranker_policy: str = RERANKER_POLICY_DIRECT,
    fallback_diagnostics: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, Any]:
    total = len(questions)
    top1_changed = 0
    top3_changed = 0
    top5_changed = 0
    top3_source_identity_preserved = 0
    top5_source_coverage_preserved = 0
    candidate_dropped_count = 0
    candidate_duplicated_count = 0
    candidate_introduced_count = 0
    metadata_preservation_violation_count = 0
    would_fail_closed_question_ids: set[str] = set()
    would_fail_closed_reasons: dict[str, int] = {}
    top3_changed_question_ids: list[str] = []
    top5_changed_question_ids: list[str] = []
    base_scores_by_question = {str(row["question_id"]): row for row in base_summary["per_question"]}
    reranked_scores_by_question = {str(row["question_id"]): row for row in reranked_summary["per_question"]}
    for question in questions:
        base_rows = base_results.get(question.question_id, [])
        reranked_rows = reranked_results.get(question.question_id, [])
        if top_k_signature(base_rows, 1) != top_k_signature(reranked_rows, 1):
            top1_changed += 1
        if top_k_signature(base_rows, 3) != top_k_signature(reranked_rows, 3):
            top3_changed += 1
            top3_changed_question_ids.append(question.question_id)
        if top_k_signature(base_rows, 5) != top_k_signature(reranked_rows, 5):
            top5_changed += 1
            top5_changed_question_ids.append(question.question_id)

        question_reasons: set[str] = set()
        if source_identity_set(base_rows[:3]).issubset(source_identity_set(reranked_rows[:3])):
            top3_source_identity_preserved += 1
        else:
            question_reasons.add("top3_source_identity_lost")
        if source_identity_set(base_rows[:5]).issubset(source_identity_set(reranked_rows[:5])):
            top5_source_coverage_preserved += 1
        else:
            question_reasons.add("top5_source_coverage_lost")

        candidate_delta = candidate_preservation_delta(base_rows, reranked_rows)
        candidate_dropped_count += candidate_delta["dropped"]
        candidate_duplicated_count += candidate_delta["duplicated"]
        candidate_introduced_count += candidate_delta["introduced"]
        if candidate_delta["dropped"]:
            question_reasons.add("candidate_dropped")
        if candidate_delta["duplicated"]:
            question_reasons.add("candidate_duplicated")
        if candidate_delta["introduced"]:
            question_reasons.add("candidate_introduced")

        metadata_violations = grounding_metadata_violation_count(base_rows, reranked_rows)
        metadata_preservation_violation_count += metadata_violations
        if metadata_violations:
            question_reasons.add("grounding_metadata_mutated")

        base_score = base_scores_by_question.get(question.question_id, {})
        reranked_score = reranked_scores_by_question.get(question.question_id, {})
        question_reasons.update(per_question_regression_reasons(base_score, reranked_score))
        if question_reasons:
            would_fail_closed_question_ids.add(question.question_id)
            for reason in sorted(question_reasons):
                would_fail_closed_reasons[reason] = would_fail_closed_reasons.get(reason, 0) + 1

    comparison = {
        "base_mode": base_mode,
        "reranker": reranker_name,
        "total_questions": total,
        "top1_changed_count": top1_changed,
        "top3_changed_count": top3_changed,
        "top5_changed_count": top5_changed,
        "top3_source_identity_preserved_count": top3_source_identity_preserved,
        "top5_source_coverage_preserved_count": top5_source_coverage_preserved,
        "candidate_dropped_count": candidate_dropped_count,
        "candidate_duplicated_count": candidate_duplicated_count,
        "candidate_introduced_count": candidate_introduced_count,
        "metadata_preservation_violation_count": metadata_preservation_violation_count,
        "would_fail_closed_count": len(would_fail_closed_question_ids),
        "would_fail_closed_reasons": dict(sorted(would_fail_closed_reasons.items())),
        "top3_changed_question_ids": top3_changed_question_ids,
        "top5_changed_question_ids": top5_changed_question_ids,
        "source_file_match_at_3_before": base_summary["source_file_match_at_3"],
        "source_file_match_at_3_after": reranked_summary["source_file_match_at_3"],
        "source_file_match_at_3_delta": reranked_summary["source_file_match_at_3"] - base_summary["source_file_match_at_3"],
        "source_file_match_at_5_before": base_summary["source_file_match_at_5"],
        "source_file_match_at_5_after": reranked_summary["source_file_match_at_5"],
        "source_file_match_at_5_delta": reranked_summary["source_file_match_at_5"] - base_summary["source_file_match_at_5"],
        "source_priority_match_before": base_summary["source_priority_match"],
        "source_priority_match_after": reranked_summary["source_priority_match"],
        "source_priority_match_delta": reranked_summary["source_priority_match"] - base_summary["source_priority_match"],
        "evidence_label_match_before": base_summary["evidence_label_match"],
        "evidence_label_match_after": reranked_summary["evidence_label_match"],
        "evidence_label_match_delta": reranked_summary["evidence_label_match"] - base_summary["evidence_label_match"],
        "section_match_before": base_summary["section_match"],
        "section_match_after": reranked_summary["section_match"],
        "section_match_delta": nullable_delta(base_summary["section_match"], reranked_summary["section_match"]),
        "path_context_match_before": base_summary["path_context_match"],
        "path_context_match_after": reranked_summary["path_context_match"],
        "path_context_match_delta": nullable_delta(base_summary["path_context_match"], reranked_summary["path_context_match"]),
        "overall_pass_rate_before": base_summary["overall_pass_rate"],
        "overall_pass_rate_after": reranked_summary["overall_pass_rate"],
        "overall_pass_rate_delta": reranked_summary["overall_pass_rate"] - base_summary["overall_pass_rate"],
    }
    if reranker_policy == RERANKER_POLICY_FAIL_CLOSED:
        fallback_diagnostics = fallback_diagnostics or {}
        fallback_reasons: dict[str, int] = {}
        fallback_by_question: list[dict[str, Any]] = []
        for question_id, reasons in sorted(fallback_diagnostics.items()):
            fallback_by_question.append({"question_id": question_id, "fallback_reasons": list(reasons)})
            for reason in reasons:
                fallback_reasons[reason] = fallback_reasons.get(reason, 0) + 1
        comparison["reranker_policy"] = reranker_policy
        comparison["fallback_count"] = len(fallback_diagnostics)
        comparison["fallback_reasons"] = dict(sorted(fallback_reasons.items()))
        comparison["fallback_by_question"] = fallback_by_question
    return comparison


def nullable_delta(before: float | None, after: float | None) -> float | None:
    if before is None or after is None:
        return None
    return after - before


def top_k_signature(results: list[dict[str, Any]], top_k: int) -> tuple[str, ...]:
    return tuple(result_identity(row) for row in results[:top_k])


def result_identity(row: dict[str, Any]) -> str:
    return str(row.get("chunk_id") or row.get("source_file") or row.get("source_id") or "")


def candidate_identity(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("source_id") or ""),
        str(row.get("source_file") or ""),
        str(row.get("content_hash") or ""),
        str(row.get("chunk_id") or ""),
    ]
    identity = "|".join(part for part in parts if part)
    if identity:
        return identity
    return result_identity(row)


def source_identity(row: dict[str, Any]) -> str:
    return str(row.get("source_id") or row.get("source_file") or "")


def source_identity_set(results: list[dict[str, Any]]) -> set[str]:
    return {identity for identity in (source_identity(row) for row in results) if identity}


def identity_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results:
        identity = candidate_identity(row)
        if identity:
            counts[identity] = counts.get(identity, 0) + 1
    return counts


def candidate_preservation_delta(base_rows: list[dict[str, Any]], reranked_rows: list[dict[str, Any]]) -> dict[str, int]:
    base_counts = identity_counts(base_rows)
    reranked_counts = identity_counts(reranked_rows)
    dropped = sum(max(base_count - reranked_counts.get(identity, 0), 0) for identity, base_count in base_counts.items())
    duplicated = sum(max(count - 1, 0) for count in reranked_counts.values())
    introduced = sum(count for identity, count in reranked_counts.items() if identity not in base_counts)
    return {"dropped": dropped, "duplicated": duplicated, "introduced": introduced}


def grounding_metadata_violation_count(base_rows: list[dict[str, Any]], reranked_rows: list[dict[str, Any]]) -> int:
    base_by_identity = {metadata_preservation_identity(row): row for row in base_rows}
    violations = 0
    for reranked_row in reranked_rows:
        base_row = base_by_identity.get(metadata_preservation_identity(reranked_row))
        if base_row is None:
            continue
        if any(
            field_name in base_row and reranked_row.get(field_name) != base_row.get(field_name)
            for field_name in RERANK_SOURCE_GROUNDING_FIELDS
        ):
            violations += 1
    return violations


def metadata_preservation_identity(row: dict[str, Any]) -> str:
    return str(row.get("chunk_id") or candidate_identity(row))


def per_question_regression_reasons(base_score: dict[str, Any], reranked_score: dict[str, Any]) -> set[str]:
    reasons: set[str] = set()
    regression_fields = (
        ("source_file_match_top3", "source_at3_regression"),
        ("source_file_match_top5", "source_at5_regression"),
        ("source_priority_match", "priority_regression"),
        ("evidence_label_match", "evidence_label_regression"),
        ("section_match", "section_regression"),
        ("path_context_match", "path_context_regression"),
        ("overall_pass", "overall_regression"),
    )
    for field_name, reason in regression_fields:
        if base_score.get(field_name) is True and reranked_score.get(field_name) is not True:
            reasons.add(reason)
    return reasons


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


def contains_path_context(result: dict[str, Any], expected_path_context: str) -> bool | None:
    needle = expected_path_context.strip()
    if not needle:
        return None
    normalized_source_file = normalize_path(str(result.get("source_file", "")))
    normalized_needle = normalize_path(needle)
    return bool(normalized_needle and normalized_needle in normalized_source_file)


def score_question(question: EvalQuestion, results: list[dict[str, Any]]) -> dict[str, Any]:
    expected_file = normalize_path(question.expected_source_file)
    top3 = results[:3]
    top5 = results[:5]
    matched = next((result for result in top5 if normalize_path(str(result.get("source_file", ""))) == expected_file), None)
    section_match = contains_section(matched, question.expected_chunk_or_section) if matched else (None if not question.expected_chunk_or_section else False)
    path_context_match = contains_path_context(matched, question.expected_path_context) if matched else (None if not question.expected_path_context else False)
    source_file_match_top3 = any(normalize_path(str(result.get("source_file", ""))) == expected_file for result in top3)
    source_file_match_top5 = matched is not None
    source_priority_match = bool(matched and str(matched.get("source_priority")) == question.expected_source_priority)
    evidence_label_match = bool(matched and str(matched.get("evidence_label", question.expected_evidence_label)) == question.expected_evidence_label)
    overall_pass = bool(
        source_file_match_top5
        and source_priority_match
        and evidence_label_match
        and section_match is not False
        and path_context_match is not False
    )
    return {
        "question_id": question.question_id,
        "source_file_match_top3": source_file_match_top3,
        "source_file_match_top5": source_file_match_top5,
        "source_priority_match": source_priority_match,
        "evidence_label_match": evidence_label_match,
        "section_match": section_match,
        "path_context_match": path_context_match,
        "overall_pass": overall_pass,
        "top_result_source_file": str(results[0].get("source_file", "")) if results else "",
    }


def score_results(questions: list[EvalQuestion], results_by_question: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    per_question = []
    total_questions = len(questions)
    for index, question in enumerate(questions, start=1):
        emit_progress(f"scoring question {index}/{total_questions}: {question.question_id}")
        per_question.append(score_question(question, results_by_question.get(question.question_id, [])))
    total = len(per_question)
    if total == 0:
        raise EvalError("No questions to score")

    def rate(field: str) -> float:
        return sum(1 for row in per_question if row[field]) / total

    section_rows = [row for row in per_question if row["section_match"] is not None]
    section_rate = None
    if section_rows:
        section_rate = sum(1 for row in section_rows if row["section_match"]) / len(section_rows)
    path_context_rows = [row for row in per_question if row["path_context_match"] is not None]
    path_context_rate = None
    if path_context_rows:
        path_context_rate = sum(1 for row in path_context_rows if row["path_context_match"]) / len(path_context_rows)
    return {
        "total_questions": total,
        "source_file_match_at_3": rate("source_file_match_top3"),
        "source_file_match_at_5": rate("source_file_match_top5"),
        "source_priority_match": rate("source_priority_match"),
        "evidence_label_match": rate("evidence_label_match"),
        "section_match": section_rate,
        "path_context_match": path_context_rate,
        "overall_pass_rate": rate("overall_pass"),
        "per_question": per_question,
    }


def format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def format_percentage_point_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.1f} percentage points"


def evaluate_thresholds(summary: dict[str, Any], retriever: str) -> dict[str, Any]:
    thresholds = RETRIEVAL_EVAL_THRESHOLDS.get(retriever)
    if thresholds is None:
        raise EvalError(f"No retrieval eval threshold profile defined for retriever: {retriever}")

    metrics: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for metric_name, minimum in thresholds.items():
        emit_progress(f"threshold check {retriever}.{metric_name}")
        actual = summary.get(metric_name)
        not_applicable = actual is None
        passed = not_applicable or actual >= minimum
        metric_result = {
            "metric": metric_name,
            "label": THRESHOLD_METRIC_LABELS.get(metric_name, metric_name),
            "actual": actual,
            "minimum": minimum,
            "not_applicable": not_applicable,
            "passed": passed,
        }
        metrics.append(metric_result)
        if not passed:
            failures.append(metric_result)

    return {
        "profile": retriever,
        "passed": not failures,
        "metrics": metrics,
        "failures": failures,
    }


def print_threshold_report(report: dict[str, Any]) -> None:
    emit_line("Threshold gate:")
    emit_line(f"Profile: {report['profile']}")
    emit_line(f"Decision: {'pass' if report['passed'] else 'fail'}")
    for metric in report["metrics"]:
        emit_line(
            f"- {metric['label']}: actual={format_percent(metric['actual'])} "
            f"minimum={format_percent(metric['minimum'])} "
            f"status={'n/a' if metric.get('not_applicable') else ('pass' if metric['passed'] else 'fail')}"
        )


def print_summary(summary: dict[str, Any], mode: str) -> None:
    emit_line("MVP-002.5 Retrieval Evaluation")
    emit_line(f"Mode: {mode}")
    emit_line(f"Questions: {summary['total_questions']}")
    emit_line(f"Source file match @3: {format_percent(summary['source_file_match_at_3'])}")
    emit_line(f"Source file match @5: {format_percent(summary['source_file_match_at_5'])}")
    emit_line(f"Source priority match: {format_percent(summary['source_priority_match'])}")
    emit_line(f"Evidence label match: {format_percent(summary['evidence_label_match'])}")
    emit_line(f"Section match: {format_percent(summary['section_match'])}")
    if summary["path_context_match"] is not None:
        emit_line(f"Path context match: {format_percent(summary['path_context_match'])}")
    emit_line(f"Overall pass rate: {format_percent(summary['overall_pass_rate'])}")
    comparison = summary.get("reranker_comparison")
    if comparison:
        emit_line(f"Reranker: {comparison['reranker']}")
        emit_line(f"Base mode: {comparison['base_mode']}")
        emit_line(f"Top-1 ordering changed: {comparison['top1_changed_count']}/{comparison['total_questions']}")
        emit_line(f"Top-3 ordering changed: {comparison['top3_changed_count']}/{comparison['total_questions']}")
        emit_line(f"Top-5 ordering changed: {comparison['top5_changed_count']}/{comparison['total_questions']}")
        emit_line(f"Source file match @3 delta: {format_percentage_point_delta(comparison['source_file_match_at_3_delta'])}")
        emit_line(f"Source file match @5 delta: {format_percentage_point_delta(comparison['source_file_match_at_5_delta'])}")
        emit_line(f"Source priority match delta: {format_percentage_point_delta(comparison['source_priority_match_delta'])}")
        emit_line(f"Evidence label match delta: {format_percentage_point_delta(comparison['evidence_label_match_delta'])}")
        emit_line(f"Section match delta: {format_percentage_point_delta(comparison['section_match_delta'])}")
        emit_line(f"Path context match delta: {format_percentage_point_delta(comparison['path_context_match_delta'])}")
        emit_line(f"Overall pass rate delta: {format_percentage_point_delta(comparison['overall_pass_rate_delta'])}")
        emit_line("Candidate preservation:")
        emit_line(
            "Base top-3 source identity preserved: "
            f"{comparison['top3_source_identity_preserved_count']}/{comparison['total_questions']}"
        )
        emit_line(
            "Base top-5 source coverage preserved: "
            f"{comparison['top5_source_coverage_preserved_count']}/{comparison['total_questions']}"
        )
        emit_line(
            "Candidate dropped/duplicated/introduced: "
            f"{comparison['candidate_dropped_count']}/"
            f"{comparison['candidate_duplicated_count']}/"
            f"{comparison['candidate_introduced_count']}"
        )
        emit_line(f"Grounding metadata preservation violations: {comparison['metadata_preservation_violation_count']}")
        emit_line(f"Would fail closed: {comparison['would_fail_closed_count']}/{comparison['total_questions']}")
        if comparison["would_fail_closed_reasons"]:
            reason_summary = ", ".join(
                f"{reason}={count}" for reason, count in comparison["would_fail_closed_reasons"].items()
            )
            emit_line(f"Would fail closed reasons: {reason_summary}")
        else:
            emit_line("Would fail closed reasons: none")
        if comparison.get("reranker_policy") == RERANKER_POLICY_FAIL_CLOSED:
            emit_line("Fail-closed fallback:")
            emit_line(f"Fallback count: {comparison['fallback_count']}/{comparison['total_questions']}")
            if comparison["fallback_reasons"]:
                reason_summary = ", ".join(
                    f"{reason}={count}" for reason, count in comparison["fallback_reasons"].items()
                )
                emit_line(f"Fallback reasons: {reason_summary}")
            else:
                emit_line("Fallback reasons: none")
            for row in comparison["fallback_by_question"][:20]:
                emit_line(f"- {row['question_id']}: {', '.join(row['fallback_reasons'])}")
    failed = [row for row in summary["per_question"] if not row["overall_pass"]]
    if failed:
        emit_line("Failed question_ids:")
        for row in failed[:20]:
            emit_line(f"- {row['question_id']} top_result={row['top_result_source_file']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic MVP-002.5 retrieval evaluation.")
    parser.add_argument("--questions", type=Path, default=REPO_ROOT / "eval" / "retrieval_questions.jsonl")
    parser.add_argument("--expected", type=Path, default=REPO_ROOT / "eval" / "expected_sources.jsonl")
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "data" / "source_registry.csv")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "data" / "chunks.jsonl")
    parser.add_argument("--results-jsonl", type=Path, default=None, help="Optional external retrieval results to score.")
    parser.add_argument("--retriever", choices=("baseline", "mvp003", "vector", "hybrid"), default="baseline")
    parser.add_argument("--reranker", choices=(RERANKER_NONE, RERANKER_DETERMINISTIC_TEST), default=RERANKER_NONE)
    parser.add_argument(
        "--reranker-policy",
        choices=(RERANKER_POLICY_DIRECT, RERANKER_POLICY_FAIL_CLOSED),
        default=RERANKER_POLICY_DIRECT,
        help="Optional non-default reranker safety policy.",
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary JSON.")
    parser.add_argument(
        "--enforce-thresholds",
        action="store_true",
        help="Exit non-zero if the selected retriever misses its source-grounding threshold profile.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    threshold_report = None
    try:
        emit_progress(f"loading questions: {args.questions}")
        questions = load_questions(args.questions)
        emit_progress(f"loading expected sources: {args.expected}")
        expected = load_expected_sources(args.expected)
        emit_progress("validating expected source alignment")
        validate_expected_alignment(questions, expected)
        if args.results_jsonl:
            emit_progress(f"loading external results: {args.results_jsonl}")
            mode = "external-results"
            results = load_simulated_results(args.results_jsonl)
        else:
            emit_progress(f"running retriever={args.retriever} limit={args.limit}")
            mode, results = run_retriever(args.retriever, questions, args.registry, args.chunks, args.limit)
        emit_progress("aggregating retrieval metrics")
        base_summary = score_results(questions, results)
        reranker = build_reranker(args.reranker)
        if reranker is None:
            summary = base_summary
        else:
            emit_progress(f"applying reranker={args.reranker}")
            base_mode = mode
            base_results = results
            application = apply_reranker_to_results_with_diagnostics(
                questions=questions,
                results_by_question=base_results,
                reranker=reranker,
                limit=args.limit,
                reranker_policy=args.reranker_policy,
            )
            results = application.results_by_question
            mode = f"{mode}+reranker:{args.reranker}"
            if args.reranker_policy == RERANKER_POLICY_FAIL_CLOSED:
                mode = f"{mode}+policy:{args.reranker_policy}"
            emit_progress("aggregating reranked metrics")
            summary = score_results(questions, results)
            summary["reranker_comparison"] = compare_reranker_outputs(
                questions=questions,
                base_results=base_results,
                reranked_results=results,
                base_summary=base_summary,
                reranked_summary=summary,
                base_mode=base_mode,
                reranker_name=args.reranker,
                reranker_policy=args.reranker_policy,
                fallback_diagnostics=application.fallback_diagnostics,
            )
        if args.enforce_thresholds:
            emit_progress(f"enforcing threshold profile={args.retriever}")
            threshold_report = evaluate_thresholds(summary, args.retriever)
            summary["thresholds"] = threshold_report
    except EvalError as exc:
        emit_line(f"ERROR: {exc}", stream=sys.stderr)
        return 2

    if args.json:
        emit_line(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_summary(summary, mode)
        if threshold_report:
            print_threshold_report(threshold_report)
    if threshold_report and not threshold_report["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
