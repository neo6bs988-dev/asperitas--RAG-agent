# V1.9A Evaluator Coverage Expansion Preflight

Date: 2026-07-09

Status: docs-only evaluator coverage expansion preflight. This document does not add evaluator cases, evaluator tests, runtime behavior, LLM-as-judge behavior, approval routing, retrieval or generation changes, workflow changes, V1.7C asset changes, dependencies, vector DB or KG behavior, autonomous behavior, or production-readiness claims.

## 1. Executive Bottom Line

V1.9A is a docs-only coverage expansion preflight for the deterministic offline evaluator introduced in V1.8B.

It does not add evaluator cases, tests, runtime behavior, LLM-as-judge behavior, approval behavior, or any implementation change.

The goal is to identify coverage gaps before a possible V1.9B implementation PR, while preserving the diagnostic-only evaluator boundary from V1.8.

## 2. Source Status / Baseline

Baseline evidence:

- V1.8 final closure merge commit: `78d6b99213170846c4799077391bdf00fb823d0c`
- V1.8A evaluator scoring preflight: `docs/V1_8A_OFFLINE_EVALUATOR_SCORING_PREFLIGHT.md`
- V1.8B evaluator script: `scripts/evaluate_v1_8b_offline_answer_scoring.py`
- V1.8B generated-answer fixture file: `eval/v1_8b_generated_answer_scoring_cases.jsonl`
- V1.8B targeted test file: `tests/test_v1_8b_offline_answer_scoring.py`
- V1.8C Quality Gates wiring: `.github/workflows/quality-gates.yml`
- V1.7C biology/compliance golden-set assets: `eval/v1_7c_biology_compliance_golden_set.jsonl` and `eval/v1_7c_biology_compliance_labels.schema.json`

Current verified boundary:

- V1.8B is deterministic offline diagnostic evaluation.
- V1.8C wires the existing V1.8B evaluator into Quality Gates for non-docs changes.
- V1.7C assets remain static diagnostic biology/compliance fixtures.
- None of these files prove runtime safety, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, or production readiness.

## 3. Current Coverage Summary

The current V1.8B evaluator coverage is intentionally small and deterministic.

Current generated-answer fixture coverage includes:

- unsupported biological activity upgrade;
- approval, compliance, legal, biosafety, and IP overclaim language;
- human-review preservation for review-required cases;
- investor-facing overclaim;
- production-readiness overclaim;
- expected pass, fail, and review status consistency;
- expected detected-failure label consistency.

Current deterministic failure labels include:

- `forbidden_case_pattern`
- `approval_or_clearance_overclaim`
- `unsupported_biological_activity_upgrade`
- `missing_human_review_preservation`
- `investor_facing_overclaim`
- `production_readiness_overclaim`
- `input_contract_error`

Current fixture outcome distribution recorded in targeted tests:

- pass: 1
- fail: 3
- review: 1

## 4. Coverage Gap Analysis

Future synthetic generated-answer cases should consider these gaps before any implementation begins:

- citation mismatch or overbroad citation use, where a citation exists but does not support the exact claim;
- missing source context, where the answer treats absent evidence as sufficient evidence;
- conflicting evidence, where the answer fails to preserve uncertainty or source disagreement;
- species and provenance uncertainty, including missing organism identity, collection country, provider, access permission, or benefit-sharing status;
- Nagoya, CITES, LMO, and GMO jurisdictional ambiguity;
- biosafety and biosecurity caution when source context identifies engineered organisms, hazardous handling ambiguity, or unclear review status;
- IP and licensing uncertainty, including unsupported clearance, exclusivity, or license-rights claims;
- investor traction or commercial exclusivity overclaim;
- answer abstention quality, including whether an answer abstains clearly instead of merely using vague caution;
- partial compliance, where an answer preserves one warning but misses another required warning;
- false-positive risk, where a cautious answer is over-penalized by phrase matching;
- Korean/English mixed-language overclaim phrasing, if future repo fixtures or review norms include mixed-language generated answers.

These gaps are design inputs only. They do not imply the current evaluator is defective; they identify the next reviewable expansion surface.

## 5. Proposed V1.9B Expansion Contract

A future V1.9B implementation PR may:

- add additional synthetic generated-answer cases;
- optionally add new deterministic failure labels if the existing labels cannot represent the new cases cleanly;
- extend targeted tests for new case and label coverage;
- preserve the existing evaluator CLI contract;
- preserve the existing JSON output contract;
- preserve existing Quality Gates wiring.

A future V1.9B implementation PR must not:

- add runtime blocking;
- add compliance, legal, biosafety, or IP approval behavior;
- add LLM-as-judge behavior before deterministic limitations are proven with concrete examples;
- modify V1.7C assets unless a separate asset-repair PR is scoped and approved;
- change retrieval or generation behavior;
- claim production readiness.

## 6. Allowed Future Failure Labels

The following labels are design-only candidates for V1.9B. They are not implemented by V1.9A:

- `citation_mismatch`
- `missing_source_context`
- `conflicting_evidence_not_preserved`
- `species_provenance_gap_not_preserved`
- `jurisdictional_compliance_overclaim`
- `ip_licensing_overclaim`
- `missing_abstention_when_required`
- `partial_warning_omission`
- `cautious_answer_false_positive`

V1.9B should add a label only when a synthetic case demonstrates that existing labels cannot express the failure without ambiguity or brittle wording.

## 7. MVP-Gated Architecture

V1.9B should keep the smallest sufficient pattern:

1. Deterministic checks first.
2. Synthetic generated-answer fixture expansion second.
3. Targeted pytest coverage third.
4. Existing CLI and JSON output preservation fourth.

V1.9B should not introduce:

- LLM-as-judge until deterministic limitations are proven with concrete examples;
- an agent framework;
- runtime blocking;
- approval routing;
- retrieval or generation changes;
- production claims;
- new dependencies unless separately justified and approved.

The evaluator should remain an offline diagnostic tool, not a runtime safety system.

## 8. Validation Plan for Future V1.9B

Future V1.9B validation should include:

```text
python scripts/validate_v1_7c_biology_compliance_golden_set.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py --json
pytest -q tests/test_v1_8b_offline_answer_scoring.py
pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py tests/test_v1_8b_offline_answer_scoring.py
git diff --check
git diff --name-only
CI / Quality Gates
```

If V1.9B changes only generated-answer evaluator fixtures and deterministic tests, broader retrieval evals should remain out of scope unless retrieval, chunking, metadata handling, embeddings, vector DB behavior, reranking, or answer generation changes.

## 9. Risk / Digital Devil's Advocate

Expansion risks:

- expanding fixtures can overfit the evaluator to synthetic patterns;
- deterministic phrase checks can miss semantic overclaims;
- adding too many labels can create brittle tests;
- false positives can penalize safe cautious answers;
- passing an expanded evaluator still does not prove runtime safety;
- evaluator results are diagnostic only, not approval evidence.

Operational risk:

- a larger label set can look more mature than it is;
- a passing offline result can be misread as compliance clearance;
- synthetic cases can cover important failure modes while still missing real generated-answer phrasing.

Mitigation:

- keep truth-boundary language in every report path;
- preserve human-review requirements for high-risk biology, compliance, IP, legal, biosafety, biosecurity, and investor-facing outputs;
- add only labels that map to concrete testable cases.

## 10. Truth Boundary

V1.9A is docs-only evaluator coverage expansion preflight.

It does not implement expanded cases, evaluator logic, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, or production readiness.

V1.9A does not prove that the V1.8B evaluator is complete. It only records a coverage map for future implementation review.

## 11. Stop Rules

Stop future implementation if:

- V1.9B would require runtime integration;
- V1.9B would require approval behavior;
- V1.9B would require LLM-as-judge before deterministic limitations are proven;
- V1.9B would require modifying V1.7C assets without a separate asset-repair PR;
- V1.9B would require changing retrieval or generation behavior;
- coverage expansion cannot preserve the diagnostic-only boundary.

If any stop rule triggers, split the work into a separate scoped PR or return to preflight instead of widening V1.9B.
