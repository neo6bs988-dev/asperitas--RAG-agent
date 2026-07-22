from __future__ import annotations

import json
from pathlib import Path

from asperitas_agent.evalos.repository_adapter import (
    run_repository_no_effect_shadow,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "eval/evalos/public/v1.4_shadow_policy.json"
CASES_PATH = ROOT / "eval/evalos/public/v1.4_shadow_cases.json"


def test_actual_repository_agent_runs_in_no_effect_shadow() -> None:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    report = run_repository_no_effect_shadow(
        cases=cases,
        policy=policy,
        secret=b"repository-integration-secret",
        exact_repository_head_verified=False,
    )

    assert report["analysis"]["passed"]
    assert report["decision"]["status"] == "NO_EFFECT_SHADOW_SPEC_CANDIDATE"
    assert report["decision"]["promotion_allowed"] is False
    assert report["results"]
    assert all(row["external_effect_count"] == 0 for row in report["results"])
    assert all(row["network_egress_count"] == 0 for row in report["results"])
    assert all(row["provider_export_count"] == 0 for row in report["results"])
    assert all(row["input_mutation_count"] == 0 for row in report["results"])
    assert all(row["trace_valid"] for row in report["results"])
    assert all(row["privacy_valid"] for row in report["results"])
