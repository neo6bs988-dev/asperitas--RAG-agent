# Pull Request Review

## Objective

- [ ] Objective is stated clearly.
- [ ] Change matches requested scope.
- [ ] Unrelated files are excluded.
- [ ] Truth boundary is explicit.

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

## Scope Safety

- [ ] No direct `main` edit unless explicitly approved.
- [ ] Branch scope is narrow and reviewable.
- [ ] No unrelated refactor included.
- [ ] No generated artifact churn included unless intentional and explained.
- [ ] No secrets, credentials, endpoints, model binaries, generated indexes, or cloud resources added unexpectedly.

## Truth Boundary

This PR does not claim completion unless verified by evidence:

- [ ] production vector DB
- [ ] production KG
- [ ] full source ingestion
- [ ] legal/regulatory approval
- [ ] wet-lab validation
- [ ] deployed autonomous agent
- [ ] proprietary biological foundation model
- [ ] customer/investor commitment
- [ ] product-market fit

Notes:

## Required Checks

### Docs/Governance

- [ ] Edited docs were re-read from branch.
- [ ] Markdown/headings/links/paths are sane.
- [ ] No false implementation status introduced.
- [ ] No confidential or personal data exposed.
- [ ] Not applicable.

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

Deferred work:

Human approval needed:

## Merge Decision

- [ ] Ready
- [ ] Conditional
- [ ] Blocked

Reason:
