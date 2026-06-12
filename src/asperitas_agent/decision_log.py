from __future__ import annotations

import datetime as dt
from pathlib import Path

from .inventory import repo_root


def _is_text_like(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        header = path.read_bytes()[:8]
    except OSError:
        return False
    return not header.startswith(b"PK\x03\x04") and b"\x00" not in header


def append_decision(message: str, root: Path | None = None) -> Path:
    root = repo_root(root)
    preferred = root / "00_ADMIN" / "decision_log.md"
    path = preferred if _is_text_like(preferred) else root / "09_LOGS" / "decision_logs" / "mvp001_decision_log.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {timestamp}\n\n{message.strip()}\n")
    return path
