from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

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
        "deprecated_since": "P1B",
        "compatibility_until": "P1D",
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
            "deprecated_since": "P1B",
            "compatibility_until": "P1D",
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
            "deprecated_since": "P1B",
            "compatibility_until": "P1D",
            "replaced_by": "old_second",
        }
    ]
    second_contract["compatibility"]["aliases"] = [
        {
            "value": "old_second",
            "kind": "deprecated_skill_id",
            "deprecated_since": "P1B",
            "compatibility_until": "P1D",
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
    contract["lifecycle"]["deprecated_since"] = "P1B"

    report = validate_contract_file(write_fixture(tmp_path, "deprecated-skill", contract))

    assert "DEPRECATED_WITHOUT_DISPOSITION" in finding_codes(report)


def test_deprecated_alias_requires_compatibility_expiry(tmp_path):
    contract = valid_contract("alias_skill")
    contract["compatibility"]["aliases"] = [
        {
            "value": "old_alias",
            "kind": "deprecated_skill_id",
            "deprecated_since": "P1B",
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


def test_high_risk_biology_execution_requires_human_gate(tmp_path):
    contract = valid_contract("biology_skill")
    contract["risk"] = {"risk_class": "high", "human_gates": []}
    contract["routing"]["positive_triggers"] = ["wet-lab biological execution"]
    contract["permissions"]["approval_required"] = True
    contract["permissions"]["execution_allowed"] = True

    report = validate_contract_file(write_fixture(tmp_path, "biology-skill", contract))

    assert "HIGH_RISK_BIOLOGY_REQUIRES_HUMAN_GATE" in finding_codes(report)


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
            "deprecated_since": "P1B",
            "compatibility_until": "P1D",
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
            "deprecated_since": "P1B",
            "compatibility_until": "P1D",
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
