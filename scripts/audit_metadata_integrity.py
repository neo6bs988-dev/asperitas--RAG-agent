from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.metadata_integrity import audit_metadata_integrity, summarize_metadata_integrity  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit deterministic chunk/source metadata integrity gaps.")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "data" / "chunks.jsonl")
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "data" / "source_registry.csv")
    parser.add_argument("--examples", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.chunks.exists():
        print(f"ERROR: chunks file not found: {args.chunks}", file=sys.stderr)
        return 2
    if not args.registry.exists():
        print(f"ERROR: registry file not found: {args.registry}", file=sys.stderr)
        return 2
    report = audit_metadata_integrity(args.chunks, args.registry, example_limit=args.examples)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(summarize_metadata_integrity(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
