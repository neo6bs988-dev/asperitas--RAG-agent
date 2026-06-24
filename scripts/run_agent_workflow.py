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

from asperitas_agent.workflow_run import (  # noqa: E402
    build_workflow_run,
    load_workflow_run_input,
    workflow_run_to_dict,
    write_workflow_run_artifact,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic workflow-run artifact without executing the advisory plan."
    )
    parser.add_argument("--input", required=True, help="Explicit workflow-run input JSON path")
    parser.add_argument("--output", help="Optional explicit output JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output path")
    parser.add_argument("--create-dirs", action="store_true", help="Allow creating missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_data = load_workflow_run_input(args.input)
    run = build_workflow_run(input_data)
    if args.output:
        try:
            write_workflow_run_artifact(run, args.output, overwrite=args.overwrite, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write workflow run artifact: {exc}", file=sys.stderr)
            return 1
    payload = workflow_run_to_dict(run)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"ok: {payload['ok']}")
        print(f"ready_for_execution: {payload['ready_for_execution']}")
        print(f"executes_plan: {payload['executes_plan']}")
    return 0 if run.status != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
