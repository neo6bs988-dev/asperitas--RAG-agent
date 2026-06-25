from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from asperitas_agent.failure_log import (  # noqa: E402
    FAILURE_CATEGORIES,
    FAILURE_SEVERITIES,
    FAILURE_STATUSES,
    build_failure_record,
    failure_record_to_dict,
    write_failure_jsonl,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record one V1.1A failure log JSON record.")
    parser.add_argument("--query", required=True, help="Question or request that exposed the failure")
    parser.add_argument("--expected-behavior", required=True, help="Expected behavior")
    parser.add_argument("--actual-behavior", required=True, help="Observed behavior")
    parser.add_argument("--category", required=True, choices=FAILURE_CATEGORIES, help="Failure category")
    parser.add_argument("--severity", required=True, choices=FAILURE_SEVERITIES, help="Failure severity")
    parser.add_argument("--status", default="open", choices=FAILURE_STATUSES, help="Failure status")
    parser.add_argument("--created-at-utc", default="1970-01-01T00:00:00Z", help="UTC timestamp for deterministic id")
    parser.add_argument("--session-id", default="local_failure_session", help="Session id for deterministic id")
    parser.add_argument("--source-context-json", default="{}", help="JSON object with source/citation context")
    parser.add_argument("--security-result-json", default="{}", help="JSON object with security result context")
    parser.add_argument("--workflow-result-json", default="{}", help="JSON object with workflow result context")
    parser.add_argument("--dry-run-result-json", default="{}", help="JSON object with dry-run result context")
    parser.add_argument("--reproduction-step", action="append", default=[], help="Repeatable reproduction step")
    parser.add_argument("--proposed-fix", default="", help="Candidate fix or investigation path")
    parser.add_argument("--redaction-notes", default="", help="What was removed or must be redacted")
    parser.add_argument("--metadata-json", default="{}", help="JSON object with extra metadata")
    parser.add_argument("--output", help="Explicit JSONL output path")
    parser.add_argument("--append", action="store_true", help="Append to an existing JSONL file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Print the JSON record")
    return parser.parse_args(argv)


def _json_object(value: str, name: str) -> dict:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError(f"{name} must be a JSON object")
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        record = build_failure_record(
            query=args.query,
            expected_behavior=args.expected_behavior,
            actual_behavior=args.actual_behavior,
            category=args.category,
            severity=args.severity,
            status=args.status,
            created_at_utc=args.created_at_utc,
            session_id=args.session_id,
            source_context=_json_object(args.source_context_json, "--source-context-json"),
            security_result=_json_object(args.security_result_json, "--security-result-json"),
            workflow_result=_json_object(args.workflow_result_json, "--workflow-result-json"),
            dry_run_result=_json_object(args.dry_run_result_json, "--dry-run-result-json"),
            reproduction_steps=tuple(args.reproduction_step),
            proposed_fix=args.proposed_fix,
            redaction_notes=args.redaction_notes,
            metadata=_json_object(args.metadata_json, "--metadata-json"),
        )
        if args.output:
            write_failure_jsonl(record, args.output, append=args.append, create_dirs=args.create_dirs)
    except Exception as exc:
        print(f"failed to record failure log: {exc}", file=sys.stderr)
        return 1

    payload = failure_record_to_dict(record)
    if args.json or not args.output:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"failure_id: {record.failure_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
