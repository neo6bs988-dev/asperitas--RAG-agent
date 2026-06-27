from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_v1_4c_latency_eval_harness_caching.py"
CACHE_MODULE = REPO_ROOT / "scripts" / "eval_harness_cache.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_registry(path: Path, source_id: str) -> None:
    fieldnames = [
        "source_id",
        "title",
        "path",
        "original_filename",
        "source_type",
        "source_priority",
        "disclosure_level",
        "license_status",
        "verification_status",
        "parse_status",
        "checksum",
        "notes",
        "use_case",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "source_id": source_id,
                "title": "Title",
                "path": "docs/source.md",
                "original_filename": "source.md",
                "source_type": "md",
                "source_priority": "P1",
                "disclosure_level": "internal",
                "license_status": "owned",
                "verification_status": "verified",
                "parse_status": "parsed",
                "checksum": "a" * 64,
                "notes": "",
                "use_case": "",
            }
        )


def test_file_cache_uses_path_metadata_and_invalidates_on_mutation(tmp_path, monkeypatch):
    cache = load_module("eval_harness_cache_test_invalidation", CACHE_MODULE)
    monkeypatch.setenv("ASPERITAS_EVAL_CACHE", "1")
    path = tmp_path / "source_registry.csv"
    write_registry(path, "ASP-1")

    first = cache.read_registry_cached(path)
    second = cache.read_registry_cached(path)

    assert first[0].source_id == "ASP-1"
    assert second[0].source_id == "ASP-1"
    assert cache.cache_stats()["file_cache_hits"] == 1

    time.sleep(0.01)
    write_registry(path, "ASP-2")
    third = cache.read_registry_cached(path)

    assert third[0].source_id == "ASP-2"
    assert cache.cache_stats()["file_cache_misses"] == 2


def test_cache_can_be_bypassed_with_environment_flag(tmp_path, monkeypatch):
    cache = load_module("eval_harness_cache_test_bypass", CACHE_MODULE)
    monkeypatch.setenv("ASPERITAS_EVAL_CACHE", "0")
    path = tmp_path / "source_registry.csv"
    write_registry(path, "ASP-1")

    cache.read_registry_cached(path)
    cache.read_registry_cached(path)

    assert cache.cache_stats()["file_cache_hits"] == 0
    assert cache.cache_stats()["file_cache_misses"] == 0


def test_evidence_pack_cache_returns_independent_copies(monkeypatch):
    cache = load_module("eval_harness_cache_test_evidence", CACHE_MODULE)
    monkeypatch.setenv("ASPERITAS_EVAL_CACHE", "1")
    result = {
        "chunk_id": "chunk-1",
        "source_id": "ASP-P1",
        "source_file": "docs/source.md",
        "source_title": "Source",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": "Section",
        "text": "source backed evidence",
        "score": 10.0,
    }

    first = cache.build_evidence_pack_cached("query", [result], top_k=1)
    first.evidence_items[0].source_id = "mutated"
    second = cache.build_evidence_pack_cached("query", [result], top_k=1)

    assert second.evidence_items[0].source_id == "ASP-P1"
    assert cache.cache_stats()["evidence_pack_cache_hits"] == 1


def test_v1_4c_script_writes_outputs(tmp_path):
    output = tmp_path / "latency.json"
    doc = tmp_path / "latency.md"
    readme = tmp_path / "README.md"
    env = dict(os.environ)
    env["ASPERITAS_EVAL_CACHE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--overwrite",
            "--json",
            "--output",
            str(output),
            "--doc-output",
            str(doc),
            "--readme-output",
            str(readme),
        ],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(output.read_text(encoding="utf-8"))
    stdout_report = json.loads(result.stdout)
    assert report["summary"] == stdout_report["summary"]
    assert report["ok"]
    assert report["summary"]["cache_hit_count"] > 0
    assert report["scope_lock"]["eval_harness_only"] is True
    assert report["scope_lock"]["answer_behavior_changed"] is False
    assert report["scope_lock"]["retrieval_scoring_changed"] is False
    assert report["scope_lock"]["source_artifacts_mutated"] is False
    assert doc.exists()
    assert readme.exists()
