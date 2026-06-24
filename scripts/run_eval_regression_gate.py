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

from asperitas_agent.eval_regression_gate import compare_eval_artifacts  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the deterministic eval artifact regression gate without scoring, retrieval, or LLM judging."
    )
    parser.add_argument("--baseline", required=True, help="Baseline eval artifact JSON path")
    parser.add_argument("--candidate", required=True, help="Candidate eval artifact JSON path")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    decision = compare_eval_artifacts(args.baseline, args.candidate)
    payload = decision.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ok: {payload['ok']}")
        print(f"decision: {payload['decision']}")
        print(f"reasons: {len(payload['reasons'])}")
        print(f"warnings: {len(payload['warnings'])}")
    return 0 if decision.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
