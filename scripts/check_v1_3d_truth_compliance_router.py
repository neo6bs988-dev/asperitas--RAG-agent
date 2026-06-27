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

from asperitas_agent.answer_generation import generate_grounded_answer  # noqa: E402
from asperitas_agent.evidence_pack import build_evidence_pack  # noqa: E402
from asperitas_agent.guardrails import evaluate_evidence_guardrail  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_OUTPUT = REPO_ROOT / "eval_results" / "v1_3d_truth_compliance_router" / "truth_compliance_router_baseline.json"
PROTECTED_SOURCE_ARTIFACTS = (
    "data/source_registry.csv",
    "data/chunks.jsonl",
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "eval/retrieval_questions.jsonl",
    "eval/expected_sources.jsonl",
)
RETRIEVAL_FILES = ("src/asperitas_agent/retrieval_mvp003.py",)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hashes(paths: tuple[str, ...]) -> dict[str, str]:
    return {relative: sha256_file(REPO_ROOT / relative) for relative in paths if (REPO_ROOT / relative).exists()}


def result(rank: int, source_id: str, priority: str, path: str, text: str, label: str) -> dict[str, Any]:
    return {
        "chunk_id": f"{source_id}::chunk-{rank:04d}",
        "score": 100 - rank,
        "source_id": source_id,
        "source_title": Path(path).name,
        "source_path": path,
        "source_priority": priority,
        "evidence_label": label,
        "section": "V1.3D Router",
        "section_heading": "V1.3D Router",
        "section_path": ["V1.3D Router"],
        "text": text,
    }


CASES = (
    {
        "case_id": "v1_3d_internal_fact_status_boundary",
        "query": "Is Asperitas production deployed and biologically validated?",
        "results": [
            result(1, "ASP-P1", "P1", "docs/V1_KNOWN_LIMITATIONS.md", "Internal release candidate evidence only.", "Document-Supported Fact")
        ],
        "required": ("does not establish production deployment",),
        "forbidden": ("production-ready", "wet-lab validated"),
    },
    {
        "case_id": "v1_3d_p6_analogy_doctrine_only",
        "query": "Give a founder/operator benchmark comparison for Asperitas.",
        "results": [
            result(1, "ASP-P1", "P1", "docs/ops/GSTACK_OPERATING_STACK.md", "Internal docs describe local operating boundaries.", "Document-Supported Fact"),
            result(2, "ASP-P6", "P6", "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/bench.md", "P6 benchmark doctrine only.", "Inference"),
        ],
        "required": ("P6 benchmark analogy/doctrine:", "cannot override P0-P4/internal evidence", "analogy-only"),
    },
    {
        "case_id": "v1_3d_compliance_human_review_gate",
        "query": "What legal approvals are required for CITES Nagoya LMO biosafety actions?",
        "results": [
            result(1, "ASP-P1", "P1", "04_AGENT_SYSTEM/guardrails/biosafety_compliance_checklist.md", "CITES Nagoya LMO biosafety actions require human approval.", "Document-Supported Fact")
        ],
        "required": ("Compliance/biosafety/legal gate:", "Human review is required"),
    },
    {
        "case_id": "v1_3d_missing_evidence_abstention",
        "query": "No evidence available for this local no-corpus router case.",
        "results": [],
        "required": ("cannot answer from the retrieved evidence", "Missing evidence: no retrieved evidence supports"),
        "expected_status": "abstained",
    },
    {
        "case_id": "v1_3d_source_map_only_evidence_risk",
        "query": "Can a source-map-only URL be cited as ingested evidence?",
        "results": [
            result(1, "ASP-P6-URL", "P6", "https://example.com/source-map-only", "source_mapped_not_ingested external URL metadata", "Needs External Verification")
        ],
        "required": ("Source-map-only URLs are not cited as ingested evidence",),
        "expected_citations": 0,
    },
    {
        "case_id": "v1_3d_production_vector_db_claim_risk",
        "query": "Is external web ingestion complete with production vector DB indexed?",
        "results": [
            result(1, "ASP-P6", "P6", "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/bench.md", "Offline deterministic benchmark vector artifacts are not a production vector DB.", "Inference")
        ],
        "required": ("DB-completion or external-ingestion claims are refused", "Truth/compliance router:"),
    },
)


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    pack = build_evidence_pack(case["query"], case["results"], top_k=len(case["results"]) or 5)
    answer = generate_grounded_answer(pack, evaluate_evidence_guardrail(pack)).to_json()
    text = answer["answer_text"]
    lower = text.casefold()
    checks = {
        "required_text": all(term in text for term in case.get("required", ())),
        "forbidden_text_absent": not any(term in lower for term in case.get("forbidden", ())),
        "expected_status": answer["answer_status"] == case.get("expected_status", answer["answer_status"]),
        "expected_citations": len(answer["citations_used"]) == case.get("expected_citations", len(answer["citations_used"])),
        "generator_contract_preserved": answer["metadata"]["generator_version"] == "V1.3C",
    }
    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "status": answer["answer_status"],
        "citation_count": len(answer["citations_used"]),
        "checks": checks,
        "ok": all(checks.values()),
    }


def build_report() -> dict[str, Any]:
    before_artifact_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    before_retrieval_hashes = hashes(RETRIEVAL_FILES)
    cases = [run_case(case) for case in CASES]
    after_artifact_hashes = hashes(PROTECTED_SOURCE_ARTIFACTS)
    after_retrieval_hashes = hashes(RETRIEVAL_FILES)
    retrieval_scoring_changed = before_retrieval_hashes != after_retrieval_hashes
    source_artifacts_mutated = before_artifact_hashes != after_artifact_hashes
    return {
        "schema_version": "v1.3d-truth-compliance-router",
        "created_at_utc": "1970-01-01T00:00:00Z",
        "ok": all(case["ok"] for case in cases) and not retrieval_scoring_changed and not source_artifacts_mutated,
        "summary": {
            "case_count": len(cases),
            "passed_case_count": sum(1 for case in cases if case["ok"]),
            "router_cases": [case["case_id"] for case in cases],
        },
        "cases": cases,
        "router_behavior": [
            "internal factual answers remain bounded by retrieved evidence",
            "P6 benchmark material is analogy/doctrine only",
            "source-map-only URLs are not citation-eligible as ingested evidence",
            "missing evidence triggers abstention",
            "compliance/biosafety/legal questions carry a human-review gate",
            "production, deployment, vector-DB, external-ingestion, legal, regulatory, wet-lab, and foundation-model completion claims require evidence",
        ],
        "retrieval_scoring_changed": retrieval_scoring_changed,
        "source_artifacts_mutated": source_artifacts_mutated,
        "truth_boundary_statement": (
            "This check validates deterministic router behavior only. It does not prove legal clearance, regulatory clearance, "
            "production deployment, wet-lab validation, full source ingestion, or answer quality beyond these fixtures."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check V1.3D truth/compliance router behavior.")
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
