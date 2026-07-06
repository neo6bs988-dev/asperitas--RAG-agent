# V1.7B Golden-Set Fixtures / Schema Preflight

Date: 2026-07-06

Status: docs-only implementation preflight. This document does not add golden-set fixtures, does not add executable eval schema, does not change runtime behavior, does not block answers, does not approve compliance, does not approve biosafety/legal/IP claims, does not validate wet-lab claims, does not improve retrieval/generation, does not complete vector DB/KG, and does not prove production readiness.

Baseline: V1.7A is merged by PR #146 with squash merge commit `87866740e99e93b66784320561effc32a997bf82`.

## 1. Executive Bottom Line

V1.7B should be an implementation preflight only: define the contract for future biology/compliance golden-set fixtures and eval labels/schema before adding any evaluation assets.

The smallest sufficient pattern is a deterministic fixture/schema contract before implementation. The next implementation PR can then add static fixture and label/schema assets without changing runtime behavior, answer blocking, compliance approval, biosafety approval, legal approval, wet-lab validation, retrieval/generation behavior, vector DB/KG behavior, CI, dependencies, or autonomous execution.

V1.7B preflight is planning only. It does not add golden-set fixtures, does not add executable eval schema, does not change runtime behavior, does not block answers, does not approve compliance, does not approve biosafety/legal/IP claims, does not validate wet-lab claims, does not improve retrieval/generation, does not complete vector DB/KG, and does not prove production readiness.

## 2. Source Status / Assumptions

This preflight is grounded in the following read-only references:

- `docs/V1_7A_BIOLOGY_COMPLIANCE_GOLDEN_SET_PREFLIGHT.md`
- `docs/V1_6_FINAL_CLOSURE_REVIEW.md`
- `docs/V1_6D_RUNTIME_READINESS_CONSUMER_CONTRACT.md`
- `docs/DEVELOPMENT_PROCESS_V11_1_SOURCE_SYNC.md`
- `docs/QUALITY_GATES.md`
- `docs/AOS_SOURCE_POLICY.md`
- `docs/MVP_010_GOLDEN_QUERY_SUITE.md`
- `docs/MVP_011_FAILURE_TAXONOMY.md`
- `docs/MVP019C_SECURITY_GUARD.md`
- read-only inventory of existing `eval/`, `eval_results/`, and `09_LOGS/decision_logs/` paths

Assumptions carried forward:

- V1.6 is audit-closed as a metadata interpretation and consumer-contract milestone.
- V1.7A is merged as a docs-only biology/compliance golden-set preflight.
- Runtime readiness metadata remains diagnostic only.
- Planning artifacts, source maps, docs, PRs, fixture designs, and schema designs are not proof of source ingestion, legal review, compliance approval, biosafety approval, wet-lab validation, vector DB completion, KG completion, production deployment, or foundation-model capability.
- Human approval remains required for high-risk biology/compliance/IP outputs.

## 3. V1.7A Carry-Forward Boundary

V1.7A selected biology/compliance golden-set hardening as a preflight direction. It did not create fixtures, a runner, a schema, a regression gate, or human-review routing behavior.

The V1.6/V1.7A hard boundary remains:

```text
production_verification_claim=false
metadata_interpretation_only=true
```

Any future V1.7B fixture or label result must be treated as evaluation evidence only. It must not be presented as runtime blocking, production verification, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, investor-facing proof, vector DB/KG completion, autonomous lab execution, or foundation-model capability.

## 4. V1.7B Objective

V1.7B should define a future fixture and label/schema contract that allows a later implementation PR to add static evaluation assets safely.

The objective is to specify:

- where future static assets should live;
- what fields each future fixture should contain;
- which labels are required;
- which case categories must be represented;
- how source grounding, citation fidelity, evidence sufficiency, provenance, compliance risk, biological claim risk, investor overclaim risk, and human review should be represented;
- which consumer actions are allowed or forbidden for future eval outputs.

This document intentionally stops before implementation.

## 5. Proposed Future Files

The following paths are proposed for a future implementation PR. They are not created by this preflight.

| Future asset | Proposed path | Purpose |
| --- | --- | --- |
| Future golden-set fixture path | `eval/v1_7b_biology_compliance_golden_set.jsonl` | Static synthetic or approved cases for biology/compliance claim-risk evaluation. |
| Future label/schema path | `eval/v1_7b_biology_compliance_labels.schema.json` | Static JSON Schema-style label contract for fixture records and expected outcomes. |
| Future regression report path | `eval_results/v1_7b_biology_compliance_golden_set/README.md` and `eval_results/v1_7b_biology_compliance_golden_set/report.json` | Human-readable and machine-readable results after a future evaluator exists. |
| Future decision log path | `09_LOGS/decision_logs/v1_7b_biology_compliance_golden_set.md` | Evidence log for fixture scope, label choices, validation, and residual risk. |

Future implementation should add only the smallest subset needed for review. If an executable runner or tests are needed, that should be scoped as a later PR unless explicitly approved.

## 6. Golden-Set Fixture Contract

Each future fixture record should be deterministic, reviewable, and synthetic or approved for repository use.

Required fixture fields should include:

- `id`: stable unique identifier.
- `case_category`: one required case category.
- `claim_type`: biological, biodiversity, compliance, IP/licensing, investor-facing, or mixed.
- `query`: user-facing prompt or answer-review prompt.
- `source_priority_expected`: expected source priority class such as P3 for biological mechanism or P4 for legal/regulatory claims.
- `source_context`: compact approved source summary or source reference, not confidential raw text unless approved.
- `expected_answer_status`: expected high-level answer posture.
- `expected_labels`: required future labels from the label/schema contract.
- `required_evidence_conditions`: expected evidence-span, citation, provenance, and source-priority constraints.
- `forbidden_answer_patterns`: concept-level overclaims or unsafe claims that must not appear.
- `required_human_review_reason`: reviewer rationale when escalation is expected.
- `notes`: concise rationale and review caveats.

Fixture records should not contain:

- confidential, restricted, personal, paywalled, or license-ambiguous source text without approval;
- operational wet-lab instructions;
- pathogen enhancement guidance;
- regulatory evasion guidance;
- source-instruction text that should be executed;
- exact answer prose requirements unless format is the behavior under review.

## 7. Eval Label / Schema Contract

The future label/schema file should define stable, deterministic labels and allowed values. It should validate fixture expectations, not runtime outputs, unless a later evaluator PR explicitly defines that behavior.

Minimum label/schema principles:

- Use explicit enumerations instead of free-form labels.
- Keep labels diagnostic, not approving.
- Represent missing evidence as a first-class outcome.
- Separate answer posture from compliance risk.
- Separate biological claim risk from source/citation fidelity.
- Preserve human-review routing as a recommendation, not approval.
- Preserve allowed and forbidden consumer actions so downstream users cannot overread eval outputs.

The schema should reject unknown high-risk labels unless the future implementation PR also updates the documentation and decision log.

## 8. Required Case Categories

Future V1.7B implementation should include at least one reviewed case for each category before claiming fixture coverage:

| Required category | Required risk signal |
| --- | --- |
| source-grounding failure | Claim uses the wrong source priority, lacks source support, or upgrades an inference into a fact. |
| citation mismatch | Citation points to a source that does not support the exact claim. |
| unsupported biological activity claim | Biological activity, mechanism, efficacy, toxicity, yield, or ecological claim exceeds evidence. |
| species/provenance missing | Species, strain, sample, geographic origin, access path, or provider status is absent or ambiguous. |
| Nagoya/CITES/LMO/biosafety/biosecurity/IP/licensing flag | Legal, regulatory, access, safety, security, ownership, or license uncertainty is present. |
| investor-facing overclaim | Answer implies validation, approval, traction, exclusivity, market readiness, or scientific proof without evidence. |
| human-review-required case | High-risk output should route to human review without being blocked or approved by default. |

## 9. Required Labels

Future labels should include these fields:

### `expected_answer_status`

Allowed values:

- `answered_with_limits`
- `caution`
- `abstained`
- `review_required`

Meaning: the expected answer posture for the fixture. This is not a product-facing approval.

### `evidence_sufficiency`

Allowed values:

- `sufficient`
- `insufficient`
- `missing`
- `conflicting`

Meaning: whether cited or supplied evidence is enough to support the claim and its limits.

### `citation_fidelity`

Allowed values:

- `faithful`
- `mismatch`
- `missing`
- `overbroad`

Meaning: whether the citation points to evidence that supports the exact claim.

### `compliance_risk_class`

Allowed values:

- `none_identified`
- `needs_review`
- `restricted_or_unknown`
- `not_approved`

Meaning: compliance risk posture. This is not legal, compliance, biosafety, or IP approval.

### `biological_claim_risk`

Allowed values:

- `low`
- `unsupported_activity_claim`
- `provenance_gap`
- `biosafety_or_biosecurity_sensitive`
- `not_wet_lab_validated`

Meaning: biological claim risk posture for fixture evaluation.

### `human_review_required`

Allowed values:

- `true`
- `false`

Meaning: whether a human reviewer must evaluate the output before high-risk use.

### `allowed_consumer_action`

Allowed values:

- `display_diagnostic`
- `route_to_human_review`
- `record_eval_result`
- `do_not_upgrade_claim`

Meaning: safe downstream use of fixture/eval output.

### `forbidden_consumer_action`

Allowed values:

- `runtime_blocking`
- `compliance_approval`
- `biosafety_approval`
- `legal_approval`
- `ip_approval`
- `wet_lab_validation_claim`
- `retrieval_generation_improvement_claim`
- `vector_db_kg_completion_claim`
- `production_readiness_claim`

Meaning: actions or claims that future eval output must not authorize.

## 10. Acceptance Criteria for Future V1.7B Implementation

Future implementation may proceed only if it remains static, reviewable, and non-runtime.

Acceptance criteria:

- Adds only approved static fixture/schema assets unless separately approved.
- Uses synthetic or approved source material.
- Represents all required case categories.
- Includes all required labels.
- Keeps labels diagnostic and non-approving.
- Includes anti-overfitting rules in the fixture/schema documentation.
- Does not modify runtime code, tests, schemas.py, CI, retrieval, generation, reranking, compliance routing, dependencies, vector DB, KG, README, AGENTS, or `.github/**`.
- Does not create automatic blocking, approval, or human-review routing behavior.
- Reports skipped checks and residual risks.
- Preserves V1.6/V1.7A truth boundaries.

## 11. Anti-Overfitting Rules

Future implementation must preserve these rules:

- Runtime code must not read the V1.7B fixture file.
- Runtime code must not special-case fixture ids, exact query text, exact forbidden substrings, `pytest`, CI, or test filenames.
- Fixture expectations should use concept-level substrings and structured labels, not full answer prose.
- Labels should detect evidence integrity and claim-risk behavior, not reward memorized wording.
- Future evaluator code, if later approved, must not mutate source registries, chunks, eval fixtures, vector DB, KG, or runtime outputs.
- Any future regression report must label metrics as `Fresh Run`, `Historical`, or `Not Run / N/A`.

## 12. Validation Budget

Allowed validation for this docs-only preflight:

- `git diff --check`
- docs-only quality gate if cheap and already available

Do not run for this PR:

- local pytest;
- full pytest;
- compileall;
- retrieval eval;
- broad security scan;
- manual CI workflow.

Rationale: this PR changes only a planning document. It does not add fixtures, schemas, tests, executable code, runtime behavior, retrieval changes, generation changes, reranking changes, compliance routing, config, CI, vector DB, KG, dependencies, README, AGENTS, or `.github/**`.

## 13. Non-Goals

V1.7B preflight does not:

- add golden-set fixtures;
- add executable eval schema;
- add tests;
- add a runner;
- add a regression gate;
- change runtime behavior;
- block answers;
- approve compliance;
- approve biosafety, legal, or IP claims;
- validate wet-lab claims;
- improve retrieval or generation;
- complete vector DB or KG;
- prove production readiness;
- start V1.7C implementation;
- introduce LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, MCP, autonomous agents, or multi-agent orchestration.

## 14. Risks / Digital Devil's Advocate

| Risk | Why it matters | Control |
| --- | --- | --- |
| Preflight is mistaken for implemented fixtures. | Reviewers may assume evaluation assets exist. | State that this PR creates no fixtures or executable schema. |
| Labels are mistaken for approval. | Compliance, biosafety, legal, and IP decisions require human review. | Use diagnostic labels and forbidden consumer actions. |
| Future fixtures overfit behavior. | A small deterministic set can be memorized or gamed. | Preserve anti-overfitting rules and concept-level expectations. |
| Source material introduces confidentiality or license risk. | Fixture text may expose restricted data. | Require synthetic or approved source material only. |
| Investor overclaim cases are too weak. | Future outputs may imply validation or market readiness. | Require explicit investor-facing overclaim category and forbidden actions. |
| Scope expands into implementation. | Runtime/test/schema/CI/retrieval changes would exceed preflight. | Stop if implementation surfaces are required. |

## 15. Stop Rules

Stop future V1.7B or follow-on work before editing if:

- PR #146 merge commit cannot be confirmed.
- The work would require runtime, test, schema, CI, retrieval, compliance routing, dependency, vector DB, or KG edits.
- The work would implement fixtures, schema, tests, runners, or gates instead of preflighting them.
- The work weakens V1.6 or V1.7A truth boundaries.
- The work claims legal approval, compliance approval, biosafety approval, wet-lab validation, production readiness, vector DB/KG completion, autonomous lab execution, or foundation-model completion.
- The work requires LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, MCP, autonomous agents, or multi-agent orchestration.
- Human approval would be implied but no approval record exists.

## 16. Next PR Options

After V1.7B preflight review, choose the smallest safe V1.7C unit:

- static golden-set fixture file;
- static label/schema file;
- no runtime blocking;
- no approval behavior.

Do not implement runtime blocking, approval behavior, human-review routing behavior, CI gates, or executable evaluators until separately scoped and approved.
