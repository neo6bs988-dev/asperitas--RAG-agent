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

from asperitas_agent.workflow_inspector import (  # noqa: E402
    inspect_workflow_run_dict,
    workflow_inspection_to_dict,
    write_workflow_inspection_report,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a workflow-run artifact without executing retrieval, connectors, tools, or the plan."
    )
    parser.add_argument("--input", required=True, help="Explicit workflow-run artifact JSON path")
    parser.add_argument("--output", help="Optional explicit workflow inspection output JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output path")
    parser.add_argument("--create-dirs", action="store_true", help="Allow creating missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    except Exception as exc:
        payload = {"run_id": "invalid_workflow_run", "malformed_error": str(exc)}
    report = inspect_workflow_run_dict(payload)
    if args.output:
        try:
            write_workflow_inspection_report(report, args.output, overwrite=args.overwrite, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write workflow inspection report: {exc}", file=sys.stderr)
            return 1
    output = workflow_inspection_to_dict(report)
    if args.json:
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ok: {output['ok']}")
        print(f"run_status: {output['run_status']}")
        print(f"ready_for_execution: {output['ready_for_execution']}")
        print(f"executes_plan: {output['executes_plan']}")
        print(f"findings: {len(output['findings'])}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
