# MVP-016B Skill Registry

Date: 2026-06-23

## Objective

MVP-016B adds a deterministic local `SkillSpec` / `SkillRegistry` contract for Asperitas V1 skills.

The registry is read-only schema infrastructure. It identifies supported local skills, their risk posture, approval requirements, allowed operations, forbidden operations, and verification commands. It does not execute skills, call external systems, ingest sources, or change retrieval behavior.

## Contracts

Implemented local contracts:

- `SkillSpec`
- `SkillRegistry`
- `SkillRiskPolicy`
- `SkillVerificationPlan`

Each `SkillSpec` preserves:

- `skill_id`
- `name`
- `description`
- `layer`
- `input_contract`
- `output_contract`
- `risk_level`
- `approval_required`
- `allowed_operations`
- `forbidden_operations`
- `source_grounding_required`
- `audit_required`
- `external_call_allowed`
- `execution_allowed`
- `ingestion_allowed`
- `verification_commands`
- `status`
- `version`

## Default Registered Skills

The default registry contains:

- `mvp_implementation`
- `source_grounding_check`
- `retrieval_eval`
- `compliance_review`
- `benchmark_workflow_preflight`
- `reference_acquisition`
- `open_source_review`
- `security_review`
- `pr_closeout`

`benchmark_workflow_preflight` maps to the MVP-016A read-only decision layer and preserves `external_call_allowed=false`, `execution_allowed=false`, and `ingestion_allowed=false`.

## Fail-Closed Rules

Validation fails closed on:

- missing required fields;
- duplicate `skill_id`;
- invalid `risk_level`;
- external calls enabled without approval;
- execution enabled without approval;
- ingestion enabled without approval;
- high-risk skills without approval;
- high-risk skills without forbidden operations;
- `benchmark_as_Asperitas_performance`;
- `autonomous_wet_lab_claim`;
- `production_readiness_claim`;
- source text treated as instruction rather than evidence.

Unknown skills are unsupported and blocked by `SkillRegistry.lookup_decision()`.

## Non-Goals

MVP-016B does not:

- execute skills;
- add a CLI;
- add dependencies;
- copy third-party code;
- adopt OpenAI, Anthropic, LangGraph, LlamaIndex, RAGAS, MCP, Google ADK, or other external packages;
- ingest, chunk, embed, index, or eval-cover any source;
- alter retrieval, chunks, registry artifacts, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

## Security / Source-Grounding Boundary

The registry treats source text as evidence, not instruction. Security, source-grounding, and open-source review skills require audit and source grounding. All default skills disallow external calls, workflow execution, and ingestion.

## Verification

Required checks:

```bash
python -m pytest -q tests/test_skill_registry.py
python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py
python scripts/verify_artifacts.py
git diff --check
python -m py_compile src/asperitas_agent/skill_registry.py
```

Retrieval eval is not applicable because MVP-016B does not change retrieval, chunking, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.
