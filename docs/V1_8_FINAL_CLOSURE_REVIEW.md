# V1.8 Final Closure Review

Date: 2026-07-09

Status: docs-only final closure review. This document records the V1.8A through V1.8C evidence boundary. It does not add runtime behavior, evaluator logic, evaluator fixtures, evaluator tests, workflow changes, retrieval or generation changes, compliance routing, vector DB or KG behavior, dependencies, approval behavior, LLM-as-judge behavior, or production-readiness claims.

## 1. Executive Bottom Line

V1.8 is closed as an offline evaluator scoring hardening phase.

V1.8 added the minimum reviewable chain for deterministic offline answer-scoring hardening:

- docs-only evaluator scoring design;
- deterministic offline evaluator MVP;
- synthetic generated-answer scoring fixtures;
- targeted pytest coverage;
- CI/Quality Gates wiring for the existing V1.8B offline evaluator on non-docs changes.

V1.8 does not prove runtime answer safety or production readiness. It does not prove legal/compliance approval, biosafety approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or LLM-as-judge behavior.

## 2. Phase Evidence

### V1.8A: Offline Evaluator Scoring Preflight

Evidence:

- File: `docs/V1_8A_OFFLINE_EVALUATOR_SCORING_PREFLIGHT.md`
- Merge evidence: PR #156 squash merge commit `f519753c82b8e8de18301e1867644ccff5a2a30a2653dd`
- Scope: docs-only preflight for future offline evaluator scoring design.

Boundary:

- V1.8A did not implement evaluator scoring, answer behavior scoring, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

### V1.8B: Deterministic Offline Evaluator MVP

Evidence:

- File: `scripts/evaluate_v1_8b_offline_answer_scoring.py`
- File: `eval/v1_8b_generated_answer_scoring_cases.jsonl`
- File: `tests/test_v1_8b_offline_answer_scoring.py`
- Merge evidence: PR #157 squash merge commit `74c2cafa085fdc6c72e1682103fd23891f2103bc`
- Scope: deterministic offline evaluator script, synthetic generated-answer scoring cases, targeted pytest coverage, and optional JSON output.

Validation surface:

- generated-answer JSONL parsing;
- V1.7C case ID linkage;
- required generated-answer fixture fields;
- expected output status and detected-failure consistency;
- deterministic forbidden approval, biological activity, production-readiness, investor-facing overclaim, and human-review preservation checks;
- CLI exit behavior for valid and invalid generated-answer fixtures;
- optional `--json` report output with case-level results and truth-boundary text.

Boundary:

- V1.8B did not implement runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, or production readiness.

### V1.8C: CI/Quality Gates Evaluator Wiring

Evidence:

- File: `.github/workflows/quality-gates.yml`
- Merge evidence: PR #158 squash merge commit `4b5cf454dcdaefeffa5dcae9a94a6b86a1f29389`
- Scope: wired the existing V1.8B offline evaluator into Quality Gates for non-docs changes.

Quality Gates step added:

```text
python scripts/evaluate_v1_8b_offline_answer_scoring.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py --json
pytest -q tests/test_v1_8b_offline_answer_scoring.py
```

Preserved Quality Gates surface:

- existing V1.7D validator regression check;
- unit tests;
- artifact checks;
- metadata audit;
- baseline retrieval eval;
- MVP-003 metadata-aware retrieval eval;
- hybrid retrieval eval.

Boundary:

- V1.8C did not change runtime behavior, evaluator logic, fixtures, tests, retrieval/generation behavior, compliance routing, vector DB/KG behavior, dependencies, approval behavior, LLM-as-judge behavior, or production-readiness status.

## 3. Implemented / Not Implemented

### Implemented

- Docs-only evaluator scoring design.
- Deterministic offline evaluator script.
- Synthetic generated-answer scoring cases.
- Targeted pytest coverage.
- JSON output support in the offline evaluator.
- Quality Gates regression check for the V1.8B evaluator on non-docs changes.

### Not Implemented

- Runtime blocking.
- Compliance approval.
- Biosafety approval.
- Legal approval.
- IP approval.
- Wet-lab validation.
- Retrieval/generation improvement.
- Vector DB/KG completion.
- Autonomous lab execution.
- LLM-as-judge.
- Production readiness.

## 4. Validation Evidence

Local validation commands recorded during V1.8B/V1.8C work:

```text
python scripts/validate_v1_7c_biology_compliance_golden_set.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py
python scripts/evaluate_v1_8b_offline_answer_scoring.py --json
pytest -q tests/test_v1_8b_offline_answer_scoring.py
pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py tests/test_v1_8b_offline_answer_scoring.py
git diff --check
git diff --name-only
```

GitHub validation evidence:

- CI - success.
- Quality Gates - success.
- V1.8B offline evaluator regression check - success.
- Existing V1.7D validator regression check - success.
- Run unit tests - success.
- Verify artifacts - success.
- Metadata audit - success.
- Retrieval eval steps - success.

This closure review itself is docs-only. It should be validated with `git diff --check`, changed-file scope review, and docs-only review.

## 5. Risk / Digital Devil's Advocate

- Deterministic evaluator checks can miss semantic overclaims.
- Synthetic fixtures can be overfit.
- CI-gated offline scoring does not prove runtime safety.
- Evaluator output is diagnostic only.
- Evaluator output must not be interpreted as legal, compliance, biosafety, or IP approval.
- No wet-lab, regulatory, product, or production-readiness claim is justified by V1.8.
- Human review remains required for high-risk biology, compliance, IP, and investor-facing outputs.

## 6. Claim Boundary

### Safe External Wording

"Asperitas has implemented a CI-gated deterministic offline evaluator for synthetic biology/compliance answer-scoring fixtures."

### Forbidden / Unsupported Wording

"Asperitas has a production-ready biology compliance AI agent."

"Asperitas automatically blocks or approves biology/compliance claims."

"Asperitas has validated runtime answer safety."

"Asperitas has completed legal/compliance/biosafety/IP approval."

"Asperitas has wet-lab validated biological claims."

"Asperitas has completed vector DB/KG/RAG production validation."

## 7. Residual Risks

- Semantic false negatives.
- Fixture overfitting.
- Small synthetic dataset coverage.
- Diagnostic-output misuse.
- No runtime integration yet.
- No approval workflow.
- No legal, wet-lab, or regulatory validation.

## 8. Rollback Path

If needed:

- revert V1.8C to remove CI wiring;
- revert V1.8B to remove evaluator script, fixtures, and tests;
- revert V1.8A to remove the design doc.

No runtime, retrieval, generation, compliance-router, vector DB, KG, dependency, or V1.7C asset rollback should be required.

## 9. Next Phase Recommendation

The next phase should be separate scoped work only.

Preferred next phase:

- V1.9A answer-sample generation / evaluator expansion preflight; or
- V1.9A evaluator coverage expansion preflight.

Do not recommend runtime blocking yet.

Do not recommend approval behavior yet.

Do not recommend LLM-as-judge until deterministic limitations are documented with concrete examples.

## 10. Stop Rule

V1.8 should not be extended into V1.8D unless a concrete defect is found in evaluator logic, synthetic answer fixtures, tests, or CI wiring.

If no concrete defect is found, move to V1.9 as a separate scoped phase.

## 11. Truth Boundary

V1.8 closes an offline evaluator scoring hardening phase.

It does not implement runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, LLM-as-judge behavior, or production readiness.
