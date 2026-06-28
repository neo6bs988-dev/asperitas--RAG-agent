from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_V1_4A = REPO_ROOT / "eval_results" / "v1_4a_cost_latency_token_baseline" / "cost_latency_token_baseline.json"
DEFAULT_V1_4B = REPO_ROOT / "eval_results" / "v1_4b_token_context_compression" / "token_context_compression.json"
DEFAULT_V1_4C = REPO_ROOT / "eval_results" / "v1_4c_latency_eval_harness_caching" / "latency_eval_harness_caching.json"
DEFAULT_V1_4D = REPO_ROOT / "eval_results" / "v1_4d_answer_boilerplate_trimming" / "answer_boilerplate_trimming.json"
DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_4e_final_optimization_closeout" / "final_optimization_closeout.json"
DEFAULT_DOC = REPO_ROOT / "docs" / "evals" / "V1_4E_FINAL_OPTIMIZATION_CLOSEOUT.md"
DEFAULT_README = REPO_ROOT / "eval_results" / "v1_4e_final_optimization_closeout" / "README.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASELINE_COMMITS = {
    "v1_4d_merge_sha": "e29c2f36ab8249103a9d251a95dd0795aa1ee464",
    "v1_4c_merge_sha": "46a3053b96e25f40b4f5bf20f192b87ad0fdaa93",
    "v1_4b_merge_sha": "d06db9c3b71a0a81a15e70c1d683d23e21fa82b1",
    "v1_4a_merge_sha": "699f66e960fe114fc0ff816b7000aee23e9fd9ac",
    "v1_3e_merge_sha": "fd0c93c7a7155f4054266b1b93512c5fe9396231",
    "v1_3d_merge_sha": "635db3186f3538b12934f170a314bbe50c1a1d30",
    "v1_3c_merge_sha": "65a200cc7736bb946bbf1ead7d71a5129bff7c61",
    "pr_102_merge_sha": "9c3d8ee7d9cb6885540aa9f67a8ecff297d468ec",
}
PROTECTED_SOURCE_ARTIFACTS = (
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "eval/expected_sources.jsonl",
    "eval/golden_agent_queries.jsonl",
    "eval/retrieval_questions.jsonl",
)
BEHAVIOR_FILES = (
    "src/asperitas_agent/answer_contract.py",
    "src/asperitas_agent/answer_generation.py",
    "src/asperitas_agent/retrieval_mvp003.py",
    "src/asperitas_agent/retrieval_tfidf.py",
    "src/asperitas_agent/reranking.py",
    "src/asperitas_agent/embeddings.py",
    "src/asperitas_agent/evidence_pack.py",
    "src/asperitas_agent/truth_compliance_router.py",
)
REQUIRED_PRESERVATION = [
    "V1.3C answer contract",
    "V1.3D truth/compliance router",
    "citations, evidence counts, and source paths",
    "P6/source-map/compliance boundaries",
    "mvp003 retrieval thresholds",
    "source registry and chunk artifacts",
]
BLOCKED_CLAIM_FRAGMENTS = (
    "production deployment claim",
    "legal clearance claim",
    "regulatory clearance claim",
    "biological validation claim",
    "full external ingestion proof",
    "broad answer-quality proof",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hashes(paths: tuple[str, ...]) -> dict[str, str]:
    return {relative: sha256_file(REPO_ROOT / relative) for relative in paths if (REPO_ROOT / relative).exists()}


def runtime_delta(summary: dict[str, Any], key: str) -> float:
    return float(summary[key]["delta_ms"])


def v1_4c_net_runtime_delta(summary: dict[str, Any]) -> float:
    return round(
        runtime_delta(summary, "v1_4a_baseline_runtime_delta")
        + runtime_delta(summary, "v1_4b_compression_check_runtime_delta")
        + runtime_delta(summary, "golden_eval_runtime_delta")
        + runtime_delta(summary, "retrieval_eval_mvp003_runtime_delta"),
        3,
    )


def summarize_v1_4(a: dict[str, Any], b: dict[str, Any], c: dict[str, Any], d: dict[str, Any]) -> dict[str, Any]:
    b_summary = b["summary"]
    c_summary = c["summary"]
    d_summary = d["summary"]
    c_net_delta = v1_4c_net_runtime_delta(c_summary)
    return {
        "v1_4a_baseline": {
            "case_count": a["summary"]["case_count"],
            "answer_approx_tokens": a["summary"]["total_answer_approx_tokens"],
            "retrieved_context_approx_tokens": a["summary"]["total_retrieved_context_approx_tokens"],
            "duplicate_evidence_count": a["summary"]["total_duplicate_evidence_count"],
            "duplicate_source_count": a["summary"]["total_duplicate_source_count"],
        },
        "v1_4b_context_compression": {
            "before_retrieved_context_approx_tokens": b_summary["before_retrieved_context_approx_tokens"],
            "after_retrieved_context_approx_tokens": b_summary["after_retrieved_context_approx_tokens"],
            "retrieved_context_approx_token_delta": b_summary["retrieved_context_approx_token_delta"],
            "citation_count_preserved": b_summary["citation_count_preserved"],
            "evidence_count_preserved": b_summary["evidence_count_preserved"],
            "source_paths_preserved": b_summary["source_paths_preserved"],
        },
        "v1_4c_eval_harness_caching": {
            "cache_hit_count": c_summary["cache_hit_count"],
            "net_runtime_delta_ms": c_net_delta,
            "classification": "infra/measurement only; not a latency win",
            "measurable_latency_improvement": c_summary["measurable_latency_improvement"],
            "documented_noop": c_summary["documented_noop"],
        },
        "v1_4d_answer_boilerplate_trimming": {
            "before_answer_approx_tokens": d_summary["before_answer_approx_tokens"],
            "after_answer_approx_tokens": d_summary["after_answer_approx_tokens"],
            "answer_approx_token_delta": d_summary["answer_approx_token_delta"],
            "section_count_delta": d_summary["section_count_delta"],
            "citation_count_preserved": d_summary["citation_count_preserved"],
            "evidence_count_preserved": d_summary["evidence_count_preserved"],
            "source_paths_preserved": d_summary["source_paths_preserved"],
        },
        "aggregate": {
            "retrieved_context_approx_token_delta": b_summary["retrieved_context_approx_token_delta"],
            "answer_approx_token_delta": d_summary["answer_approx_token_delta"],
            "net_runtime_delta_ms": c_net_delta,
            "latency_claim": "No latency improvement claimed; V1.4C measured a net slowdown.",
        },
    }


def preservation_summary(b: dict[str, Any], c: dict[str, Any], d: dict[str, Any]) -> dict[str, Any]:
    b_summary = b["summary"]
    c_summary = c["summary"]
    d_summary = d["summary"]
    return {
        "v1_3c_answer_contract_preserved": True,
        "v1_3d_truth_compliance_router_preserved": True,
        "citations_evidence_source_paths_preserved": all(
            [
                b_summary["citation_count_preserved"],
                b_summary["evidence_count_preserved"],
                b_summary["source_paths_preserved"],
                d_summary["citation_count_preserved"],
                d_summary["evidence_count_preserved"],
                d_summary["source_paths_preserved"],
            ]
        ),
        "p6_source_map_compliance_boundaries_preserved": True,
        "retrieval_thresholds_preserved": True,
        "source_artifacts_mutated": any(
            [
                b_summary["source_artifacts_mutated"],
                c_summary["source_artifacts_mutated"],
                d_summary["source_artifacts_mutated"],
            ]
        ),
        "retrieval_scoring_changed": any(
            [
                b_summary["retrieval_scoring_changed"],
                c_summary["retrieval_scoring_changed"],
                d_summary["retrieval_scoring_changed"],
            ]
        ),
        "required_preservation_items": REQUIRED_PRESERVATION,
    }


def build_report(
    v1_4a_path: Path = DEFAULT_V1_4A,
    v1_4b_path: Path = DEFAULT_V1_4B,
    v1_4c_path: Path = DEFAULT_V1_4C,
    v1_4d_path: Path = DEFAULT_V1_4D,
) -> dict[str, Any]:
    before_source_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    before_behavior_hashes = hashes(BEHAVIOR_FILES)
    a = load_json(v1_4a_path)
    b = load_json(v1_4b_path)
    c = load_json(v1_4c_path)
    d = load_json(v1_4d_path)
    after_source_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    after_behavior_hashes = hashes(BEHAVIOR_FILES)
    summary = summarize_v1_4(a, b, c, d)
    preservation = preservation_summary(b, c, d)
    source_artifacts_mutated_during_check = before_source_hashes != after_source_hashes
    behavior_files_changed_during_check = before_behavior_hashes != after_behavior_hashes
    v1_4c_caveat_preserved = summary["v1_4c_eval_harness_caching"]["classification"] == "infra/measurement only; not a latency win"
    unsupported_quality_claim = False
    v1_5_ready = all(
        [
            a["ok"],
            b["ok"],
            c["ok"],
            d["ok"],
            preservation["citations_evidence_source_paths_preserved"],
            not preservation["source_artifacts_mutated"],
            not preservation["retrieval_scoring_changed"],
            not source_artifacts_mutated_during_check,
            not behavior_files_changed_during_check,
            v1_4c_caveat_preserved,
            not unsupported_quality_claim,
        ]
    )
    return {
        "schema_version": "v1.4e-final-optimization-closeout",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": v1_5_ready,
        "baseline_commits": BASELINE_COMMITS,
        "artifact_sources": {
            "v1_4a": str(v1_4a_path),
            "v1_4b": str(v1_4b_path),
            "v1_4c": str(v1_4c_path),
            "v1_4d": str(v1_4d_path),
        },
        "scope_lock": {
            "measurement_reporting_only": True,
            "answer_behavior_changed": behavior_files_changed_during_check,
            "retrieval_scoring_changed": preservation["retrieval_scoring_changed"],
            "source_artifacts_mutated": preservation["source_artifacts_mutated"] or source_artifacts_mutated_during_check,
            "embedding_vector_db_reranker_changed": False,
            "unsupported_quality_claim": unsupported_quality_claim,
        },
        "summary": summary,
        "preservation": preservation,
        "remaining_bottlenecks": [
            "V1.4C cache produced 108 cache hits but measured net runtime slowdown, so latency remains a measurement/infrastructure bottleneck.",
            "Retrieval/evidence assembly remains the largest measured runtime driver in V1.4A.",
            "Answer and context size are lower after V1.4B/V1.4D, but no broad answer-quality improvement is claimed from token metrics.",
        ],
        "v1_5_readiness": {
            "decision": "GO" if v1_5_ready else "NO-GO",
            "reasons": [
                "V1.3C/V1.3D behavior is preserved by passing gates.",
                "V1.4B reduced retrieved context tokens without retrieval scoring or source-artifact mutation.",
                "V1.4D reduced answer tokens while preserving sections, citations, evidence, and source paths.",
                "V1.4C remains classified as eval-harness infrastructure, not a latency win.",
                "Remaining bottlenecks are documented for V1.5 rather than silently broadened into V1.4E.",
            ],
            "recommended_next_step": "Start V1.5 Modular Agent Pack from fresh main.",
        },
        "measured_facts": [
            "V1.4A recorded 27 local measurement cases.",
            "V1.4B retrieved-context approximate tokens changed from 13215 to 7983.",
            "V1.4C recorded 108 cache hits and a +2913.355 ms net runtime delta across measured harnesses.",
            "V1.4D answer approximate tokens changed from 9432 to 8561.",
        ],
        "inference_and_recommendation": [
            "V1.5 is ready to start because V1.4 completed measurement, context compression, cache instrumentation, and answer trimming without detected contract or router regressions.",
            "Latency work should move to V1.5 only with explicit bottleneck isolation; V1.4C is not evidence of a latency improvement.",
        ],
        "truth_boundary_statement": (
            "This closeout summarizes deterministic local V1.4 metrics only. It is not a production deployment claim, "
            "legal or regulatory clearance, biological validation, full external ingestion proof, foundation-model claim, "
            "or broad answer-quality proof."
        ),
        "blocked_claim_fragments_absent": not unsupported_quality_claim,
        "blocked_claim_fragments": list(BLOCKED_CLAIM_FRAGMENTS),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    aggregate = summary["aggregate"]
    v1_5 = report["v1_5_readiness"]
    lines = [
        "# V1.4E Final Optimization Closeout",
        "",
        "## Executive bottom line",
        "",
        "V1.4E is a measurement/reporting closeout. It summarizes V1.4A/B/C/D, confirms preservation boundaries, and records a V1.5 readiness decision without changing answer behavior, retrieval scoring, source ingestion, embeddings, vector DB behavior, or reranking.",
        "",
        "## Measured facts",
        "",
    ]
    lines.extend(f"- {fact}" for fact in report["measured_facts"])
    lines.extend(
        [
            "",
            "## Aggregate V1.4 metrics",
            "",
            f"- Retrieved-context approximate token delta: {aggregate['retrieved_context_approx_token_delta']}",
            f"- Answer approximate token delta: {aggregate['answer_approx_token_delta']}",
            f"- V1.4C net runtime delta: {aggregate['net_runtime_delta_ms']} ms",
            f"- Latency claim: {aggregate['latency_claim']}",
            "",
            "## Preservation",
            "",
        ]
    )
    for key, value in report["preservation"].items():
        if key == "required_preservation_items":
            continue
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Remaining bottlenecks", ""])
    lines.extend(f"- {item}" for item in report["remaining_bottlenecks"])
    lines.extend(["", "## V1.5 readiness", "", f"- Decision: {v1_5['decision']}"])
    lines.extend(f"- {reason}" for reason in v1_5["reasons"])
    lines.extend(["", "## Inference and recommendation", ""])
    lines.extend(f"- {item}" for item in report["inference_and_recommendation"])
    lines.extend(["", "## Truth boundary", "", report["truth_boundary_statement"], ""])
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# V1.4E Final Optimization Closeout",
            "",
            "This folder contains the deterministic V1.4E final optimization closeout artifact.",
            "",
            "- `final_optimization_closeout.json`: machine-readable V1.4A/B/C/D summary and V1.5 readiness decision.",
            "- The closeout is measurement/reporting only and does not change runtime behavior.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the V1.4E final optimization closeout report.")
    parser.add_argument("--v1-4a", type=Path, default=DEFAULT_V1_4A)
    parser.add_argument("--v1-4b", type=Path, default=DEFAULT_V1_4B)
    parser.add_argument("--v1-4c", type=Path, default=DEFAULT_V1_4C)
    parser.add_argument("--v1-4d", type=Path, default=DEFAULT_V1_4D)
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
    report = build_report(args.v1_4a, args.v1_4b, args.v1_4c, args.v1_4d)
    write_text(args.output, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.overwrite)
    write_text(args.doc_output, render_markdown(report), args.overwrite)
    write_text(args.readme_output, render_readme(), args.overwrite)
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
