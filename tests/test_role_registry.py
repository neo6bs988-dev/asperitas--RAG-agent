from __future__ import annotations

import json

import pytest

from asperitas_agent.role_registry import (
    ALLOWED_RETRIEVERS,
    DEFAULT_RETRIEVER,
    HIGH_RISK_ROLE_IDS,
    HUMAN_APPROVAL_GATES,
    RERANKER_POLICY,
    get_role,
    list_role_ids,
    list_roles,
    registry_to_dict,
    require_role,
    role_to_dict,
    validate_registry,
    validate_role,
)


def test_registry_contains_exactly_10_roles():
    assert len(list_roles()) == 10


def test_all_role_ids_are_unique():
    role_ids = list_role_ids()

    assert len(role_ids) == len(set(role_ids))


def test_all_required_fields_are_populated():
    for role in list_roles():
        assert validate_role(role) == ()
        data = role_to_dict(role)
        for field_name, value in data.items():
            assert value not in ("", [], None), field_name


def test_all_roles_default_to_mvp003():
    assert {role.default_retriever for role in list_roles()} == {DEFAULT_RETRIEVER}


def test_allowed_retrievers_are_constrained_to_known_values():
    for role in list_roles():
        assert set(role.allowed_retrievers) <= set(ALLOWED_RETRIEVERS)


def test_hybrid_is_never_default():
    assert all(role.default_retriever != "hybrid" for role in list_roles())


def test_reranker_is_never_default_or_implicit():
    for role in list_roles():
        assert not hasattr(role, "default_reranker")
        assert RERANKER_POLICY in role.source_policy
        assert "non_default" in " ".join(role.source_policy)
        assert "explicit_opt_in" in " ".join(role.source_policy)


def test_high_risk_roles_include_human_approval_gates():
    for role_id in HIGH_RISK_ROLE_IDS:
        role = require_role(role_id)
        for gate in HUMAN_APPROVAL_GATES:
            assert gate in role.validation_gates
            assert gate in role.escalation_triggers
            assert gate in role.compliance_policy


def test_prohibited_tasks_are_non_empty():
    assert all(role.prohibited_tasks for role in list_roles())


def test_output_contracts_are_non_empty():
    assert all(role.output_contract for role in list_roles())


def test_unknown_role_lookup_returns_none():
    assert get_role("unknown_role") is None


def test_require_role_fails_closed_for_unknown_role():
    with pytest.raises(KeyError, match="unknown role_id"):
        require_role("unknown_role")


def test_validate_registry_returns_no_errors():
    assert validate_registry() == ()


def test_registry_to_dict_is_deterministic_across_repeated_calls():
    first = json.dumps(registry_to_dict(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(registry_to_dict(), sort_keys=True, separators=(",", ":"))

    assert first == second


def test_role_ordering_is_deterministic():
    assert list_role_ids() == tuple(role["role_id"] for role in registry_to_dict()["roles"])
