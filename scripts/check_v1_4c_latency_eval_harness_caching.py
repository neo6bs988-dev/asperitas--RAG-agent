from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_ROOT = REPO_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import eval_harness_cache  # noqa: E402
import check_v1_4b_token_context_compression as v1_4b  # noqa: E402
import measure_v1_4_cost_latency_token_baseline as baseline  # noqa: E402
import run_golden_agent_eval as golden_eval  # noqa: E402
import run_retrieval_eval as retrieval_eval  # noqa: E402


DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_4c_latency_eval_harness_caching" / "latency_eval_harness_caching.json"
DEFAULT_DOC = REPO_ROOT / "docs" / "evals" / "V1_4C_LATENCY_EVAL_HARNESS_CACHING_REPORT.md"
DEFAULT_README = REPO_ROOT / "eval_results" / "v1_4c_latency_eval_harness_caching" / "README.md"


@contextmanager
def eval_cache_mode(enabled: bool):
    previous = os.environ.get("ASPERITAS_EVAL_CACHE")
    os.environ["ASPERITAS_EVAL_CACHE"] = "1" if enabled else "0"
    eval_harness_cache.clear_eval_harness_cache()
    try:
        yield
    finally:
        eval_harness_cache.clear_eval_harness_cache()
        if previous is None:
            os.environ.pop("ASPERITAS_EVAL_CACHE", None)
        else:
            os.environ["ASPERITAS_EVAL_CACHE"] = previous


def timed(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    start = time.perf_counter()
    payload = fn()
    return {
        "label": label,
        "runtime_ms": round((time.perf_counter() - start) * 1000, 3),
        "payload": payload,
        "cache_stats": eval_harness_cache.cache_stats(),
    }


def _summary_subset(report: dict[str, Any]) -> dict[str, Any]:
    summary = dict(report.get("summary") or {})
    summary.pop("latency_ms", None)
    summary.pop("retrieval_evidence_assembly_latency_ms", None)
    return {
        "ok": report.get("ok"),
        "summary": summary,
        "scope_lock": report.get("scope_lock"),
        "case_count": len(report.get("cases", [])),
    }


def runtime_delta(before_ms: float, after_ms: float) -> dict[str, float]:
    delta = round(after_ms - before_ms, 3)
    percent = 0.0 if before_ms <= 0 else round((delta / before_ms) * 100, 3)
    return {
        "before_ms": before_ms,
        "after_ms": after_ms,
        "delta_ms": delta,
        "delta_percent": percent,
    }


def build_report() -> dict[str, Any]:
    before_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    before_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)
    with eval_cache_mode(False):
        uncached = timed("v1_4a_baseline_uncached", baseline.build_report)
    with eval_cache_mode(True):
        cached = timed("v1_4a_baseline_cached", baseline.build_report)
    with eval_cache_mode(False):
        v1_4b_uncached = timed("v1_4b_compression_uncached", v1_4b.build_report)
    with eval_cache_mode(True):
        v1_4b_cached = timed("v1_4b_compression_cached", v1_4b.build_report)
    with eval_cache_mode(False):
        golden_uncached = timed("golden_eval_uncached", golden_eval.evaluate_golden_queries)
    with eval_cache_mode(True):
        golden_cached = timed("golden_eval_cached", golden_eval.evaluate_golden_queries)

    def retrieval_summary() -> dict[str, Any]:
        questions = retrieval_eval.load_questions(REPO_ROOT / "eval" / "retrieval_questions.jsonl")
        expected = retrieval_eval.load_expected_sources(REPO_ROOT / "eval" / "expected_sources.jsonl")
        retrieval_eval.validate_expected_alignment(questions, expected)
        questions = retrieval_eval.merge_expected_oracle_fields(questions, expected)
        _mode, results = retrieval_eval.run_retriever(
            "mvp003",
            questions,
            REPO_ROOT / "data" / "source_registry.csv",
            REPO_ROOT / "data" / "chunks.jsonl",
            5,
        )
        summary = retrieval_eval.score_results(questions, results)
        summary["thresholds"] = retrieval_eval.evaluate_thresholds(summary, "mvp003")
        return summary

    with eval_cache_mode(False):
        retrieval_uncached = timed("retrieval_eval_mvp003_uncached", retrieval_summary)
    with eval_cache_mode(True):
        retrieval_cached = timed("retrieval_eval_mvp003_cached", retrieval_summary)
    after_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    after_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)

    uncached_report = uncached["payload"]
    cached_report = cached["payload"]
    source_artifacts_mutated = before_source_hashes != after_source_hashes
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    behavior_preserved = (
        _summary_subset(uncached_report) == _summary_subset(cached_report)
        and v1_4b_uncached["payload"]["summary"]["case_count"] == v1_4b_cached["payload"]["summary"]["case_count"]
        and golden_uncached["payload"]["cases"] == golden_cached["payload"]["cases"]
        and retrieval_uncached["payload"]["per_question"] == retrieval_cached["payload"]["per_question"]
    )
    cache_hit_count = sum(
        int(item["cache_stats"]["file_cache_hits"]) + int(item["cache_stats"]["evidence_pack_cache_hits"])
        for item in (cached, v1_4b_cached, golden_cached, retrieval_cached)
    )
    delta = runtime_delta(float(uncached["runtime_ms"]), float(cached["runtime_ms"]))
    v1_4b_delta = runtime_delta(float(v1_4b_uncached["runtime_ms"]), float(v1_4b_cached["runtime_ms"]))
    golden_delta = runtime_delta(float(golden_uncached["runtime_ms"]), float(golden_cached["runtime_ms"]))
    retrieval_delta = runtime_delta(float(retrieval_uncached["runtime_ms"]), float(retrieval_cached["runtime_ms"]))
    improved_or_noop_documented = any(item["delta_ms"] <= 0 for item in (delta, v1_4b_delta, golden_delta, retrieval_delta)) or cache_hit_count > 0
    return {
        "schema_version": "v1.4c-latency-eval-harness-caching",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": all(
            [
                uncached_report.get("ok"),
                cached_report.get("ok"),
                behavior_preserved,
                not source_artifacts_mutated,
                not retrieval_scoring_changed,
                cache_hit_count > 0,
                improved_or_noop_documented,
            ]
        ),
        "scope_lock": {
            "eval_harness_only": True,
            "answer_behavior_changed": False,
            "retrieval_scoring_changed": retrieval_scoring_changed,
            "source_artifacts_mutated": source_artifacts_mutated,
            "production_cache_claim": False,
        },
        "cache_targets": [
            "source registry CSV reads",
            "chunks JSONL reads",
            "retrieval/golden fixture JSONL reads",
            "repeated evidence pack assembly in local measurement harnesses",
        ],
        "invalidation_strategy": (
            "In-process cache keys include resolved path, file size, creation time, and mtime for file-backed data; "
            "evidence-pack cache keys include query, top_k, snippet config, and retrieval-result fingerprints."
        ),
        "bypass": "Set ASPERITAS_EVAL_CACHE=0 to disable the eval harness cache.",
        "summary": {
            "v1_4a_baseline_runtime_delta": delta,
            "v1_4b_compression_check_runtime_delta": v1_4b_delta,
            "golden_eval_runtime_delta": golden_delta,
            "retrieval_eval_mvp003_runtime_delta": retrieval_delta,
            "uncached_cache_stats": uncached["cache_stats"],
            "cached_cache_stats": cached["cache_stats"],
            "v1_4b_cached_cache_stats": v1_4b_cached["cache_stats"],
            "golden_cached_cache_stats": golden_cached["cache_stats"],
            "retrieval_cached_cache_stats": retrieval_cached["cache_stats"],
            "behavior_preserved": behavior_preserved,
            "cache_hit_count": cache_hit_count,
            "measurable_latency_improvement": delta["delta_ms"] < 0,
            "documented_noop": delta["delta_ms"] >= 0,
            "retrieval_scoring_changed": retrieval_scoring_changed,
            "source_artifacts_mutated": source_artifacts_mutated,
        },
        "measurements": [
            {"label": uncached["label"], "runtime_ms": uncached["runtime_ms"], "payload_summary": _summary_subset(uncached_report)},
            {"label": cached["label"], "runtime_ms": cached["runtime_ms"], "payload_summary": _summary_subset(cached_report)},
            {"label": v1_4b_uncached["label"], "runtime_ms": v1_4b_uncached["runtime_ms"]},
            {"label": v1_4b_cached["label"], "runtime_ms": v1_4b_cached["runtime_ms"]},
            {"label": golden_uncached["label"], "runtime_ms": golden_uncached["runtime_ms"]},
            {"label": golden_cached["label"], "runtime_ms": golden_cached["runtime_ms"]},
            {"label": retrieval_uncached["label"], "runtime_ms": retrieval_uncached["runtime_ms"]},
            {"label": retrieval_cached["label"], "runtime_ms": retrieval_cached["runtime_ms"]},
        ],
        "truth_boundary_statement": (
            "This check measures deterministic local eval-harness caching only. It does not change retrieval ranking, "
            "answer content, source ingestion, embeddings, vector DB behavior, reranking, or production caching."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    delta = summary["v1_4a_baseline_runtime_delta"]
    lines = [
        "# V1.4C Latency Eval Harness Caching Report",
        "",
        "## Executive bottom line",
        "",
        "V1.4C adds deterministic in-process caching for local eval and measurement harnesses only. Production answer behavior, retrieval scoring, source artifacts, embeddings, vector DB behavior, and reranking remain out of scope.",
        "",
        "## Runtime delta",
        "",
        f"- V1.4A baseline runtime: {delta['before_ms']} ms -> {delta['after_ms']} ms ({delta['delta_ms']} ms, {delta['delta_percent']}%)",
        f"- V1.4B compression check runtime: {summary['v1_4b_compression_check_runtime_delta']['before_ms']} ms -> {summary['v1_4b_compression_check_runtime_delta']['after_ms']} ms ({summary['v1_4b_compression_check_runtime_delta']['delta_ms']} ms, {summary['v1_4b_compression_check_runtime_delta']['delta_percent']}%)",
        f"- Golden eval runtime: {summary['golden_eval_runtime_delta']['before_ms']} ms -> {summary['golden_eval_runtime_delta']['after_ms']} ms ({summary['golden_eval_runtime_delta']['delta_ms']} ms, {summary['golden_eval_runtime_delta']['delta_percent']}%)",
        f"- Retrieval eval runtime: {summary['retrieval_eval_mvp003_runtime_delta']['before_ms']} ms -> {summary['retrieval_eval_mvp003_runtime_delta']['after_ms']} ms ({summary['retrieval_eval_mvp003_runtime_delta']['delta_ms']} ms, {summary['retrieval_eval_mvp003_runtime_delta']['delta_percent']}%)",
        f"- Cache hit count: {summary['cache_hit_count']}",
        f"- Measurable latency improvement: {summary['measurable_latency_improvement']}",
        f"- Documented no-op: {summary['documented_noop']}",
        "",
        "## Cache targets",
        "",
    ]
    lines.extend(f"- {item}" for item in report["cache_targets"])
    lines.extend(
        [
            "",
            "## Invalidation",
            "",
            report["invalidation_strategy"],
            "",
            "## Scope lock",
            "",
        ]
    )
    for key, value in report["scope_lock"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Truth boundary", "", report["truth_boundary_statement"], ""])
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# V1.4C Latency Eval Harness Caching",
            "",
            "This folder contains the deterministic V1.4C local eval-harness caching artifact.",
            "",
            "- `latency_eval_harness_caching.json`: machine-readable cache/runtime comparison.",
            "- Caching is in-process, file-metadata invalidated, and bypassable with `ASPERITAS_EVAL_CACHE=0`.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check deterministic V1.4C local eval-harness caching.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--doc-output", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--readme-output", type=Path, default=DEFAULT_README)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def write_text(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise SystemExit(f"output exists; pass --overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report()
    write_text(args.output, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.overwrite)
    write_text(args.doc_output, render_markdown(report), args.overwrite)
    write_text(args.readme_output, render_readme(), args.overwrite)
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
