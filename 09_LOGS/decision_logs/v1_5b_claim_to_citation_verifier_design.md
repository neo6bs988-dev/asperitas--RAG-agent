# V1.5B Claim-To-Citation Verifier Design Decision

## Date

2026-07-02

## Task

Create the V1.5B claim-to-citation verifier design/specification before any implementation PR. The objective is to define the verifier architecture, data contracts, support taxonomy, biology/compliance layers, eval metrics, eval gates, implementation phases, risks, and acceptance criteria for V1.5C.

## Issue/PR

- Issue: not yet opened.
- PR: not yet opened.
- Branch: `codex/v1-5b-claim-citation-verifier-design`
- Baseline: `main` at `7836517b110390c6fcce5d155ca983fa8ef364ce`

## Files Changed Or Inspected

Changed:

- `docs/V1_5B_CLAIM_TO_CITATION_VERIFIER_DESIGN.md`
- `docs/V1_5_PERFORMANCE_ROADMAP.md`
- `09_LOGS/decision_logs/v1_5b_claim_to_citation_verifier_design.md`

Inspected:

- `README.md`
- `AGENTS.md`
- `docs/AI_DEVELOPMENT_OS.md`
- `docs/WORKFLOW.md`
- `docs/QUALITY_GATES.md`
- `docs/ROADMAP.md`
- `docs/V1_5_PERFORMANCE_ROADMAP.md`
- `docs/AOS_SOURCE_POLICY.md`
- `.github/pull_request_template.md`
- `09_LOGS/decision_logs/`
- `docs/MVP008_SOURCE_GROUNDED_ANSWER_CONTRACT.md`
- `docs/RETRIEVAL_EVAL_THRESHOLDS.md`
- `eval_results/v1_3c_answer_contract/README.md`
- `eval_results/v1_3d_truth_compliance_router/README.md`
- `eval_results/v1_3e_retrieval_threshold_triage/README.md`
- `src/asperitas_agent/schemas.py`
- `src/asperitas_agent/evidence_pack.py`
- `src/asperitas_agent/answer_generation.py`
- `src/asperitas_agent/answer_contract.py`
- `src/asperitas_agent/truth_compliance_router.py`

## Decision

Accept a design-first V1.5B step before implementation. The repository already has retrieval diagnostics, an answer contract, evidence packaging, truth/compliance routing, V1.4 preservation boundaries, and V1.5A cost-aware quality gates, but it does not yet verify each material answer claim against specific cited evidence spans.

The next performance core is claim-to-citation verification because citations can be present at the answer level while still failing to support exact atomic claims. V1.5B therefore defines the architecture needed for V1.5C:

```text
answer -> atomic claims -> evidence spans -> citation support decision -> answer-level diagnostics
```

This is a design target only. It does not change runtime behavior, implement the verifier, generate fixtures, or claim RAG performance improvement.

## External Reference Doctrine

RAGAS-style, ARES-style, VeriCite-style, and MedRAGChecker-style ideas are treated as P6 external design references only. They inform the separation of retrieval/context quality, faithfulness, answer relevance, claim verification, supporting evidence selection, unsupported/contradictory claim diagnostics, and safety/compliance-aware error classes. They are not Asperitas implementation evidence.

## Commands And Metrics

- Branch baseline: Fresh Run, `main` at `7836517b110390c6fcce5d155ca983fa8ef364ce`.
- Risk level: Fresh Run, low.
- Changed surface: Fresh Run, docs/roadmap/decision-log only.
- Retrieval metrics: Not Run, because no retrieval, chunking, scoring, metadata filtering, embeddings, vector DB, reranking, answer generation, evidence selection, or eval behavior changed.
- Test metrics: Not Run, because no source code or executable behavior changed.
- GitHub Actions minutes: Not Run locally; should be observed after the PR opens to confirm the docs-only Quality Gates path.

## Verification Evidence

- `git status --short --branch`: Fresh Run, passed; only the V1.5B design doc, V1.5B decision log, and V1.5 roadmap sync are changed.
- `git diff --stat`: Fresh Run, reviewed; changed surface is docs/roadmap/decision-log only.
- `git diff --check`: Fresh Run, passed with only the existing LF-to-CRLF working-copy warning on `docs/V1_5_PERFORMANCE_ROADMAP.md`.
- Markdown/code-fence sanity: Fresh Run, passed; changed Markdown files have balanced code fences.
- Changed-surface sanity: Fresh Run, passed; no source code, tests, eval fixtures, source artifacts, registry data, CI config, dependency files, generated indexes, or model binaries changed.
- Truth-boundary sanity: Fresh Run, passed; production DB/KG/vector DB, wet-lab validation, legal/regulatory approval, autonomous lab, foundation-model completion, and RAG performance improvement terms appear only in negative/no-overclaim contexts.
- Roadmap consistency: Fresh Run, passed; V1.5A remains completed governance/gate sync, V1.5B is design-only, and V1.5C remains the implementation next step.

## V1.4 No-Regression Boundary

This decision does not authorize source/runtime behavior changes, answer behavior changes, retrieval scoring changes, source ingestion, chunk regeneration, metadata mutation, embedding/vector DB behavior changes, reranking behavior changes, generated index/model binary additions, dependency/service/secret additions, eval fixture generation, or claims of production DB, production KG, production vector DB, wet-lab validation, legal approval, regulatory approval, autonomous lab operation, customer/investor traction, or proprietary LLM/foundation-model completion.

## V1.5C Implementation Direction

V1.5C should proceed in small implementation PRs:

1. schema and taxonomy;
2. deterministic parser/extractor baseline;
3. evidence span matcher;
4. support classifier;
5. biology and compliance tagging;
6. verifier report and eval pack;
7. answer contract integration;
8. quality gate integration.

Each implementation PR must add or update tests and run the smallest sufficient targeted checks. Retrieval eval is required only when retrieval, evidence selection, eval fixtures, ranking, reranking, answer generation, or eval semantics change.

## Risks And Residual Issues

- GitHub Actions status cannot be reported until the PR exists.
- The design is specific enough to guide V1.5C, but it does not prove verifier accuracy.
- Future fixtures require careful source rights, disclosure, and sensitive-biology review.
- Any future model-judge or LLM-based verifier should remain out of the default path until deterministic contracts and eval gates exist.

## Next Action

Open a docs-only PR titled `docs: design V1.5B claim-to-citation verifier`. After merge, open the first V1.5C schema/taxonomy implementation PR with targeted tests and no retrieval eval unless behavior changes require it.
