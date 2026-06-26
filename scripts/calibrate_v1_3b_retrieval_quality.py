from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import asperitas_agent.retrieval_mvp003 as retrieval_mvp003  # noqa: E402
from scripts.diagnose_v1_3a_retrieval_quality import (  # noqa: E402
    DEFAULT_CHUNKS_PATH,
    DEFAULT_FIXTURE_PATH,
    DEFAULT_REGISTRY_PATH,
    build_diagnostic_result,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_BEFORE_PATH = REPO_ROOT / "eval_results" / "v1_3a_retrieval_diagnostics" / "retrieval_diagnostic_baseline.json"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "eval_results"
    / "v1_3b_retrieval_quality_calibration"
    / "retrieval_quality_before_after.json"
)
SCHEMA_VERSION = "v1.3b-2-retrieval-quality-calibration"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _case_metrics(case: dict[str, Any]) -> dict[str, Any]:
    retrieved = case.get("retrieved", [])
    expected = set(case.get("expected_source_scope", []))
    hit_ranks = [row["rank"] for row in retrieved if row.get("source_path") in expected]
    priority_counts = Counter(str(row.get("source_priority", "")) for row in retrieved)
    return {
        "case_id": case["case_id"],
        "top_k_retrieved_paths": [row.get("source_path", "") for row in retrieved],
        "expected_source_hit_at_1": bool(hit_ranks and min(hit_ranks) <= 1),
        "expected_source_hit_at_3": bool(hit_ranks and min(hit_ranks) <= 3),
        "expected_source_hit_at_5": bool(hit_ranks and min(hit_ranks) <= 5),
        "expected_source_hit_count_at_5": len(hit_ranks),
        "best_expected_rank": min(hit_ranks) if hit_ranks else None,
        "p0_retrieved_count": priority_counts.get("P0", 0),
        "p1_retrieved_count": priority_counts.get("P1", 0),
        "section_metadata_available_count": sum(1 for row in retrieved if row.get("has_section_metadata")),
        "retrieval_miss_flags": case.get("retrieval_miss_flags", []),
        "wrong_source_proxy_flags": case.get("wrong_source_priority_flags", []),
        "citation_candidate_available": case.get("citation_candidate_available", False),
    }


def _summary(case_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(case_metrics)
    if total == 0:
        return {
            "case_count": 0,
            "hit_at_1_cases": 0,
            "hit_at_3_cases": 0,
            "hit_at_5_cases": 0,
            "total_expected_hits_at_5": 0,
            "retrieval_miss_flag_count": 0,
            "wrong_source_proxy_flag_count": 0,
            "citation_candidate_case_count": 0,
            "section_metadata_available_rows": 0,
            "p0_retrieved_rows": 0,
            "p1_retrieved_rows": 0,
        }
    return {
        "case_count": total,
        "hit_at_1_cases": sum(1 for row in case_metrics if row["expected_source_hit_at_1"]),
        "hit_at_3_cases": sum(1 for row in case_metrics if row["expected_source_hit_at_3"]),
        "hit_at_5_cases": sum(1 for row in case_metrics if row["expected_source_hit_at_5"]),
        "total_expected_hits_at_5": sum(row["expected_source_hit_count_at_5"] for row in case_metrics),
        "retrieval_miss_flag_count": sum(len(row["retrieval_miss_flags"]) for row in case_metrics),
        "wrong_source_proxy_flag_count": sum(len(row["wrong_source_proxy_flags"]) for row in case_metrics),
        "citation_candidate_case_count": sum(1 for row in case_metrics if row["citation_candidate_available"]),
        "section_metadata_available_rows": sum(row["section_metadata_available_count"] for row in case_metrics),
        "p0_retrieved_rows": sum(row["p0_retrieved_count"] for row in case_metrics),
        "p1_retrieved_rows": sum(row["p1_retrieved_count"] for row in case_metrics),
    }


def _delta(before_summary: dict[str, Any], after_summary: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "hit_at_1_cases",
        "hit_at_3_cases",
        "hit_at_5_cases",
        "total_expected_hits_at_5",
        "retrieval_miss_flag_count",
        "wrong_source_proxy_flag_count",
        "section_metadata_available_rows",
        "p0_retrieved_rows",
        "p1_retrieved_rows",
    )
    return {key: after_summary[key] - before_summary[key] for key in keys}


def _case_delta(before_cases: list[dict[str, Any]], after_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    before_by_id = {case["case_id"]: case for case in before_cases}
    rows: list[dict[str, Any]] = []
    for after in after_cases:
        before = before_by_id[after["case_id"]]
        rows.append(
            {
                "case_id": after["case_id"],
                "best_expected_rank_before": before["best_expected_rank"],
                "best_expected_rank_after": after["best_expected_rank"],
                "expected_hits_at_5_before": before["expected_source_hit_count_at_5"],
                "expected_hits_at_5_after": after["expected_source_hit_count_at_5"],
                "retrieval_miss_flags_before": before["retrieval_miss_flags"],
                "retrieval_miss_flags_after": after["retrieval_miss_flags"],
                "top_k_retrieved_paths_before": before["top_k_retrieved_paths"],
                "top_k_retrieved_paths_after": after["top_k_retrieved_paths"],
            }
        )
    return rows


def build_calibration_report(
    before_path: Path = DEFAULT_BEFORE_PATH,
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    chunks_path: Path = DEFAULT_CHUNKS_PATH,
    top_k: int = 5,
) -> dict[str, Any]:
    original_calibration_state = retrieval_mvp003.ENABLE_V1_3B_CALIBRATION
    try:
        retrieval_mvp003.ENABLE_V1_3B_CALIBRATION = False
        before = build_diagnostic_result(fixture_path, registry_path, chunks_path, top_k)
    finally:
        retrieval_mvp003.ENABLE_V1_3B_CALIBRATION = original_calibration_state
    after = build_diagnostic_result(fixture_path, registry_path, chunks_path, top_k)
    before_cases = [_case_metrics(case) for case in before["cases"]]
    after_cases = [_case_metrics(case) for case in after["cases"]]
    before_summary = _summary(before_cases)
    after_summary = _summary(after_cases)
    delta = _delta(before_summary, after_summary)
    improvement_proven = (
        delta["total_expected_hits_at_5"] > 0
        or delta["hit_at_1_cases"] > 0
        or delta["hit_at_3_cases"] > 0
        or delta["retrieval_miss_flag_count"] < 0
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": "1970-01-01T00:00:00Z",
        "before_mode": "mvp003_without_v1_3b_2_calibration_components",
        "after_mode": "mvp003_with_v1_3b_2_calibration_components",
        "reference_diagnostic_path": before_path.relative_to(REPO_ROOT).as_posix() if before_path.exists() else "",
        "fixture_path": fixture_path.relative_to(REPO_ROOT).as_posix(),
        "registry_path": registry_path.relative_to(REPO_ROOT).as_posix(),
        "chunks_path": chunks_path.relative_to(REPO_ROOT).as_posix(),
        "top_k": top_k,
        "calibration_behavior": [
            "metadata-only direct source reference boost",
            "metadata-only section/heading overlap boost",
            "narrow V1 status/readiness doc boost",
        ],
        "retrieval_algorithm_changed": True,
        "answer_generation_changed": False,
        "prompt_or_answer_contract_changed": False,
        "source_artifacts_mutated": False,
        "embedding_vector_or_reranker_changed": False,
        "improvement_proven_by_diagnostics": improvement_proven,
        "before_summary": before_summary,
        "after_summary": after_summary,
        "delta_summary": delta,
        "case_comparison": _case_delta(before_cases, after_cases),
        "truth_boundary_statement": (
            "This report measures retrieval calibration only. It is not answer-quality proof, deployment evidence, "
            "legal approval, regulatory approval, biological validation, or wet-lab capability."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build V1.3B-2 retrieval quality calibration before/after report.")
    parser.add_argument("--before", type=Path, default=DEFAULT_BEFORE_PATH)
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
    if args.output.exists() and not args.overwrite:
        print(f"ERROR: output exists, pass --overwrite: {args.output}", file=sys.stderr)
        return 1
    report = build_calibration_report(args.before, args.fixture, args.registry, args.chunks, args.top_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["improvement_proven_by_diagnostics"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
