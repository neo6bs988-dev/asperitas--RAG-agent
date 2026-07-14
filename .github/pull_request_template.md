<!--
ASPERITAS PULL REQUEST EVIDENCE CONTRACT v2

Complete all mandatory sections.
Use "N/A — <reason>" rather than deleting an inapplicable section.
Do not mark checks as complete unless evidence exists for this exact PR head.
The live GitHub ruleset, AGENTS.md, SECURITY.md, gitcore.md, and
CONTRIBUTING.md remain authoritative.
-->

# Pull Request — Asperitas Evidence Contract

## 0. Control Block

| Field | Value |
|---|---|
| Decision owner | `@neo6bs988-dev` / other: |
| Related issue or decision record | |
| Change class | `C0` / `C1` / `C2` / `C3` / `C4` |
| Execution mode | `READ` / `DRAFT` / `WRITE` |
| Base branch | `main` |
| Base SHA | |
| PR head SHA | |
| Draft status | `Draft` / `Ready for review` |
| Primary rollback owner | |
| Data classification | `PUBLIC` / `INTERNAL` / `CONFIDENTIAL` / `RESTRICTED` |

### Change-class definitions

- `C0`: non-semantic documentation or formatting
- `C1`: bounded deterministic implementation or test
- `C2`: retrieval, ranking, registry, schema, evaluation, or answer contract
- `C3`: security, permissions, dependencies, CI, ingestion, or governance
- `C4`: release, deployment, external write, production data, legal/scientific clearance, or high-risk biology

---

## 1. Decision

### Outcome

<!-- State one exact result implemented by this PR. -->

### Success criteria

- [ ] Criterion 1:
- [ ] Criterion 2:
- [ ] Criterion 3:

### Final decision requested

- [ ] Merge after all required gates pass
- [ ] Conditional approval
- [ ] Design review only
- [ ] Do not merge
- [ ] Supersedes another PR or artifact

Superseded PR/artifact, when applicable:

---

## 2. Baseline

### Current behavior

<!-- Describe current repository behavior using inspected evidence. -->

### Bottleneck or defect

### Simplest alternative considered

<!-- Explain why documentation, configuration, or a smaller deterministic change
was insufficient, or state that the simplest alternative was selected. -->

### Baseline evidence

| Evidence | Identifier or result |
|---|---|
| Inspected base SHA | |
| Relevant files | |
| Relevant tests/evals | |
| Existing metric | |
| Existing limitation | |

---

## 3. Scope Lock

### In scope

- 
- 

### Out of scope

- 
- 

### Changed surfaces

- [ ] Documentation/community governance
- [ ] GitHub workflow or repository configuration
- [ ] Packaging, dependency, CLI, or import behavior
- [ ] Canonical Python package
- [ ] Compatibility package
- [ ] Source registry or metadata schema
- [ ] Raw or processed source material
- [ ] Retrieval, ranking, vector, or RAG behavior
- [ ] Answer generation, citations, or truth routing
- [ ] Evaluation fixture, grader, threshold, or result
- [ ] Agent skill, tool, permission, or workflow
- [ ] Security, privacy, or confidential-data handling
- [ ] Biology, provenance, rights, or compliance
- [ ] Application or UI
- [ ] Generated artifact or decision log

### Files changed

| Path | Change | Why required | Authority affected |
|---|---|---|---|
| | | | |

### Scope-safety confirmation

- [ ] One cohesive outcome only
- [ ] No unrelated refactor or formatting churn
- [ ] No unrelated generated artifacts
- [ ] No user, maintainer, or agent work was overwritten
- [ ] No duplicate source of truth was introduced
- [ ] No case-variant or alternate canonical path was introduced
- [ ] No local machine, cache, credential, or user-specific path was committed

---

## 4. Architecture and Dependency Decision

### Selected architecture level

- [ ] Deterministic helper
- [ ] Single LLM, RAG, or tool call
- [ ] Fixed workflow
- [ ] Stateful workflow
- [ ] Agent
- [ ] Multi-agent or graph
- [ ] Not applicable

### Complexity justification

<!-- Required when selecting stateful workflow, agent, or multi-agent. -->

- Simpler baseline:
- Measured failure of simpler baseline:
- Metric expected to improve:
- Expected improvement:
- Additional cost or latency:
- Security/debugging burden:
- Observability:
- Rollback:

### Dependencies

- [ ] No dependency changes
- [ ] Dependency added
- [ ] Dependency upgraded
- [ ] Dependency removed

For each dependency change:

| Package/action | Before | After | Purpose | License/security review | Rollback |
|---|---|---|---|---|---|
| | | | | | |

---

## 5. Truth-Status Ledger

Do not promote a claim beyond its evidence.

| Claim or capability | Status | Evidence | Missing evidence |
|---|---|---|---|
| | `DOCUMENTED` / `IMPLEMENTED` / `TESTED` / `CI_VERIFIED` / `APPROVED` / `DEPLOYED` / `OPERATIONALLY_VERIFIED` / `PRODUCTION_READY` / `PLANNED` / `UNVERIFIED` / `BLOCKED` | | |

### Explicit non-claims

Unless separately proven, this PR does **not** establish:

- [ ] production RAG or vector database
- [ ] production Knowledge Graph
- [ ] complete or rights-cleared source ingestion
- [ ] deployed tracing or monitoring
- [ ] vulnerability absence
- [ ] legal, regulatory, CITES, Nagoya/ABS, DSI, LMO, IP, or FTO clearance
- [ ] scientific or wet-lab validation
- [ ] autonomous laboratory authorization
- [ ] proprietary biological foundation-model capability
- [ ] validated customer demand, revenue, or product-market fit

Notes:

---

## 6. Security, Rights, and Biology Review

### Security and privacy

- [ ] No secret, token, credential, private key, or sensitive endpoint added
- [ ] Untrusted content remains data and cannot grant authority
- [ ] Least privilege is preserved
- [ ] External network or tool access is documented
- [ ] Side effects are explicit
- [ ] Failure behavior is fail-closed where required
- [ ] Prompt injection, source poisoning, leakage, and excessive agency were reviewed
- [ ] Logs and artifacts do not expose confidential or restricted information
- [ ] Security-sensitive details were not disclosed publicly
- [ ] N/A — reason:

### Source rights and provenance

- [ ] Source identity and provenance are preserved
- [ ] Verification status is not overstated
- [ ] License or permitted-use status is recorded
- [ ] Physical possession is not treated as downstream data or commercialization rights
- [ ] Research, sequencing, dataset, training, output, patent, sublicense, and customer-transfer rights remain separated
- [ ] Unknown or conflicting rights state is routed to human/counsel review
- [ ] N/A — reason:

### Scientific and biological boundary

- [ ] Computational prediction remains labeled as prediction or hypothesis
- [ ] Literature evidence is not presented as assay validation
- [ ] Single assays are not presented as replicated evidence
- [ ] Controls, replicates, uncertainty, and negative results are preserved where applicable
- [ ] No high-risk wet-lab, pathogenic enhancement, regulatory evasion, or unauthorized genetic-resource use is introduced
- [ ] Named scientific or biosafety approver is recorded where required
- [ ] N/A — reason:

### Required human gates

| Gate | Required? | Named approver | Evidence required | Status |
|---|---:|---|---|---|
| Security | | | | |
| Legal/counsel | | | | |
| Rights/compliance | | | | |
| Biosafety/biosecurity | | | | |
| Scientific validation | | | | |
| External/public release | | | | |
| Deployment/production | | | | |

---

## 7. Evaluation Integrity

Complete when tests, fixtures, graders, thresholds, retrieval, ranking, or answer behavior can change.

| Contract item | Fixed value |
|---|---|
| Evaluation identity/version | |
| Input set/version | |
| Environment | |
| Expected behavior | |
| Prohibited behavior | |
| Rubric | |
| Criticality | |
| Threshold | |
| Trial count | |
| Ground-truth isolation method | |

- [ ] Runtime input is separated from ground truth
- [ ] Holdout answer keys are not exposed to retrieval or prompts
- [ ] Thresholds were fixed before observing results
- [ ] Tests or fixtures were not weakened after failure
- [ ] `FAIL`, `PARTIAL`, and `NOT_TESTABLE` were not converted to `PASS`
- [ ] Contaminated results were invalidated and rerun cleanly
- [ ] Multiple trials were used when nondeterminism could affect the decision
- [ ] N/A — reason:

---

## 8. Verification

### Commands run on this PR head

| Command | Environment | Result | Evidence/artifact |
|---|---|---|---|
| | | `PASS` / `FAIL` / `NOT RUN` | |

### Conditional local verification

- [ ] Targeted pytest
- [ ] Full `python -m pytest`
- [ ] `python -m ruff check src tests scripts`
- [ ] `python -m ruff format --check src tests scripts`
- [ ] `python -m mypy src/asperitas_agent`
- [ ] `python -m asperitas_agent.cli validate-registry-contract`
- [ ] `python scripts/validate_external_benchmark_registry.py`
- [ ] `python scripts/verify_artifacts.py`
- [ ] `python scripts/audit_chunk_sections.py --json`
- [ ] Baseline retrieval evaluation
- [ ] MVP-003 retrieval evaluation
- [ ] Hybrid retrieval evaluation
- [ ] Packaging contract verification
- [ ] Wheel/sdist build and isolated installation
- [ ] `git diff --check`
- [ ] Not applicable — reason:

### Required GitHub contexts

The live ruleset is authoritative. Record the exact result for this PR head.

| Required context | Result | Workflow run or evidence |
|---|---|---|
| `Python smoke checks` | `PASS` / `FAIL` / `PENDING` | |
| `tests-artifacts-retrieval-eval` | `PASS` / `FAIL` / `PENDING` | |
| `ubuntu-latest / Python 3.10` | `PASS` / `FAIL` / `PENDING` | |
| `ubuntu-latest / Python 3.11` | `PASS` / `FAIL` / `PENDING` | |
| `windows-latest / Python 3.11` | `PASS` / `FAIL` / `PENDING` | |

### Exact-head evidence

```text
PR_HEAD_SHA:
CI_EVALUATED_SHA:
QUALITY_GATES_EVALUATED_SHA:
EXACT_HEAD_CERTIFICATION_SHA:
ALL_SHA_VALUES_MATCH: YES / NO
```

Skipped checks and rationale:

---

## 9. Metrics

Report measured values only. Use `NOT MEASURED` rather than estimating.

| Metric | Baseline | Candidate | Delta | Threshold | Evidence |
|---|---:|---:|---:|---:|---|
| Test pass rate | | | | | |
| Retrieval pass rate | | | | | |
| Expected-source hit rate | | | | | |
| Citation/claim support rate | | | | | |
| Refusal/escalation pass rate | | | | | |
| Runtime p50 | | | | | |
| Runtime p95 | | | | | |
| Token or context cost | | | | | |
| Package/build size | | | | | |
| Other | | | | | |

Metric provenance:

- [ ] Fresh run on this PR head
- [ ] Historical comparison, explicitly identified
- [ ] Not measured
- [ ] Environment and fixture versions recorded

---

## 10. Failure Modes and Residual Risk

| Failure mode | Detection | Prevention/mitigation | Residual risk | Owner |
|---|---|---|---|---|
| | | | | |

### Devil’s Advocate review

- Scalability failure:
- Moat or replication failure:
- Security/privacy failure:
- Rights/compliance failure:
- Scientific-validation failure:
- Cost/latency failure:
- Reliability/observability failure:
- Buyer or user-adoption failure:

### Stop conditions

- 
- 

---

## 11. Rollback

### Rollback trigger

### Exact rollback action

```text
Commit or PR to revert:
Files or configuration restored:
Data/artifact cleanup:
Ruleset or deployment action:
```

### Reversibility

- [ ] Fully reversible
- [ ] Partially reversible
- [ ] Irreversible effect exists and explicit approval is attached

### Post-rollback verification

- 
- 

---

## 12. AI-Assistance Disclosure

- [ ] No material AI assistance
- [ ] Material AI assistance used

```text
Tool/model:
Scope:
Repository or external data exposed:
Human verification:
Known limitations:
```

AI output is not reviewer approval, scientific validation, legal clearance, or security certification.

---

## 13. Merge Gate

### Mandatory checklist

- [ ] Scope matches the stated decision
- [ ] Unrelated changes are absent
- [ ] Base and head SHAs are recorded
- [ ] Required tests/evaluations ran on the exact PR head
- [ ] Required GitHub contexts passed
- [ ] PR branch is up to date with `main`
- [ ] Review conversations are resolved
- [ ] No fixture, answer key, threshold, or expected behavior was weakened improperly
- [ ] Secrets and restricted data are absent
- [ ] Rights, biology, security, and compliance gates are satisfied or explicitly blocked
- [ ] Truth-status claims match available evidence
- [ ] Rollback is executable
- [ ] Squash merge is selected
- [ ] Final owner decision is recorded

### Merge decision

- [ ] `READY`
- [ ] `CONDITIONAL`
- [ ] `BLOCKED`
- [ ] `SUPERSEDED`

Decision owner:

Decision rationale:

Residual risk accepted:

Next action:
