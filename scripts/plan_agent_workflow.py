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

from asperitas_agent.workflow_planner import (  # noqa: E402
    build_workflow_plan,
    build_workflow_request,
    workflow_plan_to_dict,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic local agent workflow plan without executing tools, retrieval, or LLM calls."
    )
    parser.add_argument("--request", help="User request to plan")
    parser.add_argument("--input", help="Workflow request JSON path")
    parser.add_argument("--required-skill", help="Required skill id")
    parser.add_argument("--available-skill", action="append", default=[], help="Available skill id; repeatable")
    parser.add_argument("--eval-gate", choices=("passed", "failed", "blocked"), default="passed", help="Eval gate status")
    parser.add_argument("--source-status", default="available", help="Source status")
    parser.add_argument("--risk-flag", action="append", default=[], help="Risk flag such as high or blocked; repeatable")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def _request_from_args(args: argparse.Namespace):
    if args.input:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        return build_workflow_request(
            payload.get("user_request", ""),
            required_skill_id=payload.get("required_skill_id", args.required_skill),
            request_id=payload.get("request_id", "local_workflow_request"),
        )
    return build_workflow_request(args.request or "", required_skill_id=args.required_skill)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    request = _request_from_args(args)
    plan = build_workflow_plan(
        request,
        available_skills=tuple(args.available_skill),
        eval_gate=args.eval_gate,
        source_status=args.source_status,
        risk_flags=tuple(args.risk_flag),
    )
    payload = workflow_plan_to_dict(plan)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"decision: {payload['planner_decision']['decision']}")
        print(f"ready_for_execution: {payload['ready_for_execution']}")
        print(f"executes_plan: {payload['executes_plan']}")
    return 0 if plan.planner_decision.decision != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
