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

from asperitas_agent.audit_trace import (  # noqa: E402
    audit_event_from_dict,
    audit_event_to_dict,
    build_audit_event,
    write_audit_jsonl,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write explicit JSON-safe audit trace events to JSONL.")
    parser.add_argument("--event-type", help="Audit event type for a single event")
    parser.add_argument("--trace-id", help="Trace id for a single event")
    parser.add_argument("--event-id", help="Optional event id for a single event")
    parser.add_argument("--severity", default="info", help="Audit severity")
    parser.add_argument("--actor", default="system", help="Audit actor")
    parser.add_argument("--input", help="Input JSON file containing one event object or a list of event objects")
    parser.add_argument("--output", help="Explicit output JSONL path")
    parser.add_argument("--append", action="store_true", help="Append to an existing JSONL file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing output parent directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    return parser.parse_args(argv)


def _events_from_input(path: str):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, list):
        return [audit_event_from_dict(item) for item in payload]
    if isinstance(payload, dict) and "events" in payload:
        return [audit_event_from_dict(item) for item in payload["events"]]
    return [audit_event_from_dict(payload)]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input:
        events = _events_from_input(args.input)
    else:
        events = [
            build_audit_event(
                trace_id=args.trace_id or "",
                event_type=args.event_type or "",
                event_id=args.event_id,
                severity=args.severity,
                actor=args.actor,
            )
        ]
    if args.output:
        try:
            write_audit_jsonl(events, args.output, append=args.append, create_dirs=args.create_dirs)
        except Exception as exc:
            print(f"failed to write audit JSONL: {exc}", file=sys.stderr)
            return 1
    payload = {"event_count": len(events), "events": [audit_event_to_dict(event) for event in events]}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"event_count: {payload['event_count']}")
    return 0 if all(not event.validate() for event in events) else 1


if __name__ == "__main__":
    raise SystemExit(main())
