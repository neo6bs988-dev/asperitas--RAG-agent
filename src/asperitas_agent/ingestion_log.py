from __future__ import annotations

from pathlib import Path

from .inventory import repo_root
from .schemas import IngestionLogEntry


LOG_COLUMNS = (
    "filename",
    "extension",
    "ingestion_status",
    "reason",
    "extracted_chunk_count",
    "source_priority",
    "disclosure_level",
    "compliance_flags",
    "source_id",
    "path",
)


def _cell(value: object) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    text = str(value)
    text = text.replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return text.strip()


def write_ingestion_log(entries: list[IngestionLogEntry], root: Path | None = None, path: Path | None = None) -> Path:
    root = repo_root(root)
    output = path or root / "09_LOGS" / "run_logs" / "source_ingestion_log.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    sorted_entries = sorted(entries, key=lambda entry: (entry.path.lower(), entry.filename.lower(), entry.ingestion_status))
    lines = [
        "# Source Ingestion Log",
        "",
        "MVP-002 deterministic ingestion report. This log records parsing status only; it does not imply legal approval, regulatory approval, production vector indexing, or wet-lab validation.",
        "",
        "| " + " | ".join(LOG_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in LOG_COLUMNS) + " |",
    ]
    for entry in sorted_entries:
        data = entry.to_json()
        lines.append("| " + " | ".join(_cell(data[column]) for column in LOG_COLUMNS) + " |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
