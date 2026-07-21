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

from asperitas_agent.evalos.repository_adapter import (  # noqa: E402
    run_repository_no_effect_shadow,
)


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def _current_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        type=Path,
        default=REPO_ROOT / "eval/evalos/public/v1.4_shadow_policy.json",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=REPO_ROOT / "eval/evalos/public/v1.4_shadow_cases.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "eval_results/evalos/v1.4_shadow_report.json",
    )
    parser.add_argument("--expected-head")
    args = parser.parse_args(argv)

    policy = _load_json(args.policy)
    case_document = _load_json(args.cases)
    raw_cases = case_document.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("case document must contain a cases list")

    current_head = _current_head()
    exact_head_verified = bool(
        args.expected_head
        and current_head
        and args.expected_head == current_head
    )
    report = run_repository_no_effect_shadow(
        cases=[dict(item) for item in raw_cases],
        policy=dict(policy),
        secret=b"public-safe-local-shadow-tokenization-key",
        exact_repository_head_verified=exact_head_verified,
    )
    report["repository_head"] = current_head
    report["expected_head"] = args.expected_head
    report["exact_head_verified"] = exact_head_verified

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"decision={report['decision']['status']}")
    print(f"report={args.output}")
    return 0 if report["decision"]["status"] in {
        "NO_EFFECT_SHADOW_SPEC_CANDIDATE",
        "NO_EFFECT_SHADOW_READY_FOR_CONTROLLED_RUN",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
