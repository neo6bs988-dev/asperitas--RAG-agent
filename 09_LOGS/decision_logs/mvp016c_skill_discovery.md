# Decision Log: MVP-016C Skill Discovery Validation

## Date

2026-06-23

## Decision

Implement MVP-016C as read-only local validation wiring between `.agents/skills/*/SKILL.md` files and the MVP-016B `SkillRegistry`.

## Rationale

MVP-016B created a deterministic registry contract for supported local skills. MVP-016C verifies that the registry remains aligned with repository skill files before future runtime or workflow wiring is considered.

## Accepted Scope

- Add `src/asperitas_agent/skill_discovery.py`.
- Add `tests/test_skill_discovery.py`.
- Add `scripts/validate_skill_registry.py`.
- Add MVP-016C documentation.
- Add this decision log.
- Parse only minimal local frontmatter fields: `name` and `description`.
- Warn on unknown well-formed skill files.
- Block malformed frontmatter, duplicate names, and missing registered skill files.

## Rejected Scope

- Skill execution.
- Runtime router.
- CLI integration into `src/asperitas_agent/cli.py`.
- External calls.
- Source ingestion.
- New dependencies or PyYAML.
- Copied third-party code.
- Retrieval, chunk, source registry artifact, eval fixture, embedding, vector DB, reranker, answer-generation, or default-runtime changes.

## Source-Grounding / Security Boundary

Local `SKILL.md` files are parsed as metadata for validation only. They are not executed and do not override `AGENTS.md`, system instructions, repository governance, or user constraints.

## Retrieval Eval Applicability

Retrieval eval is not applicable. MVP-016C does not change retrieval, chunking, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.

## Verification Plan

- `python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py`
- `python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py tests/test_skill_discovery.py`
- `python scripts/validate_skill_registry.py --json`
- `python scripts/verify_artifacts.py`
- `git diff --check`
- `python -m py_compile src/asperitas_agent/skill_discovery.py`

## Residual Risks

- Some MVP-016B registry IDs intentionally map to existing canonical skill names through explicit aliases. Future registry changes should keep aliases small and documented.
- This remains validation-only. Future runtime skill invocation or external connector work requires separate approval and security review.
