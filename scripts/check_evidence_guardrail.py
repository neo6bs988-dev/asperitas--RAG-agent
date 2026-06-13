from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from asperitas_agent.chunking import read_chunks  # noqa: E402
from asperitas_agent.evidence_pack import build_evidence_pack  # noqa: E402
from asperitas_agent.guardrails import evaluate_evidence_guardrail  # noqa: E402
from asperitas_agent.registry import read_registry  # noqa: E402
from asperitas_agent.retrieval_mvp003 import search_chunks_mvp003  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic evidence sufficiency guardrail over an MVP-005 evidence pack.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "data" / "source_registry.csv")
    parser.add_argument("--chunks", type=Path, default=REPO_ROOT / "data" / "chunks.jsonl")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.top_k <= 0:
        print("ERROR: --top-k must be positive", file=sys.stderr)
        return 2
    if not args.registry.exists():
        print(f"ERROR: registry not found: {args.registry}", file=sys.stderr)
        return 2
    if not args.chunks.exists():
        print(f"ERROR: chunks not found: {args.chunks}", file=sys.stderr)
        return 2

    records = read_registry(args.registry)
    chunks = read_chunks(args.chunks)
    results = search_chunks_mvp003(args.query, chunks, records, limit=args.top_k, include_explanations=True)
    pack = build_evidence_pack(args.query, results, top_k=args.top_k)
    decision = evaluate_evidence_guardrail(pack)
    print(
        json.dumps(
            {
                "query": args.query,
                "evidence_pack_summary": {
                    "evidence_count": len(pack.evidence_items),
                    "unique_source_count": pack.source_coverage_summary.unique_source_count,
                    "risk_flags": pack.risk_flags.to_json(),
                    "abstention": pack.abstention.to_json(),
                },
                "guardrail_decision": decision.to_json(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
