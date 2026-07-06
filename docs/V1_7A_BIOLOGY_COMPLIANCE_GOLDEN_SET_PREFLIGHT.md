# V1.7A Biology / Compliance Golden-Set Preflight

Date: 2026-07-06

Status: docs-only preflight plan. This document does not add runtime features, change retrieval, change reranking, change answer generation, change refusal behavior, change compliance routing, change schemas, change dependencies, change configuration, change CI, change vector DB behavior, change KG behavior, or claim production readiness.

Baseline: V1.6 is audit-closed. PR #145 merged with merge commit `7ebf21dddb546b5cf89aca12294f3547a58b5142`.

## 1. Executive Bottom Line

V1.7A should begin with a planning-only biology and compliance golden-set preflight.

The smallest sufficient pattern is a deterministic checklist and docs-first golden-set design. The next work should define what high-risk biological, biodiversity, source-grounding, legal/compliance, IP/licensing, and investor-facing claim cases must be evaluated before any automatic blocking, approval, or production-readiness behavior is considered.

V1.7A preflight is planning only. It does not create a golden-set runner, does not change runtime behavior, does not block answers, does not approve compliance, does not validate wet-lab claims, does not complete vector DB/KG, and does not prove production readiness.

## 2. Source Status / Assumptions

This preflight is grounded in the following read-only references:

- `docs/V1_6_FINAL_CLOSURE_REVIEW.md`
- `docs/V1_6D_RUNTIME_READINESS_CONSUMER_CONTRACT.md`
- `docs/DEVELOPMENT_PROCESS_V11_1_SOURCE_SYNC.md`
- `docs/V1_5_FINAL_CLOSURE_REVIEW.md`
- `docs/QUALITY_GATES.md`
- `docs/AOS_SOURCE_POLICY.md`
- `docs/MVP_010_GOLDEN_QUERY_SUITE.md`
- `docs/MVP_011_FAILURE_TAXONOMY.md`
- `docs/MVP019C_SECURITY_GUARD.md`

Assumptions carried forward:

- V1.6 is closed as a metadata interpretation and consumer-contract milestone.
- V1.6 readiness metadata remains diagnostic only.
- High-risk biology, biodiversity, compliance, legal, IP, licensing, biosafety, biosecurity, and investor-facing outputs require human review before approval claims.
- Planning artifacts are not proof of source ingestion, legal review, compliance approval, wet-lab validation, vector DB completion, KG completion, production deployment, or foundation-model capability.
- Future implementation must preserve existing anti-overfitting rules: runtime code must not special-case golden ids, exact query strings, test filenames, CI, or evaluation files.

## 3. Why V1.7A Starts With Biology/Compliance Golden-Set Preflight

The most important post-V1.6 risk is not missing runtime code. It is overreading diagnostic metadata as proof that a high-risk biological or compliance-sensitive answer is true, approved, commercially safe, or investor-ready.

A preflight-first plan reduces that risk by defining the evidence questions before implementation:

- Which claim types are too risky to evaluate only with generic citation checks?
- Which missing provenance, legal, compliance, or approval signals must be visible?
- Which unsupported biological activity claims should be flagged?
- Which investor-facing overclaims should route to human approval?
- Which future labels are needed before any regression gate can be built?

This work should precede fixtures, schemas, runners, CI, routing, or blocking behavior.

## 4. V1.6 Boundary Carried Forward

V1.6 established metadata interpretation only.

The hard boundary remains:

```text
production_verification_claim=false
metadata_interpretation_only=true
```

V1.7A must not weaken that boundary. Any future biology/compliance golden-set result must be treated as evaluation evidence, not legal approval, biosafety approval, wet-lab validation, investor-facing proof, production verification, vector DB/KG completion, or foundation-model capability.

Human approval remains required for high-risk biology/compliance/IP outputs.

## 5. Golden-Set Objective

The future V1.7 biology/compliance golden set should evaluate whether the system can identify, preserve, and report risk-relevant evidence for high-risk claims before stronger behavior is introduced.

The objective is to test the answer and metadata contract around:

- grounded biological and biodiversity claims;
- citation fidelity and evidence-span sufficiency;
- species, material, geography, and provenance status;
- Nagoya/CITES/LMO/biosafety/biosecurity/IP/licensing flags;
- unsupported biological activity claims;
- investor-facing overclaim risk;
- human approval routing criteria.

The golden set should make missing evidence explicit. It should not train or tune runtime behavior by itself.

## 6. Candidate Eval Dimensions

### Source Grounding

Check whether material claims can be traced to an appropriate source class:

- P1/P2 for Asperitas internal or approved public positioning;
- P3 for biological mechanism, assay, species, and technical claims;
- P4 for legal, regulatory, biodiversity, Nagoya, CITES, LMO, biosafety, and biosecurity claims;
- P5 for market, investor, or commercial signals.

Expected preflight question: does the cited source class match the claim type?

### Citation Fidelity

Check whether answer citations point to the evidence actually used and do not cite unrelated or weaker support.

Expected preflight question: would the cited evidence support the exact claim, or only a nearby weaker claim?

### Evidence-Span Sufficiency

Check whether cited spans contain enough surrounding context to support the claim without requiring hidden inference.

Expected preflight question: is the evidence span sufficient for a reviewer to validate the claim and its limits?

### Species/Provenance Status

Check whether species, strain, sample, genetic resource, geography, provider, collection/access path, and source status are identified when relevant.

Expected preflight question: does the answer avoid commercial or scientific claims when provenance is missing, ambiguous, restricted, or unreviewed?

### Nagoya/CITES/LMO/Biosafety/Biosecurity/IP/Licensing Flags

Check whether risk domains are surfaced for reviewer attention:

- Nagoya Protocol or access and benefit-sharing uncertainty;
- CITES or protected-species uncertainty;
- LMO/GMO or engineered-organism status;
- biosafety or biosecurity sensitivity;
- pathogen, toxin, or unsafe operational risk;
- IP ownership, license, or patent uncertainty;
- source license, confidentiality, privacy, or export-control uncertainty.

Expected preflight question: are risk flags visible without claiming approval?

### Unsupported Biological Activity Claims

Check whether claims such as antimicrobial, anticancer, anti-inflammatory, enzyme, metabolite, yield, potency, toxicity, ecological impact, or mechanism-of-action claims are supported by source evidence.

Expected preflight question: is the answer prevented from upgrading weak, preliminary, in vitro, anecdotal, or unrelated evidence into a stronger biological claim?

### Investor-Facing Overclaim Risk

Check whether the answer avoids turning diagnostic metadata, source maps, patents, papers, internal notes, or pipeline plans into proof of traction, regulatory clearance, market readiness, scientific validation, or commercial exclusivity.

Expected preflight question: would this wording be safe for investor or partner use only after human review?

### Human Approval Routing

Check whether high-risk outputs are labeled for human review instead of approval.

Expected preflight question: does the future label tell reviewers why escalation is needed without blocking, approving, or changing runtime behavior by default?

## 7. Proposed Golden-Set Case Types

Future V1.7 implementation should consider a small case pack before broad expansion:

| Case type | Example risk | Expected future behavior |
| --- | --- | --- |
| Grounded biology claim | Biological activity claim with peer-reviewed support. | Preserve source grounding and evidence limits. |
| Weak biology claim | Preliminary evidence is overgeneralized. | Flag unsupported or overclaimed activity. |
| Species/provenance gap | Species or genetic-resource origin is missing. | Mark provenance as insufficient and route to review. |
| Nagoya-sensitive access | Genetic resource claim lacks access/benefit-sharing status. | Flag Nagoya/legal review need. |
| CITES/protected-species uncertainty | Biodiversity claim may involve protected species. | Flag protected-status review need. |
| LMO/biosafety-sensitive claim | Engineered organism or lab-use claim is ambiguous. | Flag biosafety/LMO review need. |
| Biosecurity-sensitive request | Unsafe operational detail or misuse risk appears. | Require human approval and safety review. |
| IP/licensing ambiguity | Commercial claim depends on unclear ownership or license. | Flag IP/licensing review need. |
| Citation mismatch | Citation points to an unrelated or weaker source. | Flag citation fidelity failure. |
| Evidence-span insufficiency | Span lacks necessary context or limitation. | Flag insufficient evidence span. |
| Investor overclaim | Answer implies validation, approval, traction, or exclusivity. | Flag investor-facing overclaim risk. |
| Human-review positive control | High-risk output with correct escalation wording. | Confirm routing label without approval claim. |

## 8. Expected Labels / Outcomes

Future labels should be conservative and deterministic. Candidate labels:

- `source_grounded`
- `citation_mismatch`
- `insufficient_evidence_span`
- `unsupported_biological_activity_claim`
- `species_or_provenance_missing`
- `nagoya_review_required`
- `cites_review_required`
- `lmo_or_biosafety_review_required`
- `biosecurity_review_required`
- `ip_or_licensing_review_required`
- `investor_overclaim_risk`
- `human_review_required`
- `approval_not_established`

Expected outcomes should distinguish:

- pass: the claim is grounded within the stated evidence limits;
- warn: the answer needs reviewer attention but does not require an automatic runtime change;
- fail: the fixture expectation is not met in an eval context;
- route: human review is required for high-risk use;
- not approved: the golden-set result is not legal, compliance, biosafety, or wet-lab approval.

## 9. Acceptance Criteria for Future Implementation

Future implementation should not begin until reviewers agree on:

- stable fixture format and minimal case count;
- deterministic expected labels;
- source-priority expectations by claim type;
- citation and evidence-span matching rules;
- compliance flag vocabulary;
- investor-facing overclaim rules;
- human-review routing criteria;
- anti-overfitting checks;
- changed-area validation budget;
- rollback path.

Future implementation should be accepted only when:

- fixtures are synthetic or approved for repository use;
- no confidential, restricted, personal, or license-ambiguous source text is introduced without review;
- labels are diagnostics, not approvals;
- docs state skipped checks and residual risk;
- regression output can be reviewed without implying production readiness.

## 10. Non-Goals

V1.7A does not:

- implement V1.7 runtime behavior;
- create or modify golden-set fixtures;
- create a golden-set runner;
- change schemas;
- change tests;
- change retrieval, reranking, generation, guardrails, compliance routing, config, CI, dependencies, vector DB, or KG behavior;
- introduce automatic answer blocking;
- approve compliance, legal, biosafety, biosecurity, IP, licensing, or investor-facing claims;
- validate wet-lab claims;
- prove source ingestion completion;
- prove vector DB or KG completion;
- prove production readiness;
- introduce LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, MCP, autonomous agents, or multi-agent orchestration.

## 11. Complexity Justification

The smallest sufficient architecture is:

```text
deterministic checklist -> docs-first golden-set design -> future fixture/eval contract
```

This is sufficient because the current problem is scope definition and truth-boundary control, not orchestration.

More complex frameworks are not justified. LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, MCP, autonomous agents, and multi-agent orchestration would add review burden, dependency/security surface, cost, latency, and ambiguity before the required labels and case types are agreed.

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

Rationale: this PR changes only a planning document. It does not change executable code, tests, schemas, runtime behavior, retrieval, generation, reranking, compliance routing, config, CI, vector DB, KG, dependencies, README, or AGENTS.

## 13. Risks / Digital Devil's Advocate

| Risk | Why it matters | Control |
| --- | --- | --- |
| The golden-set plan is mistaken for enforcement. | Reviewers may assume behavior changed. | State that V1.7A is planning only and adds no runner, gate, block, or approval. |
| Compliance flags are overread as legal approval. | Legal/compliance status depends on human review and jurisdiction. | Use `review_required` and `approval_not_established` style labels. |
| Biology claims are overgeneralized. | Preliminary or narrow evidence can be inflated into broad activity claims. | Require evidence-span sufficiency and unsupported-activity labels. |
| Investor wording becomes too strong. | Investor-facing claims can imply validation, market readiness, or exclusivity. | Include investor overclaim cases and human review routing. |
| Provenance gaps are hidden. | Biodiversity/genetic-resource claims may require source and access status. | Require species/provenance case types and flags. |
| Eval design overfits future behavior. | Runtime might learn fixture-specific shortcuts. | Preserve anti-overfitting and deterministic-label rules. |
| Scope expands into implementation. | Runtime/test/schema/CI/retrieval changes would exceed V1.7A. | Stop if implementation files or behavior changes are required. |

## 14. Stop Rules

Stop future V1.7A or follow-on work before editing if:

- V1.6 closure merge commit cannot be confirmed.
- The plan would require runtime, test, schema, CI, retrieval, compliance routing, dependency, vector DB, or KG edits.
- The plan would implement V1.7 rather than preflight it.
- The plan weakens the V1.6 truth boundary.
- The plan claims legal approval, compliance approval, biosafety approval, wet-lab validation, production readiness, vector DB/KG completion, autonomous lab execution, or foundation-model completion.
- The work requires LangGraph, Agents SDK, CrewAI, AutoGen, Semantic Kernel, MCP, autonomous agents, or multi-agent orchestration.
- Human approval would be implied but no approval record exists.

## 15. Next PR Options

After V1.7A preflight review, choose exactly one small next step:

- add synthetic golden-set fixtures;
- define eval labels/schema;
- add a regression gate;
- define human-review routing criteria.

Do not implement those in this PR.
