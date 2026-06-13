from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.chunking import read_chunks  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def audit_chunk_sections(chunks_path: Path) -> dict[str, Any]:
    chunks = read_chunks(chunks_path)
    with_section = [chunk for chunk in chunks if chunk.section or chunk.section_heading or chunk.heading_context]
    missing = [chunk for chunk in chunks if not (chunk.section or chunk.section_heading or chunk.heading_context)]
    section_counts = Counter(chunk.heading_context or chunk.section_heading or chunk.section for chunk in with_section)
    return {
        "chunks_path": chunks_path.as_posix(),
        "total_chunks": len(chunks),
        "chunks_with_section_metadata": len(with_section),
        "chunks_missing_section_metadata": len(missing),
        "top_section_values": section_counts.most_common(20),
        "sample_section_preserved_chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "section": chunk.section,
                "heading_context": chunk.heading_context,
                "char_start": chunk.char_start,
                "text_preview": " ".join(chunk.text.split())[:180],
            }
            for chunk in with_section[:5]
        ],
        "sample_missing_section_chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "char_start": chunk.char_start,
                "text_preview": " ".join(chunk.text.split())[:180],
            }
            for chunk in missing[:5]
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit section metadata coverage in chunk artifacts.")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "data" / "chunks.jsonl")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.chunks.exists():
        print(f"ERROR: chunks file not found: {args.chunks}", file=sys.stderr)
        return 2
    report = audit_chunk_sections(args.chunks)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Chunk Section Audit")
        print(f"Chunks: {report['total_chunks']}")
        print(f"With section metadata: {report['chunks_with_section_metadata']}")
        print(f"Missing section metadata: {report['chunks_missing_section_metadata']}")
        print("Top section values:")
        for section, count in report["top_section_values"][:10]:
            print(f"- {section}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
