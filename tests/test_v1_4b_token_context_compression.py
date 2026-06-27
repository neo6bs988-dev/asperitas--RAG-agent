from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from asperitas_agent.evidence_pack import DEFAULT_SNIPPET_CHARS, PRE_COMPRESSION_SNIPPET_CHARS, build_evidence_pack


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_v1_4b_token_context_compression.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_v1_4b_token_context_compression", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def long_result(rank: int = 1) -> dict:
    return {
        "chunk_id": f"chunk-{rank}",
        "score": 99 - rank,
        "source_id": f"ASP-P1-{rank}",
        "source_title": "Internal Source",
        "source_file": f"docs/internal-{rank}.md",
        "source_priority": "P1",
        "evidence_label": "Document-Supported Fact",
        "section": "Evidence",
        "section_heading": "Evidence",
        "section_path": ["Root", "Evidence"],
        "section_level": 2,
        "parent_section": "Root",
        "subsection": "Evidence",
        "text": " ".join(["retrieved evidence text"] * 80),
    }


def test_default_context_compression_preserves_traceability_metadata():
    pack = build_evidence_pack("query", [long_result()], top_k=1).to_json()
    item = pack["evidence_items"][0]

    assert DEFAULT_SNIPPET_CHARS < PRE_COMPRESSION_SNIPPET_CHARS
    assert len(item["text_excerpt"]) <= DEFAULT_SNIPPET_CHARS
    assert item["text_excerpt"].endswith("...")
    assert item["source_id"] == "ASP-P1-1"
    assert item["source_path"] == "docs/internal-1.md"
    assert item["source_priority"] == "P1"
    assert item["evidence_label"] == "Document-Supported Fact"
    assert item["section"] == "Evidence"
    assert item["citation_key"] == "[E1]"
    assert "[E1] Excerpt:" in pack["context_block"]


def test_explicit_precompression_cap_remains_available_for_comparison():
    compressed = build_evidence_pack("query", [long_result()], top_k=1).to_json()
    precompression = build_evidence_pack(
        "query",
        [long_result()],
        top_k=1,
        snippet_chars=PRE_COMPRESSION_SNIPPET_CHARS,
    ).to_json()

    assert len(precompression["evidence_items"][0]["text_excerpt"]) > len(compressed["evidence_items"][0]["text_excerpt"])
    assert precompression["evidence_items"][0]["citation_key"] == compressed["evidence_items"][0]["citation_key"]


def test_v1_4b_comparison_script_writes_outputs(tmp_path):
    output = tmp_path / "compression.json"
    doc = tmp_path / "compression.md"
    readme = tmp_path / "README.md"
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
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(output.read_text(encoding="utf-8"))
    stdout_report = json.loads(result.stdout)
    assert report["summary"] == stdout_report["summary"]
    assert report["ok"]
    assert report["summary"]["retrieved_context_approx_token_delta"] < 0
    assert report["summary"]["answer_approx_token_delta"] <= 0
    assert report["summary"]["citation_count_preserved"]
    assert report["summary"]["evidence_count_preserved"]
    assert report["summary"]["source_paths_preserved"]
    assert not report["regressions"]
    assert doc.exists()
    assert readme.exists()
