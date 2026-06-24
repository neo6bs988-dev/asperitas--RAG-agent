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

from asperitas_agent.security_guard import (  # noqa: E402
    inspect_security_dict,
    security_guard_report_to_dict,
    summarize_security_guard,
    write_security_guard_report,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic Asperitas security guard on an explicit input file.")
    parser.add_argument("--input", required=True, help="Security guard input JSON path")
    parser.add_argument("--output", help="Optional explicit security report JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing output file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit full JSON report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
        report = inspect_security_dict(payload)
    except Exception as exc:
        print(f"failed to inspect security input: {exc}", file=sys.stderr)
        return 1
    if args.output:
        try:
            write_security_guard_report(report, args.output, overwrite=args.overwrite, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write security report: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(security_guard_report_to_dict(report), ensure_ascii=False, sort_keys=True))
    else:
        summary = summarize_security_guard(report)
        print(f"ok: {summary['ok']}")
        print(f"risk_level: {summary['risk_level']}")
        print(f"findings: {summary['finding_count']}")
    return 0 if report.ok or report.requires_human_approval else 1


if __name__ == "__main__":
    raise SystemExit(main())
