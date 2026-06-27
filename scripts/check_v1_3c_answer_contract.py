from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.agent_runner import ask_agent  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_3c_answer_contract" / "answer_contract_baseline.json"
PROTECTED_SOURCE_ARTIFACTS = (
    "data/source_registry.csv",
    "data/chunks.jsonl",
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "eval/retrieval_questions.jsonl",
    "eval/expected_sources.jsonl",
)
RETRIEVAL_FILES = ("src/asperitas_agent/retrieval_mvp003.py",)
CASES = (
    {
        "case_id": "v1_3c_status_truth_boundary",
        "query": "Can we describe the current Asperitas agent as production deployed and biologically validated?",
        "top_k": 5,
        "requires_compliance_gate": False,
    },
    {
        "case_id": "v1_3c_compliance_gate",
        "query": "What approvals are required for CITES Nagoya LMO biosafety actions?",
        "top_k": 5,
        "requires_compliance_gate": True,
    },
    {
        "case_id": "v1_3c_missing_evidence",
        "query": "No evidence available for this local no-corpus evaluation case.",
        "top_k": 5,
        "mode": "empty_corpus",
        "requires_compliance_gate": False,
    },
)
REQUIRED_SECTIONS = (
    "Bottom line:",
    "Missing evidence:",
    "Limitations/truth-boundary:",
    "Next action:",
)
EVIDENCE_SECTIONS = (
    "Source-supported facts:",
    "Key evidence:",
    "Inference:",
)
FORBIDDEN_UNSUPPORTED_CLAIMS = (
    "production-ready",
    "production ready",
    "wet-lab validated",
    "regulatory approval granted",
    "automatically approved",
    "no approval required",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hashes(paths: tuple[str, ...]) -> dict[str, str]:
    return {relative: sha256_file(REPO_ROOT / relative) for relative in paths if (REPO_ROOT / relative).exists()}


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    if case.get("mode") == "empty_corpus":
        response = ask_agent(case["query"], top_k=int(case["top_k"]), records=[], chunks=[]).to_json()
    else:
        response = ask_agent(case["query"], top_k=int(case["top_k"])).to_json()
    answer = response["answer"]
    lower = answer.casefold()
    evidence_count = int(response["evidence_count"])
    required_sections = list(REQUIRED_SECTIONS)
    if evidence_count:
        required_sections.extend(EVIDENCE_SECTIONS)
    checks = {
        "required_sections": all(section in answer for section in required_sections),
        "citation_presence_when_evidence_available": not evidence_count or bool(response["citations_used"]),
        "citations_subset_of_evidence": bool(response["metadata"]["citation_integrity"]["citations_subset_of_evidence"]),
        "no_unsupported_claims": not any(term in lower for term in FORBIDDEN_UNSUPPORTED_CLAIMS),
        "missing_evidence_statement": "Missing evidence:" in answer,
        "next_action_present": "Next action:" in answer,
        "compliance_gate_when_relevant": (
            "Compliance/biosafety/legal gate:" in answer if case["requires_compliance_gate"] else True
        ),
        "generator_version": response["metadata"]["answer_generation"]["generator_version"] == "V1.3C",
    }
    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "status": response["status"],
        "evidence_count": response["evidence_count"],
        "citation_count": len(response["citations_used"]),
        "checks": checks,
        "ok": all(checks.values()),
    }


def build_report() -> dict[str, Any]:
    before_artifact_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    before_retrieval_hashes = hashes(RETRIEVAL_FILES)
    cases = [run_case(case) for case in CASES]
    after_artifact_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    after_retrieval_hashes = hashes(RETRIEVAL_FILES)
    summary = {
        "case_count": len(cases),
        "passed_case_count": sum(1 for case in cases if case["ok"]),
        "cases_with_citations_when_evidence_available": sum(
            1
            for case in cases
            if case["evidence_count"] == 0 or case["checks"]["citation_presence_when_evidence_available"]
        ),
        "cases_with_missing_evidence_statement": sum(1 for case in cases if case["checks"]["missing_evidence_statement"]),
        "cases_with_next_action": sum(1 for case in cases if case["checks"]["next_action_present"]),
    }
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    source_artifacts_mutated = before_artifact_hashes != after_artifact_hashes
    return {
        "schema_version": "v1.3c-answer-contract",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": all(case["ok"] for case in cases) and not retrieval_scoring_changed and not source_artifacts_mutated,
        "summary": summary,
        "cases": cases,
        "answer_contract_behavior": [
            "bottom line first",
            "source-supported facts with citations",
            "cited evidence excerpt list",
            "bounded inference label",
            "missing evidence statement",
            "limitations/truth-boundary",
            "next action",
            "compliance/biosafety/legal gate when relevant",
        ],
        "retrieval_scoring_changed": retrieval_scoring_changed,
        "source_artifacts_mutated": source_artifacts_mutated,
        "truth_boundary_statement": (
            "This check validates deterministic answer contract structure only. It is not answer-quality proof, "
            "deployment evidence, legal clearance, regulatory clearance, biological validation, or wet-lab capability."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check V1.3C deterministic answer contract behavior.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report()
    if args.output:
        if args.output.exists() and not args.overwrite:
            raise SystemExit(f"output exists; pass --overwrite: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=None if args.json else 2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
