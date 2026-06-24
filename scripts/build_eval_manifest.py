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

from asperitas_agent.eval_manifest import (  # noqa: E402
    EvalManifestError,
    build_eval_manifest,
    write_eval_manifest,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an explicit eval artifact manifest from provided artifact paths."
    )
    parser.add_argument("--artifact", action="append", required=True, help="Explicit eval artifact JSON path")
    parser.add_argument("--output", required=True, help="Explicit manifest output path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing output file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing parent directories for --output")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_eval_manifest(args.artifact)
        output_path = write_eval_manifest(
            manifest,
            args.output,
            overwrite=args.overwrite,
            create_dirs=args.create_dirs,
        )
        summary = {
            "ok": True,
            "manifest_id": manifest.manifest_id,
            "entry_count": len(manifest.entries),
            "output": str(output_path),
            "warnings": [],
            "errors": [],
        }
    except EvalManifestError as exc:
        summary = {
            "ok": False,
            "manifest_id": None,
            "entry_count": 0,
            "output": args.output,
            "warnings": [],
            "errors": [str(exc)],
        }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ok: {summary['ok']}")
        print(f"manifest_id: {summary['manifest_id']}")
        print(f"entry_count: {summary['entry_count']}")
        print(f"errors: {len(summary['errors'])}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
