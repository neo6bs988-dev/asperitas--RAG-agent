from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from asperitas_agent.skill_discovery import (
    SKILL_ALIASES,
    discover_skill_files,
    validate_skill_files_against_registry,
)
from asperitas_agent.skill_registry import SkillRegistry, require_skill

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_skill_registry.py"
EXPECTED_REMAINING_WARNINGS = [
    "unknown well-formed skill file: embeddings-vector-db-mvp005",
    "unknown well-formed skill file: github-pr-review",
    "unknown well-formed skill file: open-source-adoption-review",
]


def write_skill(root: Path, directory: str, frontmatter: str, body: str = "# Body\n") -> Path:
    path = root / ".agents" / "skills" / directory / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + "\n" + body, encoding="utf-8")
    return path


def skill_frontmatter(name: str, description: str) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---"


def test_discovers_valid_skill_files(tmp_path):
    write_skill(tmp_path, "source-grounding-check", skill_frontmatter("source-grounding-check", "Checks grounding."))

    discovered = discover_skill_files(tmp_path)

    assert len(discovered) == 1
    assert discovered[0].name == "source-grounding-check"
    assert discovered[0].description == "Checks grounding."
    assert discovered[0].relative_path == ".agents/skills/source-grounding-check/SKILL.md"


def test_parses_quoted_frontmatter(tmp_path):
    write_skill(
        tmp_path,
        "security-review",
        '---\nname: "security-review"\ndescription: "Checks security boundaries."\n---',
    )

    discovered = discover_skill_files(tmp_path)

    assert discovered[0].name == "security-review"
    assert discovered[0].description == "Checks security boundaries."


def test_validates_current_default_registry_against_repo_skill_files():
    report = validate_skill_files_against_registry(REPO_ROOT).to_dict()

    assert report["ok"] is True
    assert report["missing_skill_files"] == []
    assert report["invalid_frontmatter"] == []
    assert report["errors"] == []
    assert report["warnings"] == EXPECTED_REMAINING_WARNINGS


def test_no_missing_skill_files_for_registered_default_skills():
    report = validate_skill_files_against_registry(REPO_ROOT).to_dict()

    assert report["missing_skill_files"] == []


def test_skill_aliases_are_documented_and_stable():
    assert SKILL_ALIASES == {
        "benchmark_workflow_preflight": ("benchmark-workflow-preflight", "mvp-implementation"),
        "compliance_review": ("compliance-review", "compliance-biosafety-review"),
        "retrieval_eval": ("retrieval-eval", "retrieval-eval-quality-gate"),
    }


def test_underscore_hyphen_matching_works(tmp_path):
    skill = require_skill("source_grounding_check")
    registry = SkillRegistry((skill,))
    write_skill(tmp_path, "source-grounding-check", skill_frontmatter("source-grounding-check", "Checks grounding."))

    report = validate_skill_files_against_registry(tmp_path, registry).to_dict()

    assert report["ok"] is True
    assert report["missing_skill_files"] == []


def test_missing_skill_file_fails(tmp_path):
    registry = SkillRegistry((require_skill("source_grounding_check"),))

    report = validate_skill_files_against_registry(tmp_path, registry).to_dict()

    assert report["ok"] is False
    assert report["missing_skill_files"] == ["source_grounding_check"]
    assert "missing skill file for registered skill: source_grounding_check" in report["errors"]


def test_duplicate_skill_names_fail(tmp_path):
    write_skill(tmp_path, "one", skill_frontmatter("duplicate-skill", "First."))
    write_skill(tmp_path, "two", skill_frontmatter("duplicate-skill", "Second."))

    report = validate_skill_files_against_registry(tmp_path, SkillRegistry(())).to_dict()

    assert report["ok"] is False
    assert report["duplicate_skill_names"] == ["duplicate-skill"]
    assert "duplicate skill name: duplicate-skill" in report["errors"]


def test_missing_description_fails(tmp_path):
    write_skill(tmp_path, "source-grounding-check", "---\nname: source-grounding-check\n---")

    report = validate_skill_files_against_registry(tmp_path, SkillRegistry((require_skill("source_grounding_check"),))).to_dict()

    assert report["ok"] is False
    assert report["invalid_frontmatter"][0]["errors"] == ["description is required"]


def test_unknown_well_formed_skill_warns(tmp_path):
    write_skill(tmp_path, "unknown-skill", skill_frontmatter("unknown-skill", "Unknown but valid."))

    report = validate_skill_files_against_registry(tmp_path, SkillRegistry(())).to_dict()

    assert report["ok"] is True
    assert report["missing_registry_specs"] == ["unknown-skill"]
    assert report["warnings"] == ["unknown well-formed skill file: unknown-skill"]


def test_report_is_json_serializable_and_stable(tmp_path):
    write_skill(tmp_path, "source-grounding-check", skill_frontmatter("source-grounding-check", "Checks grounding."))
    registry = SkillRegistry((require_skill("source_grounding_check"),))

    first = json.dumps(validate_skill_files_against_registry(tmp_path, registry).to_dict(), sort_keys=True)
    second = json.dumps(validate_skill_files_against_registry(tmp_path, registry).to_dict(), sort_keys=True)

    assert first == second
    assert json.loads(first)["ok"] is True


def test_script_returns_success_on_repo_state():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["discovered_skills"]
    assert payload["registered_skills"]
