from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_ROOT = REPO_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import measure_v1_4_cost_latency_token_baseline as baseline  # noqa: E402
import asperitas_agent.agent_runner as agent_runner  # noqa: E402
from asperitas_agent.evidence_pack import DEFAULT_SNIPPET_CHARS, PRE_COMPRESSION_SNIPPET_CHARS  # noqa: E402
from asperitas_agent.evidence_pack import build_evidence_pack as _build_evidence_pack  # noqa: E402


DEFAULT_BASELINE = REPO_ROOT / "eval_results" / "v1_4a_cost_latency_token_baseline" / "cost_latency_token_baseline.json"
DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_4b_token_context_compression" / "token_context_compression.json"
DEFAULT_DOC = REPO_ROOT / "docs" / "evals" / "V1_4B_TOKEN_CONTEXT_COMPRESSION_REPORT.md"
DEFAULT_README = REPO_ROOT / "eval_results" / "v1_4b_token_context_compression" / "README.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def snippet_cap(snippet_chars: int):
    original_baseline_builder = baseline.build_evidence_pack
    original_runner_builder = agent_runner.build_evidence_pack

    def capped_builder(query: str, retrieval_results: Any, **kwargs: Any):
        kwargs["snippet_chars"] = snippet_chars
        return _build_evidence_pack(query, retrieval_results, **kwargs)

    baseline.build_evidence_pack = capped_builder
    agent_runner.build_evidence_pack = capped_builder
    try:
        yield
    finally:
        baseline.build_evidence_pack = original_baseline_builder
        agent_runner.build_evidence_pack = original_runner_builder


def collect_report_with_snippet_cap(snippet_chars: int) -> dict[str, Any]:
    with snippet_cap(snippet_chars):
        return baseline.build_report()


def case_key(case: dict[str, Any]) -> tuple[str, str]:
    return str(case["suite"]), str(case["case_id"])


def delta(before: int | float, after: int | float) -> int | float:
    return after - before


def compare_cases(before_cases: list[dict[str, Any]], after_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    before_by_key = {case_key(case): case for case in before_cases}
    rows: list[dict[str, Any]] = []
    for after in after_cases:
        before = before_by_key[case_key(after)]
        rows.append(
            {
                "case_id": after["case_id"],
                "suite": after["suite"],
                "query": after["query"],
                "before_answer_approx_token_count": before["answer_approx_token_count"],
                "after_answer_approx_token_count": after["answer_approx_token_count"],
                "answer_approx_token_delta": delta(before["answer_approx_token_count"], after["answer_approx_token_count"]),
                "before_retrieved_context_approx_token_count": before["retrieved_context_approx_token_count"],
                "after_retrieved_context_approx_token_count": after["retrieved_context_approx_token_count"],
                "retrieved_context_approx_token_delta": delta(
                    before["retrieved_context_approx_token_count"],
                    after["retrieved_context_approx_token_count"],
                ),
                "before_ask_agent_runtime_ms": before["ask_agent_runtime_ms"],
                "after_ask_agent_runtime_ms": after["ask_agent_runtime_ms"],
                "ask_agent_runtime_ms_delta": round(delta(before["ask_agent_runtime_ms"], after["ask_agent_runtime_ms"]), 3),
                "before_retrieval_evidence_assembly_runtime_ms": before["retrieval_evidence_assembly_runtime_ms"],
                "after_retrieval_evidence_assembly_runtime_ms": after["retrieval_evidence_assembly_runtime_ms"],
                "evidence_count_preserved": before["evidence_count"] == after["evidence_count"],
                "citation_count_preserved": before["citation_count"] == after["citation_count"],
                "source_paths_preserved": before["source_paths"] == after["source_paths"],
            }
        )
    return rows


def improved_cases(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: int(row["retrieved_context_approx_token_delta"]))
    return [
        {
            "case_id": row["case_id"],
            "suite": row["suite"],
            "query": row["query"],
            "retrieved_context_approx_token_delta": row["retrieved_context_approx_token_delta"],
            "answer_approx_token_delta": row["answer_approx_token_delta"],
        }
        for row in ranked[:limit]
    ]


def build_report(baseline_path: Path = DEFAULT_BASELINE) -> dict[str, Any]:
    before_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    before_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)
    if not baseline_path.exists():
        raise SystemExit(f"baseline artifact missing: {baseline_path}")
    artifact_before = load_json(baseline_path)
    before = collect_report_with_snippet_cap(PRE_COMPRESSION_SNIPPET_CHARS)
    after = collect_report_with_snippet_cap(DEFAULT_SNIPPET_CHARS)
    after_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    after_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)
    rows = compare_cases(before["cases"], after["cases"])
    total_before_answer = int(before["summary"]["total_answer_approx_tokens"])
    total_after_answer = int(after["summary"]["total_answer_approx_tokens"])
    total_before_context = int(before["summary"]["total_retrieved_context_approx_tokens"])
    total_after_context = int(after["summary"]["total_retrieved_context_approx_tokens"])
    evidence_preserved = all(row["evidence_count_preserved"] for row in rows)
    citations_preserved = all(row["citation_count_preserved"] for row in rows)
    source_paths_preserved = all(row["source_paths_preserved"] for row in rows)
    source_artifacts_mutated = before_source_hashes != after_source_hashes
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    context_reduced = total_after_context < total_before_context
    answer_not_increased = total_after_answer <= total_before_answer
    return {
        "schema_version": "v1.4b-token-context-compression",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": all(
            [
                after["ok"],
                context_reduced,
                answer_not_increased,
                evidence_preserved,
                citations_preserved,
                source_paths_preserved,
                not source_artifacts_mutated,
                not retrieval_scoring_changed,
            ]
        ),
        "compression_config": {
            "pre_compression_snippet_chars": PRE_COMPRESSION_SNIPPET_CHARS,
            "post_compression_snippet_chars": DEFAULT_SNIPPET_CHARS,
            "baseline_artifact": str(baseline_path),
            "baseline_artifact_schema_version": artifact_before.get("schema_version"),
            "strategy": "deterministic whitespace compaction plus excerpt cap after retrieval scoring and before answer assembly",
        },
        "summary": {
            "case_count": len(rows),
            "before_answer_approx_tokens": total_before_answer,
            "after_answer_approx_tokens": total_after_answer,
            "answer_approx_token_delta": total_after_answer - total_before_answer,
            "before_retrieved_context_approx_tokens": total_before_context,
            "after_retrieved_context_approx_tokens": total_after_context,
            "retrieved_context_approx_token_delta": total_after_context - total_before_context,
            "before_latency_ms": before["summary"]["latency_ms"],
            "after_latency_ms": after["summary"]["latency_ms"],
            "before_retrieval_evidence_assembly_latency_ms": before["summary"]["retrieval_evidence_assembly_latency_ms"],
            "after_retrieval_evidence_assembly_latency_ms": after["summary"]["retrieval_evidence_assembly_latency_ms"],
            "citation_count_preserved": citations_preserved,
            "evidence_count_preserved": evidence_preserved,
            "source_paths_preserved": source_paths_preserved,
            "retrieval_scoring_changed": retrieval_scoring_changed,
            "source_artifacts_mutated": source_artifacts_mutated,
        },
        "highest_improved_cases": improved_cases(rows),
        "regressions": [
            row
            for row in rows
            if not row["evidence_count_preserved"]
            or not row["citation_count_preserved"]
            or not row["source_paths_preserved"]
            or int(row["answer_approx_token_delta"]) > 0
        ],
        "not_currently_prioritized_v1_4b": [
            "Duplicate evidence reduction is not prioritized because V1.4A measured duplicate evidence and duplicate source counts as zero."
        ],
        "quality_eval_statement": (
            "This artifact compares deterministic token/context metrics. Answer quality is guarded by the separate "
            "V1.3C, V1.3D, golden, retrieval, and pytest validation commands; it is not claimed from this metric alone."
        ),
        "cases": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# V1.4B Token Context Compression Report",
        "",
        "## Executive bottom line",
        "",
        "V1.4B applies deterministic post-retrieval context compression by compacting whitespace and lowering the evidence excerpt cap after retrieval scoring, preserving citation keys, source IDs, source paths, source priority, evidence labels, section metadata, and source boundaries.",
        "",
        "## Token/context delta",
        "",
        f"- Answer approximate tokens: {summary['before_answer_approx_tokens']} -> {summary['after_answer_approx_tokens']} ({summary['answer_approx_token_delta']})",
        f"- Retrieved-context approximate tokens: {summary['before_retrieved_context_approx_tokens']} -> {summary['after_retrieved_context_approx_tokens']} ({summary['retrieved_context_approx_token_delta']})",
        f"- Citation count preserved: {summary['citation_count_preserved']}",
        f"- Evidence count preserved: {summary['evidence_count_preserved']}",
        f"- Source paths preserved: {summary['source_paths_preserved']}",
        f"- Retrieval scoring changed: {summary['retrieval_scoring_changed']}",
        f"- Source artifacts mutated: {summary['source_artifacts_mutated']}",
        "",
        "## Highest improved cases",
        "",
    ]
    for row in report["highest_improved_cases"]:
        lines.append(
            f"- {row['case_id']} ({row['suite']}): context {row['retrieved_context_approx_token_delta']}, answer {row['answer_approx_token_delta']}"
        )
    lines.extend(["", "## Regressions", ""])
    if report["regressions"]:
        lines.extend(f"- {row['case_id']} ({row['suite']})" for row in report["regressions"])
    else:
        lines.append("- None detected by this deterministic comparison.")
    lines.extend(["", "## Quality boundary", "", report["quality_eval_statement"], ""])
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# V1.4B Token Context Compression",
            "",
            "This folder contains the deterministic V1.4B before/after compression artifact.",
            "",
            "- `token_context_compression.json`: machine-readable comparison against V1.4A.",
            "- Compression is post-retrieval and does not change retrieval scoring or source artifacts.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check deterministic V1.4B token/context compression.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
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
    report = build_report(args.baseline)
    write_text(args.output, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.overwrite)
    write_text(args.doc_output, render_markdown(report), args.overwrite)
    write_text(args.readme_output, render_readme(), args.overwrite)
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
