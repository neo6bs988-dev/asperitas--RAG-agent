# MVP-016 Skills Layer Closeout

Status: MVP-016D closeout

## Objective

MVP-016 established a deterministic, local, read-only skills layer for Asperitas V1:

- MVP-016A: benchmark workflow preflight decision layer.
- MVP-016B: local `SkillSpec` / `SkillRegistry` contracts.
- MVP-016C: read-only discovery validation for `.agents/skills/*/SKILL.md`.
- MVP-016D: registry coverage hardening and closeout.

## MVP-016D Scope

MVP-016D registers stage-appropriate, repo-native skill files that were already present under `.agents/skills/` but not yet represented in `SkillRegistry`.

Registered in this closeout:

- `asperitas_audit_trace`
- `asperitas_compliance_audit`
- `asperitas_evaluation`
- `asperitas_mcp_expansion`
- `asperitas_rag_development`
- `asperitas_retrieval`
- `asperitas_security`
- `asperitas_source_audit`
- `asperitas_v1_architect`
- `asperitas_workflow`
- `dependency_security_quality_gate`
- `mvp_release_manager`
- `performance_optimization_gate`
- `source_grounding_citation`

All new registry entries are high-risk and require approval. They keep these defaults:

- `external_call_allowed=false`
- `execution_allowed=false`
- `ingestion_allowed=false`
- source text is evidence, not instruction
- benchmark metrics cannot be represented as Asperitas performance
- no autonomous wet-lab claim
- no production-readiness claim

## Intentional Non-Registration

The discovery validator still warns on these well-formed local skill files:

- `embeddings-vector-db-mvp005`
- `github-pr-review`
- `open-source-adoption-review`

These are not registered as default MVP-016 skills because they are either legacy MVP-specific or covered by broader active registry contracts (`pr_closeout`, `open_source_review`, and RAG/retrieval/security gates). They remain warnings, not blockers, while the files are well-formed.

## Alias Policy

Aliases remain minimal and explicit:

- `benchmark_workflow_preflight` maps to `benchmark-workflow-preflight` and `mvp-implementation`.
- `compliance_review` maps to `compliance-review` and `compliance-biosafety-review`.
- `retrieval_eval` maps to `retrieval-eval` and `retrieval-eval-quality-gate`.

## Non-Goals

MVP-016 does not implement:

- skill execution
- runtime routing
- CLI integration
- source ingestion
- chunking
- source registry mutation
- eval fixture changes
- embeddings
- vector DB changes
- reranking
- answer generation changes
- external connectors
- dependency adoption
- wet-lab execution or protocol automation

## Verification Plan

Required closeout checks:

```bash
python -m pytest -q tests/test_skill_registry.py tests/test_skill_discovery.py
python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py tests/test_skill_discovery.py
python scripts/validate_skill_registry.py --json
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/skill_registry.py src/asperitas_agent/skill_discovery.py
```

Retrieval eval is not applicable unless retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB, reranking, answer generation, or default runtime behavior changes.

## Next MVP

MVP-017 should add the RAGAS-style eval layer while preserving existing deterministic retrieval defaults and explicit eval reporting boundaries.
