# V1.5B Claim-To-Citation Verifier Design

Date: 2026-07-02

Status: design/specification only. This document prepares V1.5C implementation work and does not change retrieval, answer generation, citation rendering, compliance routing, eval fixtures, source registry data, chunk artifacts, embeddings, vector DB behavior, reranking, dependencies, services, secrets, or runtime defaults.

Baseline: `main` at `7836517b110390c6fcce5d155ca983fa8ef364ce`.

## Objective

V1.5B defines the design target for moving Asperitas from answer-level citation presence toward claim-level source grounding:

```text
answer -> atomic claims -> evidence spans -> citation support decision -> answer-level diagnostics
```

The verifier is a proposed V1.5C layer that should inspect a generated answer, its citations, retrieved contexts, source metadata, and truth/compliance outputs, then produce auditable claim-level support decisions. V1.5B is not evidence that the verifier is implemented or that RAG performance has improved.

## V1.5A Preflight

| Field | V1.5B classification |
|---|---|
| Risk level | Low for this PR because the change is docs/decision-log only |
| Changed surface | Docs, roadmap text, decision log |
| Behavior impact | None |
| Required verification | Re-read edited docs, Markdown/code-fence sanity, changed-surface sanity, truth-boundary review, `git diff --check` |
| Skipped checks | `pytest` and retrieval evals are not required because no source code, eval fixtures, source registry data, chunks, retrieval, answer generation, compliance routing, embeddings, vector DB, or reranking behavior changes |
| Metric provenance | Not Run for retrieval, answer, latency, cost, and compliance metrics |

## Current Gap

V1.3, V1.4, and V1.5A created the foundation for source-grounded answers, but they do not yet prove claim-level support:

| Layer | Current value | Remaining V1.5B gap |
|---|---|---|
| Retrieval diagnostics and source coverage | Retrieval modes and evals track source hits, source priority, evidence labels, section metadata, and path context | Retrieval quality does not prove each generated answer claim is supported |
| V1.3C answer contract | `EvidencePack`, `EvidenceItem`, `GroundedAnswer`, citation keys, limitations, and source-grounding structure exist | Citation coverage is answer-level and does not classify support per atomic claim |
| V1.3D truth/compliance router | Blocks source-map citations, P6 misuse, missing-evidence overclaims, completion claims, and human-review risk | Router checks are not a complete claim/evidence-span verifier |
| V1.4 optimization closeout | Preserves the answer contract while measuring token, context, latency, and closeout boundaries | Efficiency work does not measure claim-level faithfulness |
| V1.5A governance | Defines risk-based gates, docs-only path, and changed-surface discipline | V1.5B must define the actual verifier architecture before V1.5C implementation |

The design target is a layer that can distinguish "the answer has citations" from "each material claim is supported by the cited evidence spans."

## External Reference Doctrine

The following are P6 external design references only. They are operating doctrine, not Asperitas implementation evidence.

| Reference family | P6 principle to adapt | Asperitas-specific control |
|---|---|---|
| RAGAS-style evaluation | Separate retrieval/context quality, faithfulness, and answer relevance | Keep retrieval metrics, claim support metrics, and answer usefulness metrics separate |
| ARES-style evaluation | Evaluate context relevance, answer faithfulness, and answer relevance as different questions | Do not let high source hit rate substitute for claim-level faithfulness |
| VeriCite-style principle | Verify claims, select supporting evidence, and refine attribution | Require claim records to identify supporting spans or explicit failure modes |
| MedRAGChecker-style principle | Biomedical and biology RAG needs claim-level verification, unsupported/contradictory diagnostics, and safety/compliance-aware error classes | Add biology entity tags and compliance-sensitive claim tags to the verifier contract |

No P6 source proves an Asperitas capability until a future PR implements code, tests, evals, and review evidence.

## Core Pipeline

### Inputs

The proposed verifier should accept:

- user question;
- generated answer text;
- answer-level citation markers, such as `[E1]`;
- retrieved contexts or `EvidencePack` records;
- citation records and `EvidenceItem` metadata;
- source metadata including source ID, path, priority, evidence label, verification status, disclosure level, and license/compliance fields when available;
- truth/compliance router outputs when available;
- retrieval diagnostics, ranks, scores, and score components when available;
- answer contract outputs, including limitations and unsupported-claim records when available.

### Processing

V1.5C should implement the smallest deterministic or semi-deterministic version of this flow:

1. Segment answer text into material statements, bullets, caveats, limitations, and non-claim text.
2. Extract atomic claims from material statements.
3. Classify each claim type and required evidence type.
4. Resolve cited citation keys to candidate evidence spans.
5. Align claims to cited spans and, when allowed, nearby retrieved spans from the same evidence pack.
6. Classify support status: supported, partially supported, unsupported, contradicted, citation missing, citation mismatch, ambiguous, not verifiable from context, or compliance blocked.
7. Tag biology entities and relation types when present.
8. Tag compliance-sensitive claims and truth-boundary risk.
9. Aggregate claim decisions into answer-level diagnostics.
10. Emit machine-readable reports and human-readable warnings.

### Outputs

The verifier should emit:

- `claim_verification_report`;
- `answer_verification_summary`;
- blocking warnings;
- non-blocking warnings;
- eval metrics and fixture-compatible result records.

## Data Contracts

The following schemas are design targets for V1.5C. Field names are proposed and should be implemented in the smallest backward-compatible way that fits the existing `src/asperitas_agent/schemas.py` style.

### Atomic Claim Schema

| Field | Required | Purpose |
|---|---:|---|
| `claim_id` | Yes | Stable ID within the answer, such as `C1` |
| `answer_id` | No | Optional parent answer/run ID when available |
| `claim_text` | Yes | Minimal atomic claim text extracted from the answer |
| `claim_type` | Yes | Claim category, such as `sourced_fact`, `bounded_inference`, `biology_relation`, `measurement`, `method`, `status`, `compliance_sensitive`, `limitation`, or `non_material` |
| `source_sentence` | No | Original sentence or bullet before atomization |
| `sentence_index` | No | Position in answer text for debug trace |
| `cited_source_ids` | Yes | Source IDs explicitly cited by the claim |
| `cited_span_ids` | Yes | Evidence span IDs explicitly cited by the claim |
| `citation_keys` | Yes | Citation markers attached to the claim |
| `required_evidence_type` | Yes | Evidence needed to support the claim, such as exact text, source metadata, peer-reviewed mechanism source, regulatory source, completion log, or compliance approval artifact |
| `detected_entities` | Yes | Biology-specific entity records when detected |
| `compliance_tags` | Yes | Compliance/truth-boundary tags |
| `support_status` | Yes | Status from the support taxonomy |
| `confidence` | Yes | Verifier confidence in its classification, separate from truth of the claim |
| `verifier_notes` | Yes | Human-readable explanation of why the status was assigned |
| `failure_mode` | No | Normalized failure mode when not fully supported |
| `blocking` | Yes | Whether the claim should block or force caution in answer output |
| `metadata` | No | Verifier version, extraction method, timestamps, or trace IDs |

### Evidence Span Schema

| Field | Required | Purpose |
|---|---:|---|
| `source_id` | Yes when available | Source registry identity |
| `span_id` | Yes | Stable span identity within the verifier report |
| `citation_key` | No | Answer-level citation marker, such as `[E1]` |
| `chunk_id` | No | Existing chunk reference when available |
| `document_title` | No | Human-readable source title |
| `source_path` | Yes when available | Source path or provenance |
| `section` | No | Section label |
| `section_heading` | No | Section heading |
| `section_path` | No | Heading ancestry |
| `stable_locator` | No | Preferred stable locator when offsets are unavailable |
| `character_start` | No | Character start offset when available |
| `character_end` | No | Character end offset when available |
| `excerpt_boundary` | Yes | Quoted or bounded evidence excerpt used by the verifier |
| `excerpt_hash` | Yes | Hash of the normalized excerpt for audit and drift checks |
| `metadata_keys` | No | Metadata fields available for verification |
| `source_priority` | Yes when available | P0-P6 source priority |
| `evidence_label` | Yes when available | Existing evidence label |
| `verification_status` | No | Source verification status when available |
| `license_status` | No | License status when available |
| `disclosure_level` | No | Confidentiality/disclosure level when available |
| `compliance_flags` | No | Source-level or span-level compliance flags |
| `retrieval_rank` | No | Retrieval rank |
| `retrieval_score` | No | Retrieval score |
| `score_components` | No | Hybrid/reranker/debug components when available |

Evidence spans should preserve source metadata; missing optional fields must remain empty or explicitly `unknown`, never fabricated.

### Claim Verification Report

The proposed top-level report should include:

| Field | Purpose |
|---|---|
| `schema_version` | Version of the verifier report contract |
| `verifier_name` | Verifier implementation name |
| `verifier_version` | Verifier implementation version |
| `query` | User question |
| `answer_text` | Verified answer text or answer hash if text storage is too sensitive |
| `retriever_metadata` | Retriever name, version, top-k, and mode when available |
| `claims` | List of atomic claim records |
| `evidence_spans` | List of evidence span records |
| `answer_verification_summary` | Aggregated answer-level result |
| `blocking_warnings` | Findings that should block, abstain, or require human review |
| `non_blocking_warnings` | Findings that should be surfaced but may not block |
| `metrics` | Fixture-compatible metric outputs |
| `metadata` | Run timestamp, deterministic flag, and debug trace data when available |

### Answer Verification Summary

The answer-level summary should include:

- `claim_count`;
- `material_claim_count`;
- `supported_claim_count`;
- `partially_supported_claim_count`;
- `unsupported_claim_count`;
- `contradicted_claim_count`;
- `citation_missing_count`;
- `citation_mismatch_count`;
- `ambiguous_claim_count`;
- `not_verifiable_from_context_count`;
- `compliance_blocked_count`;
- `claim_support_rate`;
- `citation_coverage_rate`;
- `citation_precision`;
- `answer_faithfulness_status`, such as `pass`, `caution`, `fail`, or `not_scored`;
- `human_review_required`;
- `recommended_next_action`.

## Support Status Taxonomy

| Status | Meaning | Typical action |
|---|---|---|
| `supported` | Cited evidence directly supports the atomic claim | Count as supported |
| `partially_supported` | Evidence supports part of the claim but misses scope, qualifier, quantity, entity, or causal relation | Warn or require rewrite |
| `unsupported` | Retrieved/cited context does not support the claim | Block or move to unsupported claims |
| `contradicted` | Retrieved/cited context conflicts with the claim | Block and require correction |
| `citation_missing` | Material claim has no citation marker or source linkage | Block or require citation |
| `citation_mismatch` | Citation points to a source/span that supports a different claim | Block or require citation repair |
| `ambiguous` | Claim is too vague, compound, or underspecified to verify | Require atomization or clarification |
| `not_verifiable_from_context` | Claim may be true, but retrieved context is insufficient | Mark missing evidence or abstain |
| `compliance_blocked` | Claim requires human/legal/regulatory/biosafety/compliance review before it can be treated as supported | Block, abstain, or require human approval |

Existing gate wording such as `too vague` and `needs verification` can map to `ambiguous` and `not_verifiable_from_context` unless V1.5C keeps those as aliases for backward compatibility.

## Biology-Specific Entity Layer

The verifier should preserve biology-specific context without pretending to be a scientific validation system. Detected entity records should include the entity text, normalized label when deterministic normalization is available, entity type, source span IDs, and confidence.

Required entity types:

| Entity type | Examples of what to capture |
|---|---|
| `species` | Scientific/common names, strain when available |
| `gene` | Gene symbols and aliases |
| `protein` | Protein names, enzyme classes, receptor names |
| `compound` | Metabolites, natural products, chemical classes |
| `pathway` | Biological pathway or process |
| `assay` | Assay type, readout, screening method |
| `phenotype` | Observable biological trait or outcome |
| `tissue_or_cell_type` | Tissue, cell type, cell line, organoid, source tissue |
| `disease_or_condition` | Disease, condition, pest, pathogen, or phenotype context when applicable |
| `organism_or_source_material` | Biodiversity source, specimen, extract, sample, accession, or source material |
| `experimental_method` | Method, protocol class, instrument class, or study design |
| `measurement_value_unit` | Quantity, unit, threshold, concentration, dose, time, p-value, confidence interval |
| `biological_relation_type` | Relation such as inhibits, activates, binds, expresses, produces, associated with, causes, or correlates with |

Biology entity extraction should support verification, not overclaiming. A recognized entity does not mean the biological claim is validated.

## Compliance And Truth-Boundary Layer

The verifier should tag claims that touch compliance, disclosure, legal, regulatory, biosafety, biosecurity, IP, investor, public-communication, or validation boundaries.

Required compliance/truth tags:

| Tag | Trigger examples |
|---|---|
| `cites` | CITES-listed species, derivatives, permits, trade, export/import |
| `nagoya_abs` | Access and benefit sharing, prior informed consent, mutually agreed terms, source-country obligations |
| `lmo_gmo` | Living modified organisms, genetic modification, contained use, environmental release |
| `biosafety` | Wet-lab execution, biological risk, containment, organism handling, safety review |
| `ip_license` | Patentability, freedom to operate, proprietary source, license status, restricted source |
| `human_clinical_sensitivity` | Human subjects, clinical claims, diagnostics, therapy, patient data, medical efficacy |
| `export_security_sensitive_biology` | Biosecurity, export control, dual-use, operational sensitive biology |
| `public_investor_claim` | External/public/investor-facing claims, customer traction, committed capital, product performance |
| `truth_boundary_status` | Deployment, validation, approval, production, completion, or readiness status claim |
| `p6_doctrine_only` | Benchmark or external operating doctrine used as analogy rather than internal fact |

The verifier must not allow unsupported claims of:

- production DB completion;
- production KG completion;
- production vector DB completion;
- wet-lab validation;
- legal approval;
- regulatory approval;
- autonomous lab operation;
- proprietary LLM or biological foundation-model completion.

When these topics appear without direct supporting evidence and human approval, the expected support status is `compliance_blocked`, `unsupported`, or `not_verifiable_from_context`.

## Metrics

V1.5B defines metrics for V1.5C. It does not report measured improvements.

| Metric | Definition target | Why it matters |
|---|---|---|
| Claim extraction coverage | Extracted material claims divided by expected material claims in fixtures | Prevents hiding unsupported claims by failing to extract them |
| Citation coverage | Material claims with at least one citation divided by material claims | Measures answer-level citation completeness |
| Citation precision | Claim citations judged support-relevant divided by all claim citations | Detects decorative or mismatched citations |
| Evidence-span support accuracy | Verifier support status matches fixture oracle divided by evaluated claims | Measures core verifier correctness |
| Unsupported claim rate | Unsupported claims divided by material claims | Tracks hallucination/overclaim surface |
| Contradicted claim rate | Contradicted claims divided by material claims | Tracks severe faithfulness failures |
| Citation mismatch rate | Citation-mismatch claims divided by cited material claims | Finds wrong-source or wrong-span citations |
| Answer-level faithfulness | Aggregated pass/caution/fail from claim support statuses | Separates answer-level groundedness from retrieval hit rate |
| Compliance-sensitive claim detection | Compliance-sensitive claims correctly tagged divided by expected compliance-sensitive claims | Protects CITES/Nagoya/LMO/biosafety/IP/public-claim boundaries |
| Abstention/refusal correctness | Correct abstentions/refusals divided by abstention/refusal fixtures | Measures missing-evidence honesty |
| Latency/cost overhead | Verifier runtime and token/cost proxy added to answer pipeline | Keeps verifier useful without uncontrolled overhead |
| Regression vs V1.4 answer contract | Existing answer-contract checks remain passing after verifier integration | Protects current answer structure and no-overclaim guarantees |

Metric reports should label provenance as `Fresh Run`, `Historical`, or `Not Run`. No metric should be claimed as improved without before/after evidence.

## Eval Fixtures And Golden Set Requirements

V1.5C should add a small verifier fixture pack before broader golden-set expansion. Fixture data should be text fixtures committed only after review for source rights, confidentiality, and no sensitive biological operational content.

Each fixture should include:

- `case_id`;
- `question`;
- `answer_text`;
- retrieved contexts or serialized `EvidencePack`;
- citation records;
- source metadata fields needed by the test;
- expected atomic claims;
- expected evidence span matches;
- expected support statuses;
- expected biology entities when relevant;
- expected compliance/truth-boundary tags when relevant;
- expected answer-level summary;
- fixture rationale and source provenance.

Required fixture categories:

| Category | Required cases |
|---|---|
| Support taxonomy | supported, partially supported, unsupported, contradicted, citation missing, citation mismatch, ambiguous, not verifiable from context |
| Biology | species, gene, protein, compound, pathway, assay, phenotype, tissue/cell type, disease/condition, source material, method, measurement/value/unit, relation type |
| Compliance/truth boundary | CITES, Nagoya/ABS, LMO/GMO, biosafety, IP/license, human/clinical sensitivity, export/security sensitive biology, public/investor claim, production/completion overclaim |
| Answer contract regression | Existing V1.4 answer-contract-safe outputs remain accepted |
| Abstention/refusal | Missing evidence, source-map-only citation, source-priority mismatch, compliance-required abstention |

The first V1.5C implementation should prefer compact deterministic fixtures over broad model-judge scoring.

## V1.5C Eval Gates

The V1.5C implementation PRs should use these gates:

| Gate | Required when |
|---|---|
| Unit tests for schemas and taxonomy | Any verifier schema, support taxonomy, report model, or serialization code changes |
| Fixture tests for support cases | Any claim extraction, citation alignment, span matching, or support classification code changes |
| Biology fixture tests | Any biology entity tagging or biology-specific failure modes are added |
| Compliance/truth-boundary fixture tests | Any compliance tags, truth-boundary blocking, or human-review classifications are added |
| No-regression against V1.4 answer contract | Any integration with answer generation, `GroundedAnswer`, citation output, limitations, or router text |
| Targeted retrieval/eval gates | Only when retrieval inputs, retrieval mode choice, evidence selection, ranking, reranking, eval fixtures, or eval semantics change |
| Full Quality Gates | Implementation PRs that touch core RAG behavior, answer generation, compliance/security behavior, eval fixtures, retrieval, CI/config, release/main readiness, or unclear blast radius |

Docs-only V1.5B does not run these gates locally because no implementation exists in this PR.

## Integration Points For V1.5C

V1.5C should inspect these files before implementation. This design PR does not edit them.

| Area | Likely files to inspect | Expected integration |
|---|---|---|
| Data schemas | `src/asperitas_agent/schemas.py` | Add backward-compatible claim, evidence span, report, and summary dataclasses |
| Evidence packaging | `src/asperitas_agent/evidence_pack.py`, `scripts/build_evidence_pack.py` | Preserve citation keys, source IDs, source paths, source priority, evidence labels, section metadata, rank, score, and excerpt hashes |
| Answer generation | `src/asperitas_agent/answer_generation.py`, `src/asperitas_agent/answer_contract.py`, `scripts/generate_grounded_answer.py` | Feed generated answer and citations into verifier without changing answer behavior in early PRs |
| Truth/compliance routing | `src/asperitas_agent/truth_compliance_router.py`, `src/asperitas_agent/compliance.py`, `src/asperitas_agent/guardrails.py` | Reuse existing compliance and overclaim signals as inputs; do not weaken fail-closed routing |
| Retrieval diagnostics | `src/asperitas_agent/retrieval_mvp003.py`, `src/asperitas_agent/retrieval_tfidf.py`, `src/asperitas_agent/hybrid_scoring.py`, `src/asperitas_agent/reranking.py` | Consume rank/score/debug metadata without changing retrieval defaults |
| Eval harness | `src/asperitas_agent/eval_metrics.py`, `src/asperitas_agent/eval_artifacts.py`, `src/asperitas_agent/eval_report.py`, `scripts/run_retrieval_eval.py`, `scripts/run_golden_agent_eval.py` | Add verifier-specific metrics and fixture result reporting without replacing strict retrieval metrics |
| Quality gates | `docs/QUALITY_GATES.md`, `.github/pull_request_template.md`, relevant tests | Add implementation-specific verifier gates after V1.5C creates executable behavior |
| Source policy | `docs/AOS_SOURCE_POLICY.md`, registry and metadata docs | Preserve source priority, evidence label, disclosure, license, and verification status boundaries |

## V1.5C Implementation Plan

Break implementation into small PRs unless a future owner explicitly narrows or combines safe steps:

1. Schema and taxonomy PR
   - Add support-status taxonomy and report dataclasses.
   - Add serialization tests.
   - No answer behavior change.
2. Deterministic parser/extractor baseline PR
   - Segment answer text into candidate material claims.
   - Extract simple atomic claims from bullets and sentences.
   - Add claim extraction fixture tests.
3. Evidence span matcher PR
   - Resolve citation keys to `EvidenceItem` records.
   - Generate stable span IDs and excerpt hashes.
   - Add citation missing and citation mismatch tests.
4. Support classifier PR
   - Implement conservative lexical/metadata support classes first.
   - Classify supported, partially supported, unsupported, contradicted, ambiguous, not verifiable from context, and compliance blocked.
   - Add support taxonomy fixtures.
5. Biology and compliance tagging PR
   - Add deterministic biology entity tags and compliance/truth-boundary tags.
   - Add CITES/Nagoya/LMO/biosafety/IP/public-claim fixtures.
6. Verifier report and eval pack PR
   - Emit `claim_verification_report`, `answer_verification_summary`, and metrics.
   - Add fixture-backed eval command or targeted pytest entrypoints.
7. Answer contract integration PR
   - Integrate verifier report with answer output or diagnostics.
   - Preserve V1.4 answer contract and V1.3D truth/compliance router behavior.
8. Quality gate integration PR
   - Update quality gates and PR templates only after executable verifier behavior exists.
   - Define when verifier gates are required in CI.

## Risk Register

| Risk | Failure mode | Mitigation |
|---|---|---|
| Overclaiming design as capability | Docs imply verifier is implemented or performance improved | Use `design target`, `proposed`, and `V1.5C should implement`; report metrics as Not Run |
| Claim extraction misses material claims | Unsupported claims avoid verification | Fixture-based claim extraction coverage metric |
| Claim extraction over-splits | Noise creates false failures | Mark non-material text and keep claim type explicit |
| Citation matching is too loose | Decorative citations pass | Require cited span IDs and support rationale |
| Contradiction detection is weak | Conflicts are treated as unsupported instead of contradicted | Start conservative; mark uncertain conflicts as `ambiguous` or `not_verifiable_from_context` |
| Biology entities are ambiguous | Species/gene/protein aliases cause false tags | Keep deterministic tags auditable and do not claim biological validation |
| Compliance false negatives | Sensitive claims pass as normal support | Reuse truth/compliance router signals and add compliance fixture coverage |
| Latency/cost overhead grows | Verifier becomes too expensive for routine use | Track overhead as a metric before making it default |
| Eval fixture leakage | Fixtures expose confidential or sensitive source text | Review fixture source rights, disclosure, and operational biology risk before commit |
| Model-judge dependency | Verifier becomes non-deterministic too early | Start with deterministic baseline and add any judge only behind explicit eval gates |

## Non-Goals

V1.5B does not:

- implement verifier code;
- modify source/runtime behavior;
- change retrieval algorithms;
- change document chunking;
- change metadata handling;
- change embeddings;
- change vector DB behavior;
- change reranking;
- change answer generation;
- change truth/compliance routing;
- generate eval fixtures;
- add dependencies, services, model calls, endpoints, cloud resources, or secrets;
- claim RAG performance improvement;
- claim production DB, production KG, production vector DB, wet-lab validation, legal approval, regulatory approval, autonomous lab operation, or proprietary LLM/foundation-model completion.

## Acceptance Criteria For This Design

V1.5B is acceptable when:

- the verifier purpose is clear and scoped to design/specification;
- the current V1.3/V1.4/V1.5A gap is identified;
- the architecture names inputs, processing, and outputs;
- atomic claim and evidence span schemas are defined;
- support statuses are defined;
- biology-specific entity fields are defined;
- compliance/truth-boundary tags are defined;
- eval metrics and gates are defined;
- fixture/golden-set requirements are defined;
- V1.5C implementation phases are actionable;
- risks, non-goals, and truth-boundary limits are explicit;
- no implementation or performance improvement is claimed.

## Recommended Next Step

After this design PR is reviewed and merged, open the first V1.5C implementation PR for schema and taxonomy only. That PR should add tests, run targeted pytest, and continue to skip retrieval eval unless retrieval, evidence selection, answer generation, eval fixtures, or retrieval-facing behavior changes.
