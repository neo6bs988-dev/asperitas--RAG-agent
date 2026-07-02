# V1.5C Claim-To-Citation Verifier Schema And Taxonomy Decision

## Date

2026-07-02

## Task

Implement V1.5C step 1: data contracts and taxonomy constants for the future claim-to-citation verifier. This implementation is schema/taxonomy only and does not implement claim extraction, evidence matching, support classification, model judging, retrieval integration, answer generation integration, compliance router behavior, eval fixtures, or runtime behavior changes.

## Issue/PR

- Issue: not yet opened.
- PR: not yet opened.
- Branch: `codex/v1-5c-verifier-schema-taxonomy`
- Baseline: `main` at `7f4715f6264f370a049cb7a984d8cf21f53d691d`

## Preflight

| Field | Classification |
|---|---|
| Risk level | Medium |
| Changed surface | Source code, tests, decision log |
| Behavior impact | No retrieval, answer generation, compliance routing, eval fixture, source registry, chunking, embedding, vector DB, reranking, dependency, service, or runtime-default behavior change |
| Required verification | Targeted schema unit tests, import/syntax check, `git diff --check`, changed-surface sanity, truth-boundary review |
| Skipped checks | Retrieval evals are not required because retrieval logic, evidence selection, answer generation, eval semantics, chunking, metadata handling, embeddings, vector DB behavior, and reranking are not changed |

## Decision

Add an isolated verifier schema module for V1.5C data contracts. The module defines stable string taxonomies and dataclass contracts for:

- atomic claims;
- evidence spans;
- claim verification reports;
- answer verification summaries;
- biology entities;
- support status values;
- biology entity types;
- compliance/truth-boundary tags;
- normalized verifier failure modes.

The contracts use deterministic validation helpers and JSON-safe serialization/round-trip helpers so later verifier PRs can build extraction, matching, support classification, and report generation without changing the existing RAG runtime.

## Truth Boundary

This decision records schema/taxonomy implementation only. It does not prove that Asperitas has a working claim-to-citation verifier, claim extractor, evidence matcher, support classifier, NLI/LLM judge, answer-faithfulness evaluator, production DB, production KG, production vector DB, wet-lab validation, legal/regulatory approval, autonomous lab capability, or biological foundation model.

## Validation Plan

- `python -m pytest tests/test_claim_verifier_schema.py`
- `python -m compileall -q src/asperitas_agent/claim_verifier_schema.py`
- `git diff --check`
- inspect changed files and verify no runtime integration was added

## Next Action

Open the V1.5C schema/taxonomy PR. The next implementation PR should add the deterministic extractor or evidence-span matcher, depending on repo fit and review feedback.
