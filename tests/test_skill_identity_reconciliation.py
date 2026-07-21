from __future__ import annotations

from datetime import date
from pathlib import Path

from asperitas_agent.skill_discovery import validate_skill_files_against_registry
from asperitas_agent.skill_registry import (
    DEFAULT_SKILL_IDENTITY_AUTHORITY,
    DEFAULT_SKILL_REGISTRY,
    SkillIdentityAlias,
    SkillIdentityAuthority,
    require_skill,
)


def alias(
    legacy: str,
    canonical: str,
    *,
    classification: str = "true_compatibility_alias",
    deprecated: str = "2026-01-01",
    until: str = "2026-12-31",
) -> SkillIdentityAlias:
    return SkillIdentityAlias(legacy, canonical, classification, deprecated, until)


def test_canonical_compatibility_migration_and_unknown_lookups_are_explicit() -> None:
    canonical = DEFAULT_SKILL_REGISTRY.lookup_decision("mvp_implementation")
    compatibility = DEFAULT_SKILL_REGISTRY.lookup_decision("compliance_review")
    migration = DEFAULT_SKILL_REGISTRY.lookup_decision("benchmark_workflow_preflight")
    unknown = DEFAULT_SKILL_REGISTRY.lookup_decision("unknown_identity")

    assert canonical["identity"]["identity_kind"] == "canonical"
    assert compatibility["supported"] is True
    assert compatibility["identity"]["canonical_id"] == "compliance_biosafety_review"
    assert compatibility["identity"]["identity_kind"] == "deprecated_compatibility_alias"
    assert migration["supported"] is False
    assert migration["decision"] == "migration_required"
    assert migration["identity"]["canonical_id"] == "mvp_implementation"
    assert unknown["identity"]["identity_kind"] == "unknown"


def test_canonical_successor_without_runtime_spec_is_visible_but_not_auto_registered() -> None:
    decision = DEFAULT_SKILL_REGISTRY.lookup_decision("compliance_biosafety_review")

    assert decision["supported"] is False
    assert decision["identity"]["identity_kind"] == "canonical"
    assert DEFAULT_SKILL_REGISTRY.get_skill("compliance_biosafety_review") is None


def test_legacy_lookup_preserves_incumbent_spec_and_cannot_inherit_successor_capabilities() -> None:
    legacy = DEFAULT_SKILL_REGISTRY.get_skill("benchmark_workflow_preflight")
    successor = require_skill("mvp_implementation")

    assert legacy is not None
    assert legacy.skill_id == "benchmark_workflow_preflight"
    assert "make_local_code_change" not in legacy.allowed_operations
    assert "make_local_code_change" in successor.allowed_operations
    assert legacy.execution_allowed is False
    assert legacy.external_call_allowed is False
    assert legacy.ingestion_allowed is False


def test_legacy_identity_cannot_satisfy_a_different_canonical_skill_file(tmp_path: Path) -> None:
    skill = require_skill("compliance_review")
    registry = type(DEFAULT_SKILL_REGISTRY)((skill,))
    unrelated = tmp_path / ".agents" / "skills" / "mvp-implementation" / "SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text(
        "---\nname: mvp-implementation\ndescription: Unrelated canonical Skill.\n---\n",
        encoding="utf-8",
    )

    report = validate_skill_files_against_registry(tmp_path, registry)

    assert report.ok is False
    assert report.missing_skill_files == ("compliance_biosafety_review",)


def test_expired_compatibility_alias_fails_closed_as_migration_required() -> None:
    resolution = DEFAULT_SKILL_IDENTITY_AUTHORITY.resolve("retrieval_eval", as_of=date(2027, 1, 1))

    assert resolution.decision == "migration_required"
    assert resolution.migration_required is True


def test_identity_authority_rejects_collision_duplicate_self_cycle_and_missing_successor() -> None:
    collision = SkillIdentityAuthority(("canonical",), (alias("canonical", "canonical"),))
    duplicate = SkillIdentityAuthority(("canonical",), (alias("old", "canonical"), alias("old", "canonical")))
    cycle = SkillIdentityAuthority((), (alias("one", "two"), alias("two", "one")))
    missing = SkillIdentityAuthority(("canonical",), (alias("old", "missing"),))

    assert "alias collides with canonical skill_id: canonical" in collision.validate()
    assert "self alias: canonical" in collision.validate()
    assert "duplicate legacy alias" in duplicate.validate()
    assert any(error.startswith("alias cycle:") for error in cycle.validate())
    assert "missing alias successor: old -> missing" in missing.validate()


def test_identity_authority_rejects_invalid_lifecycle_dates_and_window() -> None:
    invalid_date = SkillIdentityAuthority(("canonical",), (alias("old", "canonical", deprecated="2026-02-30"),))
    invalid_window = SkillIdentityAuthority(("canonical",), (alias("old", "canonical", deprecated="2026-02-01", until="2026-01-31"),))

    assert "invalid deprecated_since: old" in invalid_date.validate()
    assert "invalid compatibility window: old" in invalid_window.validate()


def test_resolution_and_validation_order_are_deterministic() -> None:
    authority = SkillIdentityAuthority(
        ("z", "a"),
        (alias("old_z", "z"), alias("old_a", "a")),
    )

    assert authority.validate() == authority.validate()
    assert authority.resolve("old_a").to_dict() == authority.resolve("old_a").to_dict()
