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

from asperitas_agent.release_readiness import (  # noqa: E402
    ReleaseReadinessPolicy,
    build_v1_release_readiness_report,
    release_readiness_to_dict,
    summarize_release_readiness,
    write_release_readiness_report,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic V1 internal release-readiness checks.")
    parser.add_argument("--output", help="Optional explicit release readiness JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing output file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit full JSON report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_v1_release_readiness_report(policy=ReleaseReadinessPolicy(repo_root=str(REPO_ROOT)))
    if args.output:
        try:
            write_release_readiness_report(report, args.output, overwrite=args.overwrite, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write release readiness report: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps(release_readiness_to_dict(report), ensure_ascii=False, sort_keys=True))
    else:
        summary = summarize_release_readiness(report)
        print(f"status: {summary['status']}")
        print(f"ok: {summary['ok']}")
        print(f"blocked: {summary['blocked_count']}")
    return 0 if report.status == "ready_for_internal_rc" else 1


if __name__ == "__main__":
    raise SystemExit(main())
