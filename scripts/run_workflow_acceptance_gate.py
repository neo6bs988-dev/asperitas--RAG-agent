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

from asperitas_agent.workflow_acceptance import (  # noqa: E402
    accept_workflow_artifact_dicts,
    workflow_acceptance_to_dict,
    write_workflow_acceptance_decision,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic workflow acceptance gate without executing workflow plans."
    )
    parser.add_argument("--run", required=True, help="Explicit workflow-run artifact JSON path")
    parser.add_argument("--inspection", required=True, help="Explicit workflow-inspection report JSON path")
    parser.add_argument("--output", help="Optional explicit workflow acceptance output JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output path")
    parser.add_argument("--create-dirs", action="store_true", help="Allow creating missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_data = _load_json(args.run)
    except Exception as exc:
        run_data = {"run_id": "invalid_workflow_run", "load_error": str(exc)}
    try:
        inspection_data = _load_json(args.inspection)
    except Exception as exc:
        inspection_data = {"report_id": "invalid_workflow_inspection", "load_error": str(exc)}
    decision = accept_workflow_artifact_dicts(run_data, inspection_data)
    if args.output:
        try:
            write_workflow_acceptance_decision(
                decision,
                args.output,
                overwrite=args.overwrite,
                create_dirs=args.create_dirs,
            )
        except Exception as exc:
            print(f"failed to write workflow acceptance decision: {exc}", file=sys.stderr)
            return 1
    payload = workflow_acceptance_to_dict(decision)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"ok: {payload['ok']}")
        print(f"ready_for_execution: {payload['ready_for_execution']}")
        print(f"executes_plan: {payload['executes_plan']}")
        print(f"reasons: {len(payload['reasons'])}")
    return 0 if decision.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
