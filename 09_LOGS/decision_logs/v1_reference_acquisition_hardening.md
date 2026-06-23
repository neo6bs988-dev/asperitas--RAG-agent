# Decision Log — V1 Reference Acquisition and Architecture Hardening

Date: 2026-06-23
Status: docs-only governance hardening
Branch: v1-reference-acquisition-hardening

## Decision

Adopt a V1 reference acquisition and architecture-hardening policy before proceeding with deeper MVP-016+ implementation.

## Rationale

The user requested that future V1 development and performance-hardening work incorporate:

- OpenAI Codex Skills architecture;
- Anthropic Skills + MCP architecture;
- LangGraph workflow architecture;
- LlamaIndex RAG architecture;
- RAGAS evaluation framework;
- Ginkgo autonomous-lab validation philosophy;
- Recursion data-flywheel philosophy;
- Benchling metadata/audit philosophy;
- official-source-first knowledge acquisition;
- provenance metadata for every reference source.

This decision strengthens V1 development without changing runtime behavior.

## Architecture Impact

This decision reframes the post-MVP-015 roadmap around six V1 layers:

```text
Knowledge Layer
+ Skills Layer
+ Workflow Layer
+ Evaluation Layer
+ Audit Layer
+ Security Layer
```

Each future implementation must improve at least one layer.

## Accepted Scope

- Add a docs-only V1 reference acquisition and hardening guide.
- Define allowed reference source classes.
- Define metadata-only reference schema.
- Define MVP-016 to MVP-019 priority mapping.
- Define performance-hardening workflow.
- Preserve no-overclaim and source-grounding constraints.

## Rejected / Deferred Scope

- No source ingestion.
- No registry mutation.
- No chunk mutation.
- No embedding or vector DB change.
- No retrieval behavior change.
- No reranker or hybrid default change.
- No answer-generation change.
- No RAGAS package integration.
- No external API integration.
- No production deployment claim.
- No autonomous wet-lab claim.

## Verification

Docs-only change. Required checks:

```bash
git status --short --branch
git diff --check
```

No pytest or retrieval eval is required because no source code, retrieval behavior, chunks, registry, eval fixtures, embeddings, vector DB, reranking, or answer generation were changed.

## Risks

- The guide could be mistaken for implemented functionality. Mitigation: explicitly labels all items as policy, metadata candidates, or future MVP scope.
- Reference-source URLs and versions still require later review before production ingestion.
- MVP-016 still requires a clean implementation branch and focused tests.

## Next Recommended MVP

MVP-016 — Skills Framework preflight and implementation:

- inspect existing `.agents/skills`;
- define local `SkillSpec` / `SkillRegistry` contracts;
- test skill validation, risk gating, JSON output, and no-external-execution defaults;
- preserve all current RAG/retrieval boundaries.
