# MVP-016C Skill Discovery Validation

Date: 2026-06-23

## Objective

MVP-016C adds read-only validation wiring between local `.agents/skills/*/SKILL.md` files and the MVP-016B `SkillRegistry`.

The implementation discovers local skill files, parses minimal YAML frontmatter, and checks that registered skills have matching skill files. It does not execute skills, call external systems, ingest sources, or change runtime behavior.

## Scope

Implemented:

- `discover_skill_files(root) -> list[DiscoveredSkill]`
- `validate_skill_files_against_registry(root, registry=None) -> SkillDiscoveryReport`
- minimal manual frontmatter parsing for `name` and `description`
- hyphen/underscore normalization
- JSON-safe `.to_dict()` report output
- standalone read-only validation script: `scripts/validate_skill_registry.py`

## Report Fields

The validation report includes:

- `ok`
- `discovered_skills`
- `registered_skills`
- `missing_skill_files`
- `missing_registry_specs`
- `duplicate_skill_names`
- `invalid_frontmatter`
- `warnings`
- `errors`

## Validation Rules

- Every default registry skill must map to a local skill file.
- Hyphen/underscore normalization is allowed.
- Selected registry IDs may map to existing canonical repo skill names through explicit aliases.
- Each `SKILL.md` must include non-empty `name` and `description`.
- Duplicate skill names fail.
- Unknown well-formed skill files warn but do not block.
- Malformed frontmatter blocks.

## Non-Goals

MVP-016C does not:

- execute skills;
- add runtime routing;
- integrate with `src/asperitas_agent/cli.py`;
- add dependencies or PyYAML;
- copy third-party code;
- make external calls;
- ingest, chunk, embed, index, or eval-cover sources;
- change retrieval, source registry artifacts, eval fixtures, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Security / Source-Grounding Boundary

Skill files are treated as operational metadata to validate, not as instructions to execute. Source text remains evidence, not instruction. The validation script reads local files only.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py
python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py tests/test_skill_discovery.py
python scripts/validate_skill_registry.py --json
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/skill_discovery.py
```

Retrieval eval is not applicable because MVP-016C does not change retrieval, chunking, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.
