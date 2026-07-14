from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.validate_external_benchmark_registry import (
    DEFAULT_CANONICAL_SCHEMA,
    DEFAULT_REGISTRY,
    DEFAULT_SCHEMA,
    parse_canonical_enum_values,
    validate_registry,
)


def _rows() -> list[dict[str, str]]:
    with DEFAULT_REGISTRY.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def test_external_benchmark_registry_v2_passes_contract() -> None:
    report = validate_registry()
    assert report["ok"], report["errors"]
    assert report["record_count"] == 19
    assert report["warnings"] == []


def test_registry_schema_uses_current_canonical_authority_and_topology() -> None:
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    assert schema["canonical_authority"] == "00_ADMIN/metadata_schema.yaml"
    assert schema["canonical_benchmark_topology"] == "01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/"
    assert schema["status"] == "metadata_only_candidate_registry"
    assert schema["invariants"]["metadata_only"] is True
    assert schema["invariants"]["production_ingestion_allowed"] is False


def test_registry_schema_enums_are_subsets_of_canonical_metadata_schema() -> None:
    schema = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    canonical = parse_canonical_enum_values(DEFAULT_CANONICAL_SCHEMA)
    for field in (
        "source_priority",
        "source_type",
        "disclosure_level",
        "origin",
        "jurisdiction",
        "license_status",
        "verification_status",
        "ingestion_status",
        "evidence_label",
        "risk_flags",
        "allowed_use_cases",
    ):
        assert set(schema["allowed_values"][field]) <= canonical[field]


def test_registry_is_metadata_only_and_fail_closed() -> None:
    rows = _rows()
    assert rows
    for row in rows:
        assert row["disclosure_level"] == "external-safe"
        assert row["license_status"] == "needs_review"
        assert row["verification_status"] == "needs_external_verification"
        assert row["ingestion_status"] == "registered"
        assert row["version_or_date"] == "unverified_current_version"
        assert row["notes"] == "url_inherited_from_current_main_manifest_external_content_not_refetched"
        assert "raw_ingestion_without_review" in row["prohibited_use_cases"].split("|")
        assert "external_claim_without_verification" in row["prohibited_use_cases"].split("|")


def test_registry_uses_only_canonical_benchmark_provenance() -> None:
    for row in _rows():
        assert row["provenance"].startswith("01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/")
        assert "P6_EXTERNAL_BENCHMARK/" not in row["provenance"]


def test_source_ids_and_urls_are_unique_https_values() -> None:
    rows = _rows()
    source_ids = [row["source_id"] for row in rows]
    source_urls = [row["source_url"] for row in rows]
    assert len(source_ids) == len(set(source_ids))
    assert len(source_urls) == len(set(source_urls))
    assert all(url.startswith("https://") for url in source_urls)


def test_p5_is_reserved_for_ai_bio_platform_benchmarks() -> None:
    for row in _rows():
        if row["source_priority"] == "P5":
            assert row["source_family"] == "ai_bio_platform_benchmark"
            assert row["evidence_label"] == "Industry Signal"
        if row["source_family"] == "ai_bio_platform_benchmark":
            assert row["source_priority"] == "P5"


def test_unverified_papers_do_not_claim_peer_review_or_scientific_validation() -> None:
    paper_rows = [row for row in _rows() if row["source_type"] == "paper"]
    assert paper_rows
    for row in paper_rows:
        assert row["evidence_label"] == "Needs External Verification"
        assert "scientific_validation_claim" in row["prohibited_use_cases"].split("|")


def test_registry_files_are_repository_relative() -> None:
    root = Path(__file__).resolve().parents[1]
    assert DEFAULT_REGISTRY.is_relative_to(root)
    assert DEFAULT_SCHEMA.is_relative_to(root)
    assert DEFAULT_CANONICAL_SCHEMA.is_relative_to(root)
