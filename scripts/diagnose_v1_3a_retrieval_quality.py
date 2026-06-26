from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.chunking import read_chunks  # noqa: E402
from asperitas_agent.registry import read_registry  # noqa: E402
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_FIXTURE_PATH = REPO_ROOT / "docs" / "evals" / "V1_2_GOLDEN_EVAL_SET.json"
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "source_registry.csv"
DEFAULT_CHUNKS_PATH = REPO_ROOT / "data" / "chunks.jsonl"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "eval_results" / "v1_3a_retrieval_diagnostics" / "retrieval_diagnostic_baseline.json"
)
SCHEMA_VERSION = "v1.3a-retrieval-diagnostic-baseline"


def _repo_relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_fixture(path: Path = DEFAULT_FIXTURE_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    if not isinstance(fixture, dict) or not isinstance(fixture.get("cases"), list):
        raise ValueError(f"Invalid V1.2 fixture shape: {path}")
    return fixture


def _record_lookup(records: list[Any]) -> dict[str, Any]:
    return {record.path.replace("\\", "/"): record for record in records}


def _chunks_by_source_id(chunks: list[Any]) -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = {}
    for chunk in chunks:
        grouped.setdefault(chunk.source_id, []).append(chunk)
    return grouped


def _source_metadata(path: str, records_by_path: dict[str, Any], chunks_by_source: dict[str, list[Any]]) -> dict[str, Any]:
    normalized_path = path.replace("\\", "/")
    repo_path = REPO_ROOT / normalized_path
    record = records_by_path.get(normalized_path)
    source_chunks = chunks_by_source.get(record.source_id, []) if record else []
    section_chunks = [
        chunk
        for chunk in source_chunks
        if chunk.section or chunk.section_heading or chunk.section_path or chunk.heading_context
    ]
    return {
        "path": normalized_path,
        "exists": repo_path.exists(),
        "registry_represented": record is not None,
        "source_id": record.source_id if record else "",
        "source_priority": record.source_priority if record else "",
        "chunk_represented": bool(source_chunks),
        "chunk_count": len(source_chunks),
        "section_metadata_present": bool(section_chunks),
    }


def _retrieval_row(result: Any, rank: int, expected_paths: set[str]) -> dict[str, Any]:
    row = result.to_json()
    source_path = str(row.get("source_file", "")).replace("\\", "/")
    has_section = bool(
        row.get("section") or row.get("section_heading") or row.get("section_path") or row.get("heading_context")
    )
    return {
        "rank": rank,
        "source_id": row.get("source_id", ""),
        "source_path": source_path,
        "source_priority": row.get("source_priority", ""),
        "chunk_id": row.get("chunk_id", ""),
        "section": row.get("section", ""),
        "section_heading": row.get("section_heading", ""),
        "section_path": row.get("section_path", []),
        "heading_context": row.get("heading_context", ""),
        "score": row.get("score"),
        "is_expected_source": source_path in expected_paths,
        "has_section_metadata": has_section,
        "citation_candidate_available": bool(row.get("chunk_id") and source_path),
    }


def _run_case_retrieval(
    case: dict[str, Any],
    records: list[Any],
    chunks: list[Any],
    top_k: int,
) -> tuple[str, list[dict[str, Any]]]:
    if not records or not chunks:
        return "retrieval_execution_not_available", []
    question = str(case.get("question", "")).strip()
    if not question:
        return "retrieval_execution_not_available", []
    retrieved = search_chunks_mvp003(question, chunks, records, limit=top_k, include_explanations=True)
    expected_paths = {str(path).replace("\\", "/") for path in case.get("source_scope", [])}
    return "retrieval_executed_read_only", [
        _retrieval_row(result, rank, expected_paths) for rank, result in enumerate(retrieved, start=1)
    ]


def build_diagnostic_result(
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    chunks_path: Path = DEFAULT_CHUNKS_PATH,
    top_k: int = 5,
) -> dict[str, Any]:
    fixture = load_fixture(fixture_path)
    records = read_registry(registry_path) if registry_path.exists() else []
    chunks = read_chunks(chunks_path) if chunks_path.exists() else []
    records_by_path = _record_lookup(records)
    chunks_by_source = _chunks_by_source_id(chunks)
    retrieval_available = bool(records and chunks)

    cases: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        source_scope = [str(path).replace("\\", "/") for path in case.get("source_scope", [])]
        source_rows = [_source_metadata(path, records_by_path, chunks_by_source) for path in source_scope]
        diagnostic_status, retrieved = _run_case_retrieval(case, records, chunks, top_k)
        expected_retrieved = {row["source_path"] for row in retrieved if row["is_expected_source"]}
        cases.append(
            {
                "case_id": case.get("id", ""),
                "question": case.get("question", ""),
                "expected_source_scope": source_scope,
                "expected_sources": source_rows,
                "source_paths_existing": sum(1 for row in source_rows if row["exists"]),
                "source_paths_expected": len(source_rows),
                "registry_represented_count": sum(1 for row in source_rows if row["registry_represented"]),
                "chunk_represented_count": sum(1 for row in source_rows if row["chunk_represented"]),
                "section_metadata_present_count": sum(1 for row in source_rows if row["section_metadata_present"]),
                "retrieval_execution_available": retrieval_available,
                "diagnostic_status": diagnostic_status,
                "top_k": top_k,
                "retrieved": retrieved,
                "retrieval_miss_flags": sorted(set(source_scope) - expected_retrieved) if retrieved else source_scope,
                "wrong_source_priority_flags": [
                    row["source_path"] for row in retrieved if row["source_path"] and not row["is_expected_source"]
                ],
                "citation_candidate_available": any(row["citation_candidate_available"] for row in retrieved),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": "1970-01-01T00:00:00Z",
        "diagnostic_only": True,
        "answer_generation_executed": False,
        "retrieval_behavior_changed": False,
        "registry_or_chunk_mutation": False,
        "fixture_path": _repo_relative(fixture_path),
        "registry_path": _repo_relative(registry_path),
        "chunks_path": _repo_relative(chunks_path),
        "retrieval_interface": "asperitas_agent.retrieval_mvp003.search_chunks_mvp003",
        "retrieval_execution_available": retrieval_available,
        "retrieval_execution_status": "available_read_only" if retrieval_available else "retrieval_execution_not_available",
        "top_k": top_k,
        "summary": {
            "case_count": len(cases),
            "expected_source_path_count": sum(case["source_paths_expected"] for case in cases),
            "existing_source_path_count": sum(case["source_paths_existing"] for case in cases),
            "registry_represented_source_count": sum(case["registry_represented_count"] for case in cases),
            "chunk_represented_source_count": sum(case["chunk_represented_count"] for case in cases),
            "section_metadata_present_source_count": sum(case["section_metadata_present_count"] for case in cases),
            "cases_with_retrieval_execution": sum(
                1 for case in cases if case["diagnostic_status"] == "retrieval_executed_read_only"
            ),
            "cases_with_any_citation_candidate": sum(1 for case in cases if case["citation_candidate_available"]),
        },
        "cases": cases,
        "truth_boundary_statement": (
            "This diagnostic reports retrieval-readiness observations against V1.2 fixture cases. "
            "It is not an answer-quality score, not an optimization result, and not evidence of deployment, "
            "biological validation, legal approval, or regulatory approval."
        ),
        "non_mutation_statement": (
            "This script reads V1.2 fixtures, source registry, chunk artifacts, and current retrieval code only. "
            "It does not mutate retrieval, ranking, embeddings, vector DB behavior, reranking, answer generation, "
            "source ingestion, source registry artifacts, chunk artifacts, or source artifacts."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V1.3A read-only retrieval diagnostics.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_diagnostic_result(args.fixture, args.registry, args.chunks, args.top_k)
    if args.output:
        if args.output.exists() and not args.overwrite:
            print(f"ERROR: output exists, pass --overwrite: {args.output}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
