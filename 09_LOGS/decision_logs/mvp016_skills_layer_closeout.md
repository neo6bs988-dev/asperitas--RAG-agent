# Decision Log: MVP-016 Skills Layer Closeout

Date: 2026-06-23

## Decision

Close MVP-016 by hardening `SkillRegistry` coverage against existing local `.agents/skills/*/SKILL.md` files and documenting the completed skills layer.

## Rationale

MVP-016C validation was already read-only and passing, but it surfaced 17 warnings for well-formed local skill files missing from `SkillRegistry`. MVP-016D registers the stage-appropriate, repo-native governance and quality skills so the local registry better reflects the repository's active skill surface.

## Added Registry Coverage

Registered high-risk, approval-required contracts for:

- audit trace
- compliance audit
- evaluation
- MCP expansion planning
- RAG development
- retrieval
- security
- source audit
- V1 architecture
- workflow planning
- dependency security quality gate
- MVP release management
- performance optimization gate
- source-grounding citation

## Remaining Warnings

Three warnings remain intentional:

- `embeddings-vector-db-mvp005`: legacy MVP-specific skill, not a default V1 registry skill.
- `github-pr-review`: covered by `pr_closeout` for the current registry layer.
- `open-source-adoption-review`: covered by `open_source_review` for the current registry layer.

## Safety Boundary

This change is registry and validation hardening only. It does not enable:

- execution
- external calls
- ingestion
- runtime routing
- CLI integration
- retrieval behavior changes
- chunking changes
- source registry data changes
- eval fixture changes
- embeddings or vector DB changes
- reranker changes
- answer generation changes

All new skills preserve fail-closed overclaim blocks for:

- benchmark metrics represented as Asperitas performance
- autonomous wet-lab claims
- production-readiness claims

## Verification

Run the MVP-016D closeout test set before merge:

```bash
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py
python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py tests/test_skill_discovery.py
python scripts/validate_skill_registry.py --json
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/skill_registry.py src/asperitas_agent/skill_discovery.py
```

Retrieval eval is not applicable because retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, and default runtime behavior are unchanged.

## Next

Proceed to MVP-017: RAGAS-style eval layer.
