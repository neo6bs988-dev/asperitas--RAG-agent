from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .skill_registry import (
    DEFAULT_SKILL_REGISTRY,
    SKILL_IDENTITY_ALIASES,
    SkillRegistry,
    build_skill_identity_authority,
)


@dataclass(frozen=True)
class DiscoveredSkill:
    name: str
    description: str
    relative_path: str
    directory_name: str
    normalized_name: str
    frontmatter_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class SkillDiscoveryReport:
    ok: bool
    discovered_skills: tuple[dict[str, Any], ...]
    registered_skills: tuple[str, ...]
    missing_skill_files: tuple[str, ...]
    missing_registry_specs: tuple[str, ...]
    duplicate_skill_names: tuple[str, ...]
    invalid_frontmatter: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "discovered_skills": [dict(skill) for skill in self.discovered_skills],
            "registered_skills": list(self.registered_skills),
            "missing_skill_files": list(self.missing_skill_files),
            "missing_registry_specs": list(self.missing_registry_specs),
            "duplicate_skill_names": list(self.duplicate_skill_names),
            "invalid_frontmatter": [dict(item) for item in self.invalid_frontmatter],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


def discover_skill_files(root: str | Path) -> list[DiscoveredSkill]:
    repo_root = Path(root)
    skills_root = repo_root / ".agents" / "skills"
    if not skills_root.exists():
        return []

    discovered: list[DiscoveredSkill] = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        metadata, errors = _parse_skill_frontmatter(skill_file)
        directory_name = skill_file.parent.name
        skill_name = metadata.get("name", "")
        normalized_name = _normalize_skill_name(skill_name or directory_name)
        discovered.append(
            DiscoveredSkill(
                name=skill_name,
                description=metadata.get("description", ""),
                relative_path=skill_file.relative_to(repo_root).as_posix(),
                directory_name=directory_name,
                normalized_name=normalized_name,
                frontmatter_errors=errors,
            )
        )
    return discovered


def validate_skill_files_against_registry(
    root: str | Path,
    registry: SkillRegistry | None = None,
) -> SkillDiscoveryReport:
    active_registry = registry or DEFAULT_SKILL_REGISTRY
    discovered = discover_skill_files(root)
    discovered_by_key = _discovered_lookup(discovered)
    registered_ids = active_registry.list_skill_ids()
    legacy_ids = {alias.legacy_id for alias in SKILL_IDENTITY_ALIASES}
    successor_ids = {
        alias.canonical_id for alias in SKILL_IDENTITY_ALIASES if alias.legacy_id in registered_ids
    }
    canonical_ids = tuple(
        sorted(
            {skill_id for skill_id in registered_ids if skill_id not in legacy_ids}
            | successor_ids
        )
    )
    identity_authority = build_skill_identity_authority(canonical_ids)

    invalid_frontmatter = tuple(
        {
            "relative_path": skill.relative_path,
            "name": skill.name,
            "description": skill.description,
            "errors": list(skill.frontmatter_errors),
        }
        for skill in discovered
        if skill.frontmatter_errors
    )
    duplicate_names = _duplicate_skill_names(discovered)

    missing_skill_files = tuple(
        skill_id
        for skill_id in canonical_ids
        if _normalize_skill_name(skill_id) not in discovered_by_key
    )
    missing_registry_specs = tuple(
        skill.normalized_name
        for skill in discovered
        if not skill.frontmatter_errors
        and identity_authority.resolve(skill.normalized_name.replace("-", "_")).identity_kind != "canonical"
    )
    warnings = tuple(f"unknown well-formed skill file: {skill_id}" for skill_id in missing_registry_specs)
    errors = tuple(
        [
            *(f"missing skill file for registered skill: {skill_id}" for skill_id in missing_skill_files),
            *(f"duplicate skill name: {name}" for name in duplicate_names),
            *(f"invalid frontmatter: {item['relative_path']}" for item in invalid_frontmatter),
        ]
    )
    return SkillDiscoveryReport(
        ok=not errors,
        discovered_skills=tuple(skill.to_dict() for skill in discovered),
        registered_skills=registered_ids,
        missing_skill_files=missing_skill_files,
        missing_registry_specs=missing_registry_specs,
        duplicate_skill_names=duplicate_names,
        invalid_frontmatter=invalid_frontmatter,
        warnings=warnings,
        errors=errors,
    )


def _parse_skill_frontmatter(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    metadata = {"name": "", "description": ""}
    if not text.startswith("---\n"):
        return metadata, ("missing opening frontmatter delimiter", "name is required", "description is required")

    lines = text.splitlines()
    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return metadata, ("missing closing frontmatter delimiter", "name is required", "description is required")

    for line in lines[1:closing_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        clean_key = key.strip()
        if clean_key in metadata:
            metadata[clean_key] = _strip_simple_yaml_scalar(value)

    if not metadata["name"]:
        errors.append("name is required")
    if not metadata["description"]:
        errors.append("description is required")
    return metadata, tuple(errors)


def _strip_simple_yaml_scalar(value: str) -> str:
    clean = value.strip()
    if len(clean) >= 2 and clean[0] == clean[-1] and clean[0] in {"'", '"'}:
        return clean[1:-1].strip()
    return clean


def _normalize_skill_name(value: str) -> str:
    return value.strip().casefold().replace("_", "-").replace(" ", "-")


def _discovered_lookup(discovered: list[DiscoveredSkill]) -> set[str]:
    keys: set[str] = set()
    for skill in discovered:
        keys.add(_normalize_skill_name(skill.directory_name))
        if skill.name:
            keys.add(skill.normalized_name)
    return keys


def _duplicate_skill_names(discovered: list[DiscoveredSkill]) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    display: dict[str, str] = {}
    for skill in discovered:
        if not skill.name:
            continue
        normalized = skill.normalized_name
        counts[normalized] = counts.get(normalized, 0) + 1
        display.setdefault(normalized, skill.name)
    return tuple(display[name] for name, count in sorted(counts.items()) if count > 1)
