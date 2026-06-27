import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "00_ADMIN" / "source_registries" / "external_benchmark_source_registry.csv"
SCHEMA_PATH = ROOT / "00_ADMIN" / "source_registries" / "external_benchmark_source_registry.schema.json"


def _rows():
    with REGISTRY_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_external_benchmark_registry_files_exist():
    assert REGISTRY_PATH.exists()
    assert SCHEMA_PATH.exists()


def test_required_fields_present_and_non_empty():
    rows = _rows()
    required = _schema()["required"]
    assert rows
    for row in rows:
        for field in required:
            assert field in row
            assert row[field].strip(), f"{row.get('source_id')} missing {field}"


def test_source_ids_are_unique():
    rows = _rows()
    source_ids = [row["source_id"] for row in rows]
    assert len(source_ids) == len(set(source_ids))


def test_allowed_enum_values_match_schema():
    rows = _rows()
    schema = _schema()["properties"]
    enum_fields = [
        "category",
        "source_type",
        "source_priority",
        "disclosure",
        "license_status",
        "ingestion_status",
    ]
    for row in rows:
        for field in enum_fields:
            assert row[field] in schema[field]["enum"], f"{row['source_id']} invalid {field}={row[field]}"


def test_registered_only_scaffold_counts():
    rows = _rows()
    counts = Counter(row["category"] for row in rows)
    assert counts["founder_operator_doctrine"] == 15
    assert counts["ai_agent_architecture"] == 16
    assert counts["ai_bio_platform_benchmark"] == 10
    assert len(rows) == 41


def test_no_raw_or_processed_ingestion_claims():
    rows = _rows()
    assert all(row["ingestion_status"] == "registered_only" for row in rows)
    disallowed_statuses = {"raw_acquired", "processed_markdown", "chunked", "embedded", "evaluated"}
    assert not any(row["ingestion_status"] in disallowed_statuses for row in rows)


def test_external_priorities_are_not_internal_source_of_truth():
    rows = _rows()
    assert all(row["source_priority"] not in {"P0", "P1", "P2"} for row in rows)
    assert any(row["source_priority"] == "P3" for row in rows)
    assert any(row["source_priority"] == "P4" for row in rows)
    assert any(row["source_priority"] == "P5" for row in rows)
    assert any(row["source_priority"] == "P6" for row in rows)
