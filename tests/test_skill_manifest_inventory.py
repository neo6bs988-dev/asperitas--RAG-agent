from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Callable

import pytest

from asperitas_agent.skill_contract import validate_repository
from asperitas_agent.skill_discovery import discover_skill_files
from asperitas_agent.skill_registry import DEFAULT_SKILL_REGISTRY, SKILL_IDENTITY_ALIASES


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILL_COUNT = 30
FILESYSTEM_ONLY_SKILLS = {
    "embeddings-vector-db-mvp005",
    "github-pr-review",
    "open-source-adoption-review",
}
COMPATIBILITY_TARGETS = {
    "benchmark_workflow_preflight": "mvp-implementation",
    "compliance_review": "compliance-biosafety-review",
    "retrieval_eval": "retrieval-eval-quality-gate",
}
PROTECTED_EFFECTS = {
    "WRITE": "write_allowed",
    "EXECUTE": "execution_allowed",
    "NETWORK": "network_allowed",
    "EXTERNAL_CALL": "external_call_allowed",
    "INGEST": "ingestion_allowed",
    "DESTRUCTIVE": "destructive_allowed",
}
ACTION_EFFECTS = {
    "add_decision_log": frozenset({"WRITE"}),
    "add_focused_tests": frozenset({"WRITE"}),
    "block_autonomous_execution": frozenset({"DRAFT"}),
    "block_new_dependency_without_review": frozenset({"DRAFT"}),
    "block_unreviewed_external_calls": frozenset({"DRAFT"}),
    "block_unsafe_claims": frozenset({"DRAFT"}),
    "block_unsupported_performance_claims": frozenset({"DRAFT"}),
    "check_baseline_metrics": frozenset({"READ"}),
    "check_citation_targets": frozenset({"READ"}),
    "check_evidence_labels": frozenset({"READ"}),
    "check_license_and_security_status": frozenset({"READ"}),
    "check_license_status": frozenset({"READ"}),
    "check_no_secrets": frozenset({"READ"}),
    "check_prompt_injection_risk": frozenset({"READ"}),
    "check_required_artifacts": frozenset({"READ"}),
    "check_secrets_and_scope": frozenset({"READ"}),
    "check_security_status": frozenset({"READ"}),
    "check_source_ids": frozenset({"READ"}),
    "check_source_text_not_instruction": frozenset({"READ"}),
    "classify_adoption_level": frozenset({"DRAFT"}),
    "classify_adoption_type": frozenset({"DRAFT"}),
    "classify_architecture_impact": frozenset({"DRAFT"}),
    "classify_compliance_risk": frozenset({"DRAFT"}),
    "classify_risk": frozenset({"DRAFT"}),
    "compare_local_metrics": frozenset({"READ"}),
    "compare_metrics": frozenset({"READ"}),
    "compare_retrieval_metrics": frozenset({"READ"}),
    "define_deterministic_fallback": frozenset({"DRAFT"}),
    "define_eval_scope": frozenset({"DRAFT"}),
    "flag_external_call_risk": frozenset({"DRAFT"}),
    "flag_hallucination_risk": frozenset({"DRAFT"}),
    "flag_license_review": frozenset({"DRAFT"}),
    "flag_provenance_gaps": frozenset({"DRAFT"}),
    "flag_security_review": frozenset({"DRAFT"}),
    "flag_unsupported_claims": frozenset({"DRAFT"}),
    "inspect_files": frozenset({"READ"}),
    "label_metric_provenance": frozenset({"DRAFT"}),
    "make_local_code_change": frozenset({"WRITE"}),
    "prepare_pr_summary": frozenset({"DRAFT"}),
    "preserve_historical_logs": frozenset({"DRAFT"}),
    "preserve_human_approval_gate": frozenset({"DRAFT"}),
    "preserve_ingestion_gate": frozenset({"DRAFT"}),
    "preserve_mvp003_default": frozenset({"DRAFT"}),
    "preserve_retrieval_defaults": frozenset({"DRAFT"}),
    "preserve_runtime_behavior": frozenset({"DRAFT"}),
    "preserve_source_grounding": frozenset({"DRAFT"}),
    "preserve_stage_boundary": frozenset({"DRAFT"}),
    "preserve_worktree": frozenset({"DRAFT"}),
    "prevent_performance_overclaims": frozenset({"DRAFT"}),
    "record_audit_trace": frozenset({"DRAFT"}),
    "record_decision_log": frozenset({"WRITE"}),
    "record_reference_metadata": frozenset({"DRAFT"}),
    "report_findings": frozenset({"DRAFT"}),
    "report_regressions": frozenset({"DRAFT"}),
    "report_residual_risks": frozenset({"DRAFT"}),
    "report_skipped_checks": frozenset({"DRAFT"}),
    "report_verification": frozenset({"DRAFT"}),
    "require_eval_for_claims": frozenset({"DRAFT"}),
    "require_human_approval": frozenset({"DRAFT"}),
    "require_retrieval_eval": frozenset({"DRAFT"}),
    "review_connector_metadata": frozenset({"READ"}),
    "review_dependency_metadata": frozenset({"READ"}),
    "review_embedding_vector_design": frozenset({"READ"}),
    "review_external_source_metadata": frozenset({"READ"}),
    "review_git_diff": frozenset({"READ"}),
    "review_rag_scope": frozenset({"READ"}),
    "review_retrieval_change": frozenset({"READ"}),
    "review_source_metadata": frozenset({"READ"}),
    "review_tests_and_evals": frozenset({"READ"}),
    "review_trace_requirements": frozenset({"READ"}),
    "review_workflow_contract": frozenset({"READ"}),
    "run_local_eval_command": frozenset({"EXECUTE"}),
    "summarize_mvp_closeout": frozenset({"DRAFT"}),
    "summarize_scope": frozenset({"DRAFT"}),
    "summarize_tests": frozenset({"DRAFT"}),
    "update_docs": frozenset({"WRITE"}),
    "update_governance_docs": frozenset({"WRITE"}),
}


def _manifests() -> list[Path]:
    return sorted((REPO_ROOT / ".agents" / "skills").glob("*/skill.contract.json"))


def _load_manifests() -> dict[str, dict[str, object]]:
    return {
        path.parent.name: json.loads(path.read_text(encoding="utf-8"))
        for path in _manifests()
    }


def _inventory_mismatches(skills_root: Path) -> tuple[set[str], set[str]]:
    skill_directories = {
        path.parent.relative_to(skills_root).as_posix()
        for path in skills_root.glob("*/SKILL.md")
    }
    manifest_directories = {
        path.parent.relative_to(skills_root).as_posix()
        for path in skills_root.glob("*/skill.contract.json")
    }
    return skill_directories - manifest_directories, manifest_directories - skill_directories


def _assert_capability_consistency(contract: dict[str, object]) -> None:
    permissions = contract["permissions"]
    actions = permissions["allowed_actions"]
    unknown_actions = sorted(set(actions) - ACTION_EFFECTS.keys())
    assert not unknown_actions, f"unknown allowed action IDs: {unknown_actions}"

    required_effects = set().union(*(ACTION_EFFECTS[action] for action in actions))
    for effect, permission_flag in PROTECTED_EFFECTS.items():
        expected = effect in required_effects
        assert permissions[permission_flag] is expected, (
            f"{permission_flag} must be {expected} for effects {sorted(required_effects)}"
        )

    protected_effects = sorted(required_effects & PROTECTED_EFFECTS.keys())
    if not protected_effects:
        return

    assert contract["risk"]["risk_class"] == "high", (
        f"protected effects require high risk: {protected_effects}"
    )
    assert permissions["approval_required"] is True, (
        f"protected effects require approval: {protected_effects}"
    )
    assert contract["risk"]["human_gates"], (
        f"protected effects require a human gate: {protected_effects}"
    )
    assert contract["routing"]["implicit_activation"] is False, (
        f"protected effects require explicit activation: {protected_effects}"
    )
    if "WRITE" in required_effects:
        assert "WRITE" in contract["modes"], "WRITE effect requires WRITE mode"


def _capability_probe(action: str, effect: str) -> dict[str, object]:
    contract = deepcopy(next(iter(_load_manifests().values())))
    contract["routing"]["implicit_activation"] = False
    contract["modes"] = ["READ", "DRAFT"]
    contract["risk"] = {
        "risk_class": "high",
        "human_gates": ["Explicit action-specific human approval is required."],
    }
    contract["permissions"].update(
        {
            "approval_required": True,
            "external_call_allowed": False,
            "network_allowed": False,
            "execution_allowed": False,
            "ingestion_allowed": False,
            "write_allowed": False,
            "destructive_allowed": False,
            "allowed_actions": [action],
        }
    )
    if effect == "WRITE":
        contract["modes"].append("WRITE")
    contract["permissions"][PROTECTED_EFFECTS[effect]] = True
    return contract


def test_every_discovered_skill_has_exactly_one_manifest() -> None:
    discovered = discover_skill_files(REPO_ROOT)
    manifests = _manifests()

    assert len(discovered) == EXPECTED_SKILL_COUNT
    assert len(manifests) == EXPECTED_SKILL_COUNT
    assert {skill.directory_name for skill in discovered} == {path.parent.name for path in manifests}
    assert all(len(list(path.parent.glob("skill.contract.json"))) == 1 for path in manifests)


def test_inventory_fails_closed_for_missing_and_orphan_manifests(tmp_path: Path) -> None:
    skills_root = tmp_path / ".agents" / "skills"
    live = skills_root / "live-skill"
    orphan = skills_root / "orphan-skill"
    live.mkdir(parents=True)
    orphan.mkdir()
    (live / "SKILL.md").write_text(
        "---\nname: live-skill\ndescription: Inventory probe.\n---\n",
        encoding="utf-8",
    )
    (orphan / "skill.contract.json").write_text("{}\n", encoding="utf-8")

    missing, orphaned = _inventory_mismatches(skills_root)

    assert missing == {"live-skill"}
    assert orphaned == {"orphan-skill"}


def test_manifest_identities_and_aliases_are_unique_and_resolved() -> None:
    manifests = _load_manifests()
    canonical_ids = {str(contract["skill_id"]) for contract in manifests.values()}
    aliases: dict[str, str] = {}

    assert len(canonical_ids) == EXPECTED_SKILL_COUNT
    for directory_name, contract in manifests.items():
        canonical_id = directory_name.replace("-", "_")
        assert contract["skill_id"] == canonical_id
        for alias in contract["compatibility"]["aliases"]:
            value = alias["value"]
            assert value not in aliases
            assert value not in canonical_ids
            assert value != canonical_id
            assert alias["replaced_by"] in canonical_ids
            aliases[value] = alias["replaced_by"]

    assert aliases == {
        alias: target.replace("-", "_")
        for alias, target in COMPATIBILITY_TARGETS.items()
    }


def test_registry_relationships_remain_explicit_without_runtime_registration() -> None:
    manifests = _load_manifests()
    registered_before = DEFAULT_SKILL_REGISTRY.list_skill_ids()
    registered_ids = set(registered_before)

    assert {alias.legacy_id: alias.canonical_id.replace("_", "-") for alias in SKILL_IDENTITY_ALIASES} == (
        COMPATIBILITY_TARGETS
    )
    assert FILESYSTEM_ONLY_SKILLS.isdisjoint(
        {skill_id.replace("_", "-") for skill_id in registered_ids}
    )
    for skill_name in FILESYSTEM_ONLY_SKILLS:
        contract = manifests[skill_name]
        assert contract["lifecycle"]["status"] == "unregistered_review_required"
        assert contract["routing"]["implicit_activation"] is False
        assert contract["permissions"]["write_allowed"] is False
        assert contract["permissions"]["network_allowed"] is False
        assert contract["permissions"]["execution_allowed"] is False
        assert contract["permissions"]["ingestion_allowed"] is False

    assert DEFAULT_SKILL_REGISTRY.list_skill_ids() == registered_before


def test_repository_validation_passes_with_reconciled_identity_authority() -> None:
    transition = validate_repository(REPO_ROOT, transition=True)
    strict = validate_repository(REPO_ROOT)

    assert transition.state == "PASS"
    assert transition.contracts_checked == EXPECTED_SKILL_COUNT
    assert transition.skills_discovered == EXPECTED_SKILL_COUNT
    assert transition.findings == ()
    assert strict.state == "PASS"
    assert strict.contracts_checked == EXPECTED_SKILL_COUNT
    assert strict.findings == ()


def test_action_taxonomy_covers_all_live_manifests_and_capabilities_are_consistent() -> None:
    manifests = _load_manifests()
    live_actions = {
        action
        for contract in manifests.values()
        for action in contract["permissions"]["allowed_actions"]
    }

    assert sorted(ACTION_EFFECTS) == sorted(live_actions)
    for directory_name in sorted(manifests):
        _assert_capability_consistency(manifests[directory_name])


@pytest.mark.parametrize("skill_name", ["docs-only-governance-update", "decision-log-maintainer"])
def test_write_skills_cannot_activate_implicitly(skill_name: str) -> None:
    contract = deepcopy(_load_manifests()[skill_name])
    contract["routing"]["implicit_activation"] = True

    with pytest.raises(AssertionError, match="protected effects require explicit activation"):
        _assert_capability_consistency(contract)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda contract: contract["modes"].remove("WRITE"), "WRITE effect requires WRITE mode"),
        (
            lambda contract: contract["permissions"].update(write_allowed=False),
            "write_allowed must be True",
        ),
        (
            lambda contract: contract["permissions"].update(approval_required=False),
            "protected effects require approval",
        ),
        (
            lambda contract: contract["risk"].update(human_gates=[]),
            "protected effects require a human gate",
        ),
    ],
)
def test_write_action_rejects_missing_gate(
    mutation: Callable[[dict[str, object]], object], message: str
) -> None:
    contract = _capability_probe("update_governance_docs", "WRITE")
    mutation(contract)

    with pytest.raises(AssertionError, match=message):
        _assert_capability_consistency(contract)


@pytest.mark.parametrize(
    ("action", "effect", "permission_flag"),
    [
        ("run_local_eval_command", "EXECUTE", "execution_allowed"),
        ("probe_network_action", "NETWORK", "network_allowed"),
        ("probe_external_call_action", "EXTERNAL_CALL", "external_call_allowed"),
        ("probe_ingestion_action", "INGEST", "ingestion_allowed"),
        ("probe_destructive_action", "DESTRUCTIVE", "destructive_allowed"),
    ],
)
def test_protected_action_rejects_false_permission(
    action: str, effect: str, permission_flag: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(ACTION_EFFECTS, action, frozenset({effect}))
    contract = _capability_probe(action, effect)
    contract["permissions"][permission_flag] = False

    with pytest.raises(AssertionError, match=f"{permission_flag} must be True"):
        _assert_capability_consistency(contract)


def test_unknown_action_id_fails_closed() -> None:
    contract = _capability_probe("inspect_files", "WRITE")
    contract["permissions"]["allowed_actions"] = ["unknown_action_id"]

    with pytest.raises(AssertionError, match="unknown allowed action IDs: \\['unknown_action_id'\\]"):
        _assert_capability_consistency(contract)


def test_safe_implicit_read_and_draft_actions_pass() -> None:
    contract = deepcopy(next(iter(_load_manifests().values())))
    contract["routing"]["implicit_activation"] = True
    contract["modes"] = ["READ", "DRAFT"]
    contract["risk"] = {"risk_class": "medium", "human_gates": []}
    contract["permissions"].update(
        {
            "approval_required": False,
            "external_call_allowed": False,
            "network_allowed": False,
            "execution_allowed": False,
            "ingestion_allowed": False,
            "write_allowed": False,
            "destructive_allowed": False,
            "allowed_actions": ["inspect_files", "report_findings"],
        }
    )

    _assert_capability_consistency(contract)


@pytest.mark.parametrize(
    ("action", "effect"),
    [
        ("update_governance_docs", "WRITE"),
        ("run_local_eval_command", "EXECUTE"),
    ],
)
def test_explicit_gated_protected_action_passes(action: str, effect: str) -> None:
    _assert_capability_consistency(_capability_probe(action, effect))
