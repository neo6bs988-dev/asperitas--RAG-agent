from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from asperitas_agent.evalos.runner import run  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "eval/evalos/public/v0.9_contract.json",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "eval/evalos/public/v0.9_cases.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "eval_results/evalos/v0.9/report.json",
    )
    args = parser.parse_args(argv)

    report = run(args.contract, args.cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"decision={report['decision']['status']}")
    print(f"report={args.output}")
    return 0 if report["decision"]["status"] == "PROMPT_HARNESS_RELEASE_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
