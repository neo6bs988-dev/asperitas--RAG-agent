# V1.7 Final Closure Review

Date: 2026-07-07

Status: docs-only final closure review. This document records the V1.7A through V1.7E evidence boundary. It does not add runtime behavior, evaluator scoring, retrieval or generation changes, compliance routing, vector DB or KG behavior, dependencies, CI wiring, approval behavior, or production-readiness claims.

## 1. Executive Bottom Line

V1.7 is closed as an eval/control-plane hardening phase for biology and compliance golden-set integrity.

V1.7 built the minimum reviewable chain for biology/compliance golden-set hardening:

- docs-first biology/compliance golden-set preflight;
- docs-first fixture and label/schema contract preflight;
- static V1.7C biology/compliance golden-set and schema assets;
- deterministic local validation and targeted pytest coverage;
- Quality Gates wiring so non-docs changes run the validator regression check.

V1.7 does not prove production AI-agent behavior. It does not prove generated answer quality, legal/compliance approval, biosafety approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

## 2. Phase Evidence

### V1.7A: Biology/Compliance Golden-Set Preflight

Evidence:

- File: `docs/V1_7A_BIOLOGY_COMPLIANCE_GOLDEN_SET_PREFLIGHT.md`
- Merge evidence: `87866740e99e93b66784320561effc32a997bf82`
- Scope: docs-only preflight for high-risk biology, biodiversity, source-grounding, legal/compliance, IP/licensing, and investor-facing claim cases.

Boundary:

- V1.7A did not create fixtures, tests, schemas, CI gates, runtime blocking, approval behavior, retrieval/generation changes, vector DB/KG changes, or production readiness.

### V1.7B: Fixture/Schema Contract Preflight

Evidence:

- File: `docs/V1_7B_GOLDEN_SET_FIXTURES_SCHEMA_PREFLIGHT.md`
- Merge evidence: `129f39af62ebd5251b6a35b4d829383512c9189c`
- Scope: docs-only preflight for future static fixture and label/schema contract design.

Boundary:

- V1.7B did not add golden-set fixtures, executable schemas, tests, runners, CI gates, runtime behavior, approval behavior, retrieval/generation changes, vector DB/KG changes, or production readiness.

### V1.7C: Static Golden-Set/Schema Assets

Evidence:

- File: `eval/v1_7c_biology_compliance_golden_set.jsonl`
- File: `eval/v1_7c_biology_compliance_labels.schema.json`
- Merge evidence: PR #149 squash merge commit `b1289f251a7172a1ed50a53419e14a1c10dce7b8`
- Scope: static synthetic fixture records and a static label/schema contract.

Coverage represented in the static assets:

- source-grounding failure;
- citation mismatch;
- unsupported biological activity claim;
- species/provenance missing;
- Nagoya/CITES/LMO/biosafety/biosecurity/IP/licensing flag;
- investor-facing overclaim;
- human-review-required case.

Boundary:

- V1.7C did not implement evaluator logic, regression gates, tests, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

### V1.7D: Deterministic Validator and Targeted Tests

Evidence:

- File: `scripts/validate_v1_7c_biology_compliance_golden_set.py`
- File: `tests/test_v1_7c_biology_compliance_golden_set_validator.py`
- Merge evidence: PR #153 squash merge commit `c4262532020303928151899007bfc46e79223920`
- Scope: deterministic local validator and targeted pytest coverage for the static V1.7C assets.

Validation surface:

- schema JSON parsing;
- JSONL parsing;
- required fixture fields;
- expected label enum membership;
- required category coverage;
- `synthetic_approved_safe` source context status;
- diagnostic-only forbidden consumer actions;
- conservative source-context overclaim phrase checks;
- CLI exit behavior for valid and invalid temporary assets.

Boundary:

- V1.7D did not implement evaluator scoring, regression gates, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

### V1.7E: CI/Quality Gates Wiring

Evidence:

- File: `.github/workflows/quality-gates.yml`
- Merge evidence: PR #154 squash merge commit `1005a7ca9e8bbdce198ff68e2c29b106874499f0`
- Scope: wired the existing V1.7D validator and targeted pytest into the existing Quality Gates path for non-docs changes.

Quality Gates step added:

```text
python scripts/validate_v1_7c_biology_compliance_golden_set.py
pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py
```

Boundary:

- V1.7E did not add evaluator scoring, runtime blocking, approval routing, retrieval/generation changes, new dependencies, new evaluator frameworks, vector DB/KG changes, autonomous behavior, or production-readiness claims.

## 3. Implemented / Not Implemented

### Implemented

- Static V1.7C biology/compliance golden-set assets.
- Static label/schema contract.
- Deterministic local validator.
- Targeted pytest coverage.
- Quality Gates regression check for non-docs changes.

### Not Implemented

- Offline evaluator scoring.
- Answer behavior scoring.
- Runtime blocking.
- Compliance approval.
- Biosafety approval.
- Legal approval.
- IP approval.
- Wet-lab validation.
- Retrieval/generation improvement.
- Vector DB/KG completion.
- Autonomous lab execution.
- Production readiness.

## 4. Validation Evidence

Local validation commands recorded during V1.7D/V1.7E work:

```text
python scripts/validate_v1_7c_biology_compliance_golden_set.py
pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py
python -m compileall scripts/validate_v1_7c_biology_compliance_golden_set.py tests/test_v1_7c_biology_compliance_golden_set_validator.py
git diff --check
```

GitHub validation evidence:

- CI - success.
- Quality Gates - success.
- V1.7D validator regression check - success after V1.7E wiring.

This closure review itself is docs-only. It should be validated with `git diff --check`, changed-file scope review, and the existing docs-only Quality Gates path.

## 5. Risk / Digital Devil's Advocate

- Static validation checks fixture/schema integrity only.
- Static validation does not prove answer quality.
- Static validation does not prove evaluator scoring accuracy.
- Static validation does not prove runtime safety.
- Static validation does not replace human approval for high-risk biology/compliance/IP/investor-facing outputs.
- The current gate can prevent asset drift, but cannot judge actual AI answers.
- A passing V1.7 gate should not be used as legal, compliance, biosafety, IP, scientific, wet-lab, investor-facing, or production approval.

## 6. Claim Boundary

### Safe External Wording

"Asperitas has implemented a CI-gated deterministic validation layer for static biology/compliance golden-set assets."

### Forbidden / Unsupported Wording

"Asperitas has a production-ready biology compliance AI agent."

"Asperitas automatically approves biology/compliance claims."

"Asperitas has validated wet-lab biology claims."

"Asperitas has completed vector DB/KG/RAG production validation."

## 7. Next Phase Recommendation

V1.8 should be a separate offline evaluator scoring preflight.

Recommended V1.8 scope:

- define how generated answers would be evaluated against V1.7C labels;
- define source-grounding expectations for answer-level evaluation;
- preserve diagnostic-only labels;
- avoid runtime blocking;
- avoid approval behavior;
- avoid production claims;
- keep human approval required for high-risk biology/compliance/IP/investor-facing outputs.

V1.8 should not implement runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement claims, vector DB/KG completion claims, autonomous lab execution, or production readiness.

## 8. Stop Rule

V1.7 should not be extended into V1.7F unless a concrete defect is found in the validator, schema, golden-set assets, or CI wiring.

If no concrete defect is found, the next work should move to V1.8 as a separate scoped phase for offline evaluator scoring preflight.
