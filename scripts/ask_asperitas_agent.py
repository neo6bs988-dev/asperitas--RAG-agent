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

from asperitas_agent.chat_workflow import (  # noqa: E402
    build_chat_question_input,
    chat_workflow_result_to_dict,
    run_chat_workflow,
    summarize_chat_workflow,
    write_chat_audit_jsonl,
    write_chat_workflow_result,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local dry-run Asperitas chat/QA workflow gates.")
    parser.add_argument("--input", help="Explicit chat input JSON path")
    parser.add_argument("--question", help="Question for dry-run chat workflow mode")
    parser.add_argument("--output", help="Optional explicit chat result JSON path")
    parser.add_argument("--audit-output", help="Optional explicit audit JSONL path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing result output")
    parser.add_argument("--append-audit", action="store_true", help="Append to an existing audit JSONL file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit full JSON result")
    return parser.parse_args(argv)


def _load_input(args: argparse.Namespace) -> dict:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    if args.question:
        chat_input = build_chat_question_input(
            request_id="local_chat_request",
            trace_id="local_trace",
            question=args.question,
            required_skills=("source-grounding-check",),
            available_skills=("source-grounding-check",),
            source_status={"available": True, "source_count": 1},
            eval_gate={"ok": True},
            source_texts=(),
        )
        payload = chat_input.to_dict()
        payload.pop("warnings", None)
        payload.pop("errors", None)
        return payload
    raise ValueError("--input or --question is required")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = run_chat_workflow(_load_input(args))
    except Exception as exc:
        print(f"failed to run chat workflow: {exc}", file=sys.stderr)
        return 1
    if args.output:
        try:
            write_chat_workflow_result(result, args.output, overwrite=args.overwrite, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write chat workflow result: {exc}", file=sys.stderr)
            return 1
    if args.audit_output:
        try:
            write_chat_audit_jsonl(result, args.audit_output, append=args.append_audit, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write chat workflow audit JSONL: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(chat_workflow_result_to_dict(result), ensure_ascii=False, sort_keys=True))
    else:
        summary = summarize_chat_workflow(result)
        print(f"status: {summary['status']}")
        print(f"ok: {summary['ok']}")
        print(f"dry_run: {summary['dry_run']}")
    return 0 if result.status in {"answered", "dry_run_ready", "requires_human_approval"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
