# V1.6D Runtime Readiness Consumer Contract

## Executive Bottom Line

`metadata.answer_verification.runtime_readiness` is a conservative consumer contract for interpreting V1.6C runtime readiness metadata. It is metadata interpretation only.

Downstream consumers may use this field for observability, reviewer triage, QA dashboards, regression diagnostics, and human-review routing signals. They must not use it as production verification, automatic answer blocking, compliance approval, biosafety approval, legal approval, wet-lab validation, or investor-facing proof.

V1.6D is docs-only. It does not change runtime code, answer generation, retrieval, reranking, source selection, compliance routing, schemas, CI, vector DB behavior, KG behavior, or dependencies.

## Field Path

```text
metadata.answer_verification.runtime_readiness
```

## Field Meaning

The object attached at `metadata.answer_verification.runtime_readiness` should be interpreted as follows:

| Field | Meaning | Consumer rule |
| --- | --- | --- |
| `readiness_classification` | Conservative readiness label derived from existing answer-verification metadata. | Treat as triage metadata, not truth. |
| `reason_codes` | Machine-readable explanation for why the classification was assigned. | Display or log for diagnostics. |
| `recommended_next_action` | Suggested reviewer or QA action. | Use as a routing hint only. |
| `production_verification_claim` | Must remain `false`. | Never present as production verification. |
| `metadata_interpretation_only` | Must remain `true`. | Do not convert into a hard gate without future eval evidence. |

Hard boundary:

```text
production_verification_claim=false
metadata_interpretation_only=true
```

## Allowed Use

Consumers may use `runtime_readiness` for:

- Observability.
- Reviewer triage.
- QA dashboard display.
- Regression diagnostics.
- Human-review routing signal.
- Debugging legacy or incomplete answer-verification metadata.

## Forbidden Use

Consumers must not use `runtime_readiness` for:

- Production verification claim.
- Automatic answer blocking.
- Compliance approval.
- Biosafety approval.
- Legal approval.
- Wet-lab validation.
- Investor-facing proof.
- Scientific truth claim independent of source/evidence review.
- Regulatory, IP, or commercial biological claim approval.

## Classification Interpretation

| Classification | Meaning | Required consumer behavior |
| --- | --- | --- |
| `verified_metadata_present` | Runtime verification-related metadata appears present and internally interpretable. | Show as metadata present only. Do not label the answer as true, production-verified, compliance-approved, or scientifically validated. |
| `metadata_only_fallback` | Runtime readiness was inferred from fallback metadata rather than a full runtime verification result. | Route to reviewer or QA diagnostics if the answer is high-stakes. |
| `not_scored` | No meaningful runtime readiness score is available. This may occur for legacy metadata, missing diagnostics, disabled verifier paths, or intentionally unscored answers. | Tolerate the value and avoid failing legacy consumers. |
| `insufficient_evidence` | The available answer-verification metadata does not provide enough evidence signal for a stronger readiness interpretation. | Do not upgrade claims. Consider human review or evidence-quality improvement. |
| `unsupported_claims_present` | Existing verification metadata indicates unsupported claims are present. | Treat as a review warning. Do not use as the sole blocking mechanism until future gates are approved. |
| `verifier_error` | The runtime verifier or metadata interpretation encountered an error signal. | Log and route to diagnostics. Avoid presenting the answer as verified. |
| `human_review_recommended` | The interpretation recommends human review due to uncertainty, risk, or metadata quality. | Route to human review for high-stakes use. |

## Risk Notes

- `verified_metadata_present` does not mean the answer is true in the world.
- Readiness depends on answer-verification metadata quality.
- Weak evidence span quality weakens readiness even when metadata exists.
- Legacy metadata should be tolerated.
- A clean readiness label does not replace source registry status, evidence span quality, citation fidelity checks, compliance tags, or human approval records.
- Biology, biodiversity, genetic resources, CITES, Nagoya, LMO, biosafety, biosecurity, IP, licensing, privacy, and export-control-sensitive outputs still require risk classification and human approval where applicable.

## Consumer Decision Rule

Use `runtime_readiness` as a reviewer-facing signal, not as a product-facing guarantee.

Minimum safe consumer behavior:

1. Display the classification and reason codes as diagnostics.
2. Preserve `production_verification_claim=false` and `metadata_interpretation_only=true` in any serialized downstream object.
3. Do not rewrite answer status, block answers, approve compliance, or promote investor-facing claims based only on this field.
4. Escalate high-stakes biological, legal, regulatory, IP, or investor-facing outputs to human review.

## Rollback

If the new metadata field causes downstream incompatibility, revert V1.6C.

Rollback target:

```text
562bc80765b0b4ccf981ccc8bf48df627c4329a4
```

Operational rollback rule:

- Revert the V1.6C metadata attachment if consumers cannot tolerate the nested `metadata.answer_verification.runtime_readiness` object.
- Do not patch downstream systems by redefining `verified_metadata_present` as production verification.

## Next Boundary

No automatic blocking should be introduced until a golden-set and regression evidence package supports it.

Future hardening should be handled as V1.7 preflight, not V1.6D implementation. Candidate V1.7 directions:

- Adversarial/security eval preflight.
- Biology/compliance golden-set hardening.
- Citation-fidelity and evidence-span regression tests.
- Human approval routing criteria for high-risk outputs.

## Truth Boundary

This document describes how to consume V1.6C readiness metadata. It is not proof of production verification, compliance approval, biosafety approval, legal approval, wet-lab validation, retrieval improvement, generation improvement, vector DB completion, KG completion, or foundation-model capability.
