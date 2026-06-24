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

from asperitas_agent.workflow_audit import (  # noqa: E402
    audit_workflow_artifact_dicts,
    workflow_audit_result_to_dict,
    write_workflow_audit_jsonl,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge workflow control artifacts into redacted audit JSONL events.")
    parser.add_argument("--input", help="Input JSON object containing trace_id, run, inspection, acceptance, metadata")
    parser.add_argument("--run", help="Explicit workflow-run artifact JSON path")
    parser.add_argument("--inspection", help="Explicit workflow-inspection report JSON path")
    parser.add_argument("--acceptance", help="Explicit workflow-acceptance decision JSON path")
    parser.add_argument("--trace-id", help="Trace id for direct artifact inputs")
    parser.add_argument("--output", help="Optional explicit output JSONL path")
    parser.add_argument("--append", action="store_true", help="Append to an existing JSONL file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _load_inputs(args: argparse.Namespace) -> tuple[dict, dict, dict, dict]:
    if args.input:
        payload = _load_json(args.input)
        return (
            payload.get("run", {}),
            payload.get("inspection", {}),
            payload.get("acceptance", {}),
            {"trace_id": payload.get("trace_id", "local_workflow_trace"), **dict(payload.get("metadata") or {})},
        )
    if not (args.run and args.inspection and args.acceptance):
        raise ValueError("--input or all of --run, --inspection, and --acceptance are required")
    return (
        _load_json(args.run),
        _load_json(args.inspection),
        _load_json(args.acceptance),
        {"trace_id": args.trace_id or "local_workflow_trace"},
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_data, inspection_data, acceptance_data, metadata = _load_inputs(args)
        result = audit_workflow_artifact_dicts(run_data, inspection_data, acceptance_data, metadata=metadata)
    except Exception as exc:
        print(f"failed to build workflow audit result: {exc}", file=sys.stderr)
        return 1
    if args.output:
        try:
            write_workflow_audit_jsonl(result, args.output, append=args.append, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write workflow audit JSONL: {exc}", file=sys.stderr)
            return 1
    payload = workflow_audit_result_to_dict(result)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"ok: {payload['ok']}")
        print(f"events: {len(payload['events'])}")
    return 0 if result.status in {"recorded", "rejected", "requires_human_approval"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
