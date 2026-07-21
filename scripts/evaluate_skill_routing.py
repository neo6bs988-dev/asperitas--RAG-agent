from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.skill_routing_eval import (  # noqa: E402
    EXPECTED_INCUMBENT_SHA,
    RoutingEvalError,
    build_baseline,
    write_baseline,
)


def _codex_version() -> str | None:
    try:
        result = subprocess.run(
            ["codex", "--version"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate the frozen incumbent Skill routing baseline.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--inputs", type=Path, default=REPO_ROOT / "eval" / "skill_routing_cases_v2.jsonl")
    parser.add_argument(
        "--expectations",
        type=Path,
        default=REPO_ROOT / "eval" / "skill_routing_expectations_v2.jsonl",
    )
    parser.add_argument("--evaluated-sha", default=EXPECTED_INCUMBENT_SHA)
    parser.add_argument("--codex-cli-version", default=None)
    parser.add_argument("--output", type=Path, help="Explicit path for a deterministic JSON artifact.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = build_baseline(
            args.root.resolve(),
            args.inputs.resolve(),
            args.expectations.resolve(),
            evaluated_sha=args.evaluated_sha,
            codex_cli_version=args.codex_cli_version or _codex_version(),
        )
    except (OSError, RoutingEvalError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=True, sort_keys=True))
        return 1
    if args.output is not None:
        write_baseline(args.output, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
