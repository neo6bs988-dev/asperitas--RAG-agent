from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from asperitas_agent.chunking import read_chunks
from asperitas_agent.registry import read_registry
from asperitas_agent.retrieval_mvp003 import score_candidate, search_chunks_mvp003
from scripts.calibrate_v1_3b_retrieval_quality import SCHEMA_VERSION, build_calibration_report


REPO_ROOT = Path(__file__).resolve().parents[1]


def _records_and_chunks():
    return read_registry(REPO_ROOT / "data" / "source_registry.csv"), read_chunks(REPO_ROOT / "data" / "chunks.jsonl")


def test_calibration_report_schema_and_measured_delta():
    report = build_calibration_report()

    assert report["schema_version"] == SCHEMA_VERSION
    assert report["answer_generation_changed"] is False
    assert report["prompt_or_answer_contract_changed"] is False
    assert report["source_artifacts_mutated"] is False
    assert report["embedding_vector_or_reranker_changed"] is False
    assert report["improvement_proven_by_diagnostics"] is True
    assert report["after_summary"]["total_expected_hits_at_5"] >= report["before_summary"]["total_expected_hits_at_5"]
    assert report["after_summary"]["retrieval_miss_flag_count"] <= report["before_summary"]["retrieval_miss_flag_count"]


def test_direct_source_reference_boost_orders_agents_md_first():
    records, chunks = _records_and_chunks()

    results = search_chunks_mvp003(
        "According to AGENTS.md, what source priority rules should the agent follow?",
        chunks,
        records,
        limit=5,
    )

    assert results
    assert results[0].source_file == "AGENTS.md"
    assert results[0].score_components["direct_source_reference_bonus"] > 0


def test_status_readiness_boost_surfaces_v1_status_docs():
    records, chunks = _records_and_chunks()

    results = search_chunks_mvp003(
        "Can we describe the current Asperitas agent as production deployed and biologically validated?",
        chunks,
        records,
        limit=5,
    )
    paths = {result.source_file for result in results}

    assert "docs/V1_KNOWN_LIMITATIONS.md" in paths
    assert "docs/V1_RELEASE_CLOSEOUT.md" in paths
    assert "docs/EVALS.md" in paths
    assert any(result.score_components["v1_status_readiness_bonus"] > 0 for result in results)


def test_section_heading_bonus_is_deterministic_for_matching_section():
    records, chunks = _records_and_chunks()
    record = next(record for record in records if record.path == "docs/evals/V1_2_FAILURE_TAXONOMY.md")
    chunk = next(chunk for chunk in chunks if chunk.source_id == record.source_id and chunk.section)

    first = score_candidate(f"{chunk.section} scoring taxonomy", chunk, record)
    second = score_candidate(f"{chunk.section} scoring taxonomy", chunk, record)

    assert first.score == second.score
    assert first.score_components["section_heading_bonus"] > 0


def test_cli_writes_deterministic_report(tmp_path: Path):
    output = tmp_path / "retrieval_quality_before_after.json"
    command = [
        sys.executable,
        "scripts/calibrate_v1_3b_retrieval_quality.py",
        "--output",
        str(output),
        "--overwrite",
        "--json",
    ]

    first = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    second = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")

    assert json.loads(first.stdout) == json.loads(second.stdout)
    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(second.stdout)


def test_no_answer_generation_prompt_or_source_artifact_mutation():
    result = subprocess.run(["git", "diff", "--name-only"], check=True, capture_output=True, text=True)
    forbidden = (
        "src/asperitas_agent/answer_generation.py",
        "src/asperitas_agent/agent_runner.py",
        "src/asperitas_agent/rag.py",
        "data/source_registry.csv",
        "data/chunks.jsonl",
        "01_RAW_SOURCES/",
        "03_PROCESSED_KB/chunks/",
        "04_VECTOR_DB/",
    )
    changed = tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())

    assert not [path for path in changed if path in forbidden or path.startswith(forbidden)]
