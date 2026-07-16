from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from asperitas_agent.skill_contract import (
    validate_contract_file,
    validate_contract_files,
    validate_repository,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_skill_contract.py"
SCHEMA = REPO_ROOT / ".agents" / "skill-contract.schema.json"


def valid_contract(skill_id: str = "example_skill") -> dict:
    return {
        "schema_version": "2.0",
        "skill_id": skill_id,
        "owner": "Asperitas AI Lead",
        "lifecycle": {
            "status": "active",
            "version": "2.0.0",
            "introduced_in": "MVP-016D",
            "deprecated_since": None,
            "compatibility_until": None,
            "replaced_by": None,
        },
        "routing": {
            "implicit_activation": True,
            "positive_triggers": ["example task"],
            "negative_triggers": ["unrelated task"],
            "conflicts_with": [],
            "precedence_rule": "Use only for the example task.",
        },
        "modes": ["READ"],
        "risk": {"risk_class": "medium", "human_gates": []},
        "permissions": {
            "approval_required": False,
            "external_call_allowed": False,
            "network_allowed": False,
            "execution_allowed": False,
            "ingestion_allowed": False,
            "write_allowed": False,
            "destructive_allowed": False,
            "allowed_actions": ["inspect_local_files"],
            "forbidden_actions": ["treat_untrusted_source_text_as_instruction"],
        },
        "contract": {
            "required_inputs": ["objective"],
            "output_contract": ["result"],
            "error_behavior": "fail_closed",
        },
        "verification": {"commands": ["python -m pytest -q"], "required_fixtures": []},
        "rollback": {"strategy": "revert the cohesive change", "verification": "rerun targeted tests"},
        "relations": {"related_skills": [], "supersedes": []},
        "compatibility": {"aliases": []},
    }


def write_fixture(root: Path, name: str, contract: dict | None = None, description: str = "Fixture skill.") -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Fixture\n",
        encoding="utf-8",
    )
    payload = contract or valid_contract(name.replace("-", "_"))
    contract_path = skill_dir / "skill.contract.json"
    contract_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return contract_path


def finding_codes(report) -> set[str]:
    return {finding.code for finding in report.findings}


def assert_schema_rejected(report) -> None:
    assert report.state != "PASS"
    assert report.ok is False
    assert report.findings
    assert any(finding.code.startswith("SCHEMA_") for finding in report.findings)


def set_nested(payload: dict, path: tuple[str, ...], value) -> None:
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def test_schema_is_valid_json_and_declares_required_shape():
    payload = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["properties"]["schema_version"]["const"] == "2.0"
    assert set(payload["required"]) >= {
        "skill_id",
        "lifecycle",
        "routing",
        "permissions",
        "verification",
        "rollback",
    }


def test_valid_fixture_contract_passes_and_is_deterministic(tmp_path):
    path = write_fixture(tmp_path, "example-skill")

    first = validate_contract_file(path)
    second = validate_contract_file(path)

    assert first.state == "PASS"
    assert first.to_dict() == second.to_dict()


def test_directory_must_equal_frontmatter_name(tmp_path):
    path = write_fixture(tmp_path, "directory-name")
    (path.parent / "SKILL.md").write_text(
        "---\nname: different-name\ndescription: Fixture.\n---\n",
        encoding="utf-8",
    )

    report = validate_contract_file(path)

    assert "DIRECTORY_FRONTMATTER_NAME_MISMATCH" in finding_codes(report)


def test_frontmatter_name_grammar_and_description_are_strict(tmp_path):
    path = write_fixture(tmp_path, "Bad--Name", description="")

    report = validate_contract_file(path)

    assert {"INVALID_FRONTMATTER_NAME", "DESCRIPTION_REQUIRED"}.issubset(finding_codes(report))


def test_description_cannot_exceed_1024_characters(tmp_path):
    path = write_fixture(tmp_path, "long-description", description="x" * 1025)

    assert "DESCRIPTION_TOO_LONG" in finding_codes(validate_contract_file(path))


def test_skill_id_must_match_hyphen_to_underscore_normalization(tmp_path):
    path = write_fixture(tmp_path, "canonical-skill", valid_contract("other_skill"))

    assert "SKILL_ID_NAME_MISMATCH" in finding_codes(validate_contract_file(path))


def test_canonical_skill_ids_must_be_unique(tmp_path):
    first = write_fixture(tmp_path, "first-skill", valid_contract("duplicate_id"))
    second = write_fixture(tmp_path, "second-skill", valid_contract("duplicate_id"))

    assert "DUPLICATE_CANONICAL_SKILL_ID" in finding_codes(validate_contract_files([first, second]))


def test_aliases_must_be_unique(tmp_path):
    first_contract = valid_contract("first_skill")
    second_contract = valid_contract("second_skill")
    alias = {
        "value": "old_skill",
        "kind": "deprecated_skill_id",
        "deprecated_since": "2026-01-01",
        "compatibility_until": "2026-12-31",
        "replaced_by": "first_skill",
    }
    first_contract["compatibility"]["aliases"] = [alias]
    second_contract["compatibility"]["aliases"] = [{**alias, "replaced_by": "second_skill"}]
    first = write_fixture(tmp_path, "first-skill", first_contract)
    second = write_fixture(tmp_path, "second-skill", second_contract)

    assert "DUPLICATE_ALIAS" in finding_codes(validate_contract_files([first, second]))


def test_alias_cannot_equal_canonical_id_or_frontmatter_name(tmp_path):
    first = write_fixture(tmp_path, "first-skill")
    second_contract = valid_contract("second_skill")
    second_contract["compatibility"]["aliases"] = [
        {
            "value": "first-skill",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "second_skill",
        }
    ]
    second = write_fixture(tmp_path, "second-skill", second_contract)

    codes = finding_codes(validate_contract_files([first, second]))

    assert "ALIAS_EQUALS_CANONICAL_ID" in codes
    assert "ALIAS_EQUALS_CANONICAL_NAME" in codes


def test_alias_cycles_fail(tmp_path):
    first_contract = valid_contract("first_skill")
    second_contract = valid_contract("second_skill")
    first_contract["compatibility"]["aliases"] = [
        {
            "value": "old_first",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "old_second",
        }
    ]
    second_contract["compatibility"]["aliases"] = [
        {
            "value": "old_second",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "old_first",
        }
    ]

    paths = [
        write_fixture(tmp_path, "first-skill", first_contract),
        write_fixture(tmp_path, "second-skill", second_contract),
    ]
    report = validate_contract_files(paths)

    assert "ALIAS_CYCLE" in finding_codes(report)


def test_deprecated_skill_requires_replacement_or_terminal_rationale(tmp_path):
    contract = valid_contract("deprecated_skill")
    contract["lifecycle"]["status"] = "deprecated"
    contract["lifecycle"]["deprecated_since"] = "2026-01-01"
    contract["lifecycle"]["compatibility_until"] = "2026-12-31"

    report = validate_contract_file(write_fixture(tmp_path, "deprecated-skill", contract))

    assert "DEPRECATED_WITHOUT_DISPOSITION" in finding_codes(report)


def test_deprecated_alias_requires_compatibility_expiry(tmp_path):
    contract = valid_contract("alias_skill")
    contract["compatibility"]["aliases"] = [
        {
            "value": "old_alias",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": None,
            "replaced_by": "alias_skill",
        }
    ]

    report = validate_contract_file(write_fixture(tmp_path, "alias-skill", contract))

    assert "DEPRECATED_ALIAS_REQUIRES_EXPIRY" in finding_codes(report)


def test_write_mode_without_approval_fails(tmp_path):
    contract = valid_contract("write_skill")
    contract["modes"] = ["READ", "WRITE"]
    contract["permissions"]["write_allowed"] = True

    report = validate_contract_file(write_fixture(tmp_path, "write-skill", contract))

    assert "WRITE_REQUIRES_APPROVAL" in finding_codes(report)


def test_network_or_external_call_without_approval_fails(tmp_path):
    contract = valid_contract("network_skill")
    contract["permissions"]["network_allowed"] = True
    contract["permissions"]["external_call_allowed"] = True

    report = validate_contract_file(write_fixture(tmp_path, "network-skill", contract))

    assert "EXTERNAL_ACCESS_REQUIRES_APPROVAL" in finding_codes(report)


def test_destructive_actions_are_blocked_by_default(tmp_path):
    contract = valid_contract("destructive_skill")
    contract["permissions"]["destructive_allowed"] = True

    report = validate_contract_file(write_fixture(tmp_path, "destructive-skill", contract))

    assert "DESTRUCTIVE_ACTIONS_BLOCKED_BY_DEFAULT" in finding_codes(report)


def test_high_risk_contract_requires_approval_and_forbidden_actions(tmp_path):
    contract = valid_contract("high_risk_skill")
    contract["risk"]["risk_class"] = "high"
    contract["permissions"]["forbidden_actions"] = []

    report = validate_contract_file(write_fixture(tmp_path, "high-risk-skill", contract))

    assert "HIGH_RISK_POLICY_INCOMPLETE" in finding_codes(report)


def test_high_risk_execution_requires_human_gate(tmp_path):
    contract = valid_contract("biology_skill")
    contract["risk"] = {"risk_class": "high", "human_gates": []}
    contract["routing"]["positive_triggers"] = ["wet-lab biological execution"]
    contract["permissions"]["approval_required"] = True
    contract["permissions"]["execution_allowed"] = True

    report = validate_contract_file(write_fixture(tmp_path, "biology-skill", contract))

    assert "HIGH_RISK_EXECUTION_REQUIRES_HUMAN_GATE" in finding_codes(report)


def test_untrusted_source_text_override_must_be_forbidden(tmp_path):
    contract = valid_contract("untrusted_skill")
    contract["permissions"]["forbidden_actions"] = ["expose_secrets"]

    report = validate_contract_file(write_fixture(tmp_path, "untrusted-skill", contract))

    assert "UNTRUSTED_SOURCE_POLICY_REQUIRED" in finding_codes(report)


def test_active_contract_requires_verification_command(tmp_path):
    contract = valid_contract("unverified_skill")
    contract["verification"]["commands"] = []

    report = validate_contract_file(write_fixture(tmp_path, "unverified-skill", contract))

    assert "ACTIVE_VERIFICATION_REQUIRED" in finding_codes(report)


def test_explicit_only_is_valid_for_unregistered_review_skill(tmp_path):
    contract = valid_contract("unknown_skill")
    contract["lifecycle"]["status"] = "unregistered_review_required"
    contract["routing"]["implicit_activation"] = False

    assert validate_contract_file(write_fixture(tmp_path, "unknown-skill", contract)).state == "PASS"


def test_unknown_skill_cannot_be_implicitly_activated(tmp_path):
    contract = valid_contract("unknown_skill")
    contract["lifecycle"]["status"] = "unregistered_review_required"

    report = validate_contract_file(write_fixture(tmp_path, "unknown-skill", contract))

    assert "UNREGISTERED_SKILL_MUST_BE_EXPLICIT_ONLY" in finding_codes(report)


def test_unknown_repository_skill_passes_only_when_quarantined(tmp_path):
    repo_root = tmp_path / "repo"
    skill_root = repo_root / ".agents" / "skills"
    (repo_root / ".agents").mkdir(parents=True)
    shutil.copyfile(SCHEMA, repo_root / ".agents" / "skill-contract.schema.json")
    contract = valid_contract("unknown_skill")
    contract["lifecycle"]["status"] = "unregistered_review_required"
    contract["routing"]["implicit_activation"] = False
    write_fixture(skill_root, "unknown-skill", contract)

    report = validate_repository(repo_root)

    assert report.state == "PASS"
    assert "UNREGISTERED_REPOSITORY_SKILL" not in finding_codes(report)


def test_required_fixture_path_cannot_escape_skill_directory(tmp_path):
    contract = valid_contract("unsafe_path_skill")
    contract["verification"]["required_fixtures"] = ["../outside.json"]

    report = validate_contract_file(write_fixture(tmp_path, "unsafe-path-skill", contract))

    assert "UNSAFE_RESOURCE_PATH" in finding_codes(report)


def test_description_cannot_be_duplicated_in_contract(tmp_path):
    contract = valid_contract("duplicate_description")
    contract["description"] = "Contract must not own this field."

    report = validate_contract_file(write_fixture(tmp_path, "duplicate-description", contract))

    assert "DUPLICATE_DESCRIPTION_AUTHORITY" in finding_codes(report)


def test_mvp_provenance_is_allowed_only_in_introduced_in(tmp_path):
    contract = valid_contract("versioned_skill")
    passing_path = write_fixture(tmp_path, "versioned-skill", contract)
    assert validate_contract_file(passing_path).state == "PASS"

    stale = deepcopy(contract)
    stale["lifecycle"]["version"] = "MVP-005"
    stale_path = write_fixture(tmp_path, "stale-version-skill", stale)

    assert "STALE_MVP_CANONICAL_VERSION" in finding_codes(validate_contract_file(stale_path))


def test_alias_cannot_satisfy_canonical_file_existence(tmp_path):
    contract = valid_contract("mvp_implementation")
    path = write_fixture(tmp_path, "mvp-implementation", contract)

    report = validate_contract_files([path])

    assert report.state == "PASS"
    assert report.canonical_skill_ids == ("mvp_implementation",)
    assert "benchmark_workflow_preflight" not in report.canonical_skill_ids


def test_compliance_compatibility_id_does_not_replace_canonical_identity(tmp_path):
    contract = valid_contract("compliance_biosafety_review")
    contract["compatibility"]["aliases"] = [
        {
            "value": "compliance_review",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "compliance_biosafety_review",
        }
    ]
    path = write_fixture(tmp_path, "compliance-biosafety-review", contract)

    report = validate_contract_files([path])

    assert report.state == "PASS"
    assert report.canonical_skill_ids == ("compliance_biosafety_review",)
    assert "compliance_review" not in report.canonical_skill_ids


def test_retrieval_compatibility_id_does_not_replace_canonical_identity(tmp_path):
    contract = valid_contract("retrieval_eval_quality_gate")
    contract["compatibility"]["aliases"] = [
        {
            "value": "retrieval_eval",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "retrieval_eval_quality_gate",
        }
    ]
    path = write_fixture(tmp_path, "retrieval-eval-quality-gate", contract)

    report = validate_contract_files([path])

    assert report.state == "PASS"
    assert report.canonical_skill_ids == ("retrieval_eval_quality_gate",)
    assert "retrieval_eval" not in report.canonical_skill_ids


def test_repository_transition_audit_is_partial_and_reports_current_drift():
    report = validate_repository(REPO_ROOT, transition=True)
    codes = finding_codes(report)

    assert report.state == "PARTIAL"
    assert report.ok is False
    assert report.skills_discovered == 30
    assert report.contracts_checked == 0
    assert "MISSING_SKILL_CONTRACT" in codes
    assert "UNREGISTERED_REPOSITORY_SKILL" in codes
    assert "LEGACY_ALIAS_SATISFIES_DIFFERENT_SKILL" in codes


def test_repository_strict_validation_fails_before_manifests_exist():
    report = validate_repository(REPO_ROOT)

    assert report.state == "FAIL"
    assert report.ok is False


def test_missing_skills_root_is_not_testable(tmp_path):
    report = validate_repository(tmp_path, transition=True)

    assert report.state == "NOT_TESTABLE"
    assert report.ok is False
    assert finding_codes(report) == {"SKILLS_ROOT_NOT_FOUND"}


def test_cli_transition_returns_zero_but_never_reports_pass():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(REPO_ROOT), "--transition", "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stderr
    assert payload["state"] == "PARTIAL"
    assert payload["ok"] is False


def test_cli_invalid_json_returns_one(tmp_path):
    skill_dir = tmp_path / "invalid-json"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: invalid-json\ndescription: Invalid fixture.\n---\n",
        encoding="utf-8",
    )
    contract_path = skill_dir / "skill.contract.json"
    contract_path.write_text("{", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--contract", str(contract_path), "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["state"] == "INVALID"


NESTED_OBJECTS = (
    "lifecycle",
    "routing",
    "risk",
    "permissions",
    "contract",
    "verification",
    "rollback",
    "relations",
    "compatibility",
)


@pytest.mark.parametrize("object_name", NESTED_OBJECTS)
def test_schema_rejects_unknown_property_in_every_nested_object(tmp_path, object_name):
    contract = valid_contract("unknown_nested")
    contract[object_name]["unexpected"] = True

    report = validate_contract_file(write_fixture(tmp_path, "unknown-nested", contract))

    assert_schema_rejected(report)
    assert "SCHEMA_ADDITIONAL_PROPERTY" in finding_codes(report)


def test_schema_rejects_unknown_top_level_and_alias_properties(tmp_path):
    top_level = valid_contract("unknown_top")
    top_level["unexpected"] = True
    assert_schema_rejected(validate_contract_file(write_fixture(tmp_path, "unknown-top", top_level)))

    alias_contract = valid_contract("alias_target")
    alias_contract["compatibility"]["aliases"] = [
        {
            "value": "old_target",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "alias_target",
            "unexpected": True,
        }
    ]
    report = validate_contract_file(write_fixture(tmp_path, "alias-target", alias_contract))
    assert_schema_rejected(report)
    assert "SCHEMA_ADDITIONAL_PROPERTY" in finding_codes(report)


def required_field_paths() -> tuple[tuple[str, ...], ...]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    paths = [(name,) for name in schema["required"]]
    for object_name in NESTED_OBJECTS:
        nested = schema["properties"][object_name]
        paths.extend((object_name, name) for name in nested["required"])
    paths.extend(
        ("compatibility", "aliases", "0", name)
        for name in schema["properties"]["compatibility"]["properties"]["aliases"]["items"]["required"]
    )
    return tuple(paths)


@pytest.mark.parametrize("field_path", required_field_paths())
def test_schema_rejects_every_missing_required_field(tmp_path, field_path):
    contract = valid_contract("missing_field")
    contract["compatibility"]["aliases"] = [
        {
            "value": "old_missing_field",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "missing_field",
        }
    ]
    target = contract
    for key in field_path[:-1]:
        target = target[int(key)] if isinstance(target, list) else target[key]
    del target[field_path[-1]]

    report = validate_contract_file(write_fixture(tmp_path, "missing-field", contract))

    assert_schema_rejected(report)
    assert "SCHEMA_REQUIRED" in finding_codes(report)


WRONG_TYPE_CASES = (
    (("schema_version",), 2),
    (("skill_id",), True),
    (("owner",), 7),
    (("lifecycle",), []),
    (("lifecycle", "deprecated_since"), 20260101),
    (("routing", "implicit_activation"), 1),
    (("routing", "positive_triggers"), "trigger"),
    (("routing", "negative_triggers"), [1]),
    (("modes",), "READ"),
    (("risk", "human_gates"), "gate"),
    (("permissions", "approval_required"), 1),
    (("permissions", "allowed_actions"), "inspect"),
    (("contract", "required_inputs"), [False]),
    (("verification", "commands"), "pytest"),
    (("verification", "required_fixtures"), [1]),
    (("rollback", "strategy"), False),
    (("relations", "related_skills"), "other"),
    (("compatibility", "aliases"), {}),
)


@pytest.mark.parametrize(("field_path", "wrong_value"), WRONG_TYPE_CASES)
def test_schema_rejects_representative_wrong_types(tmp_path, field_path, wrong_value):
    contract = valid_contract("wrong_type")
    set_nested(contract, field_path, wrong_value)

    assert_schema_rejected(validate_contract_file(write_fixture(tmp_path, "wrong-type", contract)))


def test_schema_rejects_alias_kind_integer_and_invalid_const_enum_and_duplicates(tmp_path):
    alias_contract = valid_contract("typed_alias")
    alias_contract["compatibility"]["aliases"] = [
        {
            "value": "old_typed_alias",
            "kind": 7,
            "deprecated_since": "2026-01-01",
            "compatibility_until": "2026-12-31",
            "replaced_by": "typed_alias",
        }
    ]
    assert_schema_rejected(validate_contract_file(write_fixture(tmp_path, "typed-alias", alias_contract)))

    for name, path, value in (
        ("bad-const", ("schema_version",), "3.0"),
        ("bad-enum", ("modes",), ["EXECUTE"]),
        ("duplicates", ("modes",), ["READ", "READ"]),
    ):
        contract = valid_contract(name.replace("-", "_"))
        set_nested(contract, path, value)
        assert_schema_rejected(validate_contract_file(write_fixture(tmp_path, name, contract)))


@pytest.mark.parametrize("value", ["never", "P1B", "P1D", "2026-02-30", "2026-1-1", "2026-01-01T00:00:00Z"])
def test_malformed_lifecycle_dates_fail(tmp_path, value):
    contract = valid_contract("bad_date")
    contract["lifecycle"].update(
        status="deprecated",
        deprecated_since=value,
        compatibility_until="2026-12-31",
        terminal_rationale="retired without successor",
    )

    report = validate_contract_file(write_fixture(tmp_path, "bad-date", contract))

    assert report.state == "FAIL"
    assert {"SCHEMA_PATTERN", "INVALID_FULL_DATE"} & finding_codes(report)


def deprecated_contract(skill_id: str, replaced_by: str) -> dict:
    contract = valid_contract(skill_id)
    contract["lifecycle"].update(
        status="deprecated",
        deprecated_since="2026-01-01",
        compatibility_until="2026-12-31",
        replaced_by=replaced_by,
    )
    return contract


def test_deprecated_successor_must_exist_and_cannot_be_self(tmp_path):
    missing = write_fixture(tmp_path, "missing-successor", deprecated_contract("missing_successor", "absent"))
    assert "SUCCESSOR_NOT_FOUND" in finding_codes(validate_contract_files([missing]))

    self_path = write_fixture(tmp_path, "self-successor", deprecated_contract("self_successor", "self_successor"))
    assert "SELF_REPLACEMENT" in finding_codes(validate_contract_files([self_path]))


def test_deprecated_successor_must_be_active_or_planned_and_acyclic(tmp_path):
    first = write_fixture(tmp_path, "first-cycle", deprecated_contract("first_cycle", "second_cycle"))
    second = write_fixture(tmp_path, "second-cycle", deprecated_contract("second_cycle", "first_cycle"))
    report = validate_contract_files([first, second])
    assert "SUCCESSOR_CYCLE" in finding_codes(report)
    assert "INVALID_SUCCESSOR_STATUS" in finding_codes(report)


def test_lifecycle_and_alias_date_ordering_fail(tmp_path):
    lifecycle = deprecated_contract("ordered_lifecycle", "successor")
    lifecycle["lifecycle"]["compatibility_until"] = "2025-12-31"
    successor = valid_contract("successor")
    report = validate_contract_files(
        [
            write_fixture(tmp_path, "ordered-lifecycle", lifecycle),
            write_fixture(tmp_path, "successor", successor),
        ]
    )
    assert "INVALID_LIFECYCLE_DATE_ORDER" in finding_codes(report)

    alias = valid_contract("ordered_alias")
    alias["compatibility"]["aliases"] = [
        {
            "value": "old_ordered_alias",
            "kind": "deprecated_skill_id",
            "deprecated_since": "2026-12-31",
            "compatibility_until": "2026-01-01",
            "replaced_by": "ordered_alias",
        }
    ]
    assert "INVALID_ALIAS_DATE_ORDER" in finding_codes(
        validate_contract_file(write_fixture(tmp_path, "ordered-alias", alias))
    )


@pytest.mark.parametrize(
    ("skill_id", "write_allowed", "trigger"),
    (
        ("generic_exec", False, "run task"),
        ("generic_write", True, "modify output"),
        ("paraphrased_exec", False, "operate on living-system workflow"),
    ),
)
def test_high_risk_execution_or_write_requires_gate_without_keyword_inference(
    tmp_path, skill_id, write_allowed, trigger
):
    contract = valid_contract(skill_id)
    contract["risk"]["risk_class"] = "high"
    contract["routing"]["positive_triggers"] = [trigger]
    contract["permissions"].update(
        approval_required=True,
        execution_allowed=not write_allowed,
        write_allowed=write_allowed,
    )
    report = validate_contract_file(write_fixture(tmp_path, skill_id.replace("_", "-"), contract))
    assert "HIGH_RISK_EXECUTION_REQUIRES_HUMAN_GATE" in finding_codes(report)


def test_high_risk_execution_with_explicit_gate_passes(tmp_path):
    contract = valid_contract("gated_execution")
    contract["risk"] = {"risk_class": "high", "human_gates": ["named owner approval"]}
    contract["permissions"].update(approval_required=True, execution_allowed=True)
    assert validate_contract_file(write_fixture(tmp_path, "gated-execution", contract)).state == "PASS"


@pytest.mark.parametrize(
    "unsafe_path",
    (
        "/tmp/file.json",
        r"C:\restricted\fixture.json",
        "C:/restricted/fixture.json",
        r"\\server\share\fixture.json",
        "//server/share/fixture.json",
        r"\\?\C:\fixture.json",
        r"\\.\device",
        "../file.json",
        r"..\file.json",
        "nested/../../file.json",
        r"nested\..\..\file.json",
        "mixed/..\\../file.json",
        "bad\x00path",
        "",
    ),
)
def test_resource_paths_are_rejected_host_independently(tmp_path, unsafe_path):
    contract = valid_contract("portable_path")
    contract["verification"]["required_fixtures"] = [unsafe_path]
    report = validate_contract_file(write_fixture(tmp_path, "portable-path", contract))
    assert {"UNSAFE_RESOURCE_PATH", "SCHEMA_MIN_LENGTH"} & finding_codes(report)


def write_schema(tmp_path: Path, mutation) -> Path:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    mutation(schema)
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(schema), encoding="utf-8")
    return path


def test_schema_engine_fails_closed_on_unsupported_keyword_and_external_ref(tmp_path):
    contract_path = write_fixture(tmp_path, "schema-guard")
    unsupported = write_schema(tmp_path, lambda schema: schema.update({"oneOf": []}))
    report = validate_contract_file(contract_path, schema_path=unsupported)
    assert_schema_rejected(report)
    assert "SCHEMA_UNSUPPORTED_KEYWORD" in finding_codes(report)

    external = write_schema(
        tmp_path, lambda schema: schema["properties"]["owner"].update({"$ref": "https://example.invalid/schema"})
    )
    report = validate_contract_file(contract_path, schema_path=external)
    assert_schema_rejected(report)
    assert "SCHEMA_EXTERNAL_REF" in finding_codes(report)


def test_schema_engine_fails_closed_on_missing_and_malformed_schema(tmp_path):
    contract_path = write_fixture(tmp_path, "missing-schema")
    missing = tmp_path / "absent-schema.json"
    assert_schema_rejected(validate_contract_file(contract_path, schema_path=missing))

    malformed = tmp_path / "malformed-schema.json"
    malformed.write_text("{", encoding="utf-8")
    report = validate_contract_file(contract_path, schema_path=malformed)
    assert_schema_rejected(report)
    assert report.state == "INVALID"


def test_schema_findings_have_deterministic_order_and_json_pointers(tmp_path):
    contract = valid_contract("ordered_findings")
    contract["z_unknown"] = True
    contract["a_unknown"] = True
    del contract["owner"]
    path = write_fixture(tmp_path, "ordered-findings", contract)

    first = validate_contract_file(path)
    second = validate_contract_file(path)

    assert first.to_dict() == second.to_dict()
    assert list(first.findings) == sorted(first.findings)
    assert any("#/owner" in finding.path for finding in first.findings)
