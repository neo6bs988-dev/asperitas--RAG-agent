# Pull Request Review

## Objective

- [ ] Objective is stated clearly.
- [ ] Change matches requested scope.
- [ ] Unrelated files are excluded.
- [ ] Truth boundary is explicit.

## Scope Lock

- Codex reasoning level: [ ] 낮음 [ ] 중간 [ ] 높음 [ ] 매우높음
- Risk class: [ ] Low [ ] Medium [ ] High [ ] Block
- Changed surface: [ ] Docs [ ] Templates [ ] CI/config [ ] Source code [ ] Retrieval/chunking/metadata [ ] Embeddings/vector DB [ ] Reranking [ ] Answer generation/citation [ ] Compliance/security [ ] Evals/fixtures [ ] Trace/logging [ ] Schema
- Minimal sufficient architecture level: [ ] Deterministic helper [ ] Single LLM/RAG/tool call [ ] Fixed workflow [ ] Stateful workflow [ ] Agent [ ] Multi-agent/graph
- Verification scope:
- Skipped-test/eval rationale:
- Residual risk:
- Metric provenance: [ ] Fresh Run [ ] Historical [ ] Not Run / N/A

## Change Type

- [ ] Docs/governance only
- [ ] Source code
- [ ] Tests
- [ ] Source registry / metadata / chunks
- [ ] Retrieval / ranking / scoring
- [ ] Answer generation / citation / truth router
- [ ] Compliance / biosafety / security
- [ ] Token / cost / latency metrics
- [ ] CI / workflow / release
- [ ] Codex config / agent instructions

## Scope Safety

- [ ] No direct `main` edit unless explicitly approved.
- [ ] Branch scope is narrow and reviewable.
- [ ] No unrelated refactor included.
- [ ] No generated artifact churn included unless intentional and explained.
- [ ] No secrets, credentials, endpoints, model binaries, generated indexes, or cloud resources added unexpectedly.
- [ ] No local-only paths, user-level config, runtime cache paths, or machine-specific plugin paths added.

## Truth Boundary

This PR does not claim completion unless verified by evidence:

- [ ] production RAG
- [ ] production vector DB
- [ ] production KG
- [ ] full source ingestion
- [ ] deployed eval suite
- [ ] deployed tracing
- [ ] legal/regulatory approval
- [ ] biosafety approval
- [ ] wet-lab validation
- [ ] deployed autonomous agent
- [ ] proprietary agent-stack implementation
- [ ] proprietary biological foundation model
- [ ] customer/investor commitment
- [ ] product-market fit

Notes:

## P0+ AI Lead Operating Layer Impact

- [ ] Goal / Scope / Evidence / Constraints / Output / Verification / Stop Rules considered.
- [ ] Prompt -> Workflow -> Evaluation -> Governance -> Organizational Learning impact considered.
- [ ] Reusable asset added or updated where appropriate.
- [ ] Failure taxonomy / SOP / checklist / playbook / eval case impact considered.
- [ ] Digital Devil's Advocate review completed for Scalability, Moat, Governance, Cost, Evaluation, and Failure Modes.
- [ ] Human approval gate preserved or added where needed.

## Required Checks

### Docs/Governance

- [ ] Edited docs were re-read from branch.
- [ ] Markdown/headings/links/paths are sane.
- [ ] No false implementation status introduced.
- [ ] No confidential or personal data exposed.
- [ ] Not applicable; reason:

### Source Code

- [ ] Targeted tests run:
- [ ] `python -m pytest`
- [ ] Lint/type/schema check if relevant:
- [ ] Not applicable; reason:

### Artifact / Registry / Chunking

- [ ] `python scripts/verify_artifacts.py`
- [ ] `python scripts/audit_chunk_sections.py --json`
- [ ] Not applicable; reason:

### Retrieval / Ranking / Scoring

- [ ] `python scripts/run_retrieval_eval.py --retriever baseline --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever vector --limit 5`
- [ ] `python scripts/run_retrieval_eval.py --retriever hybrid --limit 5`
- [ ] `--enforce-thresholds` run where required.
- [ ] Not applicable; reason:

### Answer / Citation / Truth Router

- [ ] Answer contract check run where available.
- [ ] Truth/compliance router check run where available.
- [ ] Source IDs, priorities, evidence labels, paths, and confidence preserved.
- [ ] Unsupported claims are removed or labeled.
- [ ] Not applicable; reason:

### Compliance / Security

- [ ] CITES/Nagoya/LMO/biosafety/biosecurity reviewed if relevant.
- [ ] Privacy/security/IP/legal/investor/public-claim risk reviewed if relevant.
- [ ] Prompt injection, source poisoning, leakage, and excessive agency considered if relevant.
- [ ] Human approval need stated.
- [ ] Not applicable; reason:

### Config / Agent Instructions

- [ ] Root `AGENTS.md` impact reviewed if touched.
- [ ] `.codex/config.toml` impact reviewed if touched.
- [ ] No user-level `~/.codex/config.toml` or local machine settings committed.
- [ ] No duplicated case-variant paths introduced.
- [ ] Not applicable; reason:

## Metrics

Report only measured metrics. Do not infer wins.

| Metric | Before | After | Delta | Evidence |
|---|---:|---:|---:|---|
| Retrieved-context tokens | | | | |
| Answer tokens | | | | |
| Runtime / p50 / p95 | | | | |
| Retrieval pass rate | | | | |
| Expected-source hit rate | | | | |
| Citation/claim support rate | | | | |
| Refusal/escalation pass rate | | | | |

## Source-Grounding Review

- [ ] Source IDs preserved.
- [ ] Source priority preserved.
- [ ] Source paths/provenance preserved.
- [ ] Evidence labels preserved.
- [ ] Missing evidence is labeled.
- [ ] P6 benchmark doctrine is not treated as Asperitas internal fact.

## Risk Summary

Known risks:

Skipped checks and rationale:

GitHub Actions disconnections/timeouts, if any:

Deferred work:

Human approval needed:

## Rollback Plan

## Merge Decision

- [ ] Ready
- [ ] Conditional
- [ ] Blocked

Reason:

## Next Action
