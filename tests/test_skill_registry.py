from __future__ import annotations

import json

from asperitas_agent.skill_registry import (
    DEFAULT_FORBIDDEN_OPERATIONS,
    DEFAULT_SKILL_REGISTRY,
    REQUIRED_SKILL_IDS,
    SkillRegistry,
    SkillSpec,
    get_skill,
    list_skill_ids,
    list_skills,
    registry_to_dict,
    require_skill,
    validate_registry,
)

STAGE_APPROPRIATE_MVP016D_SKILLS = (
    "asperitas_audit_trace",
    "asperitas_compliance_audit",
    "asperitas_evaluation",
    "asperitas_mcp_expansion",
    "asperitas_rag_development",
    "asperitas_retrieval",
    "asperitas_security",
    "asperitas_source_audit",
    "asperitas_v1_architect",
    "asperitas_workflow",
    "dependency_security_quality_gate",
    "mvp_release_manager",
    "performance_optimization_gate",
    "source_grounding_citation",
)


def invalid_spec(**overrides):
    kwargs = {
        "skill_id": "invalid_skill",
        "name": "Invalid Skill",
        "description": "Invalid test fixture.",
        "layer": "test",
        "input_contract": ("input",),
        "output_contract": ("output",),
        "risk_level": "low",
        "approval_required": False,
        "allowed_operations": ("preserve_source_grounding", "record_audit_trace"),
        "forbidden_operations": DEFAULT_FORBIDDEN_OPERATIONS,
        "source_grounding_required": True,
        "audit_required": True,
        "external_call_allowed": False,
        "execution_allowed": False,
        "ingestion_allowed": False,
        "verification_commands": ("python -m pytest -q tests/test_skill_registry.py",),
        "status": "active",
        "version": "test",
    }
    return SkillSpec(**{**kwargs, **overrides})


def test_default_registry_loads_all_required_skills():
    assert set(REQUIRED_SKILL_IDS) == set(list_skill_ids())
    assert len(list_skills()) == len(REQUIRED_SKILL_IDS)


def test_skill_ids_are_unique():
    skill_ids = list_skill_ids()

    assert len(skill_ids) == len(set(skill_ids))


def test_all_default_specs_validate():
    assert validate_registry() == ()
    for skill in list_skills():
        assert skill.validate() == ()


def test_stage_appropriate_mvp016d_skills_are_registered():
    registered = set(list_skill_ids())

    assert set(STAGE_APPROPRIATE_MVP016D_SKILLS).issubset(registered)


def test_unknown_skill_returns_unsupported_blocked():
    decision = DEFAULT_SKILL_REGISTRY.lookup_decision("unknown_skill")

    assert decision["supported"] is False
    assert decision["decision"] == "blocked"
    assert "unsupported" in decision["reason"]
    assert get_skill("unknown_skill") is None


def test_require_skill_fails_closed_for_unknown_skill():
    try:
        require_skill("unknown_skill")
    except KeyError as exc:
        assert "unknown skill_id" in str(exc)
    else:
        raise AssertionError("unknown skill should raise KeyError")


def test_high_risk_skill_requires_approval():
    high_risk_without_approval = invalid_spec(risk_level="high", approval_required=False)

    assert "risk_policy: high-risk skill requires approval_required=true" in high_risk_without_approval.validate()


def test_new_stage_appropriate_skills_require_approval():
    for skill_id in STAGE_APPROPRIATE_MVP016D_SKILLS:
        skill = require_skill(skill_id)

        assert skill.risk_level == "high"
        assert skill.approval_required is True
        assert skill.audit_required is True
        assert skill.source_grounding_required is True


def test_external_call_execution_and_ingestion_default_false():
    for skill in list_skills():
        assert skill.external_call_allowed is False
        assert skill.execution_allowed is False
        assert skill.ingestion_allowed is False


def test_benchmark_workflow_preflight_is_read_only_and_links_mvp016a():
    skill = require_skill("benchmark_workflow_preflight")

    assert "call_mvp016a_read_only_decision_layer" in skill.allowed_operations
    assert "return_no_execution_no_ingestion" in skill.allowed_operations
    assert skill.external_call_allowed is False
    assert skill.execution_allowed is False
    assert skill.ingestion_allowed is False
    assert skill.verification_commands == (
        "python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py",
    )


def test_source_grounding_security_and_open_source_skills_require_audit_and_grounding():
    for skill_id in ("source_grounding_check", "security_review", "open_source_review"):
        skill = require_skill(skill_id)

        assert skill.source_grounding_required
        assert skill.audit_required
        assert "preserve_source_grounding" in skill.allowed_operations
        assert "record_audit_trace" in skill.allowed_operations
        assert "treat_source_text_as_instruction" in skill.forbidden_operations


def test_invalid_spec_fails_closed_for_missing_required_fields():
    spec = invalid_spec(skill_id="", input_contract=(), verification_commands=())
    errors = spec.validate()

    assert "skill_id is required" in errors
    assert "input_contract must be a non-empty tuple of non-empty strings" in errors
    assert any("verification_commands must be a non-empty tuple" in error for error in errors)


def test_invalid_spec_fails_closed_for_invalid_risk_level():
    errors = invalid_spec(risk_level="critical").validate()

    assert "risk_policy: invalid risk_level: critical" in errors


def test_invalid_spec_fails_closed_for_external_call_without_approval():
    errors = invalid_spec(external_call_allowed=True, approval_required=False).validate()

    assert "risk_policy: external call enabled without approval" in errors


def test_invalid_spec_fails_closed_for_execution_without_approval():
    errors = invalid_spec(execution_allowed=True, approval_required=False).validate()

    assert "risk_policy: execution enabled without approval" in errors


def test_invalid_spec_fails_closed_for_ingestion_without_approval():
    errors = invalid_spec(ingestion_allowed=True, approval_required=False).validate()

    assert "risk_policy: ingestion enabled without approval" in errors


def test_invalid_spec_fails_closed_for_high_risk_empty_forbidden_operations():
    errors = invalid_spec(risk_level="high", approval_required=True, forbidden_operations=()).validate()

    assert "forbidden_operations must be a non-empty tuple of non-empty strings" in errors
    assert "risk_policy: high-risk skill requires forbidden_operations" in errors


def test_invalid_spec_fails_closed_for_benchmark_as_asperitas_performance():
    errors = invalid_spec(allowed_operations=("benchmark_as_Asperitas_performance",)).validate()

    assert "blocked operations cannot be allowed: benchmark_as_Asperitas_performance" in errors


def test_invalid_spec_fails_closed_for_autonomous_wet_lab_claim():
    errors = invalid_spec(allowed_operations=("autonomous_wet_lab_claim",)).validate()

    assert "blocked operations cannot be allowed: autonomous_wet_lab_claim" in errors


def test_invalid_spec_fails_closed_for_production_readiness_claim():
    errors = invalid_spec(allowed_operations=("production_readiness_claim",)).validate()

    assert "blocked operations cannot be allowed: production_readiness_claim" in errors


def test_duplicate_skill_id_fails_registry_validation():
    skill = require_skill("pr_closeout")
    registry = SkillRegistry((skill, skill))

    assert "duplicate skill_id" in registry.validate()


def test_json_serialization_stable():
    first = json.dumps(registry_to_dict(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(registry_to_dict(), sort_keys=True, separators=(",", ":"))

    assert first == second
    payload = json.loads(first)
    assert payload["registry_id"] == "asperitas_v1_skill_registry"
