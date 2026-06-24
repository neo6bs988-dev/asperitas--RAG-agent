from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from asperitas_agent.metadata_integrity import audit_metadata_integrity


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "audit_metadata_integrity.py"


def _chunk(source_id: str, chunk_id: str, *, char_start: int = 0, section: str = "") -> dict[str, object]:
    return {
        "chunk_id": chunk_id,
        "source_id": source_id,
        "title": "Source Title",
        "text": "Body text with no reliable heading marker.",
        "page_start": None,
        "page_end": None,
        "char_start": char_start,
        "char_end": char_start + 36,
        "source_priority": "P1",
        "source_type": "internal",
        "disclosure_level": "confidential",
        "evidence_label": "Document-Supported Fact",
        "verification_status": "verified_internal",
        "risk_tags": [],
        "checksum": chunk_id,
        "section": section,
        "section_heading": section,
        "section_path": [section] if section else [],
        "section_level": 1 if section else None,
        "parent_section": "",
        "subsection": "",
        "heading_context": section,
    }


def _write_chunks(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _write_registry(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "source_id,title,original_filename,path,source_priority,source_type,disclosure_level,license_status,verification_status,date,author_or_owner,use_case,checksum,parse_status,notes",
                "s1,Policy Document,policy.pdf,01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/policy.pdf,P1,internal,confidential,internal_use,verified_internal,2026-06-12,unknown,rag,abc,parsed,file_type=pdf; ingest_reasons=pypdf",
                "s2,Plain Notes,notes.txt,01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/notes.txt,P1,internal,confidential,internal_use,verified_internal,2026-06-12,unknown,rag,def,parsed,file_type=text_or_binary; ingest_reasons=plain_text",
            ]
        )
        + "\n",
        encoding="utf-8-sig",
    )


def _load_script_module():
    spec = importlib.util.spec_from_file_location("audit_metadata_integrity", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_metadata_integrity_report_serializes_required_gap_counts(tmp_path: Path):
    chunks_path = tmp_path / "chunks.jsonl"
    registry_path = tmp_path / "source_registry.csv"
    _write_chunks(chunks_path, [_chunk("s1", "s1::a::chunk-0001"), _chunk("s1", "s1::a::chunk-0002", section="Methods")])
    _write_registry(registry_path)

    report = audit_metadata_integrity(chunks_path, registry_path)
    encoded = json.dumps(report, sort_keys=True)

    assert json.loads(encoded)["total_chunks"] == 2
    assert report["chunks_with_section"] == 1
    assert report["chunks_missing_section"] == 1
    assert report["missing_count_by_source_file"]["01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/policy.pdf"] == 1
    assert report["missing_count_by_parser"]["pypdf"] == 1


def test_first_chunk_title_derivation_is_reported_but_not_mutated(tmp_path: Path):
    chunks_path = tmp_path / "chunks.jsonl"
    registry_path = tmp_path / "source_registry.csv"
    original = _chunk("s1", "s1::a::chunk-0001", char_start=0)
    _write_chunks(chunks_path, [original])
    _write_registry(registry_path)

    report = audit_metadata_integrity(chunks_path, registry_path)

    example = report["examples_of_missing_chunks"][0]
    assert report["derivable_missing_count"] == 1
    assert example["risk_classification"] == "derivable"
    assert example["safely_derivable_section"] == "Policy Document"
    assert report["safe_repair_policy"]["artifact_mutation"] is False
    assert json.loads(chunks_path.read_text(encoding="utf-8").splitlines()[0])["section"] == ""


def test_non_first_chunk_without_heading_remains_unknown_not_invented(tmp_path: Path):
    chunks_path = tmp_path / "chunks.jsonl"
    registry_path = tmp_path / "source_registry.csv"
    _write_chunks(chunks_path, [_chunk("s2", "s2::a::chunk-0002", char_start=875)])
    _write_registry(registry_path)

    report = audit_metadata_integrity(chunks_path, registry_path)

    example = report["examples_of_missing_chunks"][0]
    assert report["derivable_missing_count"] == 0
    assert report["unresolved_missing_count"] == 1
    assert example["risk_classification"] == "not_derivable"
    assert example["safely_derivable_section"] == ""


def test_script_json_output_contains_machine_readable_keys(tmp_path: Path, capsys):
    chunks_path = tmp_path / "chunks.jsonl"
    registry_path = tmp_path / "source_registry.csv"
    _write_chunks(chunks_path, [_chunk("s1", "s1::a::chunk-0001")])
    _write_registry(registry_path)
    module = _load_script_module()

    exit_code = module.main(["--chunks", str(chunks_path), "--registry", str(registry_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["total_chunks"] == 1
    assert "risk_classification_counts" in payload
    assert "examples_of_missing_chunks" in payload
