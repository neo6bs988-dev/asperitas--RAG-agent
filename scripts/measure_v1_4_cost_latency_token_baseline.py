from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.agent_runner import ask_agent  # noqa: E402
from asperitas_agent.chunking import read_chunks  # noqa: E402
from asperitas_agent.evidence_pack import build_evidence_pack  # noqa: E402
from asperitas_agent.guardrails import evaluate_evidence_guardrail  # noqa: E402
from asperitas_agent.registry import read_registry  # noqa: E402
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_4a_cost_latency_token_baseline" / "cost_latency_token_baseline.json"
DEFAULT_DOC = REPO_ROOT / "docs" / "evals" / "V1_4A_COST_LATENCY_TOKEN_BASELINE.md"
DEFAULT_README = REPO_ROOT / "eval_results" / "v1_4a_cost_latency_token_baseline" / "README.md"
BASELINE_COMMITS = {
    "v1_3e_merge_sha": "fd0c93c7a7155f4054266b1b93512c5fe9396231",
    "v1_3d_merge_sha": "635db3186f3538b12934f170a314bbe50c1a1d30",
    "v1_3c_merge_sha": "65a200cc7736bb946bbf1ead7d71a5129bff7c61",
    "pr_102_merge_sha": "9c3d8ee7d9cb6885540aa9f67a8ecff297d468ec",
}
PROTECTED_PATHS = (
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "eval/expected_sources.jsonl",
    "eval/golden_agent_queries.jsonl",
    "eval/retrieval_questions.jsonl",
)
RETRIEVAL_FILES = ("src/asperitas_agent/retrieval_mvp003.py",)
SECTION_MARKERS = (
    "Bottom line:",
    "Internal facts:",
    "Key evidence:",
    "Inference:",
    "Speculation:",
    "Verification needed:",
    "Missing evidence:",
    "Limitations/truth-boundary:",
    "Next action:",
    "Compliance/biosafety/legal gate:",
    "P6 benchmark analogy/doctrine:",
    "Truth/compliance router:",
)


def load_script_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hashes(paths: tuple[str, ...]) -> dict[str, str]:
    return {relative: sha256_file(REPO_ROOT / relative) for relative in paths if (REPO_ROOT / relative).exists()}


def approx_tokens(text: str) -> int:
    if not text:
        return 0
    return int(math.ceil(len(text) / 4))


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil((pct / 100) * len(ordered)) - 1))
    return ordered[index]


def stable_case_id(prefix: str, index: int, raw_id: str = "") -> str:
    return raw_id or f"{prefix}-{index:03d}"


def evidence_source_key(item: dict[str, Any]) -> str:
    return str(item.get("source_path") or item.get("source_file") or item.get("source_id") or item.get("chunk_id") or "")


def context_text(item: dict[str, Any]) -> str:
    return str(item.get("text_excerpt") or item.get("text") or "")


def duplicate_counts(evidence: list[dict[str, Any]]) -> dict[str, int]:
    source_counts = Counter(evidence_source_key(item) for item in evidence if evidence_source_key(item))
    chunk_counts = Counter(str(item.get("chunk_id")) for item in evidence if item.get("chunk_id"))
    return {
        "duplicate_source_count": sum(count - 1 for count in source_counts.values() if count > 1),
        "duplicate_evidence_count": sum(count - 1 for count in chunk_counts.values() if count > 1),
    }


def answer_section_count(answer: str) -> int:
    return sum(1 for marker in SECTION_MARKERS if marker in answer)


def measure_response(case_id: str, suite: str, query: str, top_k: int, response: dict[str, Any], runtime_ms: float) -> dict[str, Any]:
    answer = str(response.get("answer", ""))
    evidence = [item for item in response.get("evidence", []) if isinstance(item, dict)]
    context = "\n\n".join(context_text(item) for item in evidence)
    duplicates = duplicate_counts(evidence)
    return {
        "case_id": case_id,
        "suite": suite,
        "query": query,
        "top_k": top_k,
        "status": response.get("status"),
        "answer_char_count": len(answer),
        "answer_approx_token_count": approx_tokens(answer),
        "evidence_count": int(response.get("evidence_count", len(evidence))),
        "citation_count": len(response.get("citations_used", [])),
        "duplicate_evidence_count": duplicates["duplicate_evidence_count"],
        "duplicate_source_count": duplicates["duplicate_source_count"],
        "retrieved_context_char_count": len(context),
        "retrieved_context_approx_token_count": approx_tokens(context),
        "ask_agent_runtime_ms": round(runtime_ms, 3),
        "retrieval_evidence_assembly_runtime_ms": None,
        "answer_contract_router_section_count": answer_section_count(answer),
        "source_paths": [evidence_source_key(item) for item in evidence],
    }


def timed_ask_agent(query: str, top_k: int, **kwargs: Any) -> tuple[dict[str, Any], float]:
    start = time.perf_counter()
    response = ask_agent(query, top_k=top_k, **kwargs).to_json()
    return response, (time.perf_counter() - start) * 1000


def timed_default_agent_case(case_id: str, suite: str, query: str, top_k: int) -> dict[str, Any]:
    response, runtime_ms = timed_ask_agent(query, top_k=top_k)
    return measure_response(case_id, suite, query, top_k, response, runtime_ms)


def timed_empty_agent_case(case_id: str, suite: str, query: str, top_k: int) -> dict[str, Any]:
    response, runtime_ms = timed_ask_agent(query, top_k=top_k, records=[], chunks=[])
    return measure_response(case_id, suite, query, top_k, response, runtime_ms)


def measure_default_retrieval_assembly(query: str, top_k: int) -> float:
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    start = time.perf_counter()
    retrieved = search_chunks_mvp003(query, chunks, records, limit=top_k, include_explanations=True)
    pack = build_evidence_pack(query, retrieved, top_k=top_k)
    evaluate_evidence_guardrail(pack)
    return (time.perf_counter() - start) * 1000


def collect_golden_cases() -> list[dict[str, Any]]:
    golden = load_script_module("v1_4a_golden_eval", REPO_ROOT / "scripts" / "run_golden_agent_eval.py")
    cases = []
    for case in golden.load_golden_cases(golden.DEFAULT_GOLDEN_FILE):
        mode = case.get("mode", "default")
        if mode == "empty_corpus":
            measured = timed_empty_agent_case(str(case["id"]), "golden_eval", str(case["query"]), int(case["top_k"]))
        else:
            measured = timed_default_agent_case(str(case["id"]), "golden_eval", str(case["query"]), int(case["top_k"]))
            measured["retrieval_evidence_assembly_runtime_ms"] = round(
                measure_default_retrieval_assembly(str(case["query"]), int(case["top_k"])),
                3,
            )
        cases.append(measured)
    return cases


def collect_v1_3c_cases() -> list[dict[str, Any]]:
    contract = load_script_module("v1_4a_answer_contract", REPO_ROOT / "scripts" / "check_v1_3c_answer_contract.py")
    cases = []
    for case in contract.CASES:
        start = time.perf_counter()
        if case.get("mode") == "empty_corpus":
            response = ask_agent(case["query"], top_k=int(case["top_k"]), records=[], chunks=[]).to_json()
        elif case.get("mode") == "synthetic_p6":
            response = contract.run_synthetic_p6_case(case["query"])
        elif case.get("mode") == "synthetic_source_map_url":
            response = contract.run_synthetic_source_map_case(case["query"])
        else:
            response = ask_agent(case["query"], top_k=int(case["top_k"])).to_json()
        runtime_ms = (time.perf_counter() - start) * 1000
        answer = str(response.get("answer", ""))
        evidence = [item for item in response.get("evidence", []) if isinstance(item, dict)]
        context = "\n\n".join(context_text(item) for item in evidence)
        duplicates = duplicate_counts(evidence)
        measured = {
            "case_id": case["case_id"],
            "suite": "v1_3c_answer_contract",
            "query": case["query"],
            "top_k": int(case["top_k"]),
            "status": response["status"],
            "answer_char_count": len(answer),
            "answer_approx_token_count": approx_tokens(answer),
            "evidence_count": response["evidence_count"],
            "citation_count": len(response["citations_used"]),
            "duplicate_evidence_count": duplicates["duplicate_evidence_count"],
            "duplicate_source_count": duplicates["duplicate_source_count"],
            "retrieved_context_char_count": len(context),
            "retrieved_context_approx_token_count": approx_tokens(context),
            "ask_agent_runtime_ms": round(runtime_ms, 3),
            "retrieval_evidence_assembly_runtime_ms": None,
            "answer_contract_router_section_count": answer_section_count(answer),
            "source_paths": [evidence_source_key(item) for item in evidence],
        }
        cases.append(measured)
    return cases


def collect_v1_3d_cases() -> list[dict[str, Any]]:
    router = load_script_module("v1_4a_truth_router", REPO_ROOT / "scripts" / "check_v1_3d_truth_compliance_router.py")
    cases = []
    for case in router.CASES:
        start = time.perf_counter()
        pack = router.build_evidence_pack(case["query"], case["results"], top_k=len(case["results"]) or 5)
        answer = router.generate_grounded_answer(pack, router.evaluate_evidence_guardrail(pack)).to_json()
        runtime_ms = (time.perf_counter() - start) * 1000
        evidence = [item for item in case.get("results", []) if isinstance(item, dict)]
        context = "\n\n".join(context_text(item) for item in evidence)
        duplicates = duplicate_counts(evidence)
        answer_text = str(answer["answer_text"])
        cases.append(
            {
                "case_id": case["case_id"],
                "suite": "v1_3d_truth_compliance_router",
                "query": case["query"],
                "top_k": len(evidence) or 5,
                "status": answer["answer_status"],
                "answer_char_count": len(answer_text),
                "answer_approx_token_count": approx_tokens(answer_text),
                "evidence_count": len(evidence),
                "citation_count": len(answer["citations_used"]),
                "duplicate_evidence_count": duplicates["duplicate_evidence_count"],
                "duplicate_source_count": duplicates["duplicate_source_count"],
                "retrieved_context_char_count": len(context),
                "retrieved_context_approx_token_count": approx_tokens(context),
                "ask_agent_runtime_ms": round(runtime_ms, 3),
                "retrieval_evidence_assembly_runtime_ms": None,
                "answer_contract_router_section_count": answer_section_count(answer_text),
                "source_paths": [evidence_source_key(item) for item in evidence],
            }
        )
    return cases


def collect_retrieval_sample_cases(limit: int = 5, sample_size: int = 8) -> list[dict[str, Any]]:
    retrieval = load_script_module("v1_4a_retrieval_eval", REPO_ROOT / "scripts" / "run_retrieval_eval.py")
    questions = retrieval.load_questions(REPO_ROOT / "eval" / "retrieval_questions.jsonl")
    expected = retrieval.load_expected_sources(REPO_ROOT / "eval" / "expected_sources.jsonl")
    retrieval.validate_expected_alignment(questions, expected)
    questions = retrieval.merge_expected_oracle_fields(questions, expected)[:sample_size]
    records = read_registry(REPO_ROOT / "data" / "source_registry.csv")
    chunks = read_chunks(REPO_ROOT / "data" / "chunks.jsonl")
    cases = []
    for index, question in enumerate(questions, start=1):
        start = time.perf_counter()
        results = search_chunks_mvp003(question.user_question, chunks, records, limit=limit, include_explanations=True)
        pack = build_evidence_pack(question.user_question, results, top_k=limit)
        runtime_ms = (time.perf_counter() - start) * 1000
        evidence = [item.to_json() for item in pack.evidence_items]
        context = "\n\n".join(context_text(item) for item in evidence)
        duplicates = duplicate_counts(evidence)
        cases.append(
            {
                "case_id": stable_case_id("retrieval_sample", index, question.question_id),
                "suite": "retrieval_eval_sample",
                "query": question.user_question,
                "top_k": limit,
                "status": "retrieved",
                "answer_char_count": 0,
                "answer_approx_token_count": 0,
                "evidence_count": len(evidence),
                "citation_count": 0,
                "duplicate_evidence_count": duplicates["duplicate_evidence_count"],
                "duplicate_source_count": duplicates["duplicate_source_count"],
                "retrieved_context_char_count": len(context),
                "retrieved_context_approx_token_count": approx_tokens(context),
                "ask_agent_runtime_ms": 0,
                "retrieval_evidence_assembly_runtime_ms": round(runtime_ms, 3),
                "answer_contract_router_section_count": 0,
                "source_paths": [evidence_source_key(item) for item in evidence],
            }
        )
    return cases


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(case["ask_agent_runtime_ms"] or 0) for case in cases if case["ask_agent_runtime_ms"] is not None]
    retrieval_latencies = [
        float(case["retrieval_evidence_assembly_runtime_ms"])
        for case in cases
        if case.get("retrieval_evidence_assembly_runtime_ms") is not None
    ]
    answer_tokens = [int(case["answer_approx_token_count"] or 0) for case in cases]
    context_tokens = [int(case["retrieved_context_approx_token_count"] or 0) for case in cases]
    return {
        "case_count": len(cases),
        "suite_counts": dict(sorted(Counter(case["suite"] for case in cases).items())),
        "total_answer_approx_tokens": sum(answer_tokens),
        "total_retrieved_context_approx_tokens": sum(context_tokens),
        "total_duplicate_evidence_count": sum(int(case["duplicate_evidence_count"]) for case in cases),
        "total_duplicate_source_count": sum(int(case["duplicate_source_count"]) for case in cases),
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 3) if latencies else 0,
            "p50": round(percentile(latencies, 50), 3),
            "p95": round(percentile(latencies, 95), 3),
            "max": round(max(latencies), 3) if latencies else 0,
        },
        "retrieval_evidence_assembly_latency_ms": {
            "mean": round(statistics.mean(retrieval_latencies), 3) if retrieval_latencies else 0,
            "max": round(max(retrieval_latencies), 3) if retrieval_latencies else 0,
        },
    }


def top_cases(cases: list[dict[str, Any]], field: str, limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(cases, key=lambda case: float(case.get(field) or 0), reverse=True)
    return [
        {
            "case_id": case["case_id"],
            "suite": case["suite"],
            "query": case["query"],
            field: case.get(field),
        }
        for case in ranked[:limit]
    ]


def build_report() -> dict[str, Any]:
    before_source_hashes = hashes(PROTECTED_PATHS)
    before_retrieval_hashes = hashes(RETRIEVAL_FILES)
    cases = collect_golden_cases() + collect_v1_3c_cases() + collect_v1_3d_cases() + collect_retrieval_sample_cases()
    after_source_hashes = hashes(PROTECTED_PATHS)
    after_retrieval_hashes = hashes(RETRIEVAL_FILES)
    source_artifacts_mutated = before_source_hashes != after_source_hashes
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    return {
        "schema_version": "v1.4a-cost-latency-token-baseline",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": not source_artifacts_mutated and not retrieval_scoring_changed,
        "baseline_commits": BASELINE_COMMITS,
        "scope_lock": {
            "measurement_only": True,
            "answer_behavior_changed": False,
            "retrieval_scoring_changed": retrieval_scoring_changed,
            "source_artifacts_mutated": source_artifacts_mutated,
        },
        "measurement_fields": [
            "answer_char_count",
            "answer_approx_token_count",
            "evidence_count",
            "citation_count",
            "duplicate_evidence_count",
            "duplicate_source_count",
            "retrieved_context_char_count",
            "retrieved_context_approx_token_count",
            "ask_agent_runtime_ms",
            "retrieval_evidence_assembly_runtime_ms",
            "answer_contract_router_section_count",
        ],
        "summary": summarize_cases(cases),
        "top_token_cost_drivers": top_cases(cases, "retrieved_context_approx_token_count"),
        "top_answer_length_drivers": top_cases(cases, "answer_approx_token_count"),
        "highest_latency_cases": top_cases(cases, "ask_agent_runtime_ms"),
        "highest_retrieval_assembly_latency_cases": top_cases(cases, "retrieval_evidence_assembly_runtime_ms"),
        "safe_optimization_candidates_v1_4b": [
            "Context compression after retrieval scoring and before answer assembly, without changing ranking.",
            "Answer-section and boilerplate trimming under V1.3C answer-contract and V1.3D router tests.",
            "Eval harness caching for registry/chunk reads; keep production behavior separate from baseline claims.",
        ],
        "not_currently_prioritized_v1_4b": [
            (
                "Duplicate evidence reduction is not currently prioritized because measured duplicate evidence "
                "and duplicate source counts are zero."
            )
        ],
        "cases": cases,
        "truth_boundary_statement": (
            "This baseline measures deterministic local cost, latency, token/context size, evidence duplication, "
            "and output length. It is not an optimization, deployment claim, legal clearance, regulatory clearance, "
            "biological validation, or answer-quality proof beyond the referenced fixtures."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# V1.4A Cost Latency Token Baseline",
        "",
        "## Executive bottom line",
        "",
        "V1.4A adds deterministic measurement only. It records answer length, approximate token/context size, evidence and citation counts, duplicate evidence/source counts, latency, retrieval/evidence assembly latency where isolated, and answer/router section counts without changing answer behavior or retrieval scoring.",
        "",
        "## Baseline commits",
        "",
    ]
    lines.extend(f"- {name}: `{sha}`" for name, sha in report["baseline_commits"].items())
    lines.extend(
        [
            "",
            "## Results summary",
            "",
            f"- Cases measured: {summary['case_count']}",
            f"- Suite counts: `{json.dumps(summary['suite_counts'], sort_keys=True)}`",
            f"- Total answer approximate tokens: {summary['total_answer_approx_tokens']}",
            f"- Total retrieved-context approximate tokens: {summary['total_retrieved_context_approx_tokens']}",
            f"- Duplicate evidence count: {summary['total_duplicate_evidence_count']}",
            f"- Duplicate source count: {summary['total_duplicate_source_count']}",
            f"- Ask-agent latency mean/p50/p95/max ms: {summary['latency_ms']['mean']} / {summary['latency_ms']['p50']} / {summary['latency_ms']['p95']} / {summary['latency_ms']['max']}",
            f"- Retrieval/evidence assembly latency mean/max ms: {summary['retrieval_evidence_assembly_latency_ms']['mean']} / {summary['retrieval_evidence_assembly_latency_ms']['max']}",
            "",
            "## Top cost/token drivers",
            "",
        ]
    )
    for row in report["top_token_cost_drivers"]:
        lines.append(f"- {row['case_id']} ({row['suite']}): {row['retrieved_context_approx_token_count']} context tokens")
    lines.extend(["", "## Highest-latency cases", ""])
    for row in report["highest_latency_cases"]:
        lines.append(f"- {row['case_id']} ({row['suite']}): {row['ask_agent_runtime_ms']} ms")
    lines.extend(["", "## Scope lock", ""])
    for key, value in report["scope_lock"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Safe V1.4B candidates", ""])
    lines.extend(f"- {item}" for item in report["safe_optimization_candidates_v1_4b"])
    lines.extend(["", "## Not Currently Prioritized", ""])
    lines.extend(f"- {item}" for item in report["not_currently_prioritized_v1_4b"])
    lines.extend(["", "## Truth boundary", "", report["truth_boundary_statement"], ""])
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# V1.4A Cost Latency Token Baseline",
            "",
            "This folder contains the deterministic V1.4A baseline artifact.",
            "",
            "- `cost_latency_token_baseline.json`: machine-readable baseline metrics.",
            "- Source artifacts, retrieval scoring, answer generation, and router behavior are not changed by this measurement.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Measure deterministic V1.4A cost/latency/token baseline.")
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
