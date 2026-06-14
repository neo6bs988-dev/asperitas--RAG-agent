from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ASK_AGENT = REPO_ROOT / "scripts" / "ask_agent.py"


def run_ask_agent(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(ASK_AGENT), *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_ask_agent_machine_output_is_valid_agent_response_json():
    payload = run_ask_agent("--query", "What is Asperitas?", "--top-k", "5")

    assert payload["query"] == "What is Asperitas?"
    assert payload["top_k"] == 5
    assert payload["status"] in {"answered", "caution", "abstained"}
    assert isinstance(payload["answer"], str)
    assert isinstance(payload["citations_used"], list)
    assert isinstance(payload["evidence"], list)
    assert payload["evidence_count"] == len(payload["evidence"])
    assert isinstance(payload["guardrail"], dict)
    assert payload["metadata"]["runner_version"] == "MVP-008"


def test_ask_agent_citations_are_subset_of_evidence_context():
    payload = run_ask_agent("--query", "What is Asperitas?", "--top-k", "5")
    evidence_keys = {item["citation_key"] for item in payload["evidence"]}

    assert set(payload["citations_used"]) <= evidence_keys
    assert payload["metadata"]["citation_integrity"]["citations_subset_of_evidence"]


def test_ask_agent_machine_output_is_deterministic():
    first = run_ask_agent("--query", "What is Asperitas?", "--top-k", "5")
    second = run_ask_agent("--query", "What is Asperitas?", "--top-k", "5")

    assert first == second
