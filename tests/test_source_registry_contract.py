import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "02_SOURCE_REGISTRY"
SCHEMA_PATH = REGISTRY_DIR / "source_registry.schema.json"
EXAMPLE_PATH = REGISTRY_DIR / "source_registry.example.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_registry_files_parse_as_json() -> None:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)

    assert schema["schema_version"] == "v11.1"
    assert example["schema_version"] == "v11.1"
    assert isinstance(example["entries"], list)
    assert example["entries"]


def test_example_entries_include_schema_required_fields() -> None:
    schema = load_json(SCHEMA_PATH)
    example = load_json(EXAMPLE_PATH)
    required = set(schema["$defs"]["source_registry_entry"]["required"])

    for entry in example["entries"]:
        missing = required - set(entry)
        assert not missing, f"{entry.get('source_id')} missing fields: {sorted(missing)}"


def test_candidate_entries_are_not_enabled_for_downstream_use() -> None:
    example = load_json(EXAMPLE_PATH)

    for entry in example["entries"]:
        if entry["registry_status"] == "candidate":
            assert entry["ingestion_allowed"] is False
            assert entry["embedding_allowed"] is False
            assert entry["kg_allowed"] is False
            assert entry["external_output_allowed"] is False


def test_unreviewed_license_entries_block_external_output() -> None:
    example = load_json(EXAMPLE_PATH)
    gated_license_statuses = {"unknown", "pending_review", "blocked"}

    for entry in example["entries"]:
        if entry["license_status"] in gated_license_statuses:
            assert entry["embedding_allowed"] is False
            assert entry["external_output_allowed"] is False
