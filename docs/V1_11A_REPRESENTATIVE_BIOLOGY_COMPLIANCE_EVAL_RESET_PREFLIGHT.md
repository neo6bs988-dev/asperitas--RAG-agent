# V1.11A Representative Biology / Compliance Evaluation Reset Preflight

## 1. Status and Document Boundary

Status: docs-only preflight. This document proposes an implementation-ready contract for a future representative biology/compliance evaluation benchmark. It does not create or modify a dataset, protected holdout, schema, fixture, evaluator, test, retrieval path, generation path, runtime verifier, CI workflow, registry, source artifact, vector DB, KG, deployment, approval route, or biological execution capability.

The proposed counts, fields, identifiers, splits, roles, metrics, and acceptance criteria are review hypotheses. They are not approved implementation or proof of capability.

## 2. Executive Bottom Line

V1.11A should reset evaluation design around representative, versioned, source-governed biology/compliance tasks with explicit development/protected-holdout separation and leakage controls.

The current synthetic regression pack remains useful and protected from reinterpretation. It is not representative holdout evidence. The next implementation must use a separate namespace, preserve source eligibility and human-review boundaries, and prevent expected-answer or expected-source information from entering runtime retrieval.

## 3. Confirmed GitHub Baseline

Confirmed through local Git history and GitHub metadata on 2026-07-12:

- repository: `neo6bs988-dev/asperitas--RAG-agent`;
- latest confirmed `main`: `84809ddd2f18d14ea25c2ecb0d43b2d7b01e5691`;
- PR #168 V1.10C implementation: merged at `d37ecdbaf367ff7554a59723888288f97bf253e0`;
- PR #169 V1.10 final closure: merged at `84809ddd2f18d14ea25c2ecb0d43b2d7b01e5691`;
- PR #169 GitHub checks: Python smoke checks PASS; tests-artifacts-retrieval-eval PASS;
- V1.10: closed as a CI-gated deterministic offline answer-sample diagnostic reporting and stable sample-identity phase;
- active next phase: Representative Biology / Compliance Evaluation Reset.

## 4. Source Status / Assumptions

Confirmed:

- this repository is public;
- the V1.7C, V1.8B, V1.10B, and V1.10C assets exist as deterministic synthetic/offline regression infrastructure;
- current retrieval evaluation uses 32 question records and a separate 32-row expected-source oracle;
- strict and relaxed retrieval oracle metrics are separate;
- the current roadmap identifies fixture-specific expected-section information and limited synthetic fixtures as material generalization risks.

Review hypotheses:

- an initial 32-case representative benchmark is a practical first implementation target;
- a 20-case development split and 12-case protected holdout may provide a workable initial review budget;
- qualified reviewer availability and private holdout operations can be established before implementation.

Unverified and requiring human decisions:

- private holdout storage location and access-control system;
- reviewer assignments and qualifications;
- source licenses, allowed use, and confidentiality decisions for future benchmark evidence;
- whether the proposed counts and family allocation are sufficient.

## 5. Current Evaluation Asset Inventory

| Asset | Current evidence | Intended continuing role |
|---|---|---|
| `eval/v1_7c_biology_compliance_golden_set.jsonl` | 7 synthetic biology/compliance cases | Legacy contract/regression pack |
| `eval/v1_7c_biology_compliance_labels.schema.json` | Deterministic fixture contract | Legacy schema reference only |
| `eval/v1_8b_generated_answer_scoring_cases.jsonl` | 13 synthetic generated-answer cases; 2 pass, 10 fail, 1 review | Legacy evaluator regression pack |
| `eval/v1_10b_answer_sample_manifest.jsonl` | 13 synthetic samples with stable evaluator references | Legacy report regression pack |
| `eval/retrieval_questions.jsonl` | 32 retrieval questions with strict and optional relaxed oracle metadata | Existing retrieval regression set; not the new protected holdout |
| `eval/expected_sources.jsonl` | 32 aligned expected-source rows | Existing retrieval oracle; not a protected holdout |
| `scripts/validate_v1_7c_biology_compliance_golden_set.py` | Deterministic validation | Reusable validation pattern, not the future benchmark validator |
| `scripts/evaluate_v1_8b_offline_answer_scoring.py` | Deterministic phrase/contract evaluator | Legacy offline regression evaluator |
| `scripts/report_v1_10b_answer_sample_results.py` | Stable-ID diagnostic aggregation | Reusable reporting pattern |
| `scripts/run_retrieval_eval.py` | Strict/relaxed retrieval scoring and threshold reporting | Retrieval metric reference; must not receive holdout answer keys as features |
| Targeted tests for the assets above | Contract and regression evidence | Legacy regression protection |

## 6. What Existing Assets Actually Prove

The existing assets prove only their tested deterministic contracts, including:

- required-field and schema validation for the seven V1.7C synthetic cases;
- deterministic detection of known phrase/contract failures in 13 V1.8B synthetic answers;
- stable row-level IDs and deterministic 13/13 V1.10B report joins;
- explicit failure for missing, blank, duplicate, unknown, or category-conflicting stable IDs;
- preservation of diagnostic-only output and human-review requirements;
- reproducible strict and relaxed retrieval-oracle calculations over the existing 32-question set;
- regression protection for current CLI, JSON, metadata, and source-grounding contracts.

## 7. What Existing Assets Do Not Prove

They do not prove:

- representative biology/compliance coverage;
- protected-holdout generalization;
- robustness to fresh paraphrases, languages, sources, or adversarial variants;
- real generated-answer or runtime behavior;
- production retrieval, generation, verifier, vector DB, or KG quality;
- legal, regulatory, compliance, biosafety, biosecurity, IP/FTO, publication, or release approval;
- wet-lab validation or autonomous execution;
- proprietary biological data moat or foundation-model capability.

## 8. Reusable Contracts

The future implementation should reuse these principles without mutating legacy assets:

- explicit stable task and sample identities independent of row order;
- deterministic JSON/JSONL validation with explicit errors;
- separate source, evidence, support-status, and response-disposition fields;
- strict and relaxed multi-valid-source metrics reported separately;
- preservation of `source_id`, provenance, verification status, license status, allowed use, evidence span, confidence/limitations, and compliance tags;
- diagnostic-only evaluator/report outputs;
- mandatory human review for high-risk labels and release decisions;
- fail-closed handling for missing, duplicate, conflicting, or ineligible metadata.

## 9. Known Evaluation Gaps

- The biology/compliance golden set has only seven synthetic case categories.
- Generated-answer scoring has only 13 synthetic examples and can overfit to known phrases.
- Current retrieval questions can saturate without demonstrating holdout generalization.
- Fixture-specific expected-section information is present in the existing evaluation path and must not become a retrieval feature for the protected benchmark.
- Current assets do not measure reviewer agreement, label drift, near-duplicate leakage, source-document overlap, or paraphrase-family performance.
- Real answer-provider behavior, claim-to-citation accuracy, runtime latency/cost, and operator review are not represented by the legacy pack.
- Public-repository constraints make protected-holdout handling an unresolved operational dependency.

## 10. V1.11A Goal

Define a reviewable contract for a future representative biology/compliance evaluation benchmark that:

- uses a separate version namespace;
- separates development data from protected holdout data;
- connects tasks to eligible sources and evidence spans;
- separates evidence support from response behavior;
- requires qualified human gold-label review for high-risk cases;
- measures retrieval, answer, safety/compliance, dataset, and operational layers separately;
- prevents benchmark leakage and answer-key-derived runtime behavior;
- preserves the legacy synthetic pack as regression-only evidence.

## 11. Non-Goals

This preflight does not:

- create the 32 proposed cases;
- select or ingest sources;
- assign reviewers;
- approve private storage;
- create a schema, fixture, manifest, evaluator, test, or CI gate;
- modify retrieval, reranking, answer generation, or runtime behavior;
- add dependencies, frameworks, services, vector DB, or KG systems;
- grant legal, compliance, biosafety, regulatory, IP/FTO, wet-lab, publication, investor, release, or production approval.

## 12. Legacy Regression-Pack Boundary

The following remain the legacy synthetic regression pack:

- V1.7C biology/compliance golden set and schema;
- V1.8B generated-answer scoring cases;
- V1.10B answer-sample manifest/report;
- V1.10C stable evaluator sample identity;
- the existing 32-question retrieval regression set and expected-source oracle.

Do not modify, migrate, rename, relabel, reinterpret, or expose these as representative holdout evidence in V1.11A. The future benchmark must use a separate namespace and additive implementation.

## 13. Representative Benchmark Versioning Strategy

Review hypothesis:

- proposed dataset ID: `asperitas_representative_biology_compliance_eval`;
- proposed initial implementation version: `0.1.0`;
- proposed task namespace: `v1_11_task_*`;
- proposed sample namespace: `v1_11_sample_*`.

Versioning rules proposed for future implementation:

- patch: wording, metadata, or non-semantic correction with no split/label meaning change;
- minor: additive tasks/samples or reviewed label/source additions;
- major: split changes, label meaning changes, eligibility-policy changes, or incompatible schema changes;
- every version records dataset provenance, change reason, reviewer decision, and prior-version linkage;
- published IDs are immutable and never recycled;
- protected-holdout contents remain outside public Git history even when version metadata is public.

## 14. Proposed Dataset Split

Review hypothesis only:

- total initial cases: 32;
- development: 20;
- protected holdout: 12.

Development cases may be public only when synthetic, redacted, publication-cleared, or explicitly approved for public use. Protected-holdout queries, source configurations, evidence spans, answer keys, labels, and reviewer notes must not be committed to this public repository.

Passing 32 cases would not prove production safety or generalization. Future scale-up requires failure analysis, reviewer evidence, new task variants, and versioned fresh holdout evidence.

## 15. Proposed Task-Family Allocation

| Task family | Total | Development | Protected holdout |
|---|---:|---:|---:|
| Biodiversity / species / provenance | 4 | 2 | 2 |
| Compliance / CITES / Nagoya / LMO / biosafety | 6 | 4 | 2 |
| Genome / protein / pathway / biological claims | 4 | 3 | 1 |
| DBTL planning and validation honesty | 4 | 2 | 2 |
| IP / licensing / commercial / investor claims | 4 | 2 | 2 |
| Source grounding / citation / contradiction / reasoning | 6 | 4 | 2 |
| Security / adversarial / prompt injection / source poisoning | 4 | 3 | 1 |
| Total | 32 | 20 | 12 |

These counts are preflight hypotheses. Reviewers may change them before implementation. Allocation must be rechecked for risk coverage, reviewer capacity, source eligibility, and family imbalance.

## 16. Proposed Record Schema

Future records should propose fields equivalent to:

- `dataset_id`
- `dataset_version`
- `task_id`
- `sample_id`
- `split`
- `task_family`
- `subdomain`
- `language`
- `query`
- `source_refs`
- `source_id`
- `source_status`
- `verification_status`
- `license_status`
- `allowed_use`
- `evidence_span`
- `evidence_limitations`
- `expected_support_status`
- `expected_response_disposition`
- `risk_class`
- `compliance_tags`
- `human_review_required`
- `review_role`
- `reviewer_id_or_placeholder`
- `reviewed_at`
- `dataset_provenance`
- `change_reason`
- `adversarial_tags`
- `notes`

This list is a proposed contract, not an implemented schema. Personal reviewer information should not be collected when a role placeholder or pseudonymous internal identifier is sufficient.

## 17. Stable Task and Sample Identity Contract

`task_id` represents stable semantic task identity. It remains the same across wording, language, paraphrase, source configuration, or adversarial variants when the intended decision problem is unchanged.

`sample_id` represents one specific wording, language, paraphrase, source configuration, or adversarial variant.

Proposed requirements:

- non-empty strings with a documented pattern;
- globally unique within a dataset version lineage;
- independent of row number, file order, or answer text hash;
- immutable once published;
- duplicate IDs fail validation;
- split reassignment, semantic task change, or label-meaning change requires an explicit changelog and appropriate version increment;
- runtime code must not route behavior by task/sample ID.

## 18. Source Eligibility Contract

A source is eligible only when the future implementation verifies:

- stable `source_id` and title/path reference;
- source priority and provenance;
- confidentiality classification;
- license status and allowed use;
- collection and verification status;
- owner and updated date;
- applicable compliance tags;
- approval for the intended development or protected-holdout use.

Repository presence alone does not establish eligibility. Unknown, blocked, unverified, restricted, or unclear-license sources fail closed and cannot become benchmark evidence.

## 19. Source Lifecycle and Registry Status

Proposed lifecycle:

```text
candidate
-> needs_review
-> approved
-> ingested
or blocked
```

The lifecycle records source ID, title/path, priority, confidentiality, license status, collection status, verification status, provenance, owner, updated date, allowed use, and compliance tags.

Protected-holdout evidence must not be included in a production-shaped retrieval index. A separate private storage and access-control decision requires an explicit human-approved record and is not invented by this preflight.

## 20. Evidence-Span Contract

Each gold judgment should identify the source and the minimum reviewable evidence needed to support or contradict the expected claim. Future implementation should define:

- `source_id` and version/provenance reference;
- stable document locator such as page, section, paragraph, table, or structured record key;
- bounded evidence span or private span reference;
- evidence limitations, ambiguity, conflicts, and date sensitivity;
- relationship between the span and the expected support status;
- multiple valid spans or sources when appropriate.

Evidence spans are gold-label inputs, not runtime retrieval features. Protected spans and source contents must not enter public Git history.

## 21. Expected Support-Status Contract

Proposed evidence support statuses:

- `supported`
- `unsupported`
- `contradicted`
- `insufficient`
- `conflicting`
- `not_applicable`

Support status describes evidence-to-claim relationship only. It does not determine whether the system should answer, abstain, refuse, or escalate.

## 22. Expected Response-Disposition Contract

Proposed response dispositions:

- `answer`
- `answer_with_limits`
- `abstain`
- `refuse`
- `escalate`

Evidence may be insufficient while `answer_with_limits` is correct. A harmful request may include supported background facts while `refuse` is correct. Compliance uncertainty may require `escalate`, never automated approval. Support status and response disposition must remain separate fields and metrics.

## 23. Human-Reviewed Gold-Label Contract

Future gold labels require:

- source-eligibility confirmation;
- evidence-span review;
- expected support status and response disposition;
- risk class and compliance tags;
- reviewer role, review time, provenance, and change reason;
- explicit disagreement/adjudication handling;
- qualified human review for high-risk biology, biodiversity, compliance, biosafety, security, legal, IP, investor, or public-communication cases.

Evaluator output cannot assign approval status or replace qualified human review.

## 24. Reviewer Roles and Ownership

Proposed role placeholders only:

- Biology Reviewer
- Biodiversity / Provenance Reviewer
- Compliance / Legal Reviewer
- Biosafety / Biosecurity Reviewer
- Security / Adversarial Reviewer
- Dataset Steward
- AI Lead Benchmark Approver

No reviewer is assigned by this document. Future implementation must record role ownership and an adjudication path without unnecessarily exposing personal information.

## 25. Development / Protected-Holdout Separation

Proposed controls:

- development cases may be used for implementation debugging and visible regression tests;
- protected-holdout contents are unavailable to implementation agents, runtime prompts, retrieval features, and public CI logs;
- holdout evaluation access is role-limited, logged, and separated from benchmark development;
- a holdout case exposed to developers, public history, prompts, or retrieval features is quarantined and replaced under a versioned incident record;
- development and holdout source-document overlap is measured and disclosed;
- no silent migration between splits;
- repeated evaluation on holdout is rate-limited by a future human-approved policy.

## 26. Public / Private Storage Boundary

This repository is public. Never commit protected-holdout queries, answer keys, gold labels, evidence spans, private source contents, reviewer notes, or access credentials.

Never commit unpublished assay data, specimen-level confidential records, private partner information, restricted permits/agreements, private ABS/Nagoya documents, private genomic or biological source material, personal information, unreleased investor information, operational wet-lab procedures, or restricted biological instructions.

Public development fixtures must be synthetic, redacted, publication-cleared, or explicitly approved for public use. A private holdout storage decision is a separate human-approved governance record; this preflight does not select or create that system.

## 27. Leakage and Anti-Overfitting Controls

Future implementation must require:

- holdout queries and expected answers absent from public repository history;
- holdout expected sources and expected sections absent from runtime retrieval features;
- evaluator labels unavailable to runtime retrieval and generation;
- runtime code independent of eval paths and fixture/task/sample IDs;
- no exact-query, exact-answer, filename, row-order, pytest, CI, or benchmark-aware special casing;
- no answer-key-derived query expansion;
- no hidden network-only dependency;
- explicit development/holdout source overlap reporting;
- normalized exact-duplicate and near-duplicate detection;
- paraphrase-group tracking through `task_id` and `sample_id`;
- source-document overlap reporting;
- dataset version and changelog preservation;
- quarantine and replacement procedure after leakage.

Fixture-specific expected-section leakage in the current evaluation path is a known risk and must not carry into the protected benchmark.

## 28. Strict and Multi-Valid-Source Scoring

Future scoring should report separately:

- strict source and evidence-span matches against the primary reviewed oracle;
- relaxed matches against an explicit human-reviewed set of valid source IDs, aliases, or evidence spans;
- multi-valid-source cases where more than one source legitimately supports the task;
- unavailable/not-applicable metrics when an expectation is intentionally absent.

Relaxed scoring must not silently replace strict metrics, thresholds, or historical comparisons. Valid alternatives require provenance and reviewer justification; semantic similarity alone is insufficient.

## 29. Language and Paraphrase Coverage

The initial benchmark should review Korean and English coverage where source rights and reviewer capacity permit. Variants should include plain-language, technical, ambiguous, adversarial, and code-switched wording where relevant.

Rules:

- language/paraphrase variants share `task_id` only when semantic intent is unchanged;
- every variant receives a unique stable `sample_id`;
- translations are reviewed for meaning, risk, units, entity names, jurisdictional terms, and refusal/escalation expectations;
- near-duplicates are tracked rather than counted as independent coverage;
- protected paraphrases remain protected-holdout content.

## 30. Proposed Metrics

Dataset:

- task-family, source-class, and language coverage;
- development/holdout and source-document overlap;
- exact/near-duplicate rate;
- reviewer agreement and adjudication rate;
- label-change rate and benchmark churn.

Retrieval:

- source@3 and source@5;
- Recall@k, MRR, and nDCG;
- evidence-span hit rate;
- strict and relaxed multi-valid-source metrics.

Answer / claim:

- claim-level citation precision and recall;
- unsupported-claim rate;
- contradicted-claim detection;
- missing-evidence honesty;
- answer faithfulness and citation-mismatch detection.

Safety / compliance:

- abstention, refusal, and escalation accuracy;
- high-risk recall and harmless-request false-block rate;
- prompt-injection and source-poisoning detection;
- confidential-data leakage rate;
- excessive-agency detection.

Operations:

- p50/p95 latency;
- context and answer tokens;
- cost proxy;
- trace completeness;
- reviewer decision latency;
- reproducibility.

This docs-only PR claims no metric improvement.

## 31. Acceptance Criteria for Future Implementation

A separate implementation PR may pass only when:

- approved dataset ID/version, schema, and changelog exist;
- exact development/protected-holdout boundaries and storage decisions are human-approved;
- no protected content appears in public Git history, PRs, CI logs, prompts, or runtime indexes;
- source eligibility, license, confidentiality, allowed-use, and provenance checks pass;
- stable task/sample IDs are unique and row-order independent;
- proposed support-status and response-disposition contracts are separate and validated;
- high-risk gold labels have qualified human review and adjudication evidence;
- leakage, duplicate, paraphrase, and source-overlap controls are tested;
- legacy regression assets remain unchanged and continue to pass;
- strict and relaxed scoring are reported separately;
- failure taxonomy, rollback, security review, and residual risks are explicit;
- no runtime, production, approval, wet-lab, or foundation-model claim exceeds the evidence.

## 32. Validation Budget for This PR

Run only documentation checks:

```text
git status --short
git rev-parse HEAD
git rev-parse origin/main
git diff --name-only
git diff --stat
git diff --check
```

Also verify exact four-file scope, path existence, Markdown fenced-code balance, stale-status phrases, current GitHub SHAs, truth-boundary consistency, and absence of secrets/confidential/protected-holdout content.

Do not run pytest, retrieval evaluation, evaluator/validator execution, source ingestion, artifact generation, compileall, broad security scanners, vector DB commands, or KG commands. Rationale: this PR changes documentation only and does not alter executable code, schemas, fixtures, tests, CI, runtime behavior, retrieval, generation, reranking, or dependencies.

## 33. Security and Confidentiality Review

Threats to review:

- permanent protected-holdout leakage through public Git history, PR text, CI logs, or generated artifacts;
- prompt or retrieved-document instructions that request answer keys, source restrictions, credentials, or policy bypass;
- confidential biology, biodiversity, partner, permit, legal, assay, genomic, investor, or personal data exposure;
- reviewer identity exposure and over-privileged holdout access;
- benchmark-aware runtime behavior and data exfiltration;
- source-poisoning or unreviewed-source promotion;
- evaluator results being misrepresented as approval.

Controls proposed:

- public/private separation, least privilege, access logging, redaction, source eligibility, human review, leakage scans, versioned incident handling, and fail-closed validation;
- no credentials, private data, protected queries, answer keys, evidence spans, operational wet-lab instructions, or restricted biological instructions in this public preflight;
- a separate security review before private holdout storage or tooling is selected.

## 34. Digital Devil's Advocate

Scalability risks:

- expert review can become the primary bottleneck;
- broad schema and evidence-span review increase annotation cost;
- protected-holdout operations can become difficult to reproduce;
- family imbalance and repeated paraphrases can distort metrics.

Mitigations: start with a bounded review hypothesis, measure reviewer latency/agreement, version all changes, track near-duplicates, and expand only from failure evidence. Residual risk: a 32-case benchmark remains small.

Moat risks:

- 32 cases are not a proprietary data moat;
- synthetic or public cases alone do not create defensibility;
- benchmark process can become ceremony without DBTL learning or proprietary evidence.

Mitigations: require legally usable provenance, expert labels, validation records, failure learn-back, and future DBTL feedback under separate governance. Residual risk: this preflight creates no proprietary data.

Biosafety / compliance risks:

- public-repository leakage can permanently invalidate holdout and expose restricted information;
- compliance labels can be misread as approvals;
- unqualified reviewers can create false gold labels;
- biodiversity records may carry Nagoya, CITES, permit, confidentiality, or license restrictions;
- evaluator success can be misused to authorize publication or biological execution.

Mitigations: qualified role-based review, source eligibility, public/private separation, explicit response dispositions, diagnostic-only output, and mandatory human gates. Residual risk: reviewer assignment and private storage are not yet approved.

## 35. Failure Modes

- protected content committed to public history;
- development and holdout variants are exact or near duplicates;
- same source documents silently span both splits;
- expected sources, sections, or labels become retrieval features;
- task/sample IDs encode row order or trigger runtime routing;
- source license, confidentiality, or allowed use is assumed;
- reviewer role is fabricated or inadequately qualified;
- support status is collapsed into response disposition;
- strict metrics are replaced by relaxed metrics;
- harmless requests are overblocked;
- high-risk requests are under-escalated;
- benchmark changes lack versioning or changelog;
- 32-case success is presented as production safety or generalization.

## 36. Stop Rules

Stop before implementation or publication if:

- any eval, schema, fixture, script, test, workflow, registry, source, or runtime file must change in this preflight;
- protected holdout or confidential source material would enter public Git history;
- private storage, source license, allowed use, reviewer assignment, or approval must be invented;
- expected answers/sources/sections would be exposed to retrieval or generation;
- the four-file docs-only boundary cannot be preserved;
- legacy assets would need migration or reinterpretation;
- validation or GitHub evidence is unclear;
- a dependency, framework, service, destructive Git operation, vector DB, or KG change becomes necessary;
- legal, compliance, biosafety, IP/FTO, wet-lab, publication, investor, release, or production approval would be implied.

## 37. Rollback

Revert the future PR that adds this preflight and current-state synchronization. Because this PR is documentation-only, rollback requires no dataset, schema, fixture, evaluator, retrieval, runtime, registry, source, vector DB, KG, dependency, or workflow migration.

## 38. Next Separate PR Boundary

The next PR, if approved after review, may implement only the public-safe development-side dataset contract and validation scaffold or another explicitly selected narrow slice. Protected-holdout storage, private content, reviewer assignment, source promotion, evaluator logic, runtime integration, and CI gates require separately scoped approval and evidence.

No future implementation begins merely because this preflight merges.

## 39. Truth Boundary

V1.11A is a documentation-only representative biology/compliance evaluation reset preflight. No dataset, protected holdout, schema, fixture, evaluator, retrieval, generation, runtime, approval, vector DB, KG, wet-lab, autonomous execution, commercial-readiness, or foundation-model capability was implemented by this task.
