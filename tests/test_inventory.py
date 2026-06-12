from pathlib import Path

from asperitas_agent.inventory import build_inventory, discover_raw_sources


def test_inventory_discovers_raw_sources_with_relative_paths(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    raw = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    raw.mkdir(parents=True)
    (raw / "internal.txt").write_text("internal source", encoding="utf-8")

    files = discover_raw_sources(tmp_path)
    records = build_inventory(tmp_path)

    assert len(files) == 1
    assert any(record.path == "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/internal.txt" for record in records)
    assert all("\\" not in record.path for record in records)
    assert all(record.checksum for record in records)


def test_duplicate_content_in_different_paths_gets_distinct_source_ids(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    first = tmp_path / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL"
    second = tmp_path / "01_RAW_SOURCES" / "P1_RND_PROJECTS"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "same.txt").write_text("same content", encoding="utf-8")
    (second / "same.txt").write_text("same content", encoding="utf-8")

    records = [record for record in build_inventory(tmp_path) if record.original_filename == "same.txt"]

    assert len(records) == 2
    assert len({record.checksum for record in records}) == 1
    assert len({record.source_id for record in records}) == 2
