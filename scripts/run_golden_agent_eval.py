from __future__ import annotations

import argparse
import hashlib
import json
import re
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

from asperitas_agent.agent_runner import ask_agent  # noqa: E402
from asperitas_agent.failure_taxonomy import classify_failure  # noqa: E402
from eval_harness_cache import load_jsonl_cached, read_chunks_cached, read_registry_cached  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_GOLDEN_FILE = REPO_ROOT / "eval" / "golden_agent_queries.jsonl"
ALLOWED_STATUSES = {"answered", "caution", "abstained"}
PRIORITY_RANKS = {f"P{index}": index for index in range(7)}
REQUIRED_FIELDS = {
    "id",
    "category",
    "query",
    "top_k",
    "expected_status",
    "min_evidence_count",
    "min_citation_count",
    "required_answer_substrings",
    "forbidden_answer_substrings",
}
PROTECTED_PATHS = (
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "eval/retrieval_questions.jsonl",
    "eval/expected_sources.jsonl",
    "eval/golden_agent_queries.jsonl",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_file_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in PROTECTED_PATHS:
        path = REPO_ROOT / relative
        if path.exists():
            hashes[relative] = sha256_file(path)
    return hashes


def load_golden_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"golden query file not found: {path}")

    cases = load_jsonl_cached(path)
    seen_ids: set[str] = set()
    for line_number, record in enumerate(cases, start=1):
        missing = sorted(REQUIRED_FIELDS - set(record))
        if missing:
            raise ValueError(f"{path}:{line_number}: missing required fields: {', '.join(missing)}")
        case_id = record.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{path}:{line_number}: id must be a non-empty string")
        if case_id in seen_ids:
            raise ValueError(f"{path}:{line_number}: duplicate id: {case_id}")
        seen_ids.add(case_id)
    if not 5 <= len(cases) <= 8:
        raise ValueError(f"golden query file must contain 5 to 8 cases, found {len(cases)}")
    return cases


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def run_agent_for_case(case: dict[str, Any]) -> dict[str, Any]:
    query = str(case["query"])
    top_k = int(case["top_k"])
    mode = case.get("mode", "default")
    if mode == "empty_corpus":
        return ask_agent(query, top_k=top_k, records=[], chunks=[]).to_json()
    if mode not in ("default", "", None):
        raise ValueError(f"{case['id']}: unsupported mode: {mode}")
    return ask_agent(
        query,
        top_k=top_k,
        records=read_registry_cached(REPO_ROOT / "data" / "source_registry.csv"),
        chunks=read_chunks_cached(REPO_ROOT / "data" / "chunks.jsonl"),
    ).to_json()


def _contains_all(text: str, needles: list[Any]) -> bool:
    lowered = text.casefold()
    return all(str(needle).casefold() in lowered for needle in needles)


def _contains_none(text: str, needles: list[Any]) -> bool:
    lowered = text.casefold()
    return all(str(needle).casefold() not in lowered for needle in needles)


def _schema_ok(payload: dict[str, Any]) -> bool:
    required_types: dict[str, type] = {
        "query": str,
        "top_k": int,
        "status": str,
        "answer": str,
        "citations_used": list,
        "evidence_count": int,
        "evidence": list,
        "guardrail": dict,
        "metadata": dict,
    }
    for field, expected_type in required_types.items():
        if not isinstance(payload.get(field), expected_type):
            return False
    if payload["evidence_count"] != len(payload["evidence"]):
        return False
    for item in payload["evidence"]:
        if not isinstance(item, dict):
            return False
        for field in ("rank", "chunk_id", "source_id", "source_path", "citation_key", "text_excerpt"):
            if field not in item:
                return False
    return payload["status"] in ALLOWED_STATUSES


def _citation_subset_ok(payload: dict[str, Any]) -> bool:
    evidence_keys = {item.get("citation_key") for item in payload.get("evidence", []) if isinstance(item, dict)}
    evidence_keys.discard(None)
    citation_pattern = re.compile(r"^\[E\d+\]$")
    for citation in payload.get("citations_used", []):
        if not isinstance(citation, str) or not citation_pattern.match(citation) or citation not in evidence_keys:
            return False
    answer_markers = set(re.findall(r"\[E\d+\]", payload.get("answer", "")))
    return answer_markers <= evidence_keys


def _metadata_citation_integrity_ok(payload: dict[str, Any]) -> bool:
    integrity = payload.get("metadata", {}).get("citation_integrity", {})
    value = integrity.get("citations_subset_of_evidence")
    return value is True or value is None


def _required_labels_ok(case: dict[str, Any], payload: dict[str, Any]) -> bool:
    required = set(case.get("required_evidence_labels", []))
    if not required:
        return True
    present = {item.get("evidence_label") for item in payload.get("evidence", []) if isinstance(item, dict)}
    return required <= present


def _source_priority_ok(case: dict[str, Any], payload: dict[str, Any]) -> bool:
    max_priority = case.get("required_source_priority_max")
    if not max_priority:
        return True
    max_rank = PRIORITY_RANKS.get(str(max_priority))
    if max_rank is None:
        return False
    priorities = [item.get("source_priority") for item in payload.get("evidence", []) if isinstance(item, dict)]
    if not priorities:
        return False
    ranks = [PRIORITY_RANKS.get(str(priority), 999) for priority in priorities]
    return all(rank <= max_rank for rank in ranks)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    first = run_agent_for_case(case)
    second = run_agent_for_case(case)
    guardrail = first.get("guardrail", {})
    expected_guardrail = case.get("expected_guardrail_decision")
    checks = {
        "schema": _schema_ok(first),
        "status": first.get("status") == case.get("expected_status"),
        "guardrail": True if expected_guardrail in (None, "") else guardrail.get("decision") == expected_guardrail,
        "evidence_count": first.get("evidence_count", -1) >= int(case.get("min_evidence_count", 0)),
        "citation_count": len(first.get("citations_used", [])) >= int(case.get("min_citation_count", 0)),
        "citation_subset_integrity": _citation_subset_ok(first) and _metadata_citation_integrity_ok(first),
        "required_answer_substrings": _contains_all(first.get("answer", ""), case.get("required_answer_substrings", [])),
        "forbidden_answer_substrings": _contains_none(first.get("answer", ""), case.get("forbidden_answer_substrings", [])),
        "required_evidence_labels": _required_labels_ok(case, first),
        "source_priority": _source_priority_ok(case, first),
        "determinism": _json_dumps(first) == _json_dumps(second),
    }
    failures = [name for name, ok in checks.items() if not ok]
    report = {
        "id": case["id"],
        "category": case["category"],
        "ok": not failures,
        "query": case["query"],
        "status": first.get("status"),
        "expected_status": case.get("expected_status"),
        "guardrail_decision": guardrail.get("decision"),
        "expected_guardrail_decision": expected_guardrail,
        "evidence_count": first.get("evidence_count"),
        "citation_count": len(first.get("citations_used", [])),
        "checks": checks,
        "failures": failures,
    }
    if failures:
        report["failure_category"] = classify_failure(report)
    return report


def evaluate_golden_queries(golden_file: Path = DEFAULT_GOLDEN_FILE) -> dict[str, Any]:
    before_hashes = protected_file_hashes()
    cases = load_golden_cases(golden_file)
    case_reports = [evaluate_case(case) for case in cases]
    after_hashes = protected_file_hashes()
    protected_ok = before_hashes == after_hashes
    passed = sum(1 for case in case_reports if case["ok"])
    return {
        "ok": protected_ok and passed == len(case_reports),
        "total_cases": len(case_reports),
        "passed_cases": passed,
        "failed_cases": len(case_reports) - passed,
        "protected_files_unchanged": protected_ok,
        "protected_files": sorted(before_hashes),
        "golden_file": str(golden_file.relative_to(REPO_ROOT)) if golden_file.is_relative_to(REPO_ROOT) else str(golden_file),
        "cases": case_reports,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MVP-010 golden agent answer-quality regression checks.")
    parser.add_argument("--golden-file", type=Path, default=DEFAULT_GOLDEN_FILE)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = evaluate_golden_queries(args.golden_file)
    except (FileNotFoundError, ValueError) as exc:
        report = {
            "ok": False,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "protected_files_unchanged": False,
            "error": str(exc),
            "cases": [],
        }
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
