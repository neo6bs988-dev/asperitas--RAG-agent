# V1.5 Final Closure Review

Date: 2026-07-04

Status: closure review only. This document does not add runtime features, change retrieval, change reranking, change answer generation, change refusal behavior, change the truth/compliance router, change schemas, change dependencies, change configuration, change CI, or claim production verifier performance.

Baseline: `main` at `15711b0fdf9f9d7df4d625ef85969cd7fca573d7`.

## Executive Closure

V1.5 is complete as a scoped verifier-infrastructure and closure-gate sequence. The merged chain now covers:

```text
schema/taxonomy
-> claim extraction
-> evidence-span matching
-> support classification
-> report aggregation
-> answer metadata
-> adversarial/security eval
-> biology/compliance golden set
-> metrics/regression gate
-> scoped runtime metadata
```

This is not a production verifier claim. V1.5 establishes deterministic contracts, diagnostics, fixtures, regression gates, and a passive runtime metadata hook that can carry already-produced verifier summaries.

## V1.5A Through V1.5I Summary

| Slice | Merged evidence | Closure finding |
|---|---|---|
| V1.5A harness-first policy | `d3092e5` | Added risk-based validation discipline and docs-only Quality Gate path expectations. |
| V1.5B verifier design | `7f4715f` | Defined claim-to-citation verifier architecture, support taxonomy, biology/compliance tags, metrics, and non-goals. |
| V1.5C schemas and taxonomy | `a69ac23` | Added claim, evidence-span, report, summary, support-status, failure-mode, and compliance-tag contracts. |
| V1.5C claim extraction | `a27c4bb` | Added deterministic atomic-claim extraction fixtures and tests. |
| V1.5C evidence-span matching | `454559f` | Added citation-key to evidence-span resolution with mismatch diagnostics. |
| V1.5C support classification | `3d8b014` | Added conservative deterministic support statuses for supported, unsupported, contradicted, ambiguous, citation, and context cases. |
| V1.5C report aggregation | `ccaf7a3` | Aggregated claim reports into answer-level status counts, warnings, blockers, diagnostics, and metadata. |
| V1.5D answer metadata integration | `e61206c` | Added passive `metadata.answer_verification` exposure with JSON-safe deterministic payloads and no answer mutation. |
| V1.5E adversarial/security eval pack | `d557fcf` | Added tests for prompt-injection-as-data, malformed citations, blockers, JSON safety, and passive metadata exposure. |
| V1.5F biology/compliance golden set | `cfc0e82` | Added synthetic biology/compliance fixtures with provenance, compliance tags, and deterministic summary expectations. |
| V1.5G metrics regression gate | `384c94e` | Added regression metrics for status counts, diagnostics, compliance/license tags, provenance coverage, JSON safety, deterministic ordering, and runtime-bounded imports. |
| V1.5H runtime integration readiness | `b1ed5ac` | Documented the metadata-only runtime boundary, rollback policy, human-review signals, tracing limits, and required gates. |
| V1.5I scoped runtime metadata | `15711b0` | Added optional caller-supplied verifier summary metadata to `ask_agent()` without running verifier stages or changing answer behavior. |

## Changed Surface By Category

| Category | Surface | Closure assessment |
|---|---|---|
| Docs | README/AGENTS policy, V1.5B design, V1.5H readiness, this closure review | Defines governance, architecture, readiness, truth-boundary, and next-step constraints. |
| Tests | Verifier schema, extractor, matcher, classifier, aggregator, integration, adversarial/security, biology/compliance golden set, metrics gate, runtime contract tests | Provides targeted regression coverage for the V1.5 verifier infrastructure and runtime metadata boundary. |
| Helper modules | `claim_verifier_schema.py`, `claim_extractor.py`, `evidence_span_matcher.py`, `support_status_classifier.py`, `claim_verification_report_aggregator.py`, `answer_verification_integration.py`, `claim_verification_metrics.py` | Implements deterministic helper contracts and metrics scaffolding without changing retrieval or generation defaults. |
| Runtime boundary | `agent_runner.py` | Adds optional, caller-supplied `AnswerVerificationSummary` exposure under `metadata.answer_verification`; it does not generate verifier summaries or run verifier stages. |

## What V1.5 Improves

- Verifier infrastructure: V1.5 adds typed contracts, deterministic helper layers, and narrow adapter boundaries for future claim-to-citation verification work.
- Citation/support diagnostics: V1.5 can represent unsupported, contradicted, citation-missing, citation-mismatch, ambiguous, not-verifiable, and compliance-blocked cases as structured metadata.
- Compliance/provenance metadata: V1.5 preserves source IDs, citation keys, evidence span IDs, source paths, compliance tags, license tags, diagnostics, and fixture provenance in verifier outputs.
- Regression gates: V1.5 adds targeted tests for JSON safety, deterministic ordering, non-mutation, runtime-bounded imports, adversarial citation handling, biology/compliance tags, and passive runtime metadata exposure.

These are infrastructure and regression-readiness improvements. They do not by themselves prove live answer accuracy or production RAG quality.

## What V1.5 Does Not Prove

V1.5 does not prove or claim:

- production verifier completion;
- live citation accuracy;
- answer faithfulness improvement;
- RAG performance improvement;
- retrieval quality improvement;
- production database completion;
- production knowledge graph completion;
- production vector database completion;
- wet-lab validation;
- legal approval;
- regulatory approval;
- autonomous lab capability;
- proprietary or completed biological foundation model capability.

Any future claim in these categories requires separate merged implementation, metrics, eval artifacts, and review evidence.

## Validation Evidence And Skipped Checks

Historical validation evidence is in the merged PRs and CI/Quality Gates for V1.5A through V1.5I. The required closure PR validation scope is intentionally smaller because this artifact is documentation-only.

Required checks for this closure PR:

- `git status --short --branch`
- `git diff --stat`
- `git diff --check`
- `python -m pytest tests/test_agent_runner.py -q`
- `python -m pytest tests/test_claim_verification_metrics_regression_gate.py -q`
- `python -m pytest tests/test_answer_verification_integration.py -q`
- dependency/config diff sanity
- runtime surface sanity
- truth-boundary scan

Skipped by design unless later evidence requires them:

- full `pytest`;
- retrieval eval;
- full Quality Gates local simulation;
- broad simulations;
- GitHub Actions rerun.

Rationale: this PR is docs-only and does not change source code, tests, fixtures, retrieval, reranking, answer generation, compliance routing, dependencies, config, CI, schemas, or runtime behavior.

## Runtime Surface Review

The V1.5I runtime boundary is `ask_agent()` in `src/asperitas_agent/agent_runner.py`, after retrieval, evidence packaging, guardrail evaluation, answer generation, and citation-integrity validation.

The runtime metadata path:

- accepts `answer_verification_summary: AnswerVerificationSummary | None`;
- attaches metadata only when a caller supplies an existing summary;
- delegates metadata construction to `expose_answer_verification_metadata(...)`;
- places the passive verifier payload at `metadata.answer_verification`;
- preserves answer text, answer status, citations, evidence, guardrail output, and existing metadata;
- does not call claim extraction, evidence-span matching, support classification, report aggregation, retrieval, reranking, answer generation, or the compliance router as part of metadata attachment.

Rollback is narrow: remove or stop supplying the optional summary and the runtime response returns to the previous payload shape except for the absence of `metadata.answer_verification`.

## Remaining Gaps For V1.6

V1.6 should not be treated as production verification by default. Remaining gaps include:

- runtime orchestration for producing verifier summaries from generated answers and evidence packs;
- measured verifier precision/recall against broader claim-level fixtures;
- explicit latency and cost overhead measurement before default runtime use;
- failure and timeout policy for verifier execution;
- human-review policy for blockers and compliance-sensitive diagnostics;
- richer biology entity normalization and alias handling;
- broader contradiction, numeric/unit mismatch, and citation-mismatch coverage;
- clear UI/API consumer contract for passive verifier metadata;
- release-gate policy for when verifier diagnostics should block external or public-facing use.

## V1.6 Readiness Criteria

Proceed to V1.6 only after this closure PR is green and the V1.6 scope stays narrow. V1.6 should require:

- explicit runtime verifier entrypoint design before code changes;
- no answer rewriting unless covered by a separate scoped policy and tests;
- tests proving generated answer text/status/citations/refusal behavior remain unchanged when metadata-only mode is used;
- adversarial/security, biology/compliance, and metrics gates for every runtime integration step;
- no dependency, service, framework, cloud, MCP, config, or CI expansion without a separate approval and security/license review;
- retrieval eval only if retrieval, evidence selection, metadata filtering, embeddings, vector DB behavior, reranking, answer generation, or eval semantics change;
- truth-boundary wording that continues to label verifier outputs as diagnostics until production evidence exists.

## Risks And Rollback Notes

| Risk | Current control | Rollback or next control |
|---|---|---|
| Metadata is mistaken for production verification | Truth-boundary text and passive metadata wording | Keep UI/API labels diagnostic-only until validated production policy exists. |
| Runtime coupling grows too quickly in V1.6 | V1.5I accepts caller-supplied summaries only | Require a separate V1.6 design and targeted tests before runtime summary generation. |
| Compliance tags are overread as legal or biosafety approval | Tests and docs state tags are metadata only | Require human-review policy before external/public/regulatory use. |
| Fixture coverage is too narrow | Golden set and adversarial pack are synthetic and targeted | Expand V1.6 fixtures before claiming broad verifier accuracy. |
| Performance impact is unknown | No runtime verifier execution is added by V1.5I | Measure latency/cost before enabling runtime verifier execution by default. |

## Recommendation

Proceed to V1.6 only after this closure PR is reviewed, green, and merged. The first V1.6 PR should be a narrow runtime verifier entrypoint or orchestration design that preserves the metadata-only fallback and does not change answer generation, retrieval, reranking, compliance routing, refusal behavior, dependencies, config, CI, or schemas without explicit separate scope.
