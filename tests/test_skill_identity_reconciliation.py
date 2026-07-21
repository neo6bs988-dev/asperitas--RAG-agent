from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from asperitas_agent.skill_discovery import validate_skill_files_against_registry
from asperitas_agent.skill_registry import (
    DEFAULT_SKILL_IDENTITY_AUTHORITY,
    DEFAULT_SKILL_REGISTRY,
    SkillIdentityAlias,
    SkillIdentityAuthority,
    SkillRegistry,
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
    compliance_compatibility = DEFAULT_SKILL_REGISTRY.lookup_decision("compliance_review")
    retrieval_compatibility = DEFAULT_SKILL_REGISTRY.lookup_decision("retrieval_eval")
    migration = DEFAULT_SKILL_REGISTRY.lookup_decision("benchmark_workflow_preflight")
    unknown = DEFAULT_SKILL_REGISTRY.lookup_decision("unknown_identity")

    assert canonical["identity"]["identity_kind"] == "canonical"
    assert compliance_compatibility["supported"] is True
    assert compliance_compatibility["identity"]["canonical_id"] == "compliance_biosafety_review"
    assert compliance_compatibility["identity"]["identity_kind"] == "deprecated_compatibility_alias"
    assert retrieval_compatibility["supported"] is True
    assert retrieval_compatibility["identity"]["canonical_id"] == "retrieval_eval_quality_gate"
    assert retrieval_compatibility["identity"]["identity_kind"] == "deprecated_compatibility_alias"
    assert migration["supported"] is False
    assert migration["decision"] == "migration_required"
    assert migration["identity"]["canonical_id"] == "mvp_implementation"
    assert unknown["identity"]["identity_kind"] == "unknown"


def test_canonical_successor_without_runtime_spec_is_visible_but_not_auto_registered() -> None:
    decision = DEFAULT_SKILL_REGISTRY.lookup_decision("compliance_biosafety_review")

    assert decision["supported"] is False
    assert decision["identity"]["identity_kind"] == "canonical"
    assert DEFAULT_SKILL_REGISTRY.get_skill("compliance_biosafety_review") is None


def test_valid_identity_does_not_suppress_incumbent_skill_spec_validation_failure() -> None:
    invalid_spec = replace(require_skill("mvp_implementation"), status="invalid")
    authority = SkillIdentityAuthority(("mvp_implementation",), ())
    registry = SkillRegistry((invalid_spec,), identity_authority=authority)

    decision = registry.lookup_decision("mvp_implementation")

    assert decision["supported"] is False
    assert decision["decision"] == "blocked"
    assert decision["reason"] == "registered skill failed validation"
    assert decision["validation_errors"] == ["invalid status: invalid"]
    assert decision["identity"]["decision"] == "canonical"


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


INVALID_IDENTITY_AUTHORITIES = (
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review", "compliance_biosafety_review"),
            (alias("compliance_review", "compliance_biosafety_review"),),
        ),
        id="duplicate-canonical-id",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_review", "compliance_biosafety_review"),
            (alias("compliance_review", "compliance_biosafety_review"),),
        ),
        id="alias-canonical-collision",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review",),
            (
                alias("compliance_review", "compliance_biosafety_review"),
                alias("compliance_review", "compliance_biosafety_review"),
            ),
        ),
        id="duplicate-alias",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_review",),
            (alias("compliance_review", "compliance_review"),),
        ),
        id="self-alias",
    ),
    pytest.param(
        SkillIdentityAuthority(
            (),
            (
                alias("compliance_review", "retrieval_eval"),
                alias("retrieval_eval", "compliance_review"),
            ),
        ),
        id="alias-cycle",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review",),
            (alias("compliance_review", "missing_successor"),),
        ),
        id="missing-successor",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review",),
            (
                alias(
                    "compliance_review",
                    "compliance_biosafety_review",
                    deprecated="2026-02-30",
                ),
            ),
        ),
        id="invalid-deprecated-since",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review",),
            (
                alias(
                    "compliance_review",
                    "compliance_biosafety_review",
                    until="2026-02-30",
                ),
            ),
        ),
        id="invalid-compatibility-until",
    ),
    pytest.param(
        SkillIdentityAuthority(
            ("compliance_biosafety_review",),
            (
                alias(
                    "compliance_review",
                    "compliance_biosafety_review",
                    deprecated="2026-02-01",
                    until="2026-01-31",
                ),
            ),
        ),
        id="reversed-compatibility-window",
    ),
)


@pytest.mark.parametrize("identity_authority", INVALID_IDENTITY_AUTHORITIES)
def test_invalid_identity_authority_blocks_registry_validation_and_incumbent_lookup(
    identity_authority: SkillIdentityAuthority,
) -> None:
    registry = SkillRegistry(DEFAULT_SKILL_REGISTRY.skills, identity_authority=identity_authority)
    authority_errors = identity_authority.validate()
    incumbent = registry.get_skill("compliance_review")

    assert authority_errors
    assert incumbent is not None
    assert incumbent.validate() == ()
    assert registry.validate() == tuple(sorted(registry.validate()))
    assert all(f"identity_authority: {error}" in registry.validate() for error in authority_errors)

    decisions = [registry.lookup_decision("compliance_review") for _ in range(3)]
    normalized = [json.dumps(decision, sort_keys=True, separators=(",", ":")) for decision in decisions]

    assert normalized[0] == normalized[1] == normalized[2]
    assert all(decision["supported"] is False for decision in decisions)
    assert all(decision["decision"] == "blocked" for decision in decisions)
    assert all(decision["reason"] == decision["identity"]["reason"] for decision in decisions)
    assert all(decision["identity"]["decision"] == "blocked" for decision in decisions)
    assert all(operation not in normalized[0] for operation in incumbent.allowed_operations)


def test_resolution_and_validation_order_are_deterministic() -> None:
    authority = SkillIdentityAuthority(
        ("z", "a"),
        (alias("old_z", "z"), alias("old_a", "a")),
    )

    assert authority.validate() == authority.validate()
    assert authority.resolve("old_a").to_dict() == authority.resolve("old_a").to_dict()
