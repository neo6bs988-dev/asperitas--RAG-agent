# V1.10A Answer-Sample Generation / Runtime Reporting Preflight

Status: docs-only preflight. This document defines a future answer-sample collection and deterministic offline evaluator reporting plan. It does not implement sample generation, runtime capture, runtime reporting, runtime blocking, approval routing, LLM-as-judge, retrieval/generation changes, evaluator logic changes, evaluator fixture changes, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, vector DB/KG changes, human-review replacement, or production readiness.

## 1. Executive Bottom Line

V1.10A bridges the V1.7 through V1.9 evaluator and control-plane work toward generated-answer sample reporting, but only as a docs-only preflight.

V1.10A defines a future plan for answer-sample collection or generation, sample metadata, deterministic offline evaluator reporting, human-review preservation, claim-upgrade evidence, and stop rules before any runtime or approval behavior.

This PR does not implement the plan.

## 2. Goal and Non-Goal

Goal:

- define a future sample collection or generation plan;
- define a future deterministic evaluator reporting plan;
- preserve the diagnostic-only boundary of the existing offline evaluator;
- preserve mandatory human review for high-risk outputs.

Non-goals:

- no sample generation implementation;
- no runtime capture;
- no runtime reporting implementation;
- no runtime blocking;
- no approval routing;
- no LLM-as-judge;
- no retrieval or generation changes;
- no evaluator logic, fixture, or test changes;
- no vector DB or KG changes;
- no compliance, biosafety, legal, or IP approval;
- no wet-lab validation;
- no production readiness;
- no human-review replacement.

## 3. Current Baseline

V1.7 established the biology/compliance golden-set and validator foundation for static diagnostic coverage of biology, compliance, source-grounding, and human-review boundaries.

V1.8 introduced the offline answer-scoring evaluator preflight, deterministic evaluator MVP, CI and Quality Gates wiring, and final closure documentation. The evaluator is deterministic, offline, and diagnostic.

V1.9 added evaluator coverage expansion preflight, deterministic offline evaluator coverage expansion, targeted tests, and final closure. V1.9 expanded synthetic generated-answer evaluator coverage while preserving the existing CLI and JSON output contracts.

V1.7 through V1.9 improved evaluation and control-plane capability. They did not prove runtime answer-quality improvement.

The existing evaluator remains deterministic, offline, and diagnostic. Its output is not compliance, biosafety, legal, IP, wet-lab, runtime, or production approval.

## 4. Proposed Answer-Sample Classes

1. `synthetic_fixture`

Controlled examples written for evaluator coverage.

Risk: synthetic fixtures can overfit the evaluator to known wording and miss real generated-answer phrasing.

2. `staged_generated_answer`

Answers generated from a controlled local or staging prompt set.

Risk: staged answers may not reflect production behavior, traffic mix, retrieval context, user phrasing, or operational constraints.

3. `manual_review_capture`

Human-selected examples from review sessions.

Risk: manually selected samples can create sampling bias toward obvious, memorable, or already-known failure modes.

4. `future_runtime_capture`

Future runtime-derived samples only after explicit implementation scope, privacy review, consent and retention review where applicable, security review, and human approval.

Risk: runtime capture can introduce privacy, consent, retention, confidential-data, sensitive-biology, and access-control risks.

V1.10A does not implement any capture mechanism.

## 5. Sample Metadata Contract

A future sample manifest may use a metadata contract shaped like this. V1.10A does not create JSON, JSONL, schema, fixture, manifest, or runtime files.

Proposed fields:

- `sample_id`
- `sample_class`
- `prompt_id`
- `answer_text`
- `source_context_ids`
- `risk_domain`
- `expected_outcome`
- `expected_failure_labels`
- `requires_human_review`
- `contains_sensitive_info`
- `public_or_internal`
- `created_at`
- `review_owner`
- `notes`

Allowed proposed `risk_domain` values:

- `biology`
- `biodiversity`
- `nagoya_cites_lmo_gmo`
- `biosafety_biosecurity`
- `ip_licensing`
- `investor_public_claim`
- `general_rag`
- `unknown`

Future sample metadata should preserve source context IDs where available and should not strip provenance, risk, review, or sensitivity fields to simplify reporting.

## 6. Future Evaluator Reporting Contract

A future evaluator report may consume existing deterministic offline evaluator output and present a reviewer-readable summary. V1.10A does not implement reporting code, add CLI flags, change evaluator output, or change fixtures.

Future reports should include:

- total samples;
- pass, fail, and review counts;
- failure-label distribution;
- risk-domain distribution;
- high-risk samples requiring human review;
- unsupported-claim examples;
- overclaim examples;
- safe wording examples;
- residual risks;
- skipped checks;
- evaluator script path;
- evaluator version or commit reference;
- command used;
- timestamp;
- reviewer sign-off placeholder.

Allowed reference command:

```bash
python scripts/evaluate_v1_8b_offline_answer_scoring.py --json
```

Do not add new CLI flags in V1.10A.

## 7. Human Review Gate

Evaluator output is diagnostic only.

Evaluator output cannot approve:

- compliance;
- biosafety;
- legal conclusions;
- IP conclusions;
- wet-lab claims;
- investor-facing claims;
- public website or deck claims;
- runtime release.

Human review remains mandatory for high-risk biology, compliance, IP, legal, biosafety, biosecurity, investor-facing, public-facing, or external-use outputs.

## 8. Compliance / Biosafety / IP / Legal Boundary

Deterministic labels are not regulatory decisions.

This plan does not provide:

- wet-lab protocols;
- autonomous lab execution;
- high-risk biological action;
- CITES, Nagoya, LMO, GMO, biosafety, biosecurity, legal, IP, or regulatory clearance;
- replacement for legal counsel, a biosafety officer, a compliance officer, IP review, or human domain review.

Future runtime-derived samples must not be collected or reported without separate privacy, consent, retention, security, and sensitive-content review where applicable.

## 9. Allowed Future V1.10B Scope

A future V1.10B may:

- add a sample manifest;
- add a report-generation script that consumes existing evaluator output;
- add targeted tests for report format;
- preserve diagnostic-only status;
- avoid runtime integration.

V1.10B should remain deterministic and should not promote evaluator output into approval, blocking, legal, compliance, biosafety, IP, wet-lab, or release authority.

## 10. Forbidden Future Scope Without Separate Approval

The following are forbidden without a separate scoped preflight and approval:

- runtime capture;
- runtime blocking;
- approval routing;
- LLM-as-judge;
- production dashboard;
- web productization;
- privacy-sensitive logs;
- source registry ingestion;
- retrieval or generation behavior changes;
- compliance, legal, biosafety, or IP approval automation.

## 11. Validation Plan

For this docs-only PR:

```bash
git diff --check
git diff --name-only
```

Docs-only review is required.

Full pytest should be skipped unless repository instructions demand it.

Rationale for skipping full pytest:

- V1.10A changes only this planning document;
- no source code changes;
- no evaluator script changes;
- no evaluator fixture changes;
- no tests changed;
- no runtime behavior changed;
- no CI workflow changed;
- no retrieval, generation, vector DB, KG, or dependency change.

## 12. Evidence Required to Upgrade Claims

To claim "answer-sample reporting implemented":

- sample manifest exists;
- report script exists;
- deterministic tests pass;
- evaluator output is reproducible;
- human review boundary is preserved.

To claim "runtime answer quality improved":

- real or staged generated-answer sample set exists;
- baseline versus changed behavior comparison exists;
- evaluation results are reproducible;
- failure modes are tracked;
- human review sign-off exists.

To claim "production readiness":

- explicitly not allowed from V1.10A or V1.10B alone.

## 13. Risk / Digital Devil's Advocate

Risks:

- sample bias can hide important failures;
- synthetic fixture overfitting can create brittle confidence;
- deterministic labels can create false confidence;
- deterministic rules can miss semantic overclaims;
- future runtime capture can introduce privacy, consent, retention, security, and sensitive-content risks;
- evaluator reports can be misread as approval;
- investor or public claims can be laundered through evaluator language;
- high-risk biology, compliance, IP, legal, biosafety, or investor-facing content can escape human review if reporting is treated as release authority.

Mitigations:

- preserve diagnostic-only wording in reports;
- preserve human-review fields in sample metadata;
- separate report generation from runtime blocking or approval;
- require separate scoped preflight before runtime capture, approval routing, or public-facing claim use.

## 14. Stop Rules

Stop if:

- implementation requires code changes;
- runtime behavior must be touched;
- evaluator fixture, schema, or test changes seem necessary;
- CI workflow changes seem necessary;
- source registry, retrieval, or generation files need edits;
- vector DB or KG files need edits;
- any approval or blocking behavior is requested;
- local repo has unexpected uncommitted changes;
- branch is not based on latest `main`;
- V1.10A cannot be completed with one docs file.

If any stop rule triggers, split the work into a separate scoped PR or return to planning.

## 15. Truth Boundary

V1.10A is docs-only preflight. It does not implement sample generation, runtime reporting, runtime capture, runtime blocking, approval routing, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, human-review replacement, or production readiness.
