from __future__ import annotations

import json
from pathlib import Path

from asperitas_agent.skill_contract import validate_repository
from asperitas_agent.skill_discovery import SKILL_ALIASES, discover_skill_files
from asperitas_agent.skill_registry import DEFAULT_SKILL_REGISTRY


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
EXPECTED_RESIDUAL_FINDINGS = {
    "LEGACY_ALIAS_EQUALS_CANONICAL_SKILL",
    "LEGACY_ALIAS_SATISFIES_DIFFERENT_SKILL",
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

    assert SKILL_ALIASES == {
        "benchmark_workflow_preflight": ("benchmark-workflow-preflight", "mvp-implementation"),
        "compliance_review": ("compliance-review", "compliance-biosafety-review"),
        "retrieval_eval": ("retrieval-eval", "retrieval-eval-quality-gate"),
    }
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


def test_repository_validation_has_only_incumbent_alias_authority_findings() -> None:
    transition = validate_repository(REPO_ROOT, transition=True)
    strict = validate_repository(REPO_ROOT)

    assert transition.state == "PARTIAL"
    assert transition.contracts_checked == EXPECTED_SKILL_COUNT
    assert transition.skills_discovered == EXPECTED_SKILL_COUNT
    assert {finding.code for finding in transition.findings} == EXPECTED_RESIDUAL_FINDINGS
    assert strict.state == "FAIL"
    assert strict.contracts_checked == EXPECTED_SKILL_COUNT
    assert {finding.code for finding in strict.findings} == EXPECTED_RESIDUAL_FINDINGS
    assert all(
        finding.path == "src/asperitas_agent/skill_discovery.py"
        for finding in (*transition.findings, *strict.findings)
    )


def test_manifest_declarations_do_not_grant_execution_or_write_authority() -> None:
    for contract in _load_manifests().values():
        permissions = contract["permissions"]
        assert "WRITE" not in contract["modes"]
        assert permissions["write_allowed"] is False
        assert permissions["network_allowed"] is False
        assert permissions["external_call_allowed"] is False
        assert permissions["execution_allowed"] is False
        assert permissions["ingestion_allowed"] is False
        assert permissions["destructive_allowed"] is False
