from pathlib import Path

from asperitas_agent.inventory import build_inventory
from asperitas_agent.registry import read_registry, validate_registry, write_registry
from asperitas_agent.schemas import REGISTRY_COLUMNS


def make_repo(tmp_path: Path) -> Path:
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    (tmp_path / "01_RAW_SOURCES" / "P0_ACTIVE_PROMPT").mkdir(parents=True)
    (tmp_path / "01_RAW_SOURCES" / "P0_ACTIVE_PROMPT" / "policy.md").write_text("AOS source hierarchy", encoding="utf-8")
    return tmp_path


def test_registry_schema_required_columns_exist(tmp_path):
    root = make_repo(tmp_path)
    records = build_inventory(root)
    path = write_registry(records, root, root / "data" / "source_registry.csv")
    ok, errors = validate_registry(path)

    assert ok, errors
    header = path.read_text(encoding="utf-8-sig").splitlines()[0].split(",")
    for column in REGISTRY_COLUMNS:
        assert column in header


def test_registry_missing_metadata_is_caught(tmp_path):
    bad = tmp_path / "bad_registry.csv"
    bad.write_text("source_id,path\nASP-P0-1,\n", encoding="utf-8")

    ok, errors = validate_registry(bad)

    assert not ok
    assert any("Missing required column" in error for error in errors)


def test_registry_duplicate_source_ids_are_caught(tmp_path):
    root = make_repo(tmp_path)
    records = build_inventory(root)
    records.append(records[0])
    path = write_registry(records, root, root / "data" / "source_registry.csv")

    ok, errors = validate_registry(path)

    assert not ok
    assert any("duplicate source_id" in error for error in errors)


def test_registry_invalid_enums_are_caught(tmp_path):
    root = make_repo(tmp_path)
    records = build_inventory(root)
    records[0].source_priority = "PX"
    records[0].parse_status = "done"
    path = write_registry(records, root, root / "data" / "source_registry.csv")

    ok, errors = validate_registry(path)

    assert not ok
    assert any("invalid source_priority" in error for error in errors)
    assert any("invalid parse_status" in error for error in errors)


def test_registry_unsafe_paths_are_caught(tmp_path):
    root = make_repo(tmp_path)
    records = build_inventory(root)
    records[0].path = "../outside.txt"
    path = write_registry(records, root, root / "data" / "source_registry.csv")

    ok, errors = validate_registry(path)

    assert not ok
    assert any("unsafe relative path" in error for error in errors)


def test_read_registry_ignores_future_extra_columns(tmp_path):
    root = make_repo(tmp_path)
    records = build_inventory(root)
    path = write_registry(records, root, root / "data" / "source_registry.csv")
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    lines[0] += ",future_column"
    lines[1] += ",future_value"
    path.write_text("\n".join(lines), encoding="utf-8-sig")

    loaded = read_registry(path)

    assert loaded
    assert loaded[0].source_id == records[0].source_id
