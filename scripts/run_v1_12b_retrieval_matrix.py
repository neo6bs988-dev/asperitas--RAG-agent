from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "v1.12b-retrieval-matrix-v1"
MODE_SPECS = (
    ("baseline", "baseline", "none", "direct", False),
    ("mvp003", "mvp003", "none", "direct", False),
    ("vector", "vector", "none", "direct", False),
    ("legacy-hybrid", "hybrid", "none", "direct", True),
    ("legacy-hybrid+deterministic-test", "hybrid", "deterministic-test", "direct", True),
    ("legacy-hybrid+deterministic-test+fail-closed", "hybrid", "deterministic-test", "fail-closed", True),
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=True
    )
    return completed.stdout.strip()


def mode_names() -> tuple[str, ...]:
    return tuple(spec[0] for spec in MODE_SPECS)


def build_command(spec: tuple[str, str, str, str, bool], args: argparse.Namespace) -> list[str]:
    _name, retriever, reranker, policy, _oracle_affected = spec
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_retrieval_eval.py"),
        "--retriever",
        retriever,
        "--reranker",
        reranker,
        "--reranker-policy",
        policy,
        "--limit",
        str(args.limit),
        "--json",
    ]
    if args.measure_diagnostics:
        command.append("--measure-diagnostics")
    return command


def mode_record(spec: tuple[str, str, str, str, bool], args: argparse.Namespace) -> dict[str, Any]:
    name, _retriever, _reranker, _policy, oracle_affected = spec
    blockers = ["oracle_affected_legacy_hybrid"] if oracle_affected else []
    started = utc_now()
    completed = subprocess.run(
        build_command(spec, args),
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=args.timeout_seconds,
    )
    record: dict[str, Any] = {
        "mode": name,
        "status": "failed",
        "promotion_eligible": False,
        "promotion_blockers": blockers,
        "query_count": 0,
        "successful_query_count": 0,
        "failed_query_count": 0,
        "metrics": {},
        "latency_ms": {},
        "errors": [],
        "questions": [],
        "started_at_utc": started,
        "completed_at_utc": utc_now(),
    }
    if completed.returncode:
        record["errors"] = [completed.stderr.strip() or f"exit_code={completed.returncode}"]
        return record
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        record["errors"] = [f"invalid evaluation JSON: {exc}"]
        return record
    questions = payload.get("per_question", [])
    record.update(
        {
            "status": "non_promotable" if oracle_affected else "passed",
            "query_count": payload.get("total_questions", 0),
            "successful_query_count": len(questions),
            "metrics": {key: value for key, value in payload.items() if key not in {"per_question", "diagnostics"}},
            "latency_ms": payload.get("diagnostics", {}).get("retrieval_latency_ms", {}),
            "questions": questions,
        }
    )
    return record


def write_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    temporary_path.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the V1.12B retrieval comparison matrix.")
    parser.add_argument("--mode", choices=mode_names(), action="append", help="Run only this named mode; repeatable.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--measure-diagnostics", action="store_true")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON output path; atomically replaced.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selected = set(args.mode or mode_names())
    specs = [spec for spec in MODE_SPECS if spec[0] in selected]
    started = utc_now()
    records: list[dict[str, Any]] = []
    for spec in specs:
        try:
            records.append(mode_record(spec, args))
        except subprocess.TimeoutExpired:
            records.append({"mode": spec[0], "status": "failed", "promotion_eligible": False, "promotion_blockers": ["timeout"], "query_count": 0, "successful_query_count": 0, "failed_query_count": 0, "metrics": {}, "latency_ms": {}, "errors": ["timeout"], "questions": [], "started_at_utc": utc_now(), "completed_at_utc": utc_now()})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run": {
            "commit_sha": git_value("rev-parse", "HEAD"),
            "worktree_dirty": bool(git_value("status", "--porcelain")),
            "python_version": sys.version.split()[0],
            "fixture_path": "eval/retrieval_questions.jsonl",
            "expected_sources_path": "eval/expected_sources.jsonl",
            "query_count": records[0]["query_count"] if records else 0,
            "started_at_utc": started,
            "completed_at_utc": utc_now(),
        },
        "modes": records,
    }
    if args.output:
        write_json_atomically(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all(record["status"] in {"passed", "non_promotable"} for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
