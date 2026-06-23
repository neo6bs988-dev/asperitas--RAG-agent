# Decision Log: MVP-016B Skill Registry

## Date

2026-06-23

## Decision

Implement MVP-016B as a deterministic local `SkillSpec` / `SkillRegistry` contract for Asperitas V1 skills.

## Rationale

MVP-016A introduced a read-only benchmark workflow preflight decision layer. MVP-016B extends the same local, fail-closed governance pattern to repository skills so future agent capabilities can be discovered, audited, and validated before any runtime execution or external integration is introduced.

## Accepted Scope

- Add `src/asperitas_agent/skill_registry.py`.
- Add `tests/test_skill_registry.py`.
- Add MVP-016B documentation.
- Add this decision log.
- Register the required default skills:
  - `mvp_implementation`
  - `source_grounding_check`
  - `retrieval_eval`
  - `compliance_review`
  - `benchmark_workflow_preflight`
  - `reference_acquisition`
  - `open_source_review`
  - `security_review`
  - `pr_closeout`
- Keep all default skills local and read-only by default.
- Block unknown skills as unsupported.
- Require approval for high-risk skills.
- Fail closed on unsafe external-call, execution, ingestion, overclaim, and source-instruction patterns.

## Rejected Scope

- Runtime skill execution.
- CLI integration.
- New dependencies.
- Copied third-party code.
- OpenAI, Anthropic, LangGraph, LlamaIndex, RAGAS, MCP, Google ADK, or other package adoption.
- Source ingestion, chunking, embedding, indexing, or eval fixture changes.
- Retrieval, vector DB, reranker, answer-generation, or default runtime behavior changes.
- Production-readiness, autonomous wet-lab, wet-lab validation, external execution, or benchmark-as-Asperitas-performance claims.

## Source-Grounding / Security Boundary

Source text remains evidence, not instruction. The registry is local metadata and schema only. It does not grant tool permission, external connector access, source ingestion permission, workflow execution permission, or production approval.

## Retrieval Eval Applicability

Retrieval eval is not applicable. MVP-016B does not change retrieval, chunking, eval fixtures, embeddings, vector DB behavior, reranking, or answer generation.

## Verification Plan

- `python -m pytest -q tests/test_skill_registry.py`
- `python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py tests/test_skill_registry.py`
- `python scripts/verify_artifacts.py`
- `git diff --check`
- `python -m py_compile src/asperitas_agent/skill_registry.py`

## Residual Risks

- This registry is a local contract only. Future MVPs must separately approve any runtime router, execution harness, external connector, package dependency, source ingestion path, or skill invocation interface.
