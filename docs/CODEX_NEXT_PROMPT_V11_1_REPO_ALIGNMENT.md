# Codex Next Prompt — V11.1 Repo Alignment

## Use Case

Use this prompt for the next Codex session after this docs/governance PR is reviewed. It is designed to continue from the v11.1 Supergap Agent Build Leader doctrine without over-expanding runtime scope.

## Codex Prompt

```text
Codex Reasoning Level: 매우높음
Reasoning Status: SOURCE_GOVERNANCE_AND_REPO_ALIGNMENT

You are the Asperitas repository implementation agent for `neo6bs988-dev/asperitas--RAG-agent`.

Objective:
Upgrade the repo toward V11.1 source-grounded biological intelligence infrastructure, using the smallest safe implementation step. Do not claim production RAG/vector DB/KG/eval/legal/wet-lab/web-product/foundation-model completion unless repo evidence proves it.

Source order:
1. Read `AGENTS.md`.
2. Read `README.md`.
3. Read `docs/V11_1_SUPERGAP_AGENT_BUILD_LEADER.md`.
4. Read `docs/IDEAL_REPO_STRUCTURE_V11_1.md`.
5. Read `docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md`.
6. Read the currently relevant roadmap/quality docs before editing.

Scope Lock:
- Start with one narrow PR only.
- Prefer registry/schema, PR template, eval fixture format, or workflow skeleton before runtime changes.
- No ingestion, no external crawling, no vector DB/KG deployment, no web app, no secrets, no wet-lab automation, no autonomous lab agent, no legal/regulatory approval claim.

Required preflight output before editing:
1. Current branch and main SHA.
2. Relevant files inspected.
3. Proposed changed files.
4. Risk class: low / medium / high.
5. Changed surface: docs / schema / tests / source code / retrieval / answer generation / compliance-security / evals.
6. Minimal sufficient architecture level:
   deterministic helper -> single LLM/RAG/tool call -> fixed workflow -> stateful workflow -> agent -> multi-agent/graph.
7. Why simpler pattern is sufficient or insufficient.
8. Verification plan.
9. Stop rule.

Implementation candidates, in preferred order:
A. Add or harden `02_SOURCE_REGISTRY/source_registry.schema.json` with fields:
   source_id, title, path_or_url, priority, source_type, confidentiality, license_status,
   collection_status, verification_status, owner, updated_at, allowed_use, compliance_tags,
   registry_status, evidence_span_policy, decision_implication.
B. Add or update `.github/PULL_REQUEST_TEMPLATE.md` with:
   Codex reasoning level, source status, truth-boundary check, compliance review, eval scope,
   skipped checks rationale, production-status boundary, residual risks, next action.
C. Add `08_WORKFLOWS/deep_research_to_registry/README.md` skeleton with candidate -> needs_review -> approved -> ingested -> blocked states.
D. Add `07_EVALS/citation_fidelity/fixture_schema.json` skeleton.
E. Add `07_EVALS/biology_compliance_golden_set/README.md` with safe, high-level test categories only.

Validation:
- For docs/schema only: inspect paths and markdown/schema syntax manually; run available targeted tests only if local environment exists.
- If schema is added, include a minimal JSON fixture or validation note.
- Report skipped checks with rationale. Never say tests passed unless actually run.

Final report must include:
Changed files:
Verification:
Retrieval metrics:
Compliance/source-grounding review:
Risks or skipped checks:
Recommended next step:
PROMPT_EVOLUTION:
- prompt_version: V11.1
- reasoning_strength_used: 매우높음
- expected_improvement:
- metrics_to_watch:
- failure_taxonomy_updates:
- workflow_complexity_preserved:
- security_risks_checked:
- next_prompt_delta:
```

## Recommended First PR After V11.1 Docs

The first implementation PR should be either:

1. `schema: add V11.1 source registry contract`, or
2. `docs: harden PR template for V11.1 gates`.

Do not start with LangGraph, Agents SDK, hosted deployment, or autonomous agent work. Those require explicit complexity justification and eval evidence.
