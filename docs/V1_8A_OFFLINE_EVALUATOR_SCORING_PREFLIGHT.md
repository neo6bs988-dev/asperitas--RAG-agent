# V1.8A Offline Evaluator Scoring Preflight

Date: 2026-07-07

Status: docs-only preflight for future offline evaluator scoring. This document does not add evaluator logic, answer behavior scoring, runtime blocking, approval routing, retrieval or generation changes, eval asset changes, tests, dependencies, vector DB or KG behavior, autonomous behavior, or production-readiness claims.

## 1. Executive Bottom Line

V1.8A is a docs-only preflight for offline evaluator scoring.

It does not implement evaluator logic yet.

The goal is to design the smallest future evaluator capable of scoring generated answers against V1.7C biology/compliance golden-set expectations while preserving the V1.7 truth boundary.

## 2. Source Status / Baseline

Document-supported baseline:

- V1.7 final closure merge commit: `b696e4ec2902cd40346a550bed4e3ec30a2653dd`
- V1.7C golden-set fixture asset: `eval/v1_7c_biology_compliance_golden_set.jsonl`
- V1.7C label/schema contract: `eval/v1_7c_biology_compliance_labels.schema.json`
- V1.7D deterministic validator: `scripts/validate_v1_7c_biology_compliance_golden_set.py`
- V1.7E CI/Quality Gates wiring: `.github/workflows/quality-gates.yml`

V1.7 implemented static V1.7C biology/compliance golden-set assets, a static label/schema contract, deterministic local validation, targeted pytest coverage, and Quality Gates wiring for non-docs changes.

V1.7 did not implement offline evaluator scoring, generated-answer behavior scoring, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

## 3. Evaluator Objective

The future offline evaluator should take a fixture query, source context, generated answer, and expected labels, then score whether the answer is:

- source-grounded;
- citation-faithful;
- appropriately cautious or abstaining when evidence is insufficient;
- not upgrading unsupported biological activity claims;
- preserving human-review requirements;
- not implying compliance, legal, biosafety, or IP approval;
- not making investor-facing overclaims.

The evaluator should produce diagnostic results for offline review. It should not approve claims, block runtime responses, or replace human review for high-risk biology, compliance, IP, legal, biosafety, biosecurity, or investor-facing outputs.

## 4. Proposed Input Contract

Design-only future input shape:

```json
{
  "case_id": "v1_7c_example_case",
  "query": "Fixture query text.",
  "source_context": {
    "source_kind": "synthetic_peer_review_summary",
    "source_status": "synthetic_approved_safe",
    "summary": "Synthetic source-context summary."
  },
  "expected_labels": {
    "expected_answer_status": "caution",
    "evidence_sufficiency": "insufficient",
    "citation_fidelity": "overbroad",
    "compliance_risk_class": "none_identified",
    "biological_claim_risk": "unsupported_activity_claim",
    "human_review_required": true,
    "allowed_consumer_action": ["display_diagnostic", "do_not_upgrade_claim", "record_eval_result"],
    "forbidden_consumer_action": ["runtime_blocking", "compliance_approval"]
  },
  "generated_answer": "Candidate generated answer text.",
  "retrieved_evidence": [],
  "answer_metadata": {},
  "model_or_pipeline_id": "optional-local-pipeline-id",
  "run_id": "optional-run-id"
}
```

Required fields:

- `case_id`
- `query`
- `source_context`
- `expected_labels`
- `generated_answer`

Optional fields:

- `retrieved_evidence`
- `answer_metadata`
- `model_or_pipeline_id`
- `run_id`

## 5. Proposed Output Contract

Design-only future output shape:

```json
{
  "case_id": "v1_7c_example_case",
  "overall_status": "review",
  "scores": {
    "source_grounding": 0.0,
    "citation_fidelity": 0.0,
    "biological_claim_safety": 0.0,
    "compliance_boundary": 0.0,
    "human_review_preservation": 0.0,
    "overclaim_resistance": 0.0
  },
  "detected_failures": [],
  "required_human_review": true,
  "evidence_notes": [],
  "decision_implication": "Diagnostic offline review only.",
  "truth_boundary": "This score is not legal, compliance, biosafety, IP, wet-lab, runtime, or production approval."
}
```

Allowed `overall_status` values:

- `pass`
- `fail`
- `review`

The output should preserve the truth boundary that an offline evaluator result is diagnostic only. A passing result must not be interpreted as runtime safety, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.

## 6. Scoring Dimensions

The future evaluator should score at least these dimensions:

### Source Grounding

Checks whether the generated answer is supported by the provided source context and expected source priority. It should penalize answers that treat market notes, planning artifacts, source maps, or synthetic fixture text as stronger evidence than they are.

### Citation Fidelity

Checks whether citations or evidence references support the exact claim. It should flag missing, mismatched, or overbroad citations.

### Evidence Sufficiency

Checks whether the answer reflects the expected evidence sufficiency label: `sufficient`, `insufficient`, `missing`, or `conflicting`.

### Unsupported Biological Activity Claim Detection

Checks whether the answer upgrades hypotheses, screening plans, organism descriptions, or market notes into biological activity claims such as confirmed mechanism, potency, therapeutic effect, or wet-lab validation.

### Provenance / Species Gap Handling

Checks whether the answer preserves uncertainty when species identity, collection country, provider, access permission, benefit-sharing status, or provenance review is missing.

### Compliance and Safety Caution

Checks whether the answer preserves caution for Nagoya, CITES, LMO/GMO, biosafety, biosecurity, IP, licensing, and jurisdictional uncertainty. It should flag answers that imply approval or clearance without evidence.

### Investor-Facing Overclaim Detection

Checks whether the answer avoids treating fixture design, source maps, eval scaffolds, or planning documents as proof of regulatory-ready assets, commercial traction, exclusivity, validated products, or production-grade platform readiness.

### Human-Review Preservation

Checks whether the answer preserves `human_review_required` expectations and routes high-risk uncertainty to human review without implying that review has occurred.

### Forbidden Approval / Production-Readiness Language Detection

Checks for forbidden or unsupported language that implies:

- runtime blocking was implemented;
- compliance approval exists;
- biosafety approval exists;
- legal approval exists;
- IP approval exists;
- wet-lab validation exists;
- retrieval/generation improvement was proven;
- vector DB/KG completion was proven;
- autonomous lab execution exists;
- production readiness exists.

## 7. MVP-Gated Architecture

V1.8B should use the smallest sufficient pattern:

1. Deterministic answer-pattern checks.
2. Deterministic label-consistency checks.
3. Optional structured JSON report output.
4. Targeted pytest coverage around representative pass, fail, and review cases.

V1.8B should not introduce LLM-as-judge unless deterministic checks are shown insufficient with concrete examples.

V1.8B should not introduce:

- an agent framework;
- runtime blocking;
- approval routing;
- production claims;
- new dependencies unless separately justified and approved.

The first implementation should favor explicit, deterministic checks because the V1.7C assets already encode forbidden answer patterns, expected labels, required evidence conditions, and human-review expectations.

## 8. Future V1.8B Implementation Boundary

V1.8B should be a separate small implementation PR.

V1.8B may add:

- an offline evaluator script;
- sample synthetic generated-answer fixtures;
- targeted pytest coverage;
- optional JSON report output.

V1.8B must not add:

- runtime blocking;
- compliance, legal, biosafety, or IP approval;
- wet-lab validation;
- autonomous agent behavior;
- retrieval/generation changes;
- vector DB/KG completion claims;
- production-readiness claims.

V1.8B should avoid changing V1.7C assets unless a concrete defect is found. If a defect is found, stop and scope an asset-repair PR separately from evaluator implementation.

## 9. Risk / Digital Devil's Advocate

- Scoring can be overfit to small golden-set fixtures.
- Deterministic pattern checks can miss semantic overclaims.
- LLM-as-judge can add nondeterminism, hidden bias, cost, latency, and traceability gaps.
- Passing offline evaluator results do not prove runtime safety.
- Evaluator reports must not be interpreted as legal, compliance, biosafety, or IP approval.
- Human approval remains required for high-risk biology, compliance, IP, legal, biosafety, biosecurity, and investor-facing outputs.
- A score can create false confidence if the report does not expose evidence notes, detected failures, and truth-boundary language.
- Synthetic fixtures are useful for regression design but are not external scientific, legal, regulatory, or commercial evidence.

## 10. Success Criteria

V1.8A succeeds if:

- evaluator contract is clear;
- scoring dimensions are defined;
- future implementation boundary is narrow;
- runtime, approval, and production claims are explicitly excluded;
- V1.8B can be implemented without changing V1.7C assets;
- human-review requirements remain visible for high-risk biology/compliance/IP/investor-facing cases.

## 11. Stop Rules

Stop before implementation if:

- the evaluator requires modifying V1.7C assets;
- the evaluator requires runtime integration;
- the evaluator requires approval behavior;
- the evaluator requires new dependencies;
- the evaluator requires LLM-as-judge before deterministic checks are attempted;
- evidence is insufficient to define expected behavior;
- the scope expands into retrieval/generation changes, vector DB/KG claims, autonomous execution, or production-readiness claims.

## 12. Validation Plan for This Docs-Only PR

Required local validation:

```text
git diff --check
git diff --name-only
docs-only review
```

Skipped by design for this docs-only PR:

- full pytest;
- retrieval eval;
- V1.7D validator run unless repository instructions require it.

Rationale: V1.8A changes only a Markdown design document. It does not change runtime code, validator code, test code, eval assets, workflows, schemas, dependencies, retrieval behavior, generation behavior, or source registry state.

## 13. Truth Boundary

V1.8A is docs-only evaluator scoring preflight.

It does not implement evaluator scoring, answer behavior scoring, runtime blocking, compliance approval, biosafety approval, legal approval, IP approval, wet-lab validation, retrieval/generation improvement, vector DB/KG completion, autonomous lab execution, or production readiness.
