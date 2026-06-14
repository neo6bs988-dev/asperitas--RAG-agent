from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ask_agent.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_ask_agent_cli_outputs_valid_pretty_json():
    result = run_cli("--query", "What is Asperitas?", "--top-k", "5", "--pretty")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["query"] == "What is Asperitas?"
    assert payload["top_k"] == 5
    assert payload["status"] in {"answered", "caution", "abstained"}
    assert isinstance(payload["evidence"], list)
    assert payload["metadata"]["runner_version"] == "MVP-008"


def test_ask_agent_cli_is_deterministic_for_same_query():
    first = run_cli("--query", "What is Asperitas?", "--top-k", "5", "--pretty")
    second = run_cli("--query", "What is Asperitas?", "--top-k", "5", "--pretty")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout


def test_ask_agent_cli_empty_query_fails_cleanly():
    result = run_cli("--query", "   ", "--top-k", "5")

    assert result.returncode == 2
    assert "--query must not be empty" in result.stderr


def test_ask_agent_cli_invalid_top_k_fails_cleanly():
    result = run_cli("--query", "What is Asperitas?", "--top-k", "0")

    assert result.returncode == 2
    assert "--top-k must be positive" in result.stderr
