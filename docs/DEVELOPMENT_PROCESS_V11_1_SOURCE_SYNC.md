# Development Process v11.1 Source Sync

## Executive Bottom Line

This document synchronizes the Asperitas development doctrine for V1.6D and later work. The default operating mode is source-grounded, auditable, compliance-aware, token/CI-efficient, and MVP-gated.

The immediate implication is strict scope control: V1.6D is docs-only. Do not expand into schema, runtime, retrieval, compliance routing, CI, dependency, vector DB, KG, or answer-generation changes without explicit approval.

## Source Status / Truth Boundary

This document is a development-process source sync. It is not proof that production DB, KG, vector DB, retrieval eval, compliance guardrails, legal review, wet-lab validation, autonomous lab execution, or foundation-model capability is complete.

Source maps, docs, PRs, eval design, roadmap notes, and architecture sketches are planning artifacts. They are not production DB/KG/vector DB completion evidence.

## Updated Development Loop

Use this loop for Asperitas RAG-agent, Codex, GitHub, and AI-agent development work:

```text
Scope Lock -> Source & Risk Preflight -> Contract Design -> Minimal Implementation -> Eval Harness -> Dry Run & Regression -> Human Gate -> Merge & Evidence Log -> Learn Back
```

| Stage | Required output | Stop condition |
| --- | --- | --- |
| Scope Lock | Goal, success criteria, allowed files, forbidden files, validation budget, stop rule. | Stop if requested scope touches forbidden surfaces. |
| Source & Risk Preflight | Relevant source status, risk class, truth boundary, compliance gate. | Stop if source status or legal/compliance status is missing for high-risk claims. |
| Contract Design | Data/interface/output contract, expected behavior, rollback path. | Stop if downstream interpretation is ambiguous. |
| Minimal Implementation | Smallest cohesive diff. | Stop before adding frameworks or broad rewrites. |
| Eval Harness | Targeted tests or eval fixtures for the changed risk surface. | Stop if no eval can detect the expected failure mode. |
| Dry Run & Regression | Cheap, changed-area validation only unless risk requires more. | Stop if validation budget is exceeded without approval. |
| Human Gate | Human approval for high-risk bio/compliance/legal/investor-facing decisions. | Stop if approval record is absent. |
| Merge & Evidence Log | PR state, head SHA, changed files, validation, skipped checks, residual risk. | Stop if evidence log is incomplete. |
| Learn Back | Update playbook, failure taxonomy, or regression rule. | Stop if repeated failure has no durable rule. |

## Codex Reasoning Level Rule

Always specify Codex reasoning level in Korean.

| Level | Use when | Examples |
| --- | --- | --- |
| `매우높음` | Core pipeline, retrieval, eval, compliance, security, schema, high-blast-radius, release gate. | Runtime verification gates, schema migration, source registry enforcement, retrieval ranking changes. |
| `높음` | Behavior change or multi-file bounded implementation. | Integration helper, answer metadata behavior, bounded agent-runner change. |
| `중간` | Docs, readiness gate, metadata-only narrow integration, focused review. | V1.6D docs-only consumer contract, roadmap note, source-sync document. |
| `낮음` | Trivial typo, formatting, narrow non-semantic edits. | Markdown typo, heading spacing, comment-only correction. |

V1.6D recommended level: `중간`.

## Test / CI Budget Rule

Use risk-based validation. Avoid duplicate validation that burns GitHub Actions minutes, local runtime, or reviewer time without improving confidence.

| Situation | Allowed validation | Forbidden unless explicitly approved |
| --- | --- | --- |
| Implementation stage | Changed-area targeted tests only. | Full pytest by default. |
| Patch stage | Patched-area tests only. | Broad regression runs unrelated to patch. |
| Readiness review | If PR head and scope are unchanged, do not rerun local tests. | Duplicate local tests. |
| Merge gate | Check PR state, head SHA, changed files, and GitHub Actions. | New local test run unless state changed. |
| Core pipeline/schema/retrieval/eval/compliance/CI/dependency change | Full pytest and relevant evals may be required. | Skipping high-risk gates without rationale. |
| Retrieval/evidence/ranking/chunking/embedding/eval-semantics change | Retrieval eval required. | Treating unit tests as retrieval-quality proof. |
| CI running | Check once or twice briefly, then report pending. | Polling loops that waste time. |
| Docs-only change | `git diff --check`; markdown/doc sanity only if an obvious cheap repo script exists. | Local pytest, full pytest, compileall, retrieval eval, broad security scan, manual CI workflow. |

For skipped checks, always report the rationale.

## Architecture Ladder

Choose the smallest sufficient structure first:

```text
deterministic helper -> single LLM/RAG/tool call -> fixed workflow -> stateful workflow -> agent -> multi-agent/graph
```

Escalation requires a written complexity justification:

- Why simpler patterns fail.
- Expected quality gain.
- Added latency, cost, and security risk.
- Rollback path.
- Eval evidence required.

Frameworks such as LangGraph, OpenAI Agents SDK, CrewAI, AutoGen, Semantic Kernel, LlamaIndex agents, ADK, MCP, and autonomous execution are not defaults. They require evidence that a simpler deterministic helper, single LLM/RAG/tool call, or fixed workflow is insufficient.

## Source-to-DB Boundary

Do not confuse planning artifacts with implemented infrastructure.

| Artifact | Safe claim | Forbidden claim |
| --- | --- | --- |
| Source map | Source candidate or registry planning exists. | Production corpus is fully ingested. |
| Docs | Operating doctrine or consumer contract exists. | Do not claim runtime behavior is changed. |
| PR | A reviewable change exists. | Do not claim production deployment or legal approval is complete. |
| Eval design | Proposed evaluation method exists. | Eval suite is passing in production. |
| Roadmap | Future direction exists. | Capability has been implemented. |
| Vector DB/KG sketch | Architecture is planned. | Vector DB or KG is complete. |

Boundary rule: Production DB, vector DB, KG, eval suite, compliance guardrail, legal review, wet-lab validation, or autonomous lab execution can be claimed only after implementation, logs, tests, and approval records exist.

## Biology / Compliance Hard Gates

These gates apply to biodiversity, genetic resources, CITES, Nagoya, LMO, biosafety, biosecurity, IP, licensing, privacy, export control, and commercial biological claims.

Hard rules:

- No autonomous wet-lab execution.
- No compliance, legal, or wet-lab approval claim without a human approval record.
- No commercial biological claim without provenance and legal status.
- No high-risk wet-lab protocol automation.
- No pathogen enhancement guidance.
- No regulatory evasion guidance.
- No unauthorized genetic-resource use.
- No investor-facing proof claim from metadata, docs, source maps, or PRs alone.

Safe output mode for high-risk requests:

- Provide high-level risk framing.
- Require source registry status.
- Require legal/compliance review.
- Require human approval gate.
- Preserve uncertainty and residual risk.

## Developer Output Contract

Every meaningful development report or PR body should include:

- Executive Bottom Line.
- Reasoning Level / Status.
- Scope.
- Changed files.
- Validation commands and results.
- Skipped checks and rationale.
- Truth boundary.
- Risks / Devil's Advocate.
- Rollback path.
- Residual risks.
- Next action.

For repository work, also include:

- Base branch and head branch.
- Head SHA.
- PR number or draft status.
- GitHub Actions status if checked.
- Owner/date when a decision record is needed.

## Stop Rules

Stop before expanding into any of the following unless explicitly approved:

- `src/**` runtime code.
- `tests/**` test behavior.
- `schemas.py` or schema contracts.
- `runtime_verifier.py`.
- `answer_verification_integration.py`.
- `agent_runner.py`.
- Retrieval, generation, reranking, compliance routing, config, CI, vector DB, KG, dependencies.
- README.md or AGENTS.md.
- Any automatic blocking or approval behavior.
- Any production verification, compliance approval, biosafety approval, legal approval, wet-lab validation, or investor-facing proof claim.

## Claim Upgrade Evidence

A claim can be upgraded only when the required evidence exists.

| Claim | Required evidence before upgrade |
| --- | --- |
| Runtime metadata exists | Merged code, tests, CI evidence, and documented field contract. |
| Production verification exists | Runtime gate, golden-set evidence, regression report, deployment logs, and owner approval. |
| Compliance approval exists | Human approval record, jurisdiction-specific review, source provenance, and decision log. |
| Wet-lab validation exists | Approved protocol, experiment record, data, analysis, QA review, and biosafety documentation. |
| Vector DB/KG exists | Ingestion logs, license/confidentiality pass, chunking/embedding/KG build logs, retrieval eval, and deployment evidence. |
| Foundation-model capability exists | Proprietary dataset versioning, training/eval records, model card, benchmarks, safety review, and deployment records. |

## V1.6D Decision Implication

V1.6D should remain docs-only because the next risk is downstream overreading of `verified_metadata_present`, not missing runtime code.

The next recommended phase is V1.7 preflight for adversarial/security eval or biology/compliance golden-set hardening. Do not start V1.7 implementation from this document alone.
