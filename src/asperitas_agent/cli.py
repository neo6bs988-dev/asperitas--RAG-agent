from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .chunking import chunk_document, read_chunks, write_chunks
from .compliance import detect_risk_tags
from .decision_log import append_decision
from .ingestion_log import write_ingestion_log
from .inventory import build_inventory, repo_root, write_inventory_csv
from .loaders import load_documents
from .rag import build_answer
from .registry import default_registry_path, ensure_registry, read_registry, validate_registry, write_registry
from .retrieval_tfidf import search_chunks
from .verification import verify_artifacts


def _json_print(payload: object) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _ingest_notes(existing: str, entries: list) -> str:
    base = [segment for segment in existing.split("; ") if segment.startswith("file_type=")]
    status_counts = Counter(entry.ingestion_status for entry in entries)
    if status_counts:
        base.append("ingest_status_counts=" + ",".join(f"{key}:{status_counts[key]}" for key in sorted(status_counts)))
    reasons = sorted({entry.reason for entry in entries if entry.reason})[:3]
    if reasons:
        base.append("ingest_reasons=" + " | ".join(reasons))
    return "; ".join(base)


def cmd_validate_registry(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    path = default_registry_path(root)
    if not path.exists():
        path = ensure_registry(root)
    ok, errors = validate_registry(path)
    _json_print({"ok": ok, "registry": path.as_posix(), "errors": errors})
    return 0 if ok else 1


def cmd_inventory(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    records = build_inventory(root)
    inventory_path = write_inventory_csv(records, root)
    registry_path = write_registry(records, root)
    append_decision(f"MVP-001 inventory created: {len(records)} sources. Registry: {registry_path.as_posix()}", root)
    _json_print({"source_count": len(records), "inventory": inventory_path.as_posix(), "registry": registry_path.as_posix()})
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    registry_path = default_registry_path(root)
    if registry_path.exists():
        ok, errors = validate_registry(registry_path)
        if not ok:
            _json_print({"ok": False, "registry": registry_path.as_posix(), "errors": errors})
            return 1
    records = read_registry(registry_path) or build_inventory(root)
    chunks = []
    report = []
    ingestion_entries = []
    for record in records:
        bundle = load_documents(record, root)
        record.parse_status = bundle.source_parse_status
        if bundle.entries:
            record.notes = _ingest_notes(record.notes, bundle.entries)

        chunks_for_source = 0
        for document in bundle.documents:
            record_chunks = chunk_document(document)
            chunks.extend(record_chunks)
            chunks_for_source += len(record_chunks)
            document_flags = sorted(set(detect_risk_tags(document.text + " " + document.source.title + " " + document.source.path)))
            for entry in bundle.entries:
                if entry.path == document.source.path:
                    entry.extracted_chunk_count = len(record_chunks)
                    entry.compliance_flags = document_flags

        for entry in bundle.entries:
            if not entry.compliance_flags:
                entry.compliance_flags = sorted(set(detect_risk_tags(entry.filename + " " + entry.path + " " + entry.reason)))
        ingestion_entries.extend(bundle.entries)
        report.append({"source_id": record.source_id, "path": record.path, "parse_status": record.parse_status, "chunks": chunks_for_source, "entries": [entry.to_json() for entry in bundle.entries]})
    registry_path = write_registry(records, root)
    chunk_path = write_chunks(chunks, root)
    log_path = write_ingestion_log(ingestion_entries, root)
    append_decision(f"MVP-002 ingest completed: {len(chunks)} chunks from {len(records)} registered sources. Log: {log_path.as_posix()}", root)
    _json_print({"registry": registry_path.as_posix(), "chunks": chunk_path.as_posix(), "ingestion_log": log_path.as_posix(), "chunk_count": len(chunks), "report": report})
    return 0


def _load_index(root: Path):
    chunk_path = root / "data" / "chunks.jsonl"
    if not chunk_path.exists():
        return []
    return read_chunks(chunk_path)


def cmd_search(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    results = search_chunks(args.query, _load_index(root), limit=args.limit)
    _json_print({"query": args.query, "results": [result.to_json() for result in results]})
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    answer = build_answer(args.question, _load_index(root), limit=args.limit)
    _json_print(answer.to_json())
    return 0


def cmd_verify_artifacts(args: argparse.Namespace) -> int:
    root = repo_root(Path.cwd())
    result = verify_artifacts(root)
    _json_print(result)
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Asperitas MVP-001 source-grounded RAG core CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-registry")
    validate.set_defaults(func=cmd_validate_registry)
    inventory = sub.add_parser("inventory")
    inventory.set_defaults(func=cmd_inventory)
    ingest = sub.add_parser("ingest")
    ingest.set_defaults(func=cmd_ingest)
    verify = sub.add_parser("verify-artifacts")
    verify.set_defaults(func=cmd_verify_artifacts)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=cmd_search)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    ask.add_argument("--limit", type=int, default=5)
    ask.set_defaults(func=cmd_ask)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
