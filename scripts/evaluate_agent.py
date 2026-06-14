from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.agent_runner import ask_agent  # noqa: E402
from asperitas_agent.failure_taxonomy import classify_failure  # noqa: E402


ALLOWED_STATUSES = {"answered", "caution", "abstained"}
FORBIDDEN_REFERENCES = (
    "openai",
    "anthropic",
    "google.generativeai",
    "chromadb",
    "faiss",
    "pinecone",
    "weaviate",
    "qdrant",
    "langchain",
    "llama_index",
    "streamlit",
    "flask",
    "fastapi",
    "uvicorn",
)
ANTI_CHEATING_PATTERNS = (
    r"\bpytest\b",
    r"PYTEST_CURRENT_TEST",
    r"GITHUB_ACTIONS",
    r"\bCI\b",
    r"test_[A-Za-z0-9_]+\.py",
    r"if\s+.+query\s*(==|in)\s*['\"]",
)
PROTECTED_PATHS = (
    "data/chunks.jsonl",
    "data/source_registry.csv",
    "00_ADMIN/source_registry.csv",
    "00_ADMIN/source_registry.jsonl",
    "eval/retrieval_questions.jsonl",
    "eval/expected_sources.jsonl",
    "03_PROCESSED_KB/chunks/source_chunks.jsonl",
    "03_PROCESSED_KB/chunks/source_chunks_manifest.json",
)
RUNTIME_SCRIPT_NAMES = {
    "ask_agent.py",
    "build_evidence_pack.py",
    "check_evidence_guardrail.py",
    "generate_grounded_answer.py",
}
MVP003_TARGET_SOURCE = "docs/MVP_003_RETRIEVAL_IMPROVEMENT_PLAN.md"
MVP003_THRESHOLD_PATTERNS = {
    "source_file_match_at_3": r"Source@3\s*>=\s*(\d+)%",
    "source_file_match_at_5": r"Source@5\s*>=\s*(\d+)%",
    "section_match": r"Section match\s*>=\s*(\d+)%",
    "overall_pass_rate": r"Overall pass rate\s*>=\s*(\d+)%",
}


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    query: str
    top_k: int
    expected_status: str
    mode: str = "real_agent"


EVAL_CASES = (
    EvalCase(
        case_id="normal_grounded_answer",
        query="What is the exact wet-lab validation status of the production vector DB?",
        top_k=5,
        expected_status="answered",
    ),
    EvalCase(case_id="caution_answer", query="What is Asperitas?", top_k=5, expected_status="caution"),
    EvalCase(
        case_id="abstention_no_evidence",
        query="No evidence available for this local no-corpus evaluation case.",
        top_k=5,
        expected_status="abstained",
        mode="empty_corpus",
    ),
)


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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


def run_ask_agent_cli(query: str, top_k: int, pretty: bool = False) -> dict[str, Any]:
    command = [sys.executable, str(REPO_ROOT / "scripts" / "ask_agent.py"), "--query", query, "--top-k", str(top_k)]
    if pretty:
        command.append("--pretty")
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ask_agent.py failed with code {result.returncode}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def validate_agent_response_schema(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
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
        if field not in payload:
            errors.append(f"missing field: {field}")
        elif not isinstance(payload[field], expected_type):
            errors.append(f"field {field} has wrong type: {type(payload[field]).__name__}")

    if "evidence" in payload and "evidence_count" in payload and len(payload["evidence"]) != payload["evidence_count"]:
        errors.append("evidence_count does not match evidence length")

    for index, item in enumerate(payload.get("evidence", []), start=1):
        if not isinstance(item, dict):
            errors.append(f"evidence item {index} is not an object")
            continue
        for field in ("rank", "chunk_id", "source_id", "source_path", "citation_key", "text_excerpt"):
            if field not in item:
                errors.append(f"evidence item {index} missing field: {field}")
    return errors


def validate_status(payload: dict[str, Any]) -> list[str]:
    status = payload.get("status")
    return [] if status in ALLOWED_STATUSES else [f"invalid status: {status}"]


def validate_citations(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_keys = {item.get("citation_key") for item in payload.get("evidence", []) if isinstance(item, dict)}
    evidence_keys.discard(None)
    citation_pattern = re.compile(r"^\[E\d+\]$")

    for citation in payload.get("citations_used", []):
        if not isinstance(citation, str) or not citation_pattern.match(citation):
            errors.append(f"malformed citation: {citation}")
        elif citation not in evidence_keys:
            errors.append(f"dangling citation: {citation}")

    answer_markers = set(re.findall(r"\[E\d+\]", payload.get("answer", "")))
    for marker in sorted(answer_markers):
        if marker not in evidence_keys:
            errors.append(f"answer marker has no evidence item: {marker}")

    if payload.get("status") == "abstained":
        if payload.get("citations_used"):
            errors.append("abstained response must not cite unavailable evidence")
        if answer_markers:
            errors.append("abstained response must not include evidence markers")
    return errors


def validate_guardrail(case: EvalCase, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    guardrail = payload.get("guardrail", {})
    if not isinstance(guardrail, dict):
        return ["guardrail must be an object"]
    if payload.get("status") != case.expected_status:
        errors.append(f"{case.case_id} expected {case.expected_status}, got {payload.get('status')}")
    if case.expected_status == "abstained" and not guardrail.get("should_abstain"):
        errors.append("abstention case did not preserve guardrail abstention")
    if case.expected_status == "caution" and guardrail.get("decision") != "caution":
        errors.append("caution case did not preserve guardrail caution")
    return errors


def run_case(case: EvalCase) -> tuple[dict[str, Any], list[str]]:
    if case.mode == "empty_corpus":
        payload = ask_agent(case.query, top_k=case.top_k, records=[], chunks=[]).to_json()
    else:
        payload = ask_agent(case.query, top_k=case.top_k).to_json()
    errors = []
    errors.extend(validate_agent_response_schema(payload))
    errors.extend(validate_status(payload))
    errors.extend(validate_citations(payload))
    errors.extend(validate_guardrail(case, payload))
    return payload, errors


def run_cases() -> tuple[list[dict[str, Any]], dict[str, bool]]:
    case_reports: list[dict[str, Any]] = []
    schema_ok = True
    status_ok = True
    citations_ok = True
    guardrails_ok = True

    for case in EVAL_CASES:
        payload, errors = run_case(case)
        schema_errors = validate_agent_response_schema(payload)
        status_errors = validate_status(payload)
        citation_errors = validate_citations(payload)
        guardrail_errors = validate_guardrail(case, payload)
        schema_ok = schema_ok and not schema_errors
        status_ok = status_ok and not status_errors
        citations_ok = citations_ok and not citation_errors
        guardrails_ok = guardrails_ok and not guardrail_errors
        report_checks = {
            "schema": not schema_errors,
            "status": not status_errors,
            "citations": not citation_errors,
            "guardrails": not guardrail_errors,
        }
        report = {
            "case_id": case.case_id,
            "status": payload.get("status"),
            "expected_status": case.expected_status,
            "evidence_count": payload.get("evidence_count"),
            "citations_used": payload.get("citations_used", []),
            "ok": not errors,
            "errors": errors,
            "checks": report_checks,
        }
        if errors:
            report["failure_category"] = classify_failure(report)
        case_reports.append(report)
    return case_reports, {"schema": schema_ok, "status": status_ok, "citations": citations_ok, "guardrails": guardrails_ok}


def check_json_output() -> bool:
    payload = run_ask_agent_cli("What is Asperitas?", 5, pretty=False)
    pretty_payload = run_ask_agent_cli("What is Asperitas?", 5, pretty=True)
    return payload == pretty_payload and isinstance(payload, dict)


def check_determinism() -> bool:
    first = run_ask_agent_cli("What is Asperitas?", 5, pretty=False)
    second = run_ask_agent_cli("What is Asperitas?", 5, pretty=False)
    return _json_dumps(first) == _json_dumps(second)


def _python_files_for_static_scan() -> list[Path]:
    files = list((REPO_ROOT / "src").rglob("*.py"))
    files.extend(path for path in (REPO_ROOT / "scripts").glob("*.py") if path.name in RUNTIME_SCRIPT_NAMES)
    return sorted(files)


def scan_forbidden_references() -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    patterns = [(needle, re.compile(re.escape(needle), re.IGNORECASE)) for needle in FORBIDDEN_REFERENCES]
    for path in _python_files_for_static_scan():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for needle, pattern in patterns:
                if pattern.search(line):
                    matches.append({"path": str(path.relative_to(REPO_ROOT)), "line": line_number, "match": needle})
    return matches


def scan_anti_cheating() -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    patterns = [(source, re.compile(source, re.IGNORECASE)) for source in ANTI_CHEATING_PATTERNS]
    for path in _python_files_for_static_scan():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for source, pattern in patterns:
                if pattern.search(line):
                    matches.append({"path": str(path.relative_to(REPO_ROOT)), "line": line_number, "pattern": source})
    return matches


def _run_retrieval_eval(retriever: str) -> dict[str, Any]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_retrieval_eval.py"),
        "--retriever",
        retriever,
        "--json",
    ]
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    summary: dict[str, Any] = {}
    parse_error = ""
    if result.stdout.strip():
        try:
            summary = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
    return {
        "command": f"python scripts/run_retrieval_eval.py --retriever {retriever} --json",
        "returncode": result.returncode,
        "metrics": {
            "source_file_match_at_3": summary.get("source_file_match_at_3"),
            "source_file_match_at_5": summary.get("source_file_match_at_5"),
            "source_priority_match": summary.get("source_priority_match"),
            "evidence_label_match": summary.get("evidence_label_match"),
            "section_match": summary.get("section_match"),
            "overall_pass_rate": summary.get("overall_pass_rate"),
        },
        "stdout_parse_error": parse_error,
        "stderr": result.stderr.strip(),
    }


def load_mvp003_thresholds() -> tuple[dict[str, float], str]:
    path = REPO_ROOT / MVP003_TARGET_SOURCE
    text = path.read_text(encoding="utf-8")
    thresholds: dict[str, float] = {}
    for key, pattern in MVP003_THRESHOLD_PATTERNS.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            thresholds[key] = int(match.group(1)) / 100
    return thresholds, MVP003_TARGET_SOURCE


def run_retrieval_regression() -> dict[str, Any]:
    baseline = _run_retrieval_eval("baseline")
    mvp003 = _run_retrieval_eval("mvp003")
    thresholds, threshold_source = load_mvp003_thresholds()
    failures: list[str] = []

    if baseline["returncode"] != 0:
        failures.append("baseline retrieval command failed")
    if mvp003["returncode"] != 0:
        failures.append("mvp003 retrieval command failed")
    if baseline["stdout_parse_error"]:
        failures.append(f"baseline output was not parseable JSON: {baseline['stdout_parse_error']}")
    if mvp003["stdout_parse_error"]:
        failures.append(f"mvp003 output was not parseable JSON: {mvp003['stdout_parse_error']}")
    if not thresholds:
        failures.append(f"no MVP-003 thresholds parsed from {threshold_source}")

    for metric, threshold in thresholds.items():
        value = mvp003["metrics"].get(metric)
        if not isinstance(value, (int, float)):
            failures.append(f"mvp003 metric missing or invalid: {metric}")
        elif value < threshold:
            failures.append(f"mvp003 {metric} {value:.3f} below threshold {threshold:.3f}")

    base_overall = baseline["metrics"].get("overall_pass_rate")
    mvp003_overall = mvp003["metrics"].get("overall_pass_rate")
    if isinstance(base_overall, (int, float)) and isinstance(mvp003_overall, (int, float)) and mvp003_overall < base_overall:
        failures.append("mvp003 overall pass rate is below baseline overall pass rate")

    return {
        "ok": not failures,
        "pass_fail_reason": "passed official MVP-003 command thresholds" if not failures else "; ".join(failures),
        "baseline": baseline,
        "mvp003": mvp003,
        "thresholds": thresholds,
        "threshold_source": threshold_source,
    }


def evaluate_agent() -> dict[str, Any]:
    before_hashes = protected_file_hashes()
    case_reports, case_checks = run_cases()
    json_output_ok = check_json_output()
    determinism_ok = check_determinism()
    forbidden_matches = scan_forbidden_references()
    anti_cheating_matches = scan_anti_cheating()
    retrieval_report = run_retrieval_regression()
    after_hashes = protected_file_hashes()
    protected_ok = before_hashes == after_hashes

    checks = {
        "json_output": json_output_ok,
        "schema": case_checks["schema"],
        "status": case_checks["status"],
        "citations": case_checks["citations"],
        "guardrails": case_checks["guardrails"],
        "determinism": determinism_ok,
        "protected_files_unchanged": protected_ok,
        "forbidden_imports": not forbidden_matches,
        "anti_cheating": not anti_cheating_matches,
        "retrieval_regression_unchanged": retrieval_report["ok"],
    }
    passed_cases = sum(1 for case in case_reports if case["ok"])
    return {
        "ok": all(checks.values()) and passed_cases == len(case_reports),
        "total_cases": len(case_reports),
        "passed_cases": passed_cases,
        "failed_cases": len(case_reports) - passed_cases,
        "checks": checks,
        "cases": case_reports,
        "protected_files": sorted(before_hashes),
        "static_scan": {
            "forbidden_matches": forbidden_matches,
            "anti_cheating_matches": anti_cheating_matches,
        },
        "retrieval_regression": {
            "command_checked": retrieval_report["mvp003"]["command"],
            "baseline_command_checked": retrieval_report["baseline"]["command"],
            "pass_fail_reason": retrieval_report["pass_fail_reason"],
            "threshold_source": retrieval_report["threshold_source"],
            "thresholds": retrieval_report["thresholds"],
            "baseline": retrieval_report["baseline"],
            "mvp003": retrieval_report["mvp003"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MVP-009 deterministic end-to-end agent evaluation.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = evaluate_agent()
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
