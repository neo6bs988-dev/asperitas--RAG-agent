# V1.10C Stable Evaluator Sample IDs Preflight

Status: docs-only preflight. This document defines the scope, contract, risks, tests, stop rules, rollback path, and truth boundary for a future implementation PR that may add stable per-row evaluator sample IDs. It does not implement V1.10C.

## 1. Executive Bottom Line

V1.10C should address one narrow V1.10B limitation: repeated `case_id` values in `eval/v1_8b_generated_answer_scoring_cases.jsonl` cannot be joined safely by `scripts/report_v1_10b_answer_sample_results.py` without a stable per-row identifier.

The future implementation should add stable row identity so the answer-sample report can cover repeated evaluator cases without inferring row indexes or relying on brittle file order.

This preflight PR is docs-only. It does not add IDs, edit fixtures, edit report code, edit tests, change CI, or change runtime behavior.

## 2. Current Baseline

Baseline after merged PR #164:

- V1.10B squash merge: `f21a1f5c968cf79154b3450a247e6b2c8e4d0e96`
- Prior V1.10B head SHA: `0c76350ca030f4e7fcb2cd5bf9dfbcc82c3ac305`
- V1.10B added:
  - `eval/v1_10b_answer_sample_manifest.jsonl`
  - `scripts/report_v1_10b_answer_sample_results.py`
  - `tests/test_v1_10b_answer_sample_report.py`

Current V1.10B behavior:

- joins manifest rows to evaluator output by `evaluator_case_id`;
- accepts only evaluator case IDs that appear exactly once;
- reports repeated evaluator IDs as unmatched evaluator cases;
- preserves `diagnostic_only: true`;
- preserves `approval_authority: false`;
- preserves `runtime_behavior_changed: false`;
- states that the report is not compliance, biosafety, legal, IP, wet-lab, runtime, or production approval.

Current repeated evaluator `case_id` groups:

- `v1_7c_compliance_flag_cluster`: 4 rows;
- `v1_7c_human_review_required`: 2 rows;
- `v1_7c_unsupported_biological_activity`: 3 rows.

## 3. Goal and Non-Goal

Goal:

- define a future stable per-row ID contract for evaluator generated-answer cases;
- define how V1.10B answer-sample manifest rows should reference those stable IDs;
- define the required tests for deterministic joins over repeated case groups;
- preserve the diagnostic-only evaluator and report boundary;
- preserve human review for high-risk biology, compliance, IP, legal, biosafety, investor-facing, public-facing, or external-use outputs.

Non-goals:

- no implementation in this PR;
- no fixture edits in this PR;
- no report script edits in this PR;
- no test edits in this PR;
- no CI workflow edits in this PR;
- no dependency changes;
- no runtime capture;
- no runtime reporting integration;
- no runtime blocking;
- no approval routing;
- no LLM-as-judge;
- no retrieval or generation changes;
- no source registry changes;
- no vector DB or KG changes;
- no compliance, biosafety, legal, IP, wet-lab, or production approval;
- no human-review replacement.

## 4. Proposed Future Contract

A future implementation PR may add a stable per-row identifier to each row in `eval/v1_8b_generated_answer_scoring_cases.jsonl`.

Recommended field:

```text
sample_case_id
```

Recommended properties:

- string;
- unique across the generated-answer fixture file;
- stable across row reordering;
- descriptive enough for review;
- independent from the broader `case_id` category;
- safe to reference from answer-sample manifests;
- not derived from mutable row number;
- not a hash of full answer text unless the hash stability and migration behavior are explicitly documented.

Recommended naming pattern:

```text
v1_8b_<case_id_slug>_<three_digit_sequence>
```

Example:

```text
v1_8b_unsupported_biological_activity_001
v1_8b_unsupported_biological_activity_002
v1_8b_compliance_flag_cluster_001
```

The exact naming may differ if the implementation PR justifies a clearer deterministic pattern.

## 5. Proposed Manifest Contract Update

A future implementation PR may update `eval/v1_10b_answer_sample_manifest.jsonl` or a successor manifest to reference stable evaluator row IDs.

Recommended field:

```text
evaluator_sample_case_id
```

Compatibility expectation:

- preserve `evaluator_case_id` as the category-level link unless the implementation PR explicitly documents a migration;
- use `evaluator_sample_case_id` as the row-level join key;
- do not infer row identity from file order;
- do not infer row identity from duplicate `case_id` values;
- do not silently drop repeated groups from reporting once row IDs exist.

The future report should reject:

- missing row IDs;
- duplicate row IDs;
- unknown row IDs;
- manifest rows whose `evaluator_case_id` conflicts with the matched evaluator row;
- row-ID joins that would change expected outcome or expected failure-label matching without test coverage.

## 6. Allowed Future V1.10C Implementation Scope

A future V1.10C implementation PR may:

- add stable row IDs to `eval/v1_8b_generated_answer_scoring_cases.jsonl`;
- update `scripts/evaluate_v1_8b_offline_answer_scoring.py` to preserve row IDs in JSON output if required;
- update `scripts/report_v1_10b_answer_sample_results.py` to join by stable row ID;
- update `eval/v1_10b_answer_sample_manifest.jsonl` or add a successor manifest to cover repeated evaluator groups;
- update targeted tests for row-ID uniqueness, JSON output preservation, manifest joins, and diagnostic-only boundaries.

Any implementation must remain deterministic and stdlib-only unless a separate dependency preflight approves otherwise.

## 7. Forbidden Future Scope Without Separate Approval

The following are forbidden in V1.10C unless separately scoped and approved:

- runtime capture;
- runtime blocking;
- runtime reporting integration;
- approval routing;
- compliance approval;
- biosafety approval;
- legal approval;
- IP approval;
- wet-lab validation;
- investor-claim approval;
- public-claim approval;
- LLM-as-judge;
- new dependencies;
- CI workflow changes;
- retrieval or generation behavior changes;
- source registry changes;
- vector DB or KG changes;
- production dashboarding;
- web productization;
- privacy-sensitive logs;
- human-review replacement.

## 8. Required Future Tests

Future implementation should include targeted tests for:

- every generated-answer fixture row has a non-empty stable row ID;
- row IDs are unique;
- evaluator JSON output preserves row IDs if the report consumes evaluator JSON;
- repeated `case_id` groups can be matched without row-order inference;
- manifest row IDs reference existing evaluator rows;
- manifest category-level `evaluator_case_id` agrees with the matched evaluator row;
- bad duplicate row IDs fail deterministically;
- bad unknown row IDs fail deterministically;
- `diagnostic_only` remains true in report output;
- `approval_authority` remains false in report output;
- `runtime_behavior_changed` remains false in report output;
- high-risk domains still require human review;
- report wording does not imply compliance, biosafety, legal, IP, wet-lab, runtime, or production approval.

Suggested future validation commands:

```text
python scripts/validate_v1_7c_biology_compliance_golden_set.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py --json
python scripts/report_v1_10b_answer_sample_results.py
python scripts/report_v1_10b_answer_sample_results.py --json
pytest -q tests/test_v1_8b_offline_answer_scoring.py tests/test_v1_10b_answer_sample_report.py
git diff --check
git diff --name-only
```

Broader retrieval evals should remain out of scope unless retrieval, chunking, metadata handling, embeddings, vector DB behavior, reranking, or answer generation changes.

## 9. Validation Plan for This Docs-Only PR

Required for this preflight-only PR:

```text
git diff --check
git diff --name-only
```

Docs-only review:

- changed file is exactly `docs/V1_10C_STABLE_EVALUATOR_SAMPLE_IDS_PREFLIGHT.md`;
- no source code changed;
- no tests changed;
- no fixtures changed;
- no CI workflow changed;
- no runtime, retrieval, generation, source registry, vector DB, or KG files changed;
- no approval or production-readiness claim introduced.

Full pytest should be skipped unless repository instructions demand it.

Rationale for skipping full pytest:

- this PR is docs-only;
- no Python files changed;
- no evaluator fixture changed;
- no evaluator script changed;
- no test changed;
- no runtime behavior changed;
- no retrieval/generation behavior changed;
- no dependency or workflow changed.

## 10. Risk / Digital Devil's Advocate

Risks:

- stable IDs can create a false sense of evaluator maturity;
- row IDs can become unstable if generated from mutable row order or answer text;
- manifest coverage can look complete while still using synthetic fixtures only;
- expanding matched samples can be misread as answer-quality improvement;
- deterministic report output can be misread as compliance or release approval;
- future implementation could accidentally widen into evaluator logic, tests, CI, runtime, retrieval, or generation behavior;
- repeated case groups can still overfit to known synthetic wording even after row identity is stable.

Mitigations:

- keep row IDs explicit and reviewable;
- reject row-order inference;
- preserve diagnostic-only wording in report output;
- preserve human-review fields and high-risk review requirements;
- keep implementation separate from runtime capture, approval routing, and public/investor claim use;
- require targeted tests that prove duplicate case groups are joined by stable row ID.

## 11. Stop Rules

Stop future implementation if:

- stable row IDs require runtime behavior changes;
- stable row IDs require retrieval or generation changes;
- stable row IDs require source registry, vector DB, or KG changes;
- row identity cannot be made stable without row-order inference;
- the report would need to treat evaluator output as approval evidence;
- human-review requirements would be weakened;
- new dependencies appear necessary;
- CI workflow changes appear necessary;
- more than the evaluator fixture, report script, report manifest, and targeted tests need edits;
- the future implementation cannot preserve the diagnostic-only boundary.

If any stop rule triggers, split the work into a separate scoped preflight or return to planning.

## 12. Rollback Path

For this docs-only PR:

- revert the PR that adds `docs/V1_10C_STABLE_EVALUATOR_SAMPLE_IDS_PREFLIGHT.md`.

For a future implementation PR:

- revert fixture row-ID additions;
- revert report join changes;
- revert manifest row-ID references;
- revert targeted tests;
- confirm the V1.10B report returns to its prior unique-`case_id` behavior.

No runtime, retrieval, generation, source registry, vector DB, KG, dependency, or workflow rollback should be required unless a future PR violates this preflight scope.

## 13. Claim Boundary

Safe wording after this preflight:

```text
"V1.10C has a docs-only preflight plan for stable per-row evaluator sample IDs."
```

Safe wording after a future implementation, if tests pass:

```text
"The offline diagnostic answer-sample report can reference repeated evaluator fixture rows by stable row ID."
```

Forbidden wording:

```text
"The evaluator proves runtime answer safety."
"The report approves compliance, biosafety, legal, IP, wet-lab, investor, or public claims."
"The system is production ready."
"Human review has been replaced by evaluator output."
"V1.10C improves retrieval or answer generation quality."
"V1.10C completes vector DB or KG readiness."
```

## 14. Security / Compliance Review Points

This docs-only preflight should be checked for:

- accidental secrets or tokens;
- misleading approval or production-readiness language;
- weakened diagnostic-only truth boundary;
- wording that implies compliance, biosafety, legal, IP, wet-lab, runtime, or production approval;
- instructions that would cause future runtime, CI, dependency, retrieval/generation, source registry, vector DB, or KG changes without separate approval;
- language that replaces human review with evaluator or report output.

## 15. V11.1 Alignment

V1.10C preflight supports:

- evaluator auditability;
- reproducible diagnostic reporting;
- source-grounded non-overclaim discipline;
- human-review preservation;
- future regression coverage for answer-sample reporting.

Complexity level used:

- deterministic fixture/report identity contract;
- no agent, workflow, runtime, external service, dependency, vector DB, KG, or LLM-as-judge pattern.

Why simpler pattern is enough:

- the current gap is row identity, not semantic grading, runtime enforcement, retrieval behavior, or approval routing.

## 16. Truth Boundary

V1.10C preflight is a planning artifact only.

It does not implement stable sample IDs, evaluator fixture changes, report script changes, tests, CI changes, runtime capture, runtime reporting, runtime blocking, approval routing, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, source registry changes, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, human-review replacement, or production readiness.
