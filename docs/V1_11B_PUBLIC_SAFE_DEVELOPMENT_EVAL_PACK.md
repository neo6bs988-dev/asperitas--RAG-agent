# V1.11B Public-Safe Development Evaluation Pack

## Executive Bottom Line

V1.11B implements a deterministic, standard-library-only validation contract and exactly 20 synthetic public-safe development fixtures for representative biology/compliance evaluation development.

The pack is a development fixture and validation scaffold. It contains no protected-holdout record, private source, actual reviewer identity, approved human gold label, runtime integration, retrieval/reranking change, answer-generation change, approval authority, or production-readiness evidence.

## Confirmed Base

- repository: `neo6bs988-dev/asperitas--RAG-agent`;
- PR #170: squash-merged after exact-head, exact-scope, review, CI, Quality Gates, mergeability, security, and truth-boundary checks passed;
- PR #170 merge SHA and V1.11B base SHA: `128c1c030a5e225b5767f3b2b96bf979173aa517`;
- V1.11B branch: `codex/v1-11b-public-safe-dev-eval-pack`.

## Exact Implementation

V1.11B adds exactly seven files:

1. `eval/v1_11b_representative_biology_compliance_dev.schema.json`
2. `eval/v1_11b_representative_biology_compliance_dev.jsonl`
3. `eval/v1_11b_representative_biology_compliance_dev_manifest.json`
4. `scripts/validate_v1_11b_representative_biology_compliance_dev.py`
5. `tests/test_v1_11b_representative_biology_compliance_dev.py`
6. `docs/V1_11B_PUBLIC_SAFE_DEVELOPMENT_EVAL_PACK.md`
7. `09_LOGS/decision_logs/v1_11b_public_safe_development_eval_pack.md`

Dataset identity:

- `dataset_id`: `asperitas_representative_biology_compliance_eval`;
- `dataset_version`: `0.1.0-dev`;
- status: `draft_public_safe_development_only`;
- split: `development` only.

## Dataset Distribution

| Task family | Records |
|---|---:|
| Biodiversity / species / provenance | 2 |
| Compliance / CITES / Nagoya / LMO / biosafety | 4 |
| Genome / protein / pathway / biological claims | 3 |
| DBTL planning and validation honesty | 2 |
| IP / licensing / commercial / investor claims | 2 |
| Source grounding / citation / contradiction / reasoning | 4 |
| Security / adversarial / prompt injection / source poisoning | 3 |
| Total | 20 |

Language coverage:

- Korean: 8;
- English: 8;
- Korean-English mixed: 4.

Stable variant coverage:

- 17 semantic `task_id` values;
- 20 unique `sample_id` values;
- 3 task groups have two substantive language/wording variants;
- IDs are independent of row order and answer text.

All six support statuses and all five response dispositions occur at least once. Support status and response disposition remain separate contracts.

## Schema Contract

The JSON Schema uses draft 2020-12 and provides:

- root-object-only validation;
- `additionalProperties: false` at record and source-reference boundaries;
- explicit required fields and enums;
- stable task, sample, source, and evidence-locator patterns;
- deliberate `null` for unreviewed `reviewed_at`;
- exact public-safe source constants;
- development-only split;
- diagnostic/development-only description.

The schema contains no protected-holdout field, expected answer text, expected source file, expected chunk/section, retrieval hint, runtime route, or approval status.

## Validator Contract

`scripts/validate_v1_11b_representative_biology_compliance_dev.py`:

- uses Python standard library only;
- performs deterministic read-only validation;
- accepts `--schema`, `--fixtures`, and `--manifest` overrides for isolated tests;
- provides human-readable default output and deterministic `--json` output;
- exits zero only when the complete contract passes;
- reports dataset identity, record/family/language/task/sample counts, label coverage, source eligibility, review status, leakage controls, errors, warnings, and truth boundary;
- never uses network, subprocess, shell execution, environment secrets, fixture mutation, or repository writes.

## Test Evidence

Fresh local evidence recorded during implementation:

```text
python scripts/validate_v1_11b_representative_biology_compliance_dev.py
PASS — 20 records; exact family distribution; ko=8, en=8, ko_en=4; 17 tasks; 20 samples; 3 multi-sample task groups; all support/disposition values covered; source/review/leakage checks PASS.

python scripts/validate_v1_11b_representative_biology_compliance_dev.py --json
PASS — deterministic JSON; errors=[]; warnings=[].

python -m compileall -q scripts/validate_v1_11b_representative_biology_compliance_dev.py
PASS.

python -m pytest -q tests/test_v1_11b_representative_biology_compliance_dev.py
37 passed in 1.15s.

pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py tests/test_v1_8b_offline_answer_scoring.py tests/test_v1_10b_answer_sample_report.py tests/test_v1_11b_representative_biology_compliance_dev.py
76 passed in 3.33s.

python -m asperitas_agent.cli verify-artifacts
PASS — ok=true; registry_records=59; chunk_count=2933; unsupported_sources=[]; errors=[]; warnings=[].

python -m pytest -q
INCOMPLETE — 702 passed in 2018.12s (0:33:38), then interrupted after more than 20 minutes without progress and a 30-second CPU delta of 0. This is not full-suite PASS evidence.
```

Bounded V1.4C triage result: `BASELINE_OR_ENVIRONMENT_REPRODUCED`.

- The interrupted run's collect-only order placed `tests/test_v1_4c_latency_eval_harness_caching.py::test_v1_4c_script_writes_outputs` immediately after the 702 completed nodes; collect order alone was not treated as causality proof.
- Seven directly relevant V1.4C test/script/dependency files had identical SHA-256 hashes on exact-main baseline `128c1c030a5e225b5767f3b2b96bf979173aa517` and the V1.11B branch.
- Direct V1.4C script: baseline timeout at 600.682 seconds; branch timeout at 600.686 seconds; both had empty stdout/stderr tails.
- Exact V1.4C pytest node: baseline timeout at 600.755 seconds; branch timeout at 600.497 seconds; both collected one item and stalled while running the same node.
- The whole V1.4C module probe was not run because the direct and exact-node probes did not terminate, as required by the bounded triage contract.
- No V1.11B file is in the V1.4C dependency path.

This evidence permits V1.11B publication while preserving local full-suite status as `INTERRUPTED / UNVERIFIED`. It does not turn the local run into PASS. The historical `831 passed` V1.10 result remains historical evidence only.

`pytest -q` (the console entrypoint) was also observed to fail collection for pre-existing `apps`/`scripts` imports; `python -m pytest` preserves repository-root imports and is the correct entrypoint used for the recorded run.

Retrieval evaluation is not run because retrieval, chunking, embeddings, metadata scoring, hybrid scoring, reranking, answer generation, and runtime behavior are unchanged.

## Source Eligibility

Only source references with all of these exact properties are eligible:

- `source_kind = synthetic_public_eval_summary`;
- `source_status = synthetic_public_safe`;
- `verification_status = synthetic_fixture_verified`;
- `license_status = synthetic_fixture_public_use`;
- `allowed_use = public_test_fixture_only`;
- stable synthetic source ID and evidence locator;
- compact synthetic evidence summary and limitations.

Candidate, needs-review, blocked, restricted, confidential, unknown-license, private, holdout, production-index-only, or raw unreviewed sources fail validation. Repository presence grants no eligibility. No existing Asperitas source is promoted or copied.

## Leakage Controls

The validator rejects or detects:

- non-development and protected/holdout splits;
- protected/private content markers;
- expected-answer, expected-source, expected-section, retrieval-hint, runtime-routing, and row-order identity fields;
- duplicate sample IDs and normalized queries;
- invalid stable IDs;
- manifest record/family mismatches;
- dataset ID/version mismatches;
- unknown fields and enums;
- ineligible source, verification, license, or allowed-use metadata;
- fake approval or completed-review claims;
- secret-like strings;
- unsafe operational biological instructions;
- source-instruction injection strings.

Retrieved/source text is treated as untrusted data, never as control instructions. The validator is a bounded contract checker, not a complete DLP, malware scanner, semantic evaluator, or runtime security system.

## Review-Status Boundary

Every fixture has:

- `review_status = draft_unreviewed`;
- `reviewer_id_or_placeholder = unassigned_role_placeholder`;
- `reviewed_at = null`;
- a role placeholder only.

No qualified reviewer is assigned. The validator rejects approved-gold, completed-review, legal, compliance, biosafety, publication, and release approval claims. Validator output grants no approval.

## Implemented / Not Implemented

Implemented:

- strict schema;
- exactly 20 synthetic public-safe development fixtures;
- independent manifest expectations;
- deterministic validator;
- positive and temporary-file negative regression tests;
- implementation record and decision log.

Not implemented:

- protected holdout or private storage;
- human-reviewed gold labels or reviewer assignment;
- source-registry promotion or real source ingestion;
- evaluator scoring of model answers;
- retrieval, reranking, answer-generation, runtime-verifier, or runtime-blocking behavior;
- CI workflow changes or dependencies;
- vector DB, KG, wet-lab validation, autonomous execution, release, deployment, or production readiness;
- legal, compliance, biosafety, regulatory, IP/FTO, publication, investor, or commercial approval.

## Scalability / Moat / Biosafety-Compliance Review

Scalability:

- twenty cases remain small;
- manual label review can become a bottleneck;
- schema breadth adds maintenance cost;
- deterministic rules may become brittle as contracts evolve.

Mitigation: stable versioned IDs, independent manifest counts, targeted diagnostics, and failure-driven additions. Residual risk: operational annotation and review scaling remain unproven.

Moat:

- public synthetic fixtures are not proprietary biological data;
- evaluation infrastructure is workflow leverage, not a biological moat;
- defensibility requires legally usable data, provenance, qualified expert labels, DBTL feedback, validation records, and repeated measured improvement.

Biosafety / compliance:

- synthetic labels are not legal or compliance conclusions;
- no operational biological instructions or actual sensitive biology data are included;
- source and review metadata fail closed;
- evaluator/validator success cannot authorize biology work, publication, external communication, or release;
- future protected holdout requires separate private governance and human approval.

## Validation Commands

Required validation sequence:

```text
git diff --name-only
git diff --stat
git diff --check
python scripts/validate_v1_11b_representative_biology_compliance_dev.py
python scripts/validate_v1_11b_representative_biology_compliance_dev.py --json
python -m compileall -q scripts/validate_v1_11b_representative_biology_compliance_dev.py
python -m pytest -q tests/test_v1_11b_representative_biology_compliance_dev.py
python -m pytest -q tests/test_v1_7c_biology_compliance_golden_set_validator.py tests/test_v1_8b_offline_answer_scoring.py tests/test_v1_10b_answer_sample_report.py tests/test_v1_11b_representative_biology_compliance_dev.py
python -m asperitas_agent.cli verify-artifacts
python -m pytest -q
```

## Skipped Checks

Retrieval evaluation: Not Run — unchanged retrieval surface.

Source ingestion and unrelated artifact regeneration: Not Run — forbidden and unnecessary for the seven-file additive implementation.

Full/deep Codex Security scan: Not Run — the approved security budget requires exact diff, dependency/network/shell/process, secret, protected-biology, unsafe-biology, path/write, subprocess, and untrusted-source review only.

## Residual Risks

- The dataset remains small, synthetic, public, draft, and unreviewed.
- Deterministic phrase/pattern checks can have semantic false positives or false negatives.
- Three variant groups do not demonstrate broad multilingual robustness.
- No protected holdout or generalization evidence exists.
- No model answer, retrieval system, runtime verifier, latency, token, or cost measurement is performed.
- Qualified review roles and private governance remain future human decisions.
- Local full-suite completion remains unverified because the pre-existing V1.4C stall reproduced on baseline and branch; clean GitHub Actions remains the publication and merge evidence gate.

## Rollback

Revert the V1.11B implementation commit. The change is additive and requires no runtime, registry, source, retrieval, generated-artifact, dependency, vector DB, KG, or deployment migration.

## Next Phase

After Draft PR review and explicit approval, the next bounded decision should select one of:

1. qualified human calibration of the public development labels and disagreement process; or
2. a separately governed private protected-holdout storage/access design; or
3. a retrieval-baseline experiment only after public-safe source mappings and scoring inputs are separately approved.

Do not start retrieval/reranker optimization merely because these fixtures validate.

## Truth Boundary

V1.11B implements a deterministic public-safe development evaluation pack only. It does not implement or prove a protected holdout, human-approved gold labels, retrieval improvement, generation improvement, runtime verification, runtime blocking, legal/compliance/biosafety/IP approval, vector DB, KG, wet-lab validation, autonomous execution, commercial readiness, production readiness, or biological foundation-model capability.
