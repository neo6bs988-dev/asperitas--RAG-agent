from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.skill_canary_eval import (  # noqa: E402
    EXPECTED_BASE_SHA,
    SkillCanaryError,
    build_canary,
    write_canary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate the deterministic P1C-2 Skill permission canary.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--cases", type=Path, default=REPO_ROOT / "eval" / "skill_canary_cases_v1.jsonl")
    parser.add_argument(
        "--expectations",
        type=Path,
        default=REPO_ROOT / "eval" / "skill_canary_expectations_v1.jsonl",
    )
    parser.add_argument(
        "--p1c1-inputs",
        type=Path,
        default=REPO_ROOT / "eval" / "skill_routing_cases_v2.jsonl",
    )
    parser.add_argument("--evaluated-sha", default=EXPECTED_BASE_SHA)
    parser.add_argument("--output", type=Path, help="Explicit path for a deterministic JSON artifact.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = build_canary(
            args.root.resolve(),
            args.cases.resolve(),
            args.expectations.resolve(),
            args.p1c1_inputs.resolve(),
            evaluated_sha=args.evaluated_sha,
        )
    except (OSError, SkillCanaryError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=True, sort_keys=True))
        return 1
    if args.output is not None:
        write_canary(args.output, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
