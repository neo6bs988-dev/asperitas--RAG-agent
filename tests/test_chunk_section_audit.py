from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_chunk_sections.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_chunk_sections", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_audit_chunk_sections_reports_section_coverage(tmp_path: Path):
    module = load_audit_module()
    chunks_path = tmp_path / "chunks.jsonl"
    rows = [
        {
            "chunk_id": "c1",
            "source_id": "s1",
            "title": "Doc",
            "text": "Body",
            "page_start": None,
            "page_end": None,
            "char_start": 0,
            "char_end": 4,
            "source_priority": "P1",
            "source_type": "internal",
            "disclosure_level": "confidential",
            "evidence_label": "Document-Supported Fact",
            "verification_status": "verified_internal",
            "risk_tags": [],
            "checksum": "a",
            "section": "Methods",
            "section_heading": "Methods",
            "section_path": ["Methods"],
            "section_level": 1,
            "parent_section": "",
            "subsection": "",
            "heading_context": "Methods",
        },
        {
            "chunk_id": "c2",
            "source_id": "s1",
            "title": "Doc",
            "text": "Body",
            "page_start": None,
            "page_end": None,
            "char_start": 5,
            "char_end": 9,
            "source_priority": "P1",
            "source_type": "internal",
            "disclosure_level": "confidential",
            "evidence_label": "Document-Supported Fact",
            "verification_status": "verified_internal",
            "risk_tags": [],
            "checksum": "b",
        },
    ]
    with chunks_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    report = module.audit_chunk_sections(chunks_path)

    assert report["total_chunks"] == 2
    assert report["chunks_with_section_metadata"] == 1
    assert report["chunks_missing_section_metadata"] == 1
    assert report["top_section_values"][0] == ("Methods", 1)
