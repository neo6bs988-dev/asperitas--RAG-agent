from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_benchmark_claim_cards_expose_grounding_metadata():
    rows = read_jsonl(ROOT / "03_PROCESSED_KB" / "benchmark_intelligence" / "benchmark_claim_cards.jsonl")
    required = {
        "claim_id",
        "claim",
        "source_id",
        "evidence_label",
        "confidence",
        "verification_status",
        "allowed_use",
        "forbidden_use",
    }

    assert rows
    assert all(required <= set(row) for row in rows)
    assert all(row["allowed_use"] == "benchmark_only_not_asperitas_fact" for row in rows)
    assert all(row["forbidden_use"] == "asperitas_fact_or_performance_claim" for row in rows)


def test_csv_external_urls_remain_source_map_only_not_ingested():
    path = ROOT / "00_ADMIN" / "source_registries" / "benchmark_source_registry.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert all(row["url"].startswith("https://") for row in rows)
    assert {row["license_status"] for row in rows} == {"verify_before_ingestion"}
    assert {row["ingestion_status"] for row in rows} == {"source_mapped_not_ingested"}


def test_benchmark_process_patterns_preserve_source_map_boundary():
    rows = read_jsonl(ROOT / "03_PROCESSED_KB" / "benchmark_intelligence" / "benchmark_process_patterns.jsonl")

    assert rows
    assert all(row["verification_status"] == "source_mapped_not_ingested" for row in rows)
    assert all("not infer" in row["risk"] for row in rows)


def test_workflow_synthesis_separates_fact_inference_and_verification_needs():
    text = (ROOT / "03_PROCESSED_KB" / "benchmark_intelligence" / "asperitas_best_workflow_synthesis.md").read_text(encoding="utf-8")

    assert "Implemented repo facts:" in text
    assert "Benchmark inference:" in text
    assert "Verification needs:" in text
    assert "cannot override P0/P1/P2 Asperitas facts" in text


def test_offline_vector_manifest_does_not_claim_production_vector_db():
    manifest = json.loads(
        (ROOT / "04_VECTOR_DB" / "indexes" / "P6_BENCHMARK_OPERATING" / "benchmark_development_process_index_manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["embedding_status"] == "embedded_offline_deterministic"
    assert manifest["index_status"] == "persisted_jsonl_offline_vector_artifact"
    assert manifest["production_vector_db_status"] == "not_claimed"
