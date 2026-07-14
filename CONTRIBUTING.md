# Contributing to Asperitas AI RAG Agent

> **Status:** ACTIVE CONTRIBUTION BASELINE  
> **Version:** 1.0  
> **Scope:** Human contributors, maintainers, coding agents, automation, documentation, source governance, evaluation, and repository changes  
> **Owner:** Asperitas COO / AI Lead  
> **Classification:** PUBLIC-SAFE GOVERNANCE  
> **Authority:** This guide is subordinate to [`gitcore.md`](gitcore.md), [`SECURITY.md`](SECURITY.md), the applicable [`AGENTS.md`](AGENTS.md), live GitHub rulesets, and explicit maintainer approval.  
> **Truth boundary:** Contribution acceptance, passing CI, or merge into `main` does not establish deployment, production readiness, legal clearance, scientific validation, wet-lab validation, security completeness, or product-market fit.

Thank you for contributing to the Asperitas biological-intelligence development repository.

This repository develops deterministic, source-grounded, compliance-aware infrastructure for biological evidence workflows. Contributions are evaluated not only for code quality, but also for provenance, rights, security, evaluation integrity, scientific truth, reversibility, and operational clarity.

---

## 1. Contribution Principles

A high-quality contribution should maximize:

```text
correct scope
+ smallest sufficient change
+ source fidelity
+ measurable verification
+ preserved security and rights boundaries
+ clear rollback
+ maintainable implementation
```

A contribution is not improved merely by adding more frameworks, agents, abstractions, dependencies, prompts, documents, benchmarks, or files than the outcome requires.

Prefer the lowest-complexity implementation that satisfies a falsifiable requirement:

```text
deterministic helper
-> single model, retrieval, or tool call
-> fixed workflow
-> stateful workflow
-> agent
-> multi-agent or graph
```

A higher-complexity design must identify the failed lower-level baseline, target metric, expected gain, added cost and latency, new security burden, observability, rollback, and required evaluation evidence.

---

## 2. Read Before Contributing

Before editing the repository, read the current applicable versions of:

1. [`README.md`](README.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`gitcore.md`](gitcore.md)
4. [`SECURITY.md`](SECURITY.md)
5. [`pyproject.toml`](pyproject.toml)
6. relevant nested `AGENTS.md` files
7. relevant schemas, tests, workflows, and decision records

Live repository evidence takes precedence over stale documentation.

Resolve current implementation state from:

```text
checked-out code and configuration
-> current branch and exact commit SHA
-> current worktree diff
-> merged pull requests and commit history
-> exact-head CI and Quality Gates
-> tests, evaluations, and generated artifacts
-> deployment and runtime evidence
-> named approvals
```

Roadmaps, architecture diagrams, issue text, prompts, benchmarks, and generated reports are not proof of implementation.

---

## 3. Non-Negotiable Boundaries

### 3.1 Never expose sensitive material

Do not commit, paste, attach, quote, or expose:

- API keys, tokens, cookies, credentials, private keys, or recovery material;
- customer, partner, personal, or confidential business data;
- unpublished sequences, assays, specimens, or research results;
- sensitive species or collection-location data;
- private contracts, permits, PIC/MAT, CITES, Nagoya/ABS, DSI, LMO/GMO, IP, or FTO records;
- private source-registry contents, embeddings, indexes, traces, prompts, memories, or model data;
- protected evaluation answer keys or holdouts;
- exploit details that materially enable abuse.

For sensitive security findings, follow [`SECURITY.md`](SECURITY.md). Do not disclose sensitive details through a public issue, pull request, review, commit, screenshot, or discussion.

### 3.2 Public visibility is not a license grant

This repository does not currently establish an open-source license grant.

Do not assume that repository visibility grants permission to reuse code, redistribute files, train models, ingest source content, commercialize derived data, sublicense biological information, or publish third-party material.

Do not add third-party code, data, documents, media, model weights, prompts, or datasets unless the contribution records a valid basis for inclusion and permitted use.

This guide does not create contribution-license terms. Maintainers may reject a contribution or require separate written terms before acceptance.

### 3.3 Models and agents do not grant approval

Model output, generated code, retrieval results, automated reports, or agent decisions cannot grant:

- legal or regulatory approval;
- rights clearance;
- biosafety or biosecurity approval;
- scientific validation;
- wet-lab authorization;
- release or deployment approval;
- permission to transmit confidential information.

### 3.4 Preserve evaluation integrity

Do not:

- expose answer keys to runtime retrieval;
- optimize directly against protected holdouts;
- weaken tests after observing a failure;
- lower thresholds merely to obtain a pass;
- relabel `FAIL`, `PARTIAL`, or `NOT_TESTABLE` as `PASS`;
- remove negative cases without an approved replacement;
- use grader metadata as model input;
- claim benchmark equivalence without comparable evidence.

### 3.5 Preserve scientific truth

Do not present computational prediction as experimental validation, sequence similarity as confirmed function, one assay as replicated evidence, literature plausibility as product validation, source possession as downstream rights, or software output as legal or regulatory judgment.

---

## 4. Choose the Correct Contribution Path

### Documentation-only correction

Suitable for broken links, typographical errors, formatting defects, or clarification that does not alter authority, policy, evaluation meaning, rights interpretation, security posture, or capability claims.

### Bounded code or test change

Suitable for deterministic bug fixes, bounded validation logic, isolated tests, small CLI improvements, local error handling, or type and schema consistency.

### Material architecture or governance change

Use an issue or draft pull request before broad implementation when changing retrieval, reranking, source registries, schemas, evaluation fixtures, thresholds, compliance routing, agent permissions, workflows, CI, dependencies, ingestion, packaging, security controls, confidential-data handling, or public capability claims.

### High-impact change

Explicit maintainer approval is required before deployment, release, package publication, external transmission, source ingestion with unresolved rights, production-like data mutation, legal or scientific status promotion, wet-lab execution, or high-risk biological work.

---

## 5. Repository Preflight

Before making a material change, record:

```text
TASK:
MODE:
CHANGE_CLASS:
CURRENT_BRANCH:
CURRENT_HEAD:
WORKTREE_STATUS:
APPLICABLE_INSTRUCTIONS:
IN_SCOPE:
OUT_OF_SCOPE:
AFFECTED_FILES:
BASELINE:
SUCCESS_CRITERIA:
PROHIBITED_BEHAVIOR:
VERIFICATION:
ROLLBACK:
STOP_CONDITIONS:
```

Inspect at minimum:

```bash
git status --short --branch
git rev-parse HEAD
git branch --show-current
```

Also inspect relevant implementation files, tests, schemas, workflows, recent overlapping changes, generated artifacts, and rollback options.

Do not discard or overwrite unrelated work. Do not use destructive Git commands unless explicitly authorized.

---

## 6. Local Development Setup

### Requirements

- Python 3.10 or newer
- Git
- an isolated virtual environment
- a clean working tree before material verification

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the development baseline:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,parsers]"
```

For local quality and packaging checks:

```bash
python -m pip install -e ".[dev,parsers,quality,packaging]"
```

For explicit dependency-security review:

```bash
python -m pip install -e ".[dev,parsers,security]"
```

Security scanner output is review evidence, not proof that the repository is vulnerability-free.

Verify the installation:

```bash
python -c "import asperitas_agent; print(asperitas_agent.__version__)"
python -m asperitas_agent.cli --help
asperitas-agent --help
```

The canonical package implementation is under `src/asperitas_agent/`. The root `asperitas_agent/` path is a compatibility surface and must not become a second implementation authority.

---

## 7. Change Classification

Use the highest applicable class.

| Class | Typical contribution | Minimum verification |
|---|---|---|
| `C0` | Typo, formatting, non-semantic documentation | Diff review, link/path check, `git diff --check` |
| `C1` | Bounded deterministic code or tests | Targeted tests, static/schema checks, artifact review |
| `C2` | Retrieval, reranking, evaluation, registries, schemas, answer contracts | Frozen baseline, targeted and adjacent regression, contamination review |
| `C3` | Security, permissions, CI, dependencies, ingestion, approval logic | Threat review, adversarial tests, least-privilege review, named approval |
| `C4` | Release, deployment, external write, production data, legal/scientific clearance, high-risk biology | Explicit action approval, rollback rehearsal, post-action verification |

A policy, authority, security, rights, or evaluation-semantic change is not `C0` merely because it is written in Markdown or YAML.

---

## 8. Branch Naming

Create a focused branch from current `main`.

Recommended formats:

```text
fix/<short-description>
feat/<short-description>
test/<short-description>
docs/<short-description>
ci/<short-description>
security/<short-description>
governance/<short-description>
refactor/<short-description>
chore/<short-description>
```

Branch names should describe one cohesive outcome, avoid personal names and vague labels, and remain useful in audit and rollback records.

---

## 9. Keep Changes Cohesive

A pull request should contain one primary decision.

Good scope:

```text
one bounded behavior change
+ tests
+ directly affected documentation
```

Do not perform unrelated refactoring, reformat the entire repository, rename stable paths without migration evidence, add speculative scaffolding, create duplicate sources of truth, introduce silent dependencies, weaken tests, or mix unrelated generated artifacts with source changes.

---

## 10. Coding Standards

### Prefer deterministic components

Use deterministic logic for schema validation, metadata normalization, lifecycle transitions, hashing, permission checks, citation integrity, exact parsing, source filtering, status validation, and reproducible scoring.

Use model or agent behavior only when deterministic logic cannot satisfy the requirement.

### Preserve the standard-library core

The deterministic package core intentionally has no unconditional runtime dependencies.

A new runtime dependency requires demonstrated need, simpler-alternative analysis, maintenance and supply-chain review, supported-version bounds, license review, failure behavior, rollback, and tests showing appropriate isolation.

### Error handling

Material functions should define:

```text
input contract
output contract
failure modes
error messages
side effects
idempotency
rollback or recovery
```

Fail closed for unauthorized actions, unknown permissions, invalid registry state, unresolved source rights, contaminated evaluation, missing mandatory provenance, or ambiguous external-write authority.

### Type and schema discipline

- Use explicit types where they improve correctness.
- Validate external and untrusted input.
- Keep schemas versioned and reviewable.
- Do not introduce multiple vocabularies for one lifecycle state.
- Preserve backward compatibility or provide an explicit migration.
- Do not silently reinterpret existing metadata.

### Formatting and linting

```bash
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m mypy src/asperitas_agent
```

Do not apply broad automatic formatting to unrelated files.

---

## 11. Tests and Verification

Every behavior-changing contribution should include or update tests for expected behavior, invalid input, boundary conditions, failure behavior, permission denial, provenance preservation, rollback or idempotency where applicable, and the exact defect being fixed.

Avoid tests that depend on uncontrolled network access, current time, unstable ordering, private data, exposed answer keys, weakened fixtures, or implementation details unrelated to behavior.

Run the smallest relevant suite first, then the required broader suite.

Examples:

```bash
python -m pytest -q tests/test_source_registry_contract.py
python -m pytest -q tests/test_skill_registry.py
python -m pytest -q tests/test_sitecustomize.py
```

Full test suite:

```bash
python -m pytest
```

Artifact verification:

```bash
python scripts/verify_artifacts.py
```

Registry verification:

```bash
python -m asperitas_agent.cli validate-registry-contract
python scripts/validate_external_benchmark_registry.py
```

Retrieval evaluation when retrieval, metadata routing, ranking, or chunking can be affected:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Record the evaluated commit SHA, environment, command, fixture identity, metrics, threshold, prohibited regressions, and contamination status.

Packaging verification for package, CLI, import-path, or bootstrap changes:

```bash
python -m build
check-wheel-contents dist/*.whl
python scripts/verify_packaging_contract.py --json
python scripts/verify_distribution_install.py --dist-dir dist --json
```

Diff hygiene:

```bash
git diff --check
```

---

## 12. Source and Data Contributions

Source-related contributions must be metadata-first.

A source candidate is not automatically approved, verified, licensed, ingested, indexed, retrievable, suitable for model training, suitable for commercialization, or suitable for public claims.

Record applicable fields defined by the canonical schemas, including source identity, origin, owner, date, URL, provenance, disclosure level, verification status, license status, ingestion status, permitted use, prohibited use, risk flags, and evidence label.

Do not add raw external source files merely because a metadata record exists. Do not ingest, process, chunk, embed, index, train on, redistribute, or commercialize source content until required rights and approval state are established.

Treat these rights separately:

```text
specimen possession
source-country access
collection authority
PIC/MAT
CITES movement
research
sequencing
derived data
dataset inclusion
model training
model weights
model output
commercialization
sublicensing
patenting
customer transfer
```

One right does not automatically grant another.

---

## 13. Biological and Scientific Contributions

Use the evidence ladder:

```text
computational prediction
-> literature-supported hypothesis
-> single assay
-> replicated assay
-> independent validation
-> scale-up
-> production evidence
-> commercial evidence
```

Preserve controls, replicates, uncertainty, negative results, assay conditions, versioned inputs, provenance, failure taxonomy, and next decision.

Do not submit high-risk wet-lab instructions, pathogenic enhancement, regulatory-evasion guidance, unauthorized genetic-resource use, or autonomous laboratory execution.

---

## 14. Evaluation Contributions

Before changing an evaluator, fixture, threshold, or grader, define:

```text
evaluation identity
input set
environment
expected behavior
prohibited behavior
rubric
criticality
threshold
number of trials
contamination controls
```

Separate runner input, ground truth, grader metadata, and runtime retrieval corpus. Do not expose protected ground truth to the evaluated system.

A valid evaluation report identifies exact commit SHA, evaluator version, fixture version, environment, commands, metrics, threshold, failure cases, invalid or untestable cases, and limitations.

Changes made after observing results require a fresh clean evaluation.

---

## 15. Security Contributions

Security changes should identify the protected asset, threat or failure mode, trust boundary, attacker capability, expected security property, least-privilege analysis, failure behavior, targeted test, adjacent regression, rollback, and residual risk.

Do not claim that a scanner result or passing test proves the repository is secure.

For sensitive findings, do not open a public issue or pull request. Follow [`SECURITY.md`](SECURITY.md).

---

## 16. Dependency Contributions

A dependency addition or upgrade should document:

```text
package:
current_version:
proposed_version:
purpose:
simplest_alternative:
runtime_or_optional:
license_review:
security_review:
transitive_dependency_impact:
supported_python_versions:
size_impact:
failure_behavior:
tests:
rollback:
```

Prefer compatible version ranges, optional extras for non-core capabilities, official maintained packages, and minimal transitive dependency trees.

Avoid unclear provenance, silent major-version upgrades, trivial-helper dependencies, unauthorized network access, or changes that weaken supported Python versions.

---

## 17. Documentation Contributions

Documentation must distinguish:

| Status | Meaning |
|---|---|
| `DOCUMENTED` | Described in a repository artifact |
| `IMPLEMENTED` | Code or configuration exists |
| `TESTED` | Named tests ran in a stated environment |
| `CI_VERIFIED` | Required checks passed on the exact evaluated SHA |
| `APPROVED` | A named human granted the specific authority |
| `DEPLOYED` | Deployment evidence exists for a named environment |
| `OPERATIONALLY_VERIFIED` | Runtime behavior was observed |
| `PRODUCTION_READY` | Release, security, operations, compliance, ownership, and rollback gates passed |
| `PLANNED` | Intended future work |
| `UNVERIFIED` | Evidence is missing, stale, inaccessible, or insufficient |
| `BLOCKED` | A mandatory gate failed |
| `INVALID` | Evidence integrity or comparability failed |

Do not describe a planned capability as implemented, a CI-passing component as deployed, or a public benchmark as evidence of Asperitas implementation.

Do not attribute private prompts, workflows, or undisclosed engineering methods to external companies or individuals.

---

## 18. AI-Assisted Contributions

AI-assisted work is permitted, but the contributor remains responsible for correctness, security, licensing, provenance, hallucinated APIs or files, fabricated citations, unauthorized disclosure, evaluation contamination, overclaiming, and unnecessary complexity.

Do not paste confidential material into an external model or tool without explicit authorization.

Disclose material AI assistance when it affected architecture, implementation, tests, security analysis, source selection, biological interpretation, or legal and compliance extraction.

Suggested disclosure:

```text
AI assistance:
- Tool or model:
- Scope:
- Human verification performed:
- External data transmitted:
- Known limitations:
```

Model output is not reviewer approval.

---

## 19. Commit Guidelines

Commits should be cohesive, reviewable, reversible, free of unrelated formatting, free of local artifacts or secrets, and descriptive enough for audit and rollback.

Recommended format:

```text
type(scope): imperative summary
```

Examples:

```text
fix(registry): reject duplicate source identifiers
test(bootstrap): cover repository path deduplication
docs(governance): add contribution requirements
ci(packaging): verify clean wheel installation
security(permissions): fail closed on unknown write authority
```

Do not use commit messages to claim verification that did not occur.

---

## 20. Pull Request Requirements

All changes to `main` must go through a pull request under the active repository ruleset.

A pull request should include:

```markdown
## Decision

What exact outcome does this pull request implement?

## Baseline

What is the current behavior, evidence, bottleneck, and simplest alternative?

## Scope

### In scope

- ...

### Out of scope

- ...

## Change class

C0 / C1 / C2 / C3 / C4

## Changes

- exact file and behavior changes

## Truth status

- DOCUMENTED:
- IMPLEMENTED:
- TESTED:
- CI_VERIFIED:
- UNVERIFIED:
- BLOCKED:

## Verification

- exact commands
- test results
- evaluation identity
- exact head SHA

## Security, rights, and biology review

- trust boundaries
- sensitive data
- source rights
- biosafety or compliance impact

## Failure modes

- expected failures
- prohibited behavior
- residual risks

## Rollback

- exact revert or restoration path
```

A pull request is not ready when scope is ambiguous, unrelated files are included, required tests are absent, tests are weakened, provenance is missing, rights status is overstated, sensitive information is exposed, evidence cannot be tied to the exact head, rollback is undefined, or capability claims exceed evidence.

Use a draft PR for early C2-C4 design review, architecture changes, security-sensitive design without sensitive disclosure, work awaiting baseline measurement, or work awaiting full regression.

---

## 21. Required Merge Gates

The live GitHub ruleset and workflow definitions are authoritative.

Expected required check contexts currently include:

```text
Python smoke checks
tests-artifacts-retrieval-eval
ubuntu-latest / Python 3.10
ubuntu-latest / Python 3.11
windows-latest / Python 3.11
```

Before merge:

- the PR branch must be up to date with `main`;
- all required checks must pass;
- review conversations must be resolved;
- force push must not be used to bypass review;
- merge must use the allowed repository merge method;
- the evaluated head SHA must match the merge decision.

Historical successful checks do not certify a new head.

---

## 22. Review Standards

Reviewers evaluate correctness, scope, evidence, security, source governance, evaluation integrity, biology and compliance, failure behavior, observability, maintainability, and rollback.

Review outcomes may be:

```text
APPROVE
REQUEST_CHANGES
DEFER
BLOCK
SUPERSEDED
```

A request for changes identifies unmet repository requirements; it is not a personal judgment.

---

## 23. Merge and Post-Merge Expectations

Use the repository-approved merge method, normally squash merge.

The squash commit should describe the decision, primary implementation, important verification, material limitations, and rollback identity.

After merge:

1. verify the resulting `main` commit;
2. confirm required workflows;
3. verify that no unexpected files were introduced;
4. update implementation status only when evidence supports it;
5. convert significant failures into durable tests, schemas, controls, or decision records.

A merged pull request proves only that code or documentation was merged. It does not by itself prove deployment, runtime correctness, vulnerability absence, legal or regulatory clearance, scientific validation, wet-lab validation, production readiness, or customer demand.

---

## 24. Unacceptable Contributions

Maintainers may close or reject contributions that expose confidential information, include unauthorized source material, weaken tests or thresholds, introduce prompt injection or permission bypass, make unverified legal/scientific/security/production claims, include high-risk biological instructions, duplicate authority or schema, introduce excessive architecture without baseline evidence, mix unrelated changes, lack provenance, conceal unverified AI-generated content, violate conduct expectations, or cannot be safely reviewed and rolled back.

---

## 25. Final Contributor Checklist

```text
[ ] I read README.md, AGENTS.md, gitcore.md, and SECURITY.md.
[ ] I recorded the exact base and head SHAs.
[ ] The branch contains one cohesive outcome.
[ ] Unrelated user or agent work is preserved.
[ ] No secrets, confidential data, or restricted biological information are included.
[ ] Third-party code and data have a documented permitted basis.
[ ] Scientific, legal, security, and production claims match the evidence.
[ ] Tests cover intended behavior and relevant failures.
[ ] I did not weaken fixtures, thresholds, schemas, or expected behavior to obtain a pass.
[ ] Runtime inputs are isolated from evaluation ground truth.
[ ] Targeted tests pass.
[ ] Full pytest passes when required.
[ ] Artifact and registry verification pass when applicable.
[ ] Retrieval evaluations were rerun when retrieval behavior could change.
[ ] Packaging checks were rerun when package, CLI, or import behavior could change.
[ ] Ruff and diff hygiene checks pass for the affected surface.
[ ] The PR documents verification on its exact head SHA.
[ ] Security, rights, compliance, and biology impacts are disclosed.
[ ] AI assistance is disclosed when material.
[ ] Rollback is explicit and feasible.
[ ] All required GitHub checks pass.
[ ] All review conversations are resolved.
```

Thank you for helping build verifiable, safe, and commercially credible biological-intelligence infrastructure.
