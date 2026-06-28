from __future__ import annotations

import argparse
import json
import subprocess
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


DEFAULT_BASELINE = REPO_ROOT / "eval_results" / "v1_4a_cost_latency_token_baseline" / "cost_latency_token_baseline.json"
DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_4d_answer_boilerplate_trimming" / "answer_boilerplate_trimming.json"
DEFAULT_DOC = REPO_ROOT / "docs" / "evals" / "V1_4D_ANSWER_BOILERPLATE_TRIMMING_REPORT.md"
DEFAULT_README = REPO_ROOT / "eval_results" / "v1_4d_answer_boilerplate_trimming" / "README.md"

REQUIRED_FIELDS = (
    "Bottom line:",
    "Internal facts:",
    "Key evidence:",
    "Inference:",
    "Speculation:",
    "Verification needed:",
    "Missing evidence:",
    "Limitations/truth-boundary:",
    "Next action:",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline_artifact(path: Path) -> tuple[dict[str, Any], str]:
    relative = path.relative_to(REPO_ROOT).as_posix()
    try:
        completed = subprocess.run(
            ["git", "show", f"origin/main:{relative}"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return load_json(path), str(path)
    return json.loads(completed.stdout), f"origin/main:{relative}"


def case_key(case: dict[str, Any]) -> tuple[str, str]:
    return str(case["suite"]), str(case["case_id"])


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
                "answer_approx_token_delta": after["answer_approx_token_count"] - before["answer_approx_token_count"],
                "before_section_count": before["answer_contract_router_section_count"],
                "after_section_count": after["answer_contract_router_section_count"],
                "section_count_delta": after["answer_contract_router_section_count"] - before["answer_contract_router_section_count"],
                "citation_count_preserved": before["citation_count"] == after["citation_count"],
                "evidence_count_preserved": before["evidence_count"] == after["evidence_count"],
                "source_paths_preserved": before["source_paths"] == after["source_paths"],
            }
        )
    return rows


def answer_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [case for case in cases if int(case.get("answer_approx_token_count") or 0) > 0]


def improved_cases(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: int(row["answer_approx_token_delta"]))
    return [
        {
            "case_id": row["case_id"],
            "suite": row["suite"],
            "query": row["query"],
            "answer_approx_token_delta": row["answer_approx_token_delta"],
            "section_count_delta": row["section_count_delta"],
        }
        for row in ranked[:limit]
    ]


def build_report(baseline_path: Path = DEFAULT_BASELINE) -> dict[str, Any]:
    if not baseline_path.exists():
        raise SystemExit(f"baseline artifact missing: {baseline_path}")
    before_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    before_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)
    before_artifact, baseline_source = load_baseline_artifact(baseline_path)
    after = baseline.build_report()
    after_source_hashes = baseline.hashes(baseline.PROTECTED_PATHS)
    after_retrieval_hashes = baseline.hashes(baseline.RETRIEVAL_FILES)

    before_answer_cases = answer_cases(before_artifact["cases"])
    after_answer_cases = answer_cases(after["cases"])
    rows = compare_cases(before_answer_cases, after_answer_cases)
    before_tokens = sum(int(case["answer_approx_token_count"]) for case in before_answer_cases)
    after_tokens = sum(int(case["answer_approx_token_count"]) for case in after_answer_cases)
    before_sections = sum(int(case["answer_contract_router_section_count"]) for case in before_answer_cases)
    after_sections = sum(int(case["answer_contract_router_section_count"]) for case in after_answer_cases)
    citations_preserved = all(row["citation_count_preserved"] for row in rows)
    evidence_preserved = all(row["evidence_count_preserved"] for row in rows)
    source_paths_preserved = all(row["source_paths_preserved"] for row in rows)
    source_artifacts_mutated = before_source_hashes != after_source_hashes
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    token_reduced = after_tokens < before_tokens
    section_count_preserved = after_sections == before_sections

    return {
        "schema_version": "v1.4d-answer-boilerplate-trimming",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": all(
            [
                after["ok"],
                token_reduced,
                section_count_preserved,
                citations_preserved,
                evidence_preserved,
                source_paths_preserved,
                not source_artifacts_mutated,
                not retrieval_scoring_changed,
            ]
        ),
        "baseline_artifact": baseline_source,
        "summary": {
            "case_count": len(rows),
            "before_answer_approx_tokens": before_tokens,
            "after_answer_approx_tokens": after_tokens,
            "answer_approx_token_delta": after_tokens - before_tokens,
            "before_section_count": before_sections,
            "after_section_count": after_sections,
            "section_count_delta": after_sections - before_sections,
            "citation_count_preserved": citations_preserved,
            "evidence_count_preserved": evidence_preserved,
            "source_paths_preserved": source_paths_preserved,
            "retrieval_scoring_changed": retrieval_scoring_changed,
            "source_artifacts_mutated": source_artifacts_mutated,
        },
        "trimmed_boilerplate": [
            "Shortened the repeated post-bottom-line evidence caveat.",
            "Shortened source fact bullets while preserving source path, priority, evidence label, section, and citation.",
            "Shortened deterministic inference, speculation, verification, source-map, DB-completion, and truth-boundary lines.",
        ],
        "preserved_required_fields": list(REQUIRED_FIELDS),
        "highest_improved_cases": improved_cases(rows),
        "regressions": [
            row
            for row in rows
            if not row["citation_count_preserved"]
            or not row["evidence_count_preserved"]
            or not row["source_paths_preserved"]
            or int(row["section_count_delta"]) != 0
        ],
        "cases": rows,
        "truth_boundary_statement": (
            "This check measures deterministic answer boilerplate length only. It does not change retrieval ranking, "
            "document chunking, metadata handling, embeddings, vector DB behavior, reranking, source ingestion, or answer-quality claims."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# V1.4D Answer Boilerplate Trimming Report",
        "",
        "## Executive bottom line",
        "",
        "V1.4D trims deterministic repeated answer boilerplate while preserving required answer-contract sections, citations, evidence/source separation, truth-boundary language, and compliance gates.",
        "",
        "## Answer delta",
        "",
        f"- Answer approximate tokens: {summary['before_answer_approx_tokens']} -> {summary['after_answer_approx_tokens']} ({summary['answer_approx_token_delta']})",
        f"- Section count: {summary['before_section_count']} -> {summary['after_section_count']} ({summary['section_count_delta']})",
        f"- Citation count preserved: {summary['citation_count_preserved']}",
        f"- Evidence count preserved: {summary['evidence_count_preserved']}",
        f"- Source paths preserved: {summary['source_paths_preserved']}",
        f"- Retrieval scoring changed: {summary['retrieval_scoring_changed']}",
        f"- Source artifacts mutated: {summary['source_artifacts_mutated']}",
        "",
        "## Trimmed Boilerplate",
        "",
    ]
    lines.extend(f"- {item}" for item in report["trimmed_boilerplate"])
    lines.extend(["", "## Preserved Required Fields", ""])
    lines.extend(f"- {item}" for item in report["preserved_required_fields"])
    lines.extend(["", "## Highest Improved Cases", ""])
    for row in report["highest_improved_cases"]:
        lines.append(f"- {row['case_id']} ({row['suite']}): answer {row['answer_approx_token_delta']}, sections {row['section_count_delta']}")
    lines.extend(["", "## Regressions", ""])
    if report["regressions"]:
        lines.extend(f"- {row['case_id']} ({row['suite']})" for row in report["regressions"])
    else:
        lines.append("- None detected by this deterministic comparison.")
    lines.extend(["", "## Truth Boundary", "", report["truth_boundary_statement"], ""])
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# V1.4D Answer Boilerplate Trimming",
            "",
            "This folder contains the deterministic V1.4D before/after answer boilerplate artifact.",
            "",
            "- `answer_boilerplate_trimming.json`: machine-readable comparison against the V1.4A answer-length baseline.",
            "- The check preserves citations, evidence counts, source paths, required sections, retrieval scoring, and source artifacts.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check deterministic V1.4D answer boilerplate trimming.")
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
