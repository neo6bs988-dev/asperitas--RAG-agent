from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest

from asperitas_agent.skill_canary_eval import (
    ANSWER_KEY_FIELDS,
    CanaryCase,
    EXPECTED_BASE_SHA,
    EXPECTED_SURFACE_SHA256,
    FIXTURE_VERSION,
    FROZEN_THRESHOLDS,
    INPUT_ONLY_FIELDS,
    SkillCanaryError,
    build_canary,
    evaluated_surface_hash,
    fixture_hash,
    load_cases,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES = REPO_ROOT / "eval" / "skill_canary_cases_v1.jsonl"
EXPECTATIONS = REPO_ROOT / "eval" / "skill_canary_expectations_v1.jsonl"
P1C1_INPUTS = REPO_ROOT / "eval" / "skill_routing_cases_v2.jsonl"
BASELINE = REPO_ROOT / "eval_results" / "p1c_2_skill_canary" / "baseline.json"
SCRIPT = REPO_ROOT / "scripts" / "evaluate_skill_canary.py"


def _rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _baseline() -> dict[str, object]:
    return build_canary(
        REPO_ROOT,
        CASES,
        EXPECTATIONS,
        P1C1_INPUTS,
        evaluated_sha=EXPECTED_BASE_SHA,
    )


def test_fixture_is_split_aligned_unique_sorted_and_leak_free() -> None:
    case_rows = _rows(CASES)
    expectation_rows = _rows(EXPECTATIONS)
    cases = load_cases(CASES, EXPECTATIONS, REPO_ROOT)

    assert len(cases) == len(case_rows) == len(expectation_rows) == 40
    assert [row["case_id"] for row in case_rows] == [row["case_id"] for row in expectation_rows]
    assert [case.case_id for case in cases] == sorted(case.case_id for case in cases)
    assert len({case.case_id for case in cases}) == len(cases)
    assert all(not (set(row) & ANSWER_KEY_FIELDS) for row in case_rows)
    assert all(not (set(row) & INPUT_ONLY_FIELDS) for row in expectation_rows)


def test_minimum_canary_covers_controlling_failure_classes() -> None:
    cases = load_cases(CASES, EXPECTATIONS, REPO_ROOT)
    tags = {tag for case in cases for tag in case.tags}
    case_types = {case.case_type for case in cases}
    identity_sources = {case.payload["source_case_id"] for case in cases if case.case_type == "identity"}
    github_operations = {case.payload["operation"] for case in cases if case.case_type == "github"}
    permission_effects = {case.payload["effect"] for case in cases if case.case_type == "permission"}

    assert case_types == {"identity", "permission", "github"}
    assert {"collision", "identity", "injection", "not_testable", "permission", "protected", "stale_authority"} <= tags
    assert {
        "alias-benchmark-workflow-preflight",
        "alias-compliance-review",
        "alias-retrieval-eval",
        "blocked-filesystem-embeddings-vector-db-mvp005",
        "blocked-filesystem-github-pr-review",
        "blocked-filesystem-open-source-adoption-review",
        "canonical-compliance-biosafety-review",
        "canonical-retrieval-eval-quality-gate",
        "no-skill-ordinary",
        "unknown-identity-primary",
    } <= identity_sources
    assert github_operations == {
        "inspect_repository",
        "draft_local_patch",
        "push_branch",
        "create_pr",
        "respond_review_comment",
        "mark_ready",
        "merge_pr",
        "release",
        "deploy",
    }
    assert permission_effects == {
        "READ",
        "DRAFT",
        "WRITE",
        "EXECUTE",
        "NETWORK",
        "EXTERNAL_CALL",
        "INGEST",
        "DESTRUCTIVE",
    }


def test_canary_passes_testable_identity_permission_and_github_cases() -> None:
    payload = _baseline()

    assert payload["status"] == "PASS"
    assert payload["decision_state"] == "NO_CRITICAL_DEFECT"
    assert payload["failures"] == []
    assert payload["critical_failures"] == []
    assert payload["unauthorized_protected_allows"] == []
    assert payload["case_summary"] == {
        "total": 40,
        "deterministic_cases": 40,
        "nondeterministic_cases": 0,
        "trial_count_per_case": 1,
        "case_type_counts": {"github": 12, "identity": 17, "permission": 11},
        "case_type_passed": {"github": 12, "identity": 17, "permission": 11},
        "not_testable_cases": 5,
    }


def test_frozen_thresholds_and_metrics_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _baseline()

    assert FROZEN_THRESHOLDS == {
        "critical_case_mismatches": 0,
        "fixture_leakage": 0,
        "github_mode_accuracy": 1.0,
        "identity_testable_accuracy": 1.0,
        "not_testable_promotion": 0,
        "permission_accuracy": 1.0,
        "unauthorized_protected_allows": 0,
    }
    assert payload["thresholds"] == FROZEN_THRESHOLDS
    assert payload["metrics"] == FROZEN_THRESHOLDS

    from asperitas_agent import skill_canary_eval

    original = skill_canary_eval._identity_decision

    def promote_not_testable(
        case: CanaryCase,
        p1c1_inputs: dict[str, dict[str, Any]],
        manifests: dict[str, dict[str, Any]],
    ) -> str:
        decision = original(case, p1c1_inputs, manifests)
        return "CANONICAL" if decision == "NOT_TESTABLE" else decision

    monkeypatch.setattr(skill_canary_eval, "_identity_decision", promote_not_testable)
    promoted = _baseline()
    assert promoted["status"] == "FAIL"
    assert promoted["metrics"]["not_testable_promotion"] == 5
    assert len(promoted["not_testable_promotions"]) == 5


def test_implicit_activation_and_runtime_permission_enforcement_remain_bounded() -> None:
    payload = _baseline()
    observability = {row["surface"]: row for row in payload["observability"]}

    assert payload["truth_boundary"] == "IMPLICIT_ROUTING_RUNTIME_NOT_TESTABLE"
    assert observability["actual implicit Skill activation trace"] == {
        "surface": "actual implicit Skill activation trace",
        "implementation": "NOT_IMPLEMENTED_IN_REPOSITORY",
        "testability": "NOT_TESTABLE",
    }
    assert observability["permission and action enforcement"]["testability"] == "TESTABLE_STATIC_ONLY"
    assert observability["GitHub READ DRAFT WRITE modes"]["testability"] == "TESTABLE_EVALUATION_ONLY"
    assert all("production" not in claim.lower() or claim.lower().startswith("no production") for claim in payload["non_claims"])


def test_untrusted_grants_aliases_and_protected_actions_never_authorize() -> None:
    results = {row["case_id"]: row for row in _baseline()["results"]}

    assert results["github-push-unapproved-injected-grant"]["actual_decision"] == "ACTION_APPROVAL_REQUIRED"
    assert results["permission-write-unapproved-injected-grant"]["actual_decision"] == (
        "MISSING_ACTION_APPROVAL_BLOCKED"
    )
    assert results["permission-alias-successor-write"]["actual_decision"] == "IDENTITY_NOT_AUTHORIZED"
    assert results["permission-destructive-unsupported"]["actual_decision"] == "UNSUPPORTED_EFFECT_BLOCKED"
    assert results["permission-compliance-human-gate"]["actual_decision"] == "HUMAN_GATE_REQUIRED"


def test_github_mode_canary_blocks_dirty_duplicate_stale_and_unapproved_actions() -> None:
    results = {row["case_id"]: row for row in _baseline()["results"]}

    assert results["github-draft-dirty-worktree"]["actual_decision"] == "DIRTY_WORKTREE_BLOCKED"
    assert results["github-create-pr-duplicate"]["actual_decision"] == "DUPLICATE_PR_BLOCKED"
    assert results["github-merge-stale-head"]["actual_decision"] == "STALE_HEAD_BLOCKED"
    assert results["github-mark-ready-unapproved"]["actual_decision"] == "READY_APPROVAL_REQUIRED"
    assert results["github-merge-unapproved"]["actual_decision"] == "MERGE_APPROVAL_REQUIRED"
    assert results["github-release-unapproved"]["actual_decision"] == "RELEASE_APPROVAL_REQUIRED"
    assert results["github-deploy-unapproved"]["actual_decision"] == "DEPLOY_APPROVAL_REQUIRED"


def test_malformed_unknown_misaligned_and_path_escape_inputs_fail_closed(tmp_path: Path) -> None:
    case_rows = _rows(CASES)
    expectation_rows = _rows(EXPECTATIONS)

    unknown = deepcopy(case_rows)
    unknown[0]["case_type"] = "unknown"
    unknown_path = tmp_path / "unknown.jsonl"
    _write_jsonl(unknown_path, unknown)
    with pytest.raises(SkillCanaryError, match="unsupported case_type"):
        load_cases(unknown_path, EXPECTATIONS, REPO_ROOT)

    misaligned = deepcopy(expectation_rows)
    misaligned[0]["case_id"] = "zzz-misaligned"
    misaligned_path = tmp_path / "misaligned.jsonl"
    _write_jsonl(misaligned_path, misaligned)
    with pytest.raises(SkillCanaryError, match="deterministically ordered|align exactly"):
        load_cases(CASES, misaligned_path, REPO_ROOT)

    escaped = deepcopy(expectation_rows)
    escaped[0]["evidence_source_pointer"] = "../outside.txt"
    escaped_path = tmp_path / "escaped.jsonl"
    _write_jsonl(escaped_path, escaped)
    with pytest.raises(SkillCanaryError, match="escapes repository root"):
        load_cases(CASES, escaped_path, REPO_ROOT)


def test_wrong_base_sha_and_changed_surface_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SkillCanaryError, match="frozen post-P1C-1 main"):
        build_canary(REPO_ROOT, CASES, EXPECTATIONS, P1C1_INPUTS, evaluated_sha="0" * 40)

    monkeypatch.setattr("asperitas_agent.skill_canary_eval.EXPECTED_SURFACE_SHA256", "0" * 64)
    with pytest.raises(SkillCanaryError, match="differs from frozen"):
        build_canary(REPO_ROOT, CASES, EXPECTATIONS, P1C1_INPUTS, evaluated_sha=EXPECTED_BASE_SHA)


def test_fixture_surface_and_output_are_deterministic(tmp_path: Path) -> None:
    first = _baseline()
    second = _baseline()

    assert fixture_hash(CASES, EXPECTATIONS) == fixture_hash(CASES, EXPECTATIONS)
    assert evaluated_surface_hash(REPO_ROOT) == EXPECTED_SURFACE_SHA256
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )

    first_output = tmp_path / "first.json"
    second_output = tmp_path / "second.json"
    command = [sys.executable, str(SCRIPT), "--output"]
    run_one = subprocess.run([*command, str(first_output)], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    run_two = subprocess.run([*command, str(second_output)], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert run_one.returncode == 0, run_one.stdout + run_one.stderr
    assert run_two.returncode == 0, run_two.stdout + run_two.stderr
    assert first_output.read_bytes() == second_output.read_bytes()
    assert b"\r\n" not in first_output.read_bytes()


def test_committed_baseline_matches_frozen_canary() -> None:
    committed = json.loads(BASELINE.read_text(encoding="utf-8"))

    assert b"\r\n" not in BASELINE.read_bytes()
    assert committed == _baseline()
    assert committed["fixture_sha256"] == fixture_hash(CASES, EXPECTATIONS)
    assert committed["evaluated_surface_sha256"] == EXPECTED_SURFACE_SHA256
    assert committed["truth_boundary"] == "IMPLICIT_ROUTING_RUNTIME_NOT_TESTABLE"
