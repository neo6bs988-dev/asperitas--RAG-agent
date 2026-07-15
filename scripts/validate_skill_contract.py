from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.skill_contract import validate_contract_file, validate_repository  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Asperitas Skill Contract v2 declarations.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--root", type=Path, help="Repository root containing .agents/skills.")
    target.add_argument("--contract", type=Path, help="Strictly validate one fixture skill.contract.json.")
    parser.add_argument("--transition", action="store_true", help="Audit an unmigrated repository without gating it.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic structured JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.contract is not None and args.transition:
        build_parser().error("--transition requires --root")
    report = (
        validate_contract_file(args.contract)
        if args.contract is not None
        else validate_repository(args.root, transition=args.transition)
    )
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(f"{report.state}: {report.validation_level} ({len(report.findings)} findings)")
        for finding in report.findings:
            print(f"{finding.code}: {finding.path}: {finding.message}")
    return 0 if report.state in {"PASS", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
