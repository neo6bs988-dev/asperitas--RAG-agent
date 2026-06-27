import csv
from pathlib import Path

REGISTRY = Path("00_ADMIN/source_registries/external_benchmark_source_registry.csv")
REQUIRED = ["source_id", "source_title", "source_family", "source_priority", "source_type", "evidence_type", "disclosure_level", "license_status", "license_note", "acquisition_status", "processing_status", "raw_path", "processed_path", "chunk_manifest_path", "index_status", "eval_status", "source_url", "local_path", "publisher_or_owner", "retrieval_date", "provenance_note", "allowed_use", "restricted_use", "notes"]


def main():
    rows = list(csv.DictReader(REGISTRY.open(encoding="utf-8")))
    assert rows, "empty registry"
    assert list(rows[0].keys()) == REQUIRED, "bad header"
    ids = [r["source_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate source_id"
    for row in rows:
        assert row["source_priority"] in {"P5", "P6"}
        assert row["acquisition_status"] == "registered_only"
        assert row["processing_status"] == "not_processed"
        assert row["index_status"] == "not_indexed"
        assert row["eval_status"] == "not_run"
        assert not row["raw_path"]
        assert not row["processed_path"]
        assert not row["chunk_manifest_path"]
    print(f"registry_records={len(rows)}")


if __name__ == "__main__":
    main()
