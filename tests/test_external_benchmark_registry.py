import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "00_ADMIN/source_registries/external_benchmark_source_registry.csv"
SCHEMA = ROOT / "00_ADMIN/source_registries/external_benchmark_source_registry.schema.json"


def rows():
    return list(csv.DictReader(REGISTRY.open(encoding="utf-8")))


def test_registry_and_schema_exist():
    assert REGISTRY.exists()
    assert SCHEMA.exists()


def test_registry_header_matches_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    data = rows()
    assert data
    assert list(data[0].keys()) == schema["required_fields"]


def test_source_ids_are_unique():
    ids = [row["source_id"] for row in rows()]
    assert len(ids) == len(set(ids))


def test_registry_is_metadata_only():
    for row in rows():
        assert row["acquisition_status"] == "registered_only"
        assert row["processing_status"] == "not_processed"
        assert row["index_status"] == "not_indexed"
        assert row["eval_status"] == "not_run"
        assert row["license_status"] == "license_pending"
        assert row["raw_path"] == ""
        assert row["processed_path"] == ""
        assert row["chunk_manifest_path"] == ""


def test_priority_labels_are_p5_or_p6_only():
    assert {row["source_priority"] for row in rows()} <= {"P5", "P6"}


def test_p6_sources_are_external_benchmarks_only():
    for row in rows():
        if row["source_priority"] == "P6":
            assert row["source_family"] in {"founder_operator_doctrine", "ai_agent_architecture"}
            assert row["notes"] == "external_benchmark_only"


def test_p5_sources_are_industry_benchmarks_only():
    for row in rows():
        if row["source_priority"] == "P5":
            assert row["source_family"] == "ai_bio_platform_benchmark"
            assert row["evidence_type"] == "industry_benchmark"
